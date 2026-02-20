# agents/orchestrator.py
# ─────────────────────────────────────────────────────────────────────────────
# Takes the raw user task and enriches it into a clear coding specification.
# The Code Writer uses this specification — better spec = better code.
# ─────────────────────────────────────────────────────────────────────────────

import os
import anthropic
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

MODEL  = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5-20251101")
client = anthropic.Anthropic()

@traceable(name="orchestrator-agent", tags=["agent"])
def orchestrator_agent(state: dict) -> dict:
    """
    Analyse the raw user task and produce a structured coding specification.

    Args:
        state: LangGraph shared state dict

    Returns:
        Updated state with enriched task description
    """
    raw_task = state["task"]

    prompt = f"""You are a senior software architect. A developer has given you a task.
Your job is to analyse it and write a clear specification a Python developer can follow.

TASK: {raw_task}

Write a structured specification that includes:
1. Exactly which function(s) or class(es) to write, with their exact names
2. What each parameter should be called and its type
3. What the function returns and its type
4. At least two edge cases the code must handle
5. Any Python standard library modules that would be useful

Keep it concise — bullet points are fine. Do NOT write any code yourself."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    enriched_task = response.content[0].text.strip()

    return {
        **state,
        "task": enriched_task,
        "messages": [
            {"role": "orchestrator", "content": "Task analysed and structured into a specification"}
        ]
    }