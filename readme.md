Đây là file **README.md** hoàn chỉnh cho **Lab 3**, được thiết kế chuyên nghiệp để hướng dẫn sinh viên/kỹ thuật viên đi từ một Chatbot cơ bản đến một Agent có khả năng suy luận (Reasoning) và hành động (Acting).

---

# Lab 3: Building Agentic ReAct Systems 🤖

## 📋 Overview
Chào mừng bạn đến với Lab 3. Trong buổi học kéo dài **240 phút** này, chúng ta sẽ chuyển dịch từ việc viết code "chạy được" sang việc kỹ thuật hóa các hệ thống có khả năng **suy luận (Reasoning)** và **tiến hóa (Evolving)**.

Bạn sẽ không chỉ xây dựng một Chatbot biết nói, mà sẽ tạo ra một **Agent** biết sử dụng công cụ (Tools) để giải quyết các bài toán thực tế thông qua vòng lặp **ReAct (Thought -> Action -> Observation)**.

---

## 🎯 Core Learning Objectives
1.  **ReAct Mechanics**: Làm chủ chu kỳ *Suy nghĩ (Thought) -> Hành động (Action) -> Quan sát (Observation)*.
2.  **Industry Observability**: Học cách "đọc não" LLM thông qua hệ thống Logs cấu trúc JSON.
3.  **Iterative Refinement**: Cải thiện hiệu suất hệ thống dựa trên việc phân tích vết (Trace analysis) thay vì đoán mò Prompt.

---

## 📂 Project Structure
```text
.
├── src/
│   ├── tools/          # Nơi định nghĩa các công cụ cho Agent (API, Database, Calc)
│   ├── agent/          # Logic cốt lõi của ReAct Agent
│   └── chatbot.py      # Baseline Chatbot (Chỉ dùng Prompting đơn thuần)
├── logs/               # Chứa các file JSON log (Dùng cho Phase 4 & 5)
├── tests/              # Các kịch bản test case mẫu
├── .env                # Cấu hình API Keys (OpenAI, Gemini, v.v.)
└── README.md
```

---

## ⏱️ Lab Roadmap (4 Hours)

### Phase 1: Tool Design (30m)
Định nghĩa các công cụ trong `src/tools/`. 
* **Lưu ý**: LLM chỉ biết đến công cụ qua **Description**. 
* *Mục tiêu*: Viết mô tả công cụ rõ ràng, giới hạn phạm vi (ví dụ: "Tính thuế VAT 10% cho khu vực VN, nhận đầu vào là số thực").

### Phase 2: Chatbot Baseline (30m)
Chạy `chatbot.py` với các câu hỏi phức tạp (Multi-step).
* *Thử thách*: Cố gắng dùng Prompt Engineering để ép Chatbot giải quyết bài toán cần tính toán nhiều bước. Quan sát sự thất bại của nó khi không có công cụ.

### Phase 3: Building Agent v1 (60m)
Triển khai logic ReAct trong `agent/agent.py`.
* Xây dựng vòng lặp: Gửi Prompt -> Parse JSON Action -> Thực thi Tool -> Trả kết quả Observation về LLM.
* Xử lý Regex/JSON Parsing để trích xuất hành động từ phản hồi của LLM.

### Phase 4: Failure Analysis & Refinement (45m)
Mở thư mục `logs/` và tìm các sự kiện `LOG_EVENT: LLM_METRIC`.
* Phân tích tại sao Agent chọn sai công cụ hoặc tạo ra tham số ảo (Hallucination).
* Cập nhật System Prompt từ v1 lên v2 dựa trên dữ liệu thực tế từ log.

### Phase 5: Group Evaluation (30m)
Chạy bộ test suite tổng thể và đối chiếu kết quả giữa Chatbot và Agent.

---

## 📈 Evaluation Metrics (Tiêu chí đánh giá)

Trong Lab này, chúng ta đánh giá dựa trên các chỉ số công nghiệp thực tế:

### 1. Token Efficiency (Hiệu suất Token)
* **Prompt vs. Completion**: Prompt hệ thống có quá rườm rà không? Agent có "nói nhảm" quá nhiều trước khi gọi Tool không?
* **Cost Analysis**: Ít token hơn = Chi phí thấp hơn = ROI cao hơn.

### 2. Latency (Độ trễ)
* **TTFT (Time-to-First-Token)**: LLM mất bao lâu để bắt đầu phản hồi?
* **Total Duration**: Tổng thời gian hoàn thành tác vụ (bao gồm các vòng lặp và thời gian thực thi Tool).
* *Mục tiêu*: Response trong khoảng 200ms - 2s cho môi trường Production.

### 3. Loop Count (Số vòng lặp)
* **Reasoning Steps**: Agent cần bao nhiêu chu kỳ để tìm ra đáp án cuối cùng?
* **Termination Quality**: Agent có dừng đúng lúc với "Final Answer" hay bị kẹt trong vòng lặp vô tận?

### 4. Failure Analysis (Mã lỗi)
* **JSON Parser Error**: LLM trả về format sai khiến code không parse được Action.
* **Hallucination Error**: LLM tự bịa ra một công cụ không tồn tại trong danh sách.
* **Timeout**: Agent vượt quá `max_steps` quy định.

---

## 🏦 Scenario mẫu: "The Smart E-commerce Assistant"
Để hoàn thành Lab, Agent của bạn phải vượt qua test case sau:
* **Câu hỏi**: "Tôi muốn mua 2 chiếc iPhone, dùng mã giảm giá 'WINNER' và ship về Hà Nội. Tổng chi phí là bao nhiêu?"
* **Tools cần gọi**: `check_stock()` -> `get_discount()` -> `calc_shipping()`.

---

## 🛠 How to Use the Logs
Tất cả các chỉ số trên được ghi lại tự động trong thư mục `logs/`. 
Hãy sử dụng script phân tích để tính toán **Aggregate Reliability** (Độ tin cậy tổng thể) của phiên bản v1 so với v2.

> **“In the world of AI, the trace is the truth. Learn to read the logs.”**

---