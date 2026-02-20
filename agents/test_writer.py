# agents/test_writer.py
# ─────────────────────────────────────────────────────────────────────────────
# Generates pytest tests for approved code and runs them in Docker sandbox.
# ─────────────────────────────────────────────────────────────────────────────

import os
import anthropic
from dotenv import load_dotenv
from agents.mcp_client import call_mcp_tool
from langsmith import traceable
load_dotenv()

MODEL  = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5-20251101")
client = anthropic.Anthropic()


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences if the LLM added them."""
    text = text.strip()
    if text.startswith("```python"):
        text = text[9:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

@traceable(name="test-writer-agent", tags=["agent"])
def test_writer_agent(state: dict) -> dict:
    """
    Generate pytest tests for the approved code and execute them in Docker.

    Args:
        state: LangGraph shared state dict

    Returns:
        Updated state with test code and execution results
    """
    code = state["code"]
    task = state["task"]

    prompt = f"""You are a Python testing expert. Write pytest tests for this code.

ORIGINAL TASK:
{task}

CODE TO TEST:
```python
{code}
```

Write pytest tests covering:
1. Happy path — normal valid input that should work
2. Edge case 1 — boundary input (empty string, zero, empty list)
3. Edge case 2 — another tricky input
4. Error case — test that an exception is raised for invalid input

CRITICAL RULES:
- Copy the function definitions from the code above into your test file
  (do NOT use import statements — paste the functions at the top)
- Every test function name must start with test_
- Use pytest.raises() for exception tests
- Output ONLY raw Python code — no markdown, no explanations"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    tests = _strip_code_fences(response.content[0].text)

    # Combine original code + tests for self-contained execution
    combined = f"import pytest\n\n{code}\n\n# ── Tests ──\n\n{tests}"

    # Save to workspace
    call_mcp_tool("write_file", {
        "path":    "workspace/test_generated.py",
        "content": combined
    })

    # Run in Docker sandbox via MCP
    test_results = "Tests were not executed"
    try:
        exec_output = call_mcp_tool("execute_code", {"code": combined})

        if "exit code: 0" in exec_output.lower():
            test_results = f"TESTS PASSED\n\n{exec_output}"
        elif "error" in exec_output.lower() or "failed" in exec_output.lower():
            test_results = f"TESTS FAILED\n\n{exec_output}"
        else:
            test_results = exec_output

    except Exception as e:
        test_results = f"Could not execute tests: {str(e)}"

    return {
        **state,
        "tests":        tests,
        "test_results": test_results,
        "messages":     [
            {"role": "test_writer", "content": "Tests generated and executed in Docker sandbox"}
        ]
    }