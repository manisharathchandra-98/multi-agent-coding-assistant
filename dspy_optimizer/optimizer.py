# dspy_optimizer/optimizer.py
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy_optimizer.signatures import PlanTask, WriteCode, ReviewCode
from eval.metrics import score_code
from agents.graph import run_pipeline
import os
import json
from dotenv import load_dotenv

load_dotenv()

def setup_dspy():
    lm = dspy.LM(
        model="anthropic/claude-3-haiku-20240307",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=2000
    )
    dspy.configure(lm=lm)
    print("✅ DSPy configured with Claude 3 Haiku")

class CodingPipeline(dspy.Module):
    """DSPy module mirroring our multi-agent pipeline."""
    def __init__(self):
        self.planner  = dspy.ChainOfThought(PlanTask)
        self.writer   = dspy.ChainOfThought(WriteCode)
        self.reviewer = dspy.ChainOfThought(ReviewCode)

    def forward(self, task: str, rag_context: str = "") -> dspy.Prediction:
        plan     = self.planner(task=task).plan
        code_out = self.writer(task=task, plan=plan, rag_context=rag_context).code
        review   = self.reviewer(task=task, code=code_out)
        return dspy.Prediction(
            plan=plan,
            code=code_out,
            score=review.score,
            feedback=review.feedback
        )

def code_quality_metric(example, pred, trace=None) -> float:
    """DSPy metric — scores generated code using our 5-dimension scorer."""
    try:
        scores = score_code(pred.code, "")
        return scores["total"] / 100.0
    except Exception:
        return 0.0

def build_training_set():
    return [
        dspy.Example(
            task="Write a Python function to check if a string is a palindrome",
            rag_context="Use type hints. Add docstring. Handle edge cases."
        ).with_inputs("task", "rag_context"),
        dspy.Example(
            task="Write a Python function to flatten a nested list",
            rag_context="Use recursion. Add type hints with List. Handle empty lists."
        ).with_inputs("task", "rag_context"),
        dspy.Example(
            task="Write a binary search function for a sorted list",
            rag_context="Return -1 if not found. Use type hints. Add docstring."
        ).with_inputs("task", "rag_context"),
        dspy.Example(
            task="Write a function to validate an email address using regex",
            rag_context="Use re module. Raise ValueError for invalid input. Add type hints."
        ).with_inputs("task", "rag_context"),
        dspy.Example(
            task="Write a Python function to compute the factorial of a number",
            rag_context="Handle negative numbers with ValueError. Use type hints."
        ).with_inputs("task", "rag_context"),
    ]

def score_pipeline(pipeline, examples) -> float:
    """Run pipeline on all examples and return average score."""
    scores = []
    for ex in examples:
        try:
            pred = pipeline(task=ex.task, rag_context=ex.rag_context)
            scores.append(score_code(pred.code, "")["total"])
        except Exception:
            scores.append(0.0)
    return round(sum(scores) / len(scores), 1)

def run_optimization():
    setup_dspy()

    pipeline = CodingPipeline()
    trainset = build_training_set()

    # Score BEFORE optimization
    print("\n📊 Scoring baseline (before optimization)...")
    before_score = score_pipeline(pipeline, trainset)
    print(f"   Baseline score: {before_score}%")

    # Run BootstrapFewShot optimizer
    print("\n🔧 Running BootstrapFewShot optimization...")
    optimizer = BootstrapFewShot(
        metric=code_quality_metric,
        max_bootstrapped_demos=2,
        max_labeled_demos=2
    )
    optimized = optimizer.compile(pipeline, trainset=trainset)

    # Score AFTER optimization
    print("\n📊 Scoring optimized pipeline (after optimization)...")
    after_score = score_pipeline(optimized, trainset)
    print(f"   Optimized score: {after_score}%")

    # Save results
    os.makedirs("dspy_optimizer", exist_ok=True)
    optimized.save("dspy_optimizer/optimized_pipeline.json")

    results = {
        "before_score": before_score,
        "after_score":  after_score,
        "improvement":  round(after_score - before_score, 1)
    }
    with open("dspy_optimizer/optimization_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*40}")
    print(f"  DSPy Optimization Results")
    print(f"{'='*40}")
    print(f"  Before : {before_score}%")
    print(f"  After  : {after_score}%")
    print(f"  Gain   : +{results['improvement']}%")
    print(f"{'='*40}")
    print(f"\n✅ Saved optimized_pipeline.json")
    return results

if __name__ == "__main__":
    run_optimization()