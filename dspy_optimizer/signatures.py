# dspy_optimizer/signatures.py
import dspy

class PlanTask(dspy.Signature):
    """Plan a Python coding task into clear implementation steps."""
    task = dspy.InputField(desc="The coding task to implement")
    plan = dspy.OutputField(desc="Step-by-step implementation plan")

class WriteCode(dspy.Signature):
    """Write clean, production-quality Python code following best practices."""
    task        = dspy.InputField(desc="The coding task")
    plan        = dspy.InputField(desc="Implementation plan to follow")
    rag_context = dspy.InputField(desc="Relevant Python best practices from knowledge base")
    code        = dspy.OutputField(desc="Complete Python code with type hints, docstrings, and error handling")

class ReviewCode(dspy.Signature):
    """Review Python code quality and provide actionable feedback."""
    task     = dspy.InputField(desc="The original coding task")
    code     = dspy.InputField(desc="The Python code to review")
    score    = dspy.OutputField(desc="Quality score from 1-10")
    feedback = dspy.OutputField(desc="Specific, actionable improvement suggestions")