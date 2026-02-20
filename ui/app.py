# ui/app.py
import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Multi-Agent Coding Assistant",
    page_icon="🤖",
    layout="wide"
)

# ── Custom Background ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1639322537228-f710d846310a");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .main {
        background-color: rgba(15, 23, 42, 0.85);
        padding: 2rem;
        border-radius: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Agent Pipeline")
    st.markdown("""
    **How it works:**

    1. 🎯 **Orchestrator**
       Analyses your task, creates a spec

    2. ✏️ **Code Writer**
       Writes clean Python code

    3. 🔍 **Code Reviewer**
       Reviews for bugs and style

    4. 🧪 **Test Writer**
       Generates and runs pytest tests

    ↩️ *Critical issues loop back to writer (max 3 times)*
    """)
    st.divider()
    st.caption("Built with LangGraph + Claude + MCP")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🤖 Multi-Agent Coding Assistant")
st.caption("Describe a coding task — the agents will write, review, and test it for you.")

col_input, col_button = st.columns([5, 1])

with col_input:
    task = st.text_area(
        "Describe what you want to build:",
        height=140,
        placeholder=(
            "Examples:\n"
            "- Write a function that validates email addresses\n"
            "- Build a Stack class with push, pop, and peek\n"
            "- Create a function that flattens a nested list"
        )
    )

with col_button:
    st.write("")  # spacing
    st.write("")
    run_button = st.button(
        "▶ Run",
        type="primary",
        disabled=not task.strip(),
        use_container_width=True
    )
