import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent

load_dotenv()

def test_agent_simple():
    provider = GeminiProvider(
        model_name=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    agent = ReActAgent(
        llm=provider,
        max_steps=5,
    )

    user_input = "Tôi có 50 triệu VND. Nếu giá vàng SJC là 92.5 triệu/lượng, tôi mua được bao nhiêu chỉ? (1 lượng = 10 chỉ)"
    print(f"User: {user_input}")
    result = agent.run(user_input)
    print(f"Agent: {result}")


if __name__ == "__main__":
    try:
        test_agent_simple()
    except Exception as e:
        print(f"[ERROR] {e}")
        raise
