import os
import time
import json
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from src.core.gemini_provider import GeminiProvider
from src.chatbot import Chatbot
from src.agent.agent import ReActAgent, AgentAction, AgentFinish
from src.agent.tools import TOOLS as agent_tools

app = FastAPI(
    title="Gold Advisor API",
    description="REST API cho Chatbot và ReAct Agent tư vấn vàng",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ChatbotRequest(BaseModel):
    user_input: str
    history: Optional[List[Dict[str, str]]] = None  # [{"role": "user"|"assistant", "content": "..."}]


class ChatbotResponse(BaseModel):
    response: str
    latency_ms: int
    usage: Optional[Dict[str, Any]] = None


class AgentRequest(BaseModel):
    user_input: str
    max_steps: int = 5


class AgentStep(BaseModel):
    step: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None


class AgentResponse(BaseModel):
    response: str
    steps: List[AgentStep]
    total_steps: int
    latency_ms: int


# ---------------------------------------------------------------------------
# Provider factory (lazy singleton per request – stateless)
# ---------------------------------------------------------------------------


def _make_provider() -> GeminiProvider:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY chưa được cấu hình.")
    return GeminiProvider(
        model_name=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        api_key=api_key,
    )


# ---------------------------------------------------------------------------
# Instrumented agent that captures intermediate steps
# ---------------------------------------------------------------------------


class InstrumentedAgent(ReActAgent):
    """Subclass of ReActAgent that records each ReAct step."""

    def run_instrumented(self, user_input: str):
        """
        Returns (final_answer: str, steps: List[AgentStep]).
        """
        from jinja2 import Template

        histories: List[str] = []
        recorded_steps: List[AgentStep] = []
        iteration = 1
        start_time = time.time()

        while iteration <= self.max_steps:
            if self.max_time is not None and (time.time() - start_time) >= self.max_time:
                return "Agent stopped due to time limit.", recorded_steps

            prompt = self._build_human_prompt(user_input, histories)
            raw_text = self._call_llm(prompt)
            parsed, success = self._parse_output(raw_text)

            if not success:
                if self.handle_parsing_errors:
                    observation = (
                        'Invalid JSON format. Respond with one of:\n'
                        '{"thought": "...", "action": "tool_name", "action_input": "..."}\n'
                        '{"thought": "...", "final_answer": "..."}'
                    )
                    histories.append(json.dumps({"thought": "(parse error)", "observation": observation}, ensure_ascii=False))
                else:
                    raise ValueError(f"Failed to parse LLM output:\n{raw_text}")
            elif isinstance(parsed, AgentFinish):
                recorded_steps.append(AgentStep(
                    step=iteration,
                    thought=parsed.thought,
                ))
                return parsed.output, recorded_steps
            else:
                action: AgentAction = parsed
                tool_found = any(t["name"] == action.tool for t in self.tools)

                if not tool_found:
                    observation = f"Tool '{action.tool}' not found. Available: {[t['name'] for t in self.tools]}"
                else:
                    try:
                        observation = self._execute_tool(action.tool, action.tool_input)
                    except Exception as exc:
                        if self.handle_tool_errors:
                            observation = f"Error: {exc}"
                        else:
                            raise

                recorded_steps.append(AgentStep(
                    step=iteration,
                    thought=action.thought,
                    action=action.tool,
                    action_input=action.tool_input,
                    observation=str(observation),
                ))

                histories.append(json.dumps({
                    "thought": action.thought,
                    "action": action.tool,
                    "action_input": action.tool_input,
                    "observation": observation,
                }, ensure_ascii=False))

            if iteration >= self.max_steps:
                break

            iteration += 1

        return "Agent stopped due to iteration limit.", recorded_steps


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
def root():
    return {"message": "Gold Advisor API is running. See /docs for endpoints."}


@app.post("/api/chatbot", response_model=ChatbotResponse)
def chatbot_endpoint(req: ChatbotRequest):
    """
    Gửi tin nhắn tới Chatbot và nhận phản hồi.

    - **user_input**: Câu hỏi của người dùng
    - **history**: (tuỳ chọn) Lịch sử hội thoại trước đó
    """
    provider = _make_provider()
    chatbot = Chatbot(llm=provider)

    t0 = time.time()
    try:
        response = chatbot.run(req.user_input, history=req.history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    latency_ms = int((time.time() - t0) * 1000)

    return ChatbotResponse(
        response=response,
        latency_ms=latency_ms,
    )


@app.post("/api/agent", response_model=AgentResponse)
def agent_endpoint(req: AgentRequest):
    """
    Gửi yêu cầu tới ReAct Agent và nhận phản hồi kèm các bước suy luận.

    - **user_input**: Yêu cầu của người dùng
    - **max_steps**: Số bước tối đa (mặc định 5)
    """
    provider = _make_provider()
    agent = InstrumentedAgent(
        llm=provider,
        tools=agent_tools,
        max_steps=req.max_steps,
    )

    t0 = time.time()
    try:
        final_answer, steps = agent.run_instrumented(req.user_input)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    latency_ms = int((time.time() - t0) * 1000)

    return AgentResponse(
        response=final_answer,
        steps=steps,
        total_steps=len(steps),
        latency_ms=latency_ms,
    )
