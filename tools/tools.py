import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

GOLD_MARKET_DOMAINS = [
    "sjc.com.vn", "giavang.doji.vn", "kitco.com", 
    "investing.com", "vneconomy.vn", "vietstock.vn"
]

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
            include_domains=GOLD_MARKET_DOMAINS,
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

if __name__ == "__main__":
    import json
    
    # Test the function and print formatted JSON
    test_query = "Giá vàng thế giới hôm nay 6/4/2026 ?"
    print(f"Searching for: {test_query}\n")
    
    search_result = search_news(test_query)
    print(json.dumps(search_result, ensure_ascii=False, indent=2))