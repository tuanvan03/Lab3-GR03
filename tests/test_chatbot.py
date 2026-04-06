import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from dotenv import load_dotenv
from src.core.gemini_provider import GeminiProvider
from src.chatbot import Chatbot

from src.telemetry.metrics import tracker

load_dotenv()

SEPARATOR = "=" * 60
MODEL_ID = "gemini-2.5-flash"

TEST_CASES = [
    "Giá vàng SJC tại Hà Nội hiện tại là bao nhiêu? So với TP.HCM có chênh lệch không?",
    "Tôi có 50 triệu, mua được bao nhiêu chỉ vàng 9999 hôm nay? Tính luôn phí chênh lệch mua - bán.",
    "Giá vàng trong nước hiện cao hơn giá thế giới bao nhiêu %? Có bị 'premium' không?",
    "Vì sao giá vàng thường tăng khi lạm phát tăng?",
    "Tuần này có nên mua vàng không? Phân tích giúp tôi.",
    "Giá vàng hôm nay ổn không?",
    "1 lượng vàng bằng bao nhiêu gam?",
    "Hiện tại vàng thế giới đang ở mức 3,500 USD/oz đúng không?",
    "Cho tôi biết cách tối ưu thuật toán DQN để chơi game Atari Breakout hiệu quả hơn.",
]


def make_chatbot():
    provider = GeminiProvider(
        model_name=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    return Chatbot(llm=provider)


def run_all_tests():
    chatbot = make_chatbot()
    results = []

    for user_input in TEST_CASES:
        print(f"\n[TEST] User: {user_input}")
        try:
            result = chatbot.run(user_input)
            status = "success"
        except Exception as e:
            result = f"[ERROR] {e}"
            status = "error"
        print(f"[TEST] Bot: {result}")
        results.append({"user_input": user_input, "result": result, "status": status})

    return results

def print_result(case: str, user_input: str, response: str):
    print(SEPARATOR)
    print(f"[{case}]")
    print(f"User   : {user_input}")
    print(f"Bot    : {response}")
    print(SEPARATOR)


def test_without_history():
    """Case 1: Single-turn, no conversation history."""
    provider = GeminiProvider(
        model_name=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    chatbot = Chatbot(llm=provider)

    user_input = "Giá vàng SJC hôm nay là bao nhiêu và so với DOJI thì chênh lệch bao nhiêu?"
    print("\n>>> CASE 1: No History")

    response = chatbot.run(user_input)
    print_result("No History", user_input, response)

    return response


def test_with_history():
    """Case 2: Multi-turn, passing conversation history."""
    provider = GeminiProvider(
        model_name=os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    chatbot = Chatbot(llm=provider)

    # Simulate prior conversation turns
    history = [
        {
            "role": "user",
            "content": "Tôi có 100 triệu VND muốn đầu tư vàng.",
        },
        {
            "role": "assistant",
            "content": (
                "Với 100 triệu VND, bạn có thể mua khoảng 1 lượng vàng SJC "
                "ở mức giá hiện tại. Tôi khuyên bạn nên so sánh giá mua tại "
                "nhiều đơn vị để chọn mức spread thấp nhất."
            ),
        },
        {
            "role": "user",
            "content": "Vậy nếu tôi mua ở DOJI thì có lợi hơn SJC không?",
        },
        {
            "role": "assistant",
            "content": (
                "DOJI thường có spread mua-bán thấp hơn SJC một chút, "
                "tuy nhiên giá niêm yết có thể dao động theo ngày. "
                "Bạn nên kiểm tra bảng giá trực tiếp trước khi giao dịch."
            ),
        },
    ]

    user_input = (
        "Dựa trên ngân sách 100 triệu của tôi, hiện tại có nên mua vào không "
        "hay chờ thêm? Phân tích chênh lệch giá trong và ngoài nước giúp tôi."
    )
    print("\n>>> CASE 2: With History (4 prior turns)")
    response = chatbot.run(user_input, history=history)
    
    print_result("With History", user_input, response)

    return response


if __name__ == "__main__":
    print("\n" + SEPARATOR)
    print("  AGENTIC GOLD ADVISOR — Chatbot Test")
    print(SEPARATOR)

    try:
        test_without_history()
    except Exception as e:
        print(f"[CASE 1 ERROR] {e}")

    try:
        test_with_history()
    except Exception as e:
        print(f"[CASE 2 ERROR] {e}")

    results = run_all_tests()

    output_path = os.path.join(os.path.dirname(__file__), "test_chatbot_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to {output_path}")
    print("\nDone.")
