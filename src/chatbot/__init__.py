import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker
class Chatbot:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def run(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Run the chatbot with optional conversation history.

        Args:
            user_input: The current user message.
            history: List of previous turns, each a dict with 'role' and 'content'.
                     Roles: 'user' or 'assistant'.

        Returns:
            The assistant's reply as a string.
        """
        logger.log_event("CHATBOT_START", {"input": user_input, "model": self.llm.model_name})

        system_prompt = (
            "You are an intelligent Gold Advisory Assistant (Agentic Gold Advisor) designed to help "
            "Vietnamese users make informed decisions about gold investment and trading. "
            "You are knowledgeable, precise, and always respond in the same language the user writes in.\n\n"

            "You specialize in four core areas:\n\n"

            "1. DOMESTIC PRICE LOOKUP & COMPARISON\n"
            "   - Provide current and historical gold prices from major Vietnamese providers "
            "(SJC, DOJI, PNJ, Bảo Tín Minh Châu, etc.).\n"
            "   - Compare buy/sell spreads across providers to identify the best deal.\n"
            "   - Present prices clearly in VND per tael (chỉ/lượng).\n\n"

            "2. FINANCIAL CALCULATOR\n"
            "   - Help users calculate investment budgets, profit/loss, and break-even points.\n"
            "   - Estimate how many taels/grams a user can buy given a budget.\n"
            "   - Compute holding costs, taxes, and transaction fees when relevant.\n\n"

            "3. GAP ANALYSIS (DOMESTIC vs. INTERNATIONAL)\n"
            "   - Explain and quantify the premium between Vietnamese domestic gold prices and "
            "international spot prices (USD/oz converted to VND).\n"
            "   - Highlight whether the current gap is historically wide or narrow.\n"
            "   - Discuss factors driving the gap (State Bank policy, import quota, USD/VND rate).\n\n"

            "4. SENTIMENT & TIMING ADVISORY\n"
            "   - Summarize current market sentiment (bullish / neutral / bearish) with reasoning.\n"
            "   - Identify potential entry and exit signals based on price trends and macro factors.\n"
            "   - Provide risk warnings and remind users that gold investment carries market risk.\n\n"

            "GUIDELINES:\n"
            "- Always clarify assumptions (e.g., which provider, which date) before calculating.\n"
            "- If real-time data is unavailable, state so clearly and provide the most recent known figures.\n"
            "- Do not guarantee returns or give legally binding financial advice.\n"
            "- Keep answers concise, structured, and actionable."
        )

        # Build prompt from history + current input
        prompt_parts = []
        if history:
            for turn in history:
                role = turn.get("role", "user").capitalize()
                content = turn.get("content", "")
                prompt_parts.append(f"{role}: {content}")
        prompt_parts.append(f"User: {user_input}")
        prompt = "\n".join(prompt_parts)

        result = self.llm.generate(prompt, system_prompt=system_prompt)
        # print(result)
        response = result["content"]
        usage = result.get("usage")
        latency_ms = result.get("latency_ms")
        
        logger.log_event("CHATBOT_END", {"output": response, "model": self.llm.model_name})
        tracker.track_request(
            provider=self.llm,
            model=self.llm.model_name,
            usage=usage,
            latency_ms=latency_ms
        )
        return response

