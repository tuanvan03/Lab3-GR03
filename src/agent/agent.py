import os
import json
import time
from typing import List, Dict, Any, Optional
from jinja2 import Template
from src.agent.tools import TOOLS as agent_tools
from src.core.llm_provider import LLMProvider


class AgentAction:
    def __init__(self, thought: str, tool: str, tool_input: str):
        self.thought = thought
        self.tool = tool
        self.tool_input = tool_input


class AgentFinish:
    def __init__(self, thought: str, output: str):
        self.thought = thought
        self.output = output


class ReActAgent:
    """
    ReAct-style Agent that follows the Thought-Action-Observation loop.
    Implements exponential backoff on API errors, configurable error handling,
    and stopping conditions (max iterations, max time, early stopping).
    """

    def __init__(
        self,
        llm: LLMProvider,
        tools: List[Dict[str, Any]] = agent_tools,
        max_steps: int = 5,
        max_time: Optional[float] = None,
        handle_tool_errors: bool = True,
        handle_parsing_errors: bool = True,
        early_stopping: str = "force",
        retry_count: int = 3,
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.max_time = max_time
        self.handle_tool_errors = handle_tool_errors
        self.handle_parsing_errors = handle_parsing_errors
        self.early_stopping = early_stopping
        self.retry_count = retry_count

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    def get_system_prompt(self, tools: List[Dict[str, Any]]) -> str:
        template_path = os.path.join(os.path.dirname(__file__), "system_prompt.md")
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        return Template(template_str).render(
            tools=tools,
            tool_names=[t["name"] for t in tools],
        )

    def _build_human_prompt(self, question: str, histories: List[str]) -> str:
        template_path = os.path.join(os.path.dirname(__file__), "prompt.md")
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        return Template(template_str).render(
            question=question,
            histories=histories,
        )

    # ------------------------------------------------------------------
    # LLM call with retry + exponential backoff
    # ------------------------------------------------------------------

    def _call_llm(self, prompt: str) -> str:
        wait = 1
        for attempt in range(1, self.retry_count + 1):
            try:
                result = self.llm.generate(prompt, system_prompt=self.get_system_prompt(self.tools))
                return result["content"]
            except Exception as exc:
                if attempt >= self.retry_count:
                    raise RuntimeError(
                        f"LLM API failed after {self.retry_count} retries: {exc}"
                    ) from exc
                time.sleep(wait)
                wait *= 2

    # ------------------------------------------------------------------
    # Output parser
    # ------------------------------------------------------------------

    def _parse_output(self, raw_text: str):
        """
        Parse JSON output from the LLM into AgentFinish or AgentAction.
        Expected JSON schemas:
          - Action:       {"thought": "...", "action": "tool_name", "action_input": "..."}
          - Final answer: {"thought": "...", "final_answer": "..."}
        Returns (parsed_object, success: bool).
        """
        try:
            data = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            return None, False

        if not isinstance(data, dict):
            return None, False

        thought = str(data.get("thought") or "")

        final_answer = data.get("final_answer")
        if final_answer is not None:
            return AgentFinish(thought=thought, output=str(final_answer)), True

        action = data.get("action")
        action_input = data.get("action_input")
        if action and action_input is not None:
            return (
                AgentAction(
                    thought=thought,
                    tool=str(action),
                    tool_input=str(action_input),
                ),
                True,
            )

        return None, False

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        for tool in self.tools:
            if tool["name"] == tool_name:
                func = tool.get("func")
                if func is None:
                    return f"Tool '{tool_name}' has no callable function."
                return str(func(tool_input))
        available = [t["name"] for t in self.tools]
        return f"Tool '{tool_name}' not found. Available tools: {available}"

    # ------------------------------------------------------------------
    # Main run loop
    # ------------------------------------------------------------------

    def run(self, user_input: str) -> str:
        histories: List[str] = []
        iteration = 1
        start_time = time.time()

        while iteration <= self.max_steps:
            # ── Stopping conditions ──────────────────────────────────
            if self.max_time is not None and (time.time() - start_time) >= self.max_time:
                return "Agent stopped due to iteration/time limit"

            # ── Build prompt ─────────────────────────────────────────
            prompt = self._build_human_prompt(user_input, histories)

            # ── LLM call ─────────────────────────────────────────────
            raw_text = self._call_llm(prompt)

            # ── Parse output ─────────────────────────────────────────
            parsed, success = self._parse_output(raw_text)

            if not success:
                if self.handle_parsing_errors:
                    observation = (
                        'Invalid JSON format. Respond with one of:\n'
                        '{"thought": "...", "action": "tool_name", "action_input": "..."}\n'
                        '{"thought": "...", "final_answer": "..."}'
                    )
                else:
                    raise ValueError(f"Failed to parse LLM output:\n{raw_text}")
            elif isinstance(parsed, AgentFinish):
                return parsed.output
            else:
                # ── AgentAction: tool lookup + execution ──────────────
                action: AgentAction = parsed
                tool_found = any(t["name"] == action.tool for t in self.tools)

                if not tool_found:
                    available = [t["name"] for t in self.tools]
                    observation = f"Tool '{action.tool}' not found. Available tools: {available}"
                else:
                    try:
                        observation = self._execute_tool(action.tool, action.tool_input)
                    except Exception as exc:
                        if self.handle_tool_errors:
                            observation = f"Error: {exc}"
                        else:
                            raise

                # ── Update histories ──────────────────────────────────
                histories.append(json.dumps({
                    "thought": action.thought,
                    "action": action.tool,
                    "action_input": action.tool_input,
                    "observation": observation,
                }, ensure_ascii=False))

            # ── Check iteration limit ─────────────────────────────────
            if iteration >= self.max_steps:
                break

            # Handle parse error path: still append to histories so LLM sees feedback
            if not success:
                histories.append(json.dumps({
                    "thought": "(parse error)",
                    "observation": observation,
                }, ensure_ascii=False))

            iteration += 1

        # ── Force stop ────────────────────────────────────────────────
        if self.early_stopping == "force":
            return "Agent stopped due to iteration/time limit"

        return "Agent stopped without a final answer."
