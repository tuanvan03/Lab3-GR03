import streamlit as st
import requests
from datetime import datetime

API_BASE = "http://localhost:8000"

# ==========================================
# Cấu hình trang
# ==========================================
st.set_page_config(
    page_title="Agent vs Chatbot | Lab 3",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
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
    .thought     { color: #EBCB8B; }
    .action      { color: #88C0D0; }
    .observation { color: #A3BE8C; }
    .system      { color: #616E88; }
    .final       { color: #BF616A; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# State
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logs" not in st.session_state:
    st.session_state.logs = [{"type": "system", "text": "Initialize tracing engine...", "time": datetime.now().strftime("%H:%M:%S")}]
if "metrics" not in st.session_state:
    st.session_state.metrics = {"latency": 0, "steps": 0}


def clear_all():
    st.session_state.messages = []
    st.session_state.logs = [{"type": "system", "text": "Initialize tracing engine...", "time": datetime.now().strftime("%H:%M:%S")}]
    st.session_state.metrics = {"latency": 0, "steps": 0}


def add_log(log_type: str, text: str):
    st.session_state.logs.append({
        "type": log_type,
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S"),
    })


# ==========================================
# Layout
# ==========================================
col_tools, col_chat, col_logs = st.columns([1, 2, 1], gap="medium")

# ---------- CỘT 1: TOOL ARSENAL ----------
with col_tools:
    st.subheader("🛠️ Tool Arsenal")
    st.caption("Các công cụ khả dụng cho Agent")
    st.info("**search**\n\nTìm kiếm thông tin trên internet qua Tavily API.\n\n*Tham số*: `query`")
    st.info("**calculator**\n\nTính toán biểu thức số học.\n\n*Tham số*: `expression`")
    st.markdown("---")
    mode = st.radio("Chế độ:", ["💬 Standard Chatbot", "🚀 Agent (ReAct)"], index=1)
    max_steps = st.slider("Max steps (Agent)", 1, 10, 5) if "Agent" in mode else 5
    st.markdown("---")
    if st.button("Làm sạch lịch sử & Logs"):
        clear_all()

# ---------- CỘT 2: CHAT ----------
with col_chat:
    st.subheader("💬 Interaction Area")
    if not st.session_state.messages:
        st.info("👋 Nhập câu hỏi về thị trường vàng để bắt đầu.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Hỏi về giá vàng, đầu tư, thị trường...")

# ---------- CỘT 3: OBSERVABILITY ----------
with col_logs:
    st.subheader("📟 Observability Trace")
    st.caption("Theo dõi cơ chế ReAct (Thought → Action → Observation)")

    log_html = '<div class="terminal-log">'
    for log in st.session_state.logs:
        log_html += f'<div class="{log["type"]}">[{log["time"]}] {log["text"]}</div>'
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)

    st.markdown("---")
    m1, m2 = st.columns(2)
    m1.metric("Latency", f"{st.session_state.metrics['latency']}ms")
    m2.metric("Steps", f"{st.session_state.metrics['steps']}")

# ==========================================
# Xử lý logic khi có prompt
# ==========================================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(prompt)

    # Lấy lịch sử hội thoại (chỉ dùng cho chatbot)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]  # bỏ tin nhắn vừa thêm
    ]

    if "Chatbot" in mode:
        # ── Gọi /api/chatbot ───────────────────────────────────────
        add_log("system", f">> [Chatbot] Sending request to {API_BASE}/api/chatbot")
        try:
            resp = requests.post(
                f"{API_BASE}/api/chatbot",
                json={"user_input": prompt, "history": history},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data["response"]
            latency = data["latency_ms"]

            add_log("system", f">> [Chatbot] Done. Latency: {latency}ms")
            st.session_state.metrics = {"latency": latency, "steps": 1}
        except requests.exceptions.ConnectionError:
            answer = "❌ Không thể kết nối tới backend. Hãy chắc chắn server đang chạy tại `http://localhost:8000`."
            add_log("system", ">> [Chatbot] ERROR: Connection refused")
            st.session_state.metrics = {"latency": 0, "steps": 0}
        except Exception as e:
            answer = f"❌ Lỗi: {e}"
            add_log("system", f">> [Chatbot] ERROR: {e}")
            st.session_state.metrics = {"latency": 0, "steps": 0}

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with col_chat:
            with st.chat_message("assistant"):
                st.markdown(answer)

    else:
        # ── Gọi /api/agent ─────────────────────────────────────────
        add_log("system", f">> [Agent] Sending request to {API_BASE}/api/agent")
        try:
            resp = requests.post(
                f"{API_BASE}/api/agent",
                json={"user_input": prompt, "max_steps": max_steps},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()

            # Ghi từng bước vào trace log
            for step in data.get("steps", []):
                s = step["step"]
                thought = step.get("thought", "")
                action = step.get("action")
                action_input = step.get("action_input")
                observation = step.get("observation")

                if thought:
                    add_log("thought", f"[Step {s}] THOUGHT: {thought}")
                if action:
                    add_log("action", f"[Step {s}] ACTION: {action}({action_input})")
                if observation:
                    add_log("observation", f"[Step {s}] OBSERVATION: {observation}")

            answer = data["response"]
            latency = data["latency_ms"]
            total_steps = data["total_steps"]

            add_log("final", f">> [Agent] Final Answer ready. Steps: {total_steps}, Latency: {latency}ms")
            st.session_state.metrics = {"latency": latency, "steps": total_steps}

        except requests.exceptions.ConnectionError:
            answer = "❌ Không thể kết nối tới backend. Hãy chắc chắn server đang chạy tại `http://localhost:8000`."
            add_log("system", ">> [Agent] ERROR: Connection refused")
            st.session_state.metrics = {"latency": 0, "steps": 0}
        except Exception as e:
            answer = f"❌ Lỗi: {e}"
            add_log("system", f">> [Agent] ERROR: {e}")
            st.session_state.metrics = {"latency": 0, "steps": 0}

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with col_chat:
            with st.chat_message("assistant"):
                st.markdown(answer)

    st.rerun()
