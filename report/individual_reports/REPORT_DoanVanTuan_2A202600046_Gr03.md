# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đoàn Văn Tuấn
- **Student ID**: 2A202600046
- **Date**: 2026-06-04

---

## I. Technical Contribution (15 Points)
- Đảm nhận việc tạo các tool search, calculator, compare_prices, world_gold_compare
- Chịu trách nhiệm merge code và review code cho các thành viên
- Đã thử crawl data trên một số trang web như sjc.com.vn, giavang nhưng chưa thành công do các trang web này có các biện pháp chống crawl data

- **Modules Implementated**: `src/agent/tools.py`
- **Code Highlights**: 
+ Hàm search: Sử dụng Tavily API để tìm kiếm thông tin trên internet
+ Hàm calculator: Sử dụng eval để tính toán biểu thức số học
+ Hàm compare_prices: So sánh hai mức giá để tính chênh lệch tuyệt đối và phần trăm
+ Hàm world_gold_compare: So sánh giá vàng trong nước và giá vàng quốc tế quy đổi
Dưới đây highlight về hàm search() - chịu trách nhiêm chính cho việc cung cấp dữ liệu cho LLM 
```python
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
```

- **Documentation**: Những hàm tool này sử dụng bởi React Agent, thông qua việc gọi hàm `tools.get_tools()` để lấy danh sách các tool. Ở mỗi bước, Agent sẽ suy nghĩ và quyết định có nên sử dụng tool nào hay không. Nếu có, Agent sẽ gọi tool và nhận kết quả. Sau đó, Agent sẽ tiếp tục suy nghĩ và quyết định sử dụng tool nào tiếp theo hoặc đưa ra câu trả lời cuối cùng.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Agent bị ngắt giữa chừng do hết quota, khi sử dụng model gpt cho React agent mang lại hiệu quả kém hơn khi sử dụng Gemini, rất nhiều lỗi "Hiện tại tôi không tư vấn về vấn đề này" mặc dù đã có tool search
- **Log Source**: 

```json
GPT
{"timestamp": "2026-04-06T13:51:54.641016+00:00", "event": "AGENT_START", "data": {"input": "Tôi có 50 triệu, mua được bao nhiêu chỉ vàng 9999 hôm nay? Tính luôn phí chênh lệch mua - bán.", "model": "gpt-4o-mini"}}
{"timestamp": "2026-04-06T13:51:57.901562+00:00", "event": "LLM_METRIC", "data": {"model": "gpt-4o-mini", "prompt_tokens": 431, "completion_tokens": 112, "total_tokens": 543, "latency_ms": 3259, "cost_estimate": 0.000383871}}
{"timestamp": "2026-04-06T13:51:57.902513+00:00", "event": "TOOL_USAGE", "data": {"tool": "search", "input": "giá vàng 9999 hôm nay tại Việt Nam"}}
{"timestamp": "2026-04-06T13:51:59.876195+00:00", "event": "LLM_METRIC", "data": {"model": "gpt-4o-mini", "prompt_tokens": 588, "completion_tokens": 49, "total_tokens": 637, "latency_ms": 1968, "cost_estimate": 0.000264208}}
{"timestamp": "2026-04-06T13:51:59.876195+00:00", "event": "AGENT_END", "data": {"output": "Hiện tại tôi không tư vấn về vấn đề này", "model": "gpt-4o-mini"}}

GEMINI 
{"timestamp": "2026-04-06T09:41:43.798183+00:00", "event": "AGENT_START", "data": {"input": "Tôi có 50 triệu VND. Nếu giá vàng SJC là 92.5 triệu/lượng, tôi mua được bao nhiêu chỉ? (1 lượng = 10 chỉ)", "model": "gemini-2.5-flash"}}
{"timestamp": "2026-04-06T09:41:46.671550+00:00", "event": "LLM_METRIC", "data": {"model": "gemini-2.5-flash", "prompt_tokens": 226, "completion_tokens": 115, "total_tokens": 584, "latency_ms": 2867, "cost_estimate": 0.00034196599999999997}}
{"timestamp": "2026-04-06T09:41:46.671822+00:00", "event": "TOOL_USAGE", "data": {"tool": "calculator", "input": "92.5 / 10"}}
{"timestamp": "2026-04-06T09:41:48.294695+00:00", "event": "LLM_METRIC", "data": {"model": "gemini-2.5-flash", "prompt_tokens": 362, "completion_tokens": 71, "total_tokens": 506, "latency_ms": 1618, "cost_estimate": 0.000264742}}
{"timestamp": "2026-04-06T09:41:48.295072+00:00", "event": "TOOL_USAGE", "data": {"tool": "calculator", "input": "50 / 9.25"}}
{"timestamp": "2026-04-06T09:41:49.898724+00:00", "event": "LLM_METRIC", "data": {"model": "gemini-2.5-flash", "prompt_tokens": 456, "completion_tokens": 74, "total_tokens": 592, "latency_ms": 1600, "cost_estimate": 0.000294896}}
{"timestamp": "2026-04-06T09:41:49.898960+00:00", "event": "AGENT_END", "data": {"output": "Bạn có thể mua được khoảng 5.405 chỉ vàng SJC.", "model": "gemini-2.5-flash"}}
```

- **Diagnosis**: Vấn đề không phải GPT không gọi được tool, mà là nó không commit đến việc sử dụng kết quả tool để hoàn thành reasoning.
- **Solution**: Nhứng task liên quan đến ReAct Agent ưu tiên sử dụng Gemini thay vì GPT, gpt tool reasoning không ổn định.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Việc suy nghĩ từng bước giúp Agent có thể xử lý các tác vụ phức tạp hơn, đòi hỏi nhiều bước để giải quyết, nó cũng dễ dàng sử dụng những tools cần thiết để giải quyết những tác vụ này, cái mà Chatbot không thể làm được.
2.  **Reliability**: Độ tin cậy tăng lên đáng kể khi sử dụng ReAct Agent so với Chatbot nhờ cơ chế suy nghĩ từng bước và sử dụng tools.
3.  **Observation**: Những kết quả trả về vì thế cũng chính xác hơn và phù hợp với yêu cầu của người dùng hơn. Tuy nhiên, ReAct Agent cũng có nhược điểm là tốn nhiều tài nguyên hơn và chậm hơn so với Chatbot.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Muốn scale React agent cần phải khéo léo, vì ReAct bản chất là control loop, nên bottleneck nằm ở LLM calls → scale phải xoay quanh việc giảm phụ thuộc synchronous loop.
- **Safety**: React mạnh nhưng nó có rủi ro cao, do tự ý hành động và có thể gọi tools bên ngoài, cần có cơ chế kiểm soát chặt chẽ như validation input/output, HITL, nên có safety ở lớp riêng.
- **Performance**: React thường chậm, vì nhiều vòng loop goi llm, nên cần có cơ chế tối ưu hóa như prompt caching, streaming + trả kết quả sớm cho user, có cơ chế early stop tránh lặp vô hạn hoặc max steps, task đơn giản thì dùng model nhỏ, task phức tạp thì dùng model lớn.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
