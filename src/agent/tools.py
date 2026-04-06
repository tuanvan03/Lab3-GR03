import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

GOLD_MARKET_DOMAINS = [
    "sjc.com.vn", "giavang.doji.vn", "kitco.com", 
    "investing.com", "vneconomy.vn", "vietstock.vn"
]
def search():
    def search_news(query: str):
        """
        Search the web for news or information using Tavily API.
        Args:
            query (str): The search query.
        Returns:
            dict: A dictionary containing the status and the search results.
        """
        try:
            # Step 1. Instantiating your TavilyClient
            tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            
            # Perform the search query
            response = tavily_client.search(query=query, 
                search_depth="advanced", 
                # include_domains=GOLD_MARKET_DOMAINS,
                max_results=5
            )
            
            # Prepare the list of results
            results = []
            for result in response.get('results', []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", "")
                })
                
            return {"status": "success", "data": results}
        except Exception as e:
            # Return error format if something goes wrong
            return {"status": "error", "message": str(e)}
    return {
        "name": "search",
        "description": "Tìm kiếm các thông tin về câu hỏi người dùng trên internet.",
        "func": search_news,
    }

def make_calculator_tool():
    def calculate(expression: str) -> str:
        try:
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            return f"Lỗi tính toán: {e}"

    return {
        "name": "calculator",
        "description": "Tính toán biểu thức số học. Input là một biểu thức như '100 * 1.05' hoặc '(200 + 50) / 3'.",
        "func": calculate,
    }

import urllib.request
import json

def compare_prices():
    def compare(a_prices: float, b_prices: float) -> str:
        try:
            a_prices = float(a_prices)
            b_prices = float(b_prices)
            diff = a_prices - b_prices
            percent_diff = (diff / b_prices) * 100 if b_prices != 0 else 0
            if diff > 0:
                return f"Giá A cao hơn giá B {abs(diff):,.0f} (tương đương cao hơn {abs(percent_diff):.2f}%)"
            elif diff < 0:
                return f"Giá A thấp hơn giá B {abs(diff):,.0f} (tương đương thấp hơn {abs(percent_diff):.2f}%)"
            else:
                return "Giá A và giá B bằng nhau"
        except Exception as e:
            return f"Lỗi so sánh: {e}"

    return {
        "name": "compare_prices",
        "description": "So sánh hai mức giá để tính chênh lệch tuyệt đối và phần trăm (dùng cho giá cùng đơn vị, ví dụ giá vàng trong nước với nhau). Cần truyền vào tham số a_prices và b_prices.",
        "func": compare,
    }

def world_gold_compare():
    def compare(domestic_price: float, world_price_usd: float, usd_to_vnd_rate: float) -> str:
        """
        So sánh giá trong nước và giá thế giới quy đổi.
        """
        try:
            domestic_price = float(domestic_price)
            world_price_usd = float(world_price_usd)
            usd_to_vnd = float(usd_to_vnd_rate)
            
            # Tính giá thế giới quy đổi
            world_price_vnd = world_price_usd * usd_to_vnd * 1.205
            diff = domestic_price - world_price_vnd
            
            result_str = f"Giá trong nước: {domestic_price:,.0f} VND\nGiá thế giới quy đổi (x tỷ giá {usd_to_vnd:,.0f} x 1.205): {world_price_vnd:,.0f} VND\nChênh lệch: {diff:,.0f} VND"
            
            if diff > 10_000_000:
                result_str += "\nCảnh báo: Rủi ro đu đỉnh cao"
                
            return result_str
        except Exception as e:
            return f"Lỗi tính toán: {e}"

    return {
        "name": "world_gold_compare",
        "description": "So sánh giá vàng trong nước và giá vàng quốc tế ở 2 khu vực tiền tệ khác nhau. Input: domestic_price (giá vàng trong nước VND), world_price_usd (giá thế giới USD/Ounce), usd_to_vnd_rate (tỉ giá USD sang VND). Tính dựa trên tỷ giá x 1.205.",
        "func": compare,
    }

TOOLS = [make_calculator_tool(), search(), compare_prices(), world_gold_compare()]

if __name__ == "__main__":
    test_query = "Giá vàng thế giới hôm nay ?"
    print(f"Searching for: {test_query}\n")
    import json

    search_tool = search()
    search_result = search_tool["func"](test_query)
    print(json.dumps(search_result, ensure_ascii=False, indent=2))