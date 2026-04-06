# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Dương Chí Thành
- **Student ID**: 2A202600047
- **Date**: 2026-06-04

---

## I. Technical Contribution (15 Points)

Trong project này, mình chủ yếu đảm nhận vai trò Front-End Developer, chịu trách nhiệm xây dựng giao diện người dùng để tương tác với Agent. Công việc tập trung vào việc thiết kế UI/UX, kết nối API, và đảm bảo trải nghiệm mượt mà cho người dùng.
Modules Implemented:
- src/frontend/App.js
- src/frontend/indext.html
- src/frontend/styles.css
Các chức năng chính:
Các chức năng chính:
- Tạo giao diện chat trực quan với khung nhập liệu và lịch sử hội thoại.
- Kết nối API backend để hiển thị phản hồi từ Agent.
- Thêm thông báo lỗi khi hệ thống gặp sự cố (ví dụ: model không hợp lệ).


## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: - Problem Description: Trong quá trình phát triển front end, đôi khi giao diện không hiển thị phản hồi do lỗi kết nối API hoặc dữ liệu trả về không đúng định dạng JSON.
- Log Source: Dựa trên console log trong trình duyệt, lỗi thường xuất hiện khi gọi fetch("/api/chat").
**Diagnosis:
- API trả về status code 500 nhưng front end chưa có xử lý fallback.
- JSON parse error khi response không hợp lệ.
**Solution:
- Thêm khối try...catch để xử lý lỗi.
- Hiển thị thông báo lỗi thân thiện cho người dùng thay vì để trống màn hình.
- Kiểm tra định dạng dữ liệu trả về từ backend trước khi render.


---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Từ góc nhìn front end, ReAct Agent tạo ra nhiều bước trung gian (Thought, Observation) nên dữ liệu trả về phức tạp hơn. Điều này yêu cầu UI phải hiển thị rõ ràng các bước reasoning để người dùng hiểu.
**Reliability: Nếu backend gặp lỗi (ví dụ tool không trả dữ liệu), front end phải có cơ chế hiển thị fallback để tránh trải nghiệm xấu.
** Observation: Việc hiển thị observation giúp người dùng thấy quá trình suy luận, nhưng cũng cần thiết kế UI hợp lý để không gây rối mắt.


---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

**Scalability: Xây dựng front end có khả năng mở rộng, hỗ trợ nhiều loại agent khác nhau qua cấu hình.
**Safety: Thêm bộ lọc nội dung ở front end để cảnh báo người dùng nếu output có yếu tố nhạy cảm.
** Performance: Tối ưu caching ở front end (ví dụ lưu hội thoại gần đây) để giảm số lần gọi API.


---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
