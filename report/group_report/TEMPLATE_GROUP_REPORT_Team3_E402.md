# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Team3-E402
- **Team Members**: Lê Nguyễn Thanh Binh, Ninh Quang Trí, Đoàn Quang Tuấn, Vũ Minh Khải, Dương Chí Thành
- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

Hệ thống Agentic Gold Advisor được xây dựng nhằm giải quyết 2 vấn đề chính của chatbot truyền thống:
(1) không cập nhật giá vàng real-time và (2) dễ bị hallucination khi tính toán.

Chúng tôi triển khai một ReAct Agent có khả năng:

- Gọi API lấy giá vàng theo thời gian thực
- Tự tính toán quy đổi (VND ↔ USD, lượng ↔ gram)
- Trả lời các câu hỏi multi-step chính xác hơn
- Success Rate: 100% trên 5 test cases

Key Outcome:

- Agent giải quyết nhiều hơn 40% câu hỏi đa bước so với chatbot baseline nhờ sử dụng đúng tool search_news và make_calculator_tool

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
![alt text](image.png)

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_news` | `string` | Tra và tìm kiếm mọi thứ nhưng giới hạn phần agent chỉ trả lời trong lĩnh vực giá vàng |
| `make_calculator_tool` | `string` | Tool tính toán tập trung  |
| `compare_price` | `string` | So sánh giá vàng |
| `world_gold_compare` | `string` | so cánh giá vàng trong nước và quốc tế  |

### 2.3 LLM Providers Used
- **Primary**: [Gemini 2.5 Flash]
- **Secondary (Backup)**: [GPT 4o mini]

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: [e.g., 1200ms]
- **Max Latency (P99)**: [e.g., 4500ms]
- **Average Tokens per Task**: [e.g., 350 tokens]
- **Total Cost of Test Suite**: [e.g., $0.05]

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study: [e.g., Hallucinated Argument]
- **Input**: "How much is the tax for 500 in Vietnam?"
- **Observation**: Agent called `calc_tax(amount=500, region="Asia")` while the tool only accepts 2-letter country codes.
- **Root Cause**: The system prompt lacked enough `Few-Shot` examples for the tool's strict argument format.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: Thêm instruction:
    - "Luôn xác minh dữ liệu thời gian thực bằng các công cụ trước khi trả lời."
- **Result**: 
    - Giảm hallucination: -60%
    - Tăng accuracy: +20%

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q | Correct | Correct | Draw |
| Multi-step | Hallucinated | Correct | **Agent** |
| Real-time | Wrong | Correct | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: Các tool được thiết kế theo nguyên tắc không làm thay đổi hoặc lưu trữ dữ liệu người dùng, đảm bảo tính toàn vẹn và bảo mật thông tin.
- **Guardrails**: Tối đa 5 vòng để tránh chi phí thanh toán vô hạn.
- **Scaling**: Có thể thêm tool, thay đổi model

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
