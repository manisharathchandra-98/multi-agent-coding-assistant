# agents/code_writer.py
# ─────────────────────────────────────────────────────────────────────────────
# Generates clean Python code from the orchestrator's specification.
# On revision runs it fixes the specific issues raised by the reviewer.
# ─────────────────────────────────────────────────────────────────────────────

import os
import anthropic
from agents.mcp_client import call_mcp_tool
from langsmith import traceable

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@traceable(name="code-writer-agent", tags=["agent"])
def code_writer_agent(state: dict) -> dict:
    """Writes Python code based on the task specification.
    On revision loops, incorporates reviewer feedback.
    Uses RAG to find relevant best practices before writing.
    """
    task       = state.get("task", "")
    review     = state.get("review", "")
    iterations = state.get("iterations", 0)

    # ── Step 1: Search RAG knowledge base ─────────────────────────────────
    rag_context = call_mcp_tool("query_docs", {"query": task, "n_results": 3})

    # ── Step 2: Build prompt ───────────────────────────────────────────────
    if iterations == 0:
        prompt = f"""You are an expert Python developer. Write clean, production-quality Python code.

TASK:
{task}

RELEVANT BEST PRACTICES (from knowledge base):
{rag_context}

REQUIREMENTS:
- Use type hints on all function parameters and return types
- Include a clear docstring (Args, Returns, Raises sections)
- Handle edge cases and invalid inputs with proper exceptions
- Follow PEP 8 naming conventions (snake_case)
- Return ONLY the Python code, no explanation, no markdown fences
"""
    else:
        prompt = f"""You are an expert Python developer. Revise the code based on the review feedback.

ORIGINAL TASK:
{task}

CURRENT CODE:
{state.get('code', '')}

REVIEWER FEEDBACK (fix these issues):
{review}

RELEVANT BEST PRACTICES (from knowledge base):
{rag_context}

REQUIREMENTS:
- Fix ALL issues mentioned in the review
- Keep type hints, docstrings, and error handling
- Return ONLY the revised Python code, no explanation, no markdown fences
"""

    # ── Step 3: Call Claude ────────────────────────────────────────────────
    response = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    code = response.content[0].text.strip()

    # Strip markdown fences if Claude adds them
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()

    # ── Step 4: Save code to workspace via MCP ─────────────────────────────
    call_mcp_tool("write_file", {
        "filename": "generated_code.py",
        "content":  code
    })

    action = "revised" if iterations > 0 else "written"
    return {
        "code":       code,
        "iterations": iterations + 1,
        "messages":   [{"role": "code_writer", "content": f"Code {action} (iteration {iterations + 1}). RAG context retrieved successfully."}]
    }