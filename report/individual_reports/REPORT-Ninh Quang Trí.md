# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Ninh Quang Trí
- **Student ID**: 2A202600249
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**:
`src/telemetry/logger.py`, `src/telemetry/metrics.py`, `src/chatbot/__init__.py`, `src/agent/agent.py`
- **Code Highlights**: `src/telemetry/logger.py` line 9, 14-20, 21-36, `src/telemetry/metrics.py` line 17, 29-31, `src/chatbot/__init__.py` line 6, 23, 74-83, `src/agent/agent.py` line 9-10, 83-90, 145, 161, 170, 183, 184, 195, 233, 236,
- **Documentation**: Thêm class IndustryLogger the log lại các event trong quá trình, thêm dunction _calculate_cost vào class PerformanceTracker để tính chi phí mỗi lần gọi API của model Gemini-2.5-flash, lưu lại các log của các sự kiện đã xảy ra vào trong log file.
---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Agent ngừng hoạt động (crashed) ngay từ iteration đầu tiên do **Parsing Error**.
- **Log Source**: [See line 23](https://github.com/tuanvan03/Lab3-GR03/blob/main/logs/2026-04-06.log)
- **Diagnosis**: Nguyên nhân chính là **LLM (GPT-5)** không tuân thủ đúng output format mà ReAct agent yêu cầu.  
Thay vì trả về đúng cấu trúc:
`Thought: ...
Action: ...v
Action Input: ...
text` (hoặc `Final Answer: ...`), model đã sinh ra nội dung không parse được (có thể là text tự do, JSON không hợp lệ, hoặc thiếu keyword). 
- **Solution**: Cải thiện **System Prompt** bằng cách thêm nhiều ví dụ (few-shot examples) về format Thought → Action → Action Input, và nhấn mạnh "You MUST output in this exact format, do not add extra text". Thêm xử lý lỗi trong code: Sử dụng `handle_parsing_errors=True` trong `AgentExecutor` để tự động gửi lỗi parsing về lại LLM dưới dạng Observation, giúp agent tự sửa ở iteration tiếp theo.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Thought trong ReAct đóng vai trò như một "bản nháp". Thay vì trả lời ngay lập tức dựa trên xác suất (Chatbot), Agent buộc phải phân tích yêu cầu, xác định lỗ hổng thông tin và chọn công cụ phù hợp. Điều này giúp giảm thiểu hiện tượng hallucination khi trả lời về giá vàng thực tế.
2.  **Reliability**: Agent có thể hoạt động kém hơn Chatbot trong các câu hỏi mang tính chất cảm xúc hoặc tán gẫu đơn giản. Do cấu trúc ReAct yêu cầu output JSON, đôi khi model quá tập trung vào format mà làm mất đi tính tự nhiên trong văn phong so với Chatbot thông thường.
3.  **Observation**: Observations định hướng cho Agent. Nếu công cụ lookup giá vàng trả về lỗi hoặc không có dữ liệu, Agent sẽ nhìn thấy điều đó trong Observation và tự điều chỉnh như thử dùng một tool khác hoặc thông báo cho người dùng thay vì đoán mò.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Chuyển đổi hệ thống logging sang cơ chế Asynchronous Logging (sử dụng QueueHandler) để việc ghi log vào ổ cứng không làm tăng Latency của phản hồi AI.
- **Safety**: Triển khai tầng LLM Guardrails để kiểm tra tính hợp lệ của tool_input trước khi thực thi, ngăn chặn các hành vi prompt injection có thể gây hại cho hệ thống
- **Performance**: Áp dụng Prompt Caching cho phần System Prompt cực dài để giảm chi phí input token và tăng tốc độ xử lý cho các lượt hội thoại tiếp theo

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
