# agents/graph.py
# ─────────────────────────────────────────────────────────────────────────────
# The LangGraph state machine — connects all four agents together.
#
# Flow:
#   orchestrator → code_writer → code_reviewer ──► test_writer → END
#                                      │
#                     (critical issues)└──► back to code_writer (max 3 times)
# ─────────────────────────────────────────────────────────────────────────────

import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import langsmith_setup
from langsmith import traceable


from agents.orchestrator  import orchestrator_agent
from agents.code_writer   import code_writer_agent
from agents.code_reviewer import code_reviewer_agent
from agents.test_writer   import test_writer_agent


# ── Shared State ──────────────────────────────────────────────────────────────
# Every agent reads from this and writes back to this.
# Think of it as the shared whiteboard all agents can see.

class AgentState(TypedDict):
    task:         str    # The coding task (enriched by orchestrator)
    code:         str    # Latest generated code
    review:       str    # Human-readable review feedback
    review_json:  dict   # Structured review with severity level
    tests:        str    # Generated test code
    test_results: str    # Output from running the tests
    iterations:   int    # How many write cycles have happened (max 3)
    messages:     Annotated[list, operator.add]  # Activity log


# ── Routing Function ──────────────────────────────────────────────────────────
# This function runs after every review and decides what happens next.
# It is the traffic light of your agent pipeline.

def route_after_review(state: AgentState) -> str:
    """
    Read the reviewer's verdict and decide where to go next.

    Returns:
        "revise"  → sends code back to code_writer for fixes
        "approve" → sends code forward to test_writer
    """
    review_json = state.get("review_json", {})
    severity    = review_json.get("severity", "none")
    iterations  = state.get("iterations", 0)

    # Only send back for revision if issues are critical AND
    # we have not already done 3 revision loops
    if severity == "critical" and iterations < 3:
        return "revise"

    return "approve"


# ── Graph Assembly ────────────────────────────────────────────────────────────

def build_graph():
    """
    Wire all four agents together into a compiled LangGraph pipeline.

    Usage:
        graph  = build_graph()
        result = graph.invoke({"task": "Write a function...", "iterations": 0, ...})
    """
    g = StateGraph(AgentState)

    # Register each agent as a node in the graph
    g.add_node("orchestrator",  orchestrator_agent)
    g.add_node("code_writer",   code_writer_agent)
    g.add_node("code_reviewer", code_reviewer_agent)
    g.add_node("test_writer",   test_writer_agent)

    # Define the flow between nodes
    g.set_entry_point("orchestrator")
    g.add_edge("orchestrator",  "code_writer")
    g.add_edge("code_writer",   "code_reviewer")

    # After review → either revise or approve
    g.add_conditional_edges(
        "code_reviewer",
        route_after_review,
        {
            "revise":  "code_writer",  # Critical issues → back to writer
            "approve": "test_writer"   # Good code → forward to tester
        }
    )

    g.add_edge("test_writer", END)

    return g.compile()


graph = build_graph()
@traceable(name="multi-agent-pipeline", tags=["pipeline"])
def run_pipeline(task: str) -> dict:
    """Run the full multi-agent pipeline on a task and return the result."""
    result = graph.invoke({"task": task, "iterations": 0, "messages": []})
    return result