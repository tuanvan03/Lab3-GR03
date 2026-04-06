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
- **Diagnosis**: Vấn đề nằm ở mô hình, mô hình sử dụng test lần này là GPT-4o-mini. Mô hình này ko phân biệt được câu hỏi có liên quan đến domain hay ko. (trong System prompt có yêu cầu ko trả lời những câu hỏi ko liên quan domain hiện tại)
- **Solution**: Thay mô hình bằng mô hình tốt hơn như GPT-5.

- **Problem Description**: Prompt cũ chạy tốt cho model Gemini không hoạt động tốt với model của OpenAI.
- **Log Source**: Lúc test trên Gemini chưa xong phần log, file kết quả thì bị ghi đè rồi... 
- **Diagnosis**: Lý do là các mô hình được train trên bộ dữ liệu khác nhau -> Phân phối xác suất của từng mô hình khác nhau -> Cùng 1 prompt đầu vào thì kết quả sẽ khác nhau, thường là tệ hơn.
- **Solution**: Thay mô hình phải thay prompt...

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
- Mô hình sẽ phân tích câu hỏi ban đầu thành chuỗi suy luận tuần tự -> giảm xác suất model đi thẳng đến câu trả lời sai.
2.  **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?
- Với câu hỏi đơn giản: Chatbot trả về kết quả chính xác với thời gian ngắn, trong khi Agent cần nhiều thời gian hơn để suy nghĩ, đôi khi, kết quả sau khi dùng tool search gây nhiễu -> Agent còn có thể trả lời sai
3.  **Observation**: How did the environment feedback (observations) influence the next steps?
- Observation là kết quả trả về từ tool sau mỗi Action. Agent dùng kết quả này để quyết định bước tiếp theo nên trả lởi (đã có đủ thông tin) hay tiếp tục gọi tool (chưa có đủ thông tin) hay thử lại (khi tool trả về kết quả lỗi)

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Đóng gói bằng Docker để dễ deploy lên nhiều máy khi cần mở rộng.
- **Safety**: Giới hạn tool chỉ được đọc dữ liệu
- **Performance**: Cache kết quả tool cho các query giống nhau trong cùng session

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
