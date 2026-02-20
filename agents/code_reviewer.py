# agents/code_reviewer.py
# ─────────────────────────────────────────────────────────────────────────────
# Reviews the generated code and returns structured JSON feedback.
# The severity field drives the LangGraph routing decision.
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import json
import anthropic
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

MODEL  = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5-20251101")
client = anthropic.Anthropic()


def _parse_review_json(text: str) -> dict:
    """Extract and parse the JSON block from the reviewer response."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass

    return {
        "issues":   [],
        "severity": "none",
        "summary":  text[:300] if text else "Review could not be parsed"
    }


def _format_review(review_json: dict) -> str:
    """Turn structured review JSON into a readable string."""
    issues   = review_json.get("issues", [])
    severity = review_json.get("severity", "none").upper()
    summary  = review_json.get("summary", "")

    if not issues:
        return f"No issues found. {summary}"

    lines = [f"Severity: {severity}\n"]
    for i, issue in enumerate(issues, 1):
        s = issue.get("severity", "minor").upper()
        d = issue.get("description", "")
        t = issue.get("type", "general")
        lines.append(f"{i}. [{s}] ({t}) {d}")

    lines.append(f"\nSummary: {summary}")
    return "\n".join(lines)

@traceable(name="code-reviewer-agent", tags=["agent"])
def code_reviewer_agent(state: dict) -> dict:
    """
    Review generated code and return structured feedback with severity level.

    severity = "critical" → LangGraph routes back to code_writer
    severity = "minor" or "none" → LangGraph routes forward to test_writer

    Args:
        state: LangGraph shared state dict

    Returns:
        Updated state with review text and structured review_json
    """
    code = state["code"]
    task = state["task"]

    prompt = f"""You are a senior Python developer doing a thorough code review.

ORIGINAL TASK:
{task}

CODE TO REVIEW:
```python
{code}
```

Check for ALL of the following:
1. Logic bugs — does it actually do what the task asks?
2. Missing type hints — every function needs them on all parameters and return
3. Missing docstrings — every function needs a docstring
4. Security issues — unsafe eval, path traversal, hardcoded secrets
5. Unhandled edge cases — empty input, None values, negative numbers
6. Style — confusing names, overly complex logic

Respond with ONLY valid JSON, nothing else before or after:
{{
    "issues": [
        {{
            "type": "bug|missing_types|missing_docs|security|edge_case|style",
            "description": "specific description of the problem",
            "severity": "critical|minor"
        }}
    ],
    "severity": "critical|minor|none",
    "summary": "one sentence overall assessment"
}}

Top-level severity rules:
- "critical" → any issue that causes wrong behaviour, crash, or security risk
- "minor" → style or cosmetic issues only
- "none" → code is correct and complete"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    review_json = _parse_review_json(response.content[0].text.strip())
    review_text = _format_review(review_json)
    severity    = review_json.get("severity", "none")

    return {
        **state,
        "review":      review_text,
        "review_json": review_json,
        "messages":   [
            {"role": "code_reviewer", "content": f"Review done — severity: {severity.upper()}, issues: {len(review_json.get('issues', []))}"}
        ]
    }