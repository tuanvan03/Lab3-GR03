import streamlit as st
import time
import json
from datetime import datetime

# ==========================================
# Cấu hình trang Streamlit
# ==========================================
st.set_page_config(
    page_title="Agent vs Chatbot | Lab 3",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để điều chỉnh giao diện một chút
st.markdown("""
<style>
    /* Chỉnh màu cho khu vực log để giống Terminal */
    .terminal-log {
        background-color: #000000;
        color: #A3BE8C;
        font-family: 'Consolas', 'Courier New', monospace;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.85rem;
        height: 600px;
        overflow-y: auto;
    }
    .thought { color: #EBCB8B; } /* Vàng */
    .action { color: #88C0D0; } /* Xanh biển */
    .observation { color: #A3BE8C; } /* Xanh lá */
    .system { color: #616E88; } /* Xám */
    .metric-value { font-size: 1.2rem; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# State Management
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logs" not in st.session_state:
    st.session_state.logs = [{"type": "system", "text": "Initialize tracing engine...", "time": datetime.now().strftime("%H:%M:%S")}]
if "metrics" not in st.session_state:
    st.session_state.metrics = {"tokens": 0, "latency": 0.0, "steps": 0}

def clear_logs():
    st.session_state.logs = [{"type": "system", "text": "Initialize tracing engine...", "time": datetime.now().strftime("%H:%M:%S")}]
    st.session_state.messages = []
    st.session_state.metrics = {"tokens": 0, "latency": 0.0, "steps": 0}

def add_log(log_type, text):
    st.session_state.logs.append({
        "type": log_type,
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S")
    })

# ==========================================
# Layout chia làm 3 Cột Chính
# ==========================================
col_tools, col_chat, col_logs = st.columns([1, 2, 1], gap="medium")

# ----------------- CỘT 1: TOOL ARSENAL -----------------
with col_tools:
    st.subheader("🛠️ Tool Arsenal")
    st.caption("Các công cụ khả dụng cho Agent")
    
    st.info("**check_stock**\n\nKiểm tra số lượng tồn kho. \n\n*Tham số*: `item_name`")
    st.info("**get_discount**\n\nLấy phần trăm giảm giá. \n\n*Tham số*: `coupon_code`")
    st.info("**calc_shipping**\n\nTính phí giao hàng. \n\n*Tham số*: `weight`, `destination`")
    
    st.markdown("---")
    mode = st.radio("Lựa chọn Chế độ:", ["Standard Chatbot", "Agent (ReAct) 🚀"], index=1)
    
    st.markdown("---")
    if st.button("Làm sạch lịch sử & Logs"):
        clear_logs()

# ----------------- CỘT 2: CHAT INTERFACE -----------------
with col_chat:
    st.subheader("💬 Interaction Area")
    if len(st.session_state.messages) == 0:
        st.info("👋 Chào mừng đến với bài Lab 3. Hãy thử nhập một yêu cầu phức tạp (Ví dụ: Mua iPhone với mã giảm giá) để xem sự khác biệt.")
    
    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Xử lý Prompt
    prompt = st.chat_input("Nhập prompt (VD: I want to buy 2 iPhones using code WINNER and ship to Hanoi...)")

# ----------------- CỘT 3: OBSERVABILITY TRACE -----------------
with col_logs:
    st.subheader("📟 Observability Trace")
    st.caption("Theo dõi cơ chế ReAct (Thought -> Action -> Obs)")
    
    # Khung Terminal
    log_html = '<div class="terminal-log">'
    for log in st.session_state.logs:
        css_class = log["type"]
        log_html += f'<div class="{css_class}">[{log["time"]}] {log["text"]}</div>'
    log_html += '</div>'
    st.markdown(log_html, unsafe_allow_html=True)
    
    # Hiển thị Metrics
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Tokens", st.session_state.metrics["tokens"])
    m2.metric("Latency", f"{st.session_state.metrics['latency']}s")
    m3.metric("Steps", f"{st.session_state.metrics['steps']}/5")

# ==========================================
# Xử lý Logic (Simulator)
# ==========================================
if prompt:
    # 1. Thêm tin nhắn user vào màn hình (phải gọi thêm st.rerun hoặc render trực tiếp)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(prompt)
            
    # 2. Xử lý Logic
    start_time = time.time()
    
    if mode == "Standard Chatbot":
        with col_chat:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Đang suy nghĩ...")
                time.sleep(1.5) # Giả lập delay
                
                wrong_answer = """
Ah, you want to buy 2 iPhones and ship to Hanoi! I can help with that. 
The price for iPhones is usually around $999 each. So 2 iPhones would be $1998. 
I will apply the WINNER code. Assuming 5% discount, that's -$99.9. 
Shipping to Hanoi maybe around $50. 
**Total estimated price: ~$1948.10.** 
*(Note: As a standard language model, I cannot actually check live stock or real prices).*
                """
                message_placeholder.markdown(wrong_answer)
                st.session_state.messages.append({"role": "assistant", "content": wrong_answer})
                
                # Update metrics
                st.session_state.metrics["tokens"] = 125
                st.session_state.metrics["latency"] = round(time.time() - start_time, 2)
                st.session_state.metrics["steps"] = 1
                
        add_log("system", ">> [Chatbot] Generation complete. No tools called.")
        st.rerun()

    else: # Agent Mode
        is_target = "iphone" in prompt.lower() and "winner" in prompt.lower()
        
        with col_chat:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Tạo kế hoạch ReAct...")
                
                if not is_target:
                    time.sleep(1)
                    fallback_msg = "Tôi là một ReAct Agent giả lập. Tôi được thiết kế chỉ để phản hồi riêng cho kịch bản E-commerce lab (`Buy 2 iPhones, code WINNER, ship to Hanoi`). Vui lòng nhập đúng prompt đó để xem chuỗi hoạt động!"
                    message_placeholder.markdown(fallback_msg)
                    st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
                    add_log("system", ">> [Agent] LLM_METRIC: fallback generation")
                    st.rerun()
                else:
                    total_tokens = 45
                    
                    # Bước 1
                    time.sleep(1)
                    add_log("thought", "THOUGHT: I need to get the price and stock of an iPhone, apply the WINNER discount, and calculate shipping to Hanoi for 2 items. I will check the stock first.")
                    time.sleep(0.5)
                    add_log("action", f"ACTION: check_stock\n{json.dumps({'item_name': 'iPhone'}, indent=2)}")
                    time.sleep(1)
                    add_log("observation", f"OBSERVATION: {json.dumps({'qty': 15, 'price_per_unit': 1000, 'weight_kg': 0.5})}")
                    total_tokens += 52
                    st.session_state.metrics = {"tokens": total_tokens, "latency": round(time.time() - start_time, 2), "steps": 1}
                    
                    # Bước 2
                    time.sleep(1.5)
                    add_log("thought", "THOUGHT: The iPhone is in stock is $1000 per unit. Weight is 0.5kg each (1.0kg total). Next, check discount code 'WINNER'.")
                    time.sleep(0.5)
                    add_log("action", f"ACTION: get_discount\n{json.dumps({'coupon_code': 'WINNER'}, indent=2)}")
                    time.sleep(1)
                    add_log("observation", f"OBSERVATION: {json.dumps({'discount_percent': 10, 'status': 'valid'})}")
                    total_tokens += 85
                    st.session_state.metrics = {"tokens": total_tokens, "latency": round(time.time() - start_time, 2), "steps": 2}

                    # Bước 3
                    time.sleep(1.5)
                    add_log("thought", "THOUGHT: Discount is 10% valid. 10% of $2000 is $200. Discounted price: $1800. Now, calculate shipping for 1.0kg to 'Hanoi'.")
                    time.sleep(0.5)
                    add_log("action", f"ACTION: calc_shipping\n{json.dumps({'weight': 1.0, 'destination': 'Hanoi'}, indent=2)}")
                    time.sleep(1.5)
                    add_log("observation", f"OBSERVATION: {json.dumps({'shipping_cost': 25.50, 'currency': 'USD'})}")
                    total_tokens += 70
                    st.session_state.metrics = {"tokens": total_tokens, "latency": round(time.time() - start_time, 2), "steps": 3}
                    
                    # Final Answer
                    time.sleep(1)
                    add_log("thought", "THOUGHT: The shipping cost is $25.50. Total cost is $1800 + $25.50 = $1825.50. I will output the final answer.")
                    add_log("system", ">> [Agent] ReAct Loop Finished.")
                    
                    final_answer = """Here is the breakdown for your order:
    
- **Items:** 2x iPhones
- **Stock Status:** In Stock
- **Base Price:** $2,000.00 ($1,000/each)
- **Discount:** 10% off (Code 'WINNER applied') -> -$200.00
- **Shipping:** $25.50 (To Hanoi, 1.0kg total weight)

**Total Final Price: $1,825.50**"""
                    message_placeholder.markdown(final_answer)
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
                    
                    total_tokens += 120
                    st.session_state.metrics = {"tokens": total_tokens, "latency": round(time.time() - start_time, 2), "steps": 4}
                    st.rerun()
