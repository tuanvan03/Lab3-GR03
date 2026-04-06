# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Vũ Minh Khải
- **Student ID**: 2A202600343
- **Date**: 2026-06-04

---

## I. Technical Contribution (15 Points)
1. Cài đặt Agent Loop ở src/agent/agent.py (System prompt do bạn khác tối ưu)
- Đầu vào: System prompt + danh sách tool + user input + lịch sử (bước 1 chưa có)
- Băt đầu vòng lặp
    - Nội dung chuyển đến cho LLM
        - Nếu fail có thể retry tối đa 3 lần
    - Parse kết quá
        - Parse thành công
            - Chứa final answer -> trả về cho người dùng
            - Chứa tool -> gọi tool
                - Gọi được tool -> ghi lại log bước này -> quay lại bước gửi nội dung cho LLM 
                - Gọi tool bị lỗi -> Xử lý lỗi tương tự phía dưới...
        - Parse thất bại
            - Nếu biến tự sửa lỗi được bật -> Ghi lại log -> kiểm tra nếu còn vòng lặp agent -> quay lại bước gửi nội dung cho LLM 

2. Cài đặt Chatbot cơ bản ở src/chatbot/ (Phần system prompt được bạn khác tối ưu lại)
- Cái này chỉ là chatbot cơ bản, nhận user_input và system prompt có sẵn sau đó trả về câu trả lời cho người dùng

3. Phần back-end ở src/api/app.py
- Trả về kết quả cho front-end.

## II. Debugging Case Study (10 Points)
Có 1 số vấn đề như sau:

- **Problem Description**: Rất nhiều câu trả lời Agent chỉ trả về "Hiện tại tôi không tư vấn về vấn đề này"
- **Log Source**: logs/2026-04-06.log 
- **Diagnosis**: Vấn đề nằm ở mô hình, mô hình sử dụng test lần này là GPT-4o-mini.
- **Solution**: [How did you fix it? (e.g., updated `Thought` examples in the system prompt)]

- **Problem Description**: [e.g., Agent caught in an infinite loop with `Action: search(None)`]
- **Log Source**: [Link or snippet from `logs/YYYY-MM-DD.log`]
- **Diagnosis**: [Why did the LLM do this? Was it the prompt, the model, or the tool spec?]
- **Solution**: [How did you fix it? (e.g., updated `Thought` examples in the system prompt)]

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
2.  **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?
3.  **Observation**: How did the environment feedback (observations) influence the next steps?

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: [e.g., Use an asynchronous queue for tool calls]
- **Safety**: [e.g., Implement a 'Supervisor' LLM to audit the agent's actions]
- **Performance**: [e.g., Vector DB for tool retrieval in a many-tool system]

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
