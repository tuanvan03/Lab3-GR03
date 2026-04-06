import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent

load_dotenv()

TEST_CASES = [
    "Giá vàng SJC tại Hà Nội hiện tại là bao nhiêu? So với TP.HCM có chênh lệch không?",
    "Tôi có 50 triệu, mua được bao nhiêu chỉ vàng 9999 hôm nay? Tính luôn phí chênh lệch mua - bán.",
    "Giá vàng trong nước hiện cao hơn giá thế giới bao nhiêu %? Có bị 'premium' không?",
    "Vì sao giá vàng thường tăng khi lạm phát tăng?",
    "Cho tôi biết cách tối ưu thuật toán DQN để chơi game Atari Breakout hiệu quả hơn."
]


def make_agent():
    provider = GeminiProvider(
        model_name=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    return ReActAgent(llm=provider, max_steps=5)


def run_all_tests():
    agent = make_agent()
    results = []

    for user_input in TEST_CASES:
        print(f"\n[TEST] User: {user_input}")
        try:
            result = agent.run(user_input)
            status = "success"
        except Exception as e:
            result = f"[ERROR] {e}"
            status = "error"
        print(f"[TEST] Agent: {result}")
        results.append({"user_input": user_input, "result": result, "status": status})

    return results


if __name__ == "__main__":
    results = run_all_tests()

    output_path = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to {output_path}")
