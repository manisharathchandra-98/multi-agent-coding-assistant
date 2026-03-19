# ui/app.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

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
    st.write("")
    st.write("")
    run_button = st.button(
        "▶ Run",
        type="primary",
        disabled=not task.strip(),
        use_container_width=True
    )

if run_button and task.strip():
    try:
        from agents.graph import run_pipeline
        from eval.metrics import score_code
    except Exception as e:
        st.error(f"❌ Import failed: {e}")
        st.stop()

    with st.spinner("🔄 Running pipeline..."):
        try:
            result = run_pipeline(task)
        except Exception as e:
            st.error(f"❌ Pipeline failed: {e}")
            st.stop()

    # ── Extract results from dict ─────────────────────────────────────────
    code         = result.get("code", "")
    review       = result.get("review", "")
    test_results = result.get("test_results", "")
    iterations   = result.get("iterations", 1)
    severity     = result.get("severity", "NONE")

    scores = score_code(code, test_results)

    st.success("🚀 Pipeline completed successfully!")
    st.divider()

    left, right = st.columns([3, 2])

    with left:
        st.markdown("## 📄 Generated Code")
        st.code(code, language="python")

        st.markdown("## 🔍 Review")
        st.markdown(f"**Severity:** `{severity}`")
        st.write(review)

        st.markdown("## 🧪 Test Results")
        if not test_results or test_results.strip() in ["", "(no output)"]:
            st.success("✅ All tests passed")
        elif "FAILED" in test_results or "error" in test_results.lower():
            st.error(test_results)
        else:
            st.success(test_results)

    with right:
        st.markdown("## 📊 Quality Score")

        total = scores.get("total", 0)
        color = "#2ecc71" if total >= 90 else "#f39c12" if total >= 70 else "#e74c3c"

        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem;
                    background:{color}22; border-radius:12px;
                    border:2px solid {color}; margin-bottom:1rem;">
            <div style="font-size:3rem; font-weight:700; color:{color};">{total}</div>
            <div style="font-size:1rem; color:#aaa;">out of 100</div>
        </div>
        """, unsafe_allow_html=True)

        metrics = [
            ("Syntax Valid",   scores.get("syntax_valid", 0),       25),
            ("Type Hints",     scores.get("has_type_hints", 0),     20),
            ("Docstring",      scores.get("has_docstring", 0),      20),
            ("Error Handling", scores.get("has_error_handling", 0), 20),
            ("Tests Passed",   scores.get("test_pass_rate", 0),     15),
        ]

        for name, score, weight in metrics:
            icon = "✅" if score == 1 else ("⚠️" if score > 0 else "❌")
            st.markdown(f"{icon} **{name}** *(weight: {weight}%)*")
            st.progress(float(score))

        st.divider()
        st.markdown(f"**Iterations:** {iterations}")
