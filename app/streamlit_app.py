
import os
import requests
import streamlit as st

# =========================
# Configuration
# =========================

try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8010")

API_URL = API_URL.rstrip("/")

st.set_page_config(
    page_title="VentureLens",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Custom CSS
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #080D18;
    color: #E5EAF3;
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #0D1422;
    border-right: 1px solid #1C293B;
}

[data-testid="stSidebar"] > div {
    padding: 28px 20px;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #F8FAFC;
}

.brand span {
    color: #38BDF8;
}

.brand-sub {
    color: #718096;
    font-size: 11px;
    margin-top: 5px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.side-label {
    color: #64748B;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin: 28px 0 12px;
}

.side-info {
    background: #111D30;
    border: 1px solid #22334B;
    border-radius: 10px;
    padding: 13px;
    margin-top: 10px;
    color: #A8B5C8;
    font-size: 12px;
    line-height: 2;
}

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0 22px;
    border-bottom: 1px solid #1C293B;
    margin-bottom: 45px;
}

.header-label {
    color: #64748B;
    font-size: 12px;
    letter-spacing: 1px;
}

.header-title {
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 600;
    margin-top: 5px;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 13px;
    border: 1px solid #1F3D36;
    background: #10251F;
    border-radius: 30px;
    color: #6EE7B7;
    font-size: 11px;
    font-weight: 600;
}

.status-off {
    border-color: #523333;
    background: #291819;
    color: #FCA5A5;
}

.hero {
    text-align: center;
    padding: 30px 0 28px;
}

.hero-icon {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: linear-gradient(135deg, #123B60, #172B50);
    border: 1px solid #28527D;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 27px;
    margin-bottom: 22px;
}

.hero h1 {
    color: #F8FAFC;
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -2px;
    margin: 0;
}

.hero h1 span {
    color: #38BDF8;
}

.hero p {
    color: #8291A8;
    font-size: 14px;
    margin-top: 13px;
    line-height: 1.8;
}

.section-label {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 25px 0 13px;
}

div[data-testid="stChatMessage"] {
    background: #101A2A;
    border: 1px solid #202F45;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 15px;
}

div[data-testid="stChatInput"] {
    border: 1px solid #2A3B54;
    border-radius: 14px;
    background: #111D30;
}

div[data-testid="stChatInput"] textarea {
    color: #F8FAFC;
}

.stButton button {
    background: #111D30;
    border: 1px solid #263A55;
    color: #CBD5E1;
    border-radius: 10px;
    min-height: 60px;
    text-align: left;
    transition: all 0.2s ease;
}

.stButton button:hover {
    border-color: #38BDF8;
    color: #F8FAFC;
    background: #152943;
}

.source-card {
    display: inline-block;
    padding: 7px 12px;
    margin: 4px 5px 4px 0;
    border-radius: 7px;
    background: #132C46;
    border: 1px solid #234969;
    color: #7DD3FC;
    font-size: 11px;
    font-weight: 600;
}

.footer {
    color: #526178;
    text-align: center;
    font-size: 11px;
    margin-top: 55px;
    padding: 20px 0;
    border-top: 1px solid #1C293B;
}

.stSlider [data-baseweb="slider"] {
    margin-top: 10px;
}

#MainMenu, footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# =========================
# API Status
# =========================

api_online = False

try:
    health_response = requests.get(f"{API_URL}/health", timeout=3)
    api_online = health_response.ok
except requests.RequestException:
    api_online = False

# =========================
# Sidebar
# =========================

with st.sidebar:

    st.markdown("""
    <div class="brand">Venture<span>Lens</span></div>
    <div class="brand-sub">Startup Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="side-label">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 💬  AI Assistant")
    st.caption("Explore the startup ecosystem.")

    st.markdown(
        '<div class="side-label">SEARCH SETTINGS</div>',
        unsafe_allow_html=True
    )

    top_k = st.slider(
        "Retrieved companies",
        min_value=1,
        max_value=10,
        value=5
    )

    st.markdown(
        '<div class="side-label">SYSTEM STATUS</div>',
        unsafe_allow_html=True
    )

    if api_online:
        st.markdown(
            '<div class="side-info">● API Connected<br>'
            '● Neo4j Database Connected</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="side-info" style="color:#FCA5A5">'
            '● API Offline<br>Check FastAPI server</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="side-label">TECH STACK</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="side-info">
    ◈ Neo4j Aura — Knowledge Graph<br>
    ◈ Cohere — Embeddings<br>
    ◈ Groq — LLM Generation<br>
    ◈ FastAPI — Backend<br>
    ◈ Streamlit — Frontend
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("＋  New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.caption("VentureLens · Academic Project")

# =========================
# Main Header
# =========================

status_class = "status" if api_online else "status status-off"
status_text = "SYSTEM ONLINE" if api_online else "SYSTEM OFFLINE"

st.markdown(f"""
<div class="main-header">
    <div>
        <div class="header-label">WORKSPACE / AI ASSISTANT</div>
        <div class="header-title">Startup Knowledge Explorer</div>
    </div>
    <div class="{status_class}">● {status_text}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# Welcome Screen
# =========================

if not st.session_state.messages:

    st.markdown("""
    <div class="hero">
        <div class="hero-icon">🚀</div>
        <h1>Explore the <span>Startup</span><br>Ecosystem.</h1>
        <p>
            Discover companies, founders, investments and connections.<br>
            Ask questions and let GraphRAG uncover the insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-label">✦  TRY THESE QUESTIONS</div>',
        unsafe_allow_html=True
    )

    suggestions = [
        "Who founded NovaPay and how much investment did it receive?",
        "Which investors funded FinLedger?",
        "What products does NovaPay develop?",
        "Which companies operate in Fintech?"
    ]

    col1, col2 = st.columns(2)

    for index, suggestion in enumerate(suggestions):
        target_col = col1 if index % 2 == 0 else col2

        with target_col:
            if st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True
            ):
                st.session_state.pending_prompt = suggestion
                st.rerun()

# =========================
# Chat History
# =========================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("sources"):
            st.markdown("**Retrieved Sources**")

            source_html = "".join(
                f'<span class="source-card">◈ {source}</span>'
                for source in message["sources"]
            )

            st.markdown(source_html, unsafe_allow_html=True)

# =========================
# Chat Input
# =========================

question = st.chat_input(
    "Ask about companies, founders, investors..."
)

if st.session_state.pending_prompt:
    question = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        if not api_online:
            st.error("API is offline. Start the FastAPI server first.")

        else:
            with st.spinner("Searching the knowledge graph..."):

                try:
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={
                            "question": question,
                            "top_k": top_k
                        },
                        timeout=180
                    )

                    response.raise_for_status()
                    result = response.json()

                    answer = result.get("answer", "No answer returned.")
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        st.markdown("**Retrieved Sources**")

                        source_html = "".join(
                            f'<span class="source-card">◈ {source}</span>'
                            for source in sources
                        )

                        st.markdown(
                            source_html,
                            unsafe_allow_html=True
                        )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except requests.RequestException as error:
                    st.error(f"Request failed: {error}")

                except Exception as error:
                    st.error(f"Unexpected error: {error}")

# =========================
# Footer
# =========================

st.markdown("""
<div class="footer">
    VENTURELENS &nbsp;·&nbsp; GRAPH-POWERED STARTUP INTELLIGENCE
</div>
""", unsafe_allow_html=True)
