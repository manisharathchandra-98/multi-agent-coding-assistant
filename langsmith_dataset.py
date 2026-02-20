# langsmith_dataset.py
"""
Creates a LangSmith dataset from benchmark tasks and uploads
eval results so you can replay evaluations from the LangSmith UI.
"""
import json
import os
from dotenv import load_dotenv
from langsmith import Client
from eval.benchmarks import get_benchmarks

load_dotenv()

DATASET_NAME = "multi-agent-coder-benchmarks"

def create_dataset():
    client     = Client()
    benchmarks = get_benchmarks("all")

    # Delete existing dataset if it exists (clean re-run)
    try:
        existing = client.read_dataset(dataset_name=DATASET_NAME)
        client.delete_dataset(dataset_id=existing.id)
        print(f"🗑️  Deleted existing dataset: {DATASET_NAME}")
    except Exception:
        pass

    # Create fresh dataset
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Benchmark tasks for the Multi-Agent Coding Assistant pipeline"
    )
    print(f"✅ Created dataset: {DATASET_NAME}")

    # Add each benchmark task as an example
    for b in benchmarks:
        client.create_example(
            inputs={"task": b["task"], "difficulty": b["difficulty"]},
            outputs={"expected_syntax": 1, "expected_docstring": 1,
                     "expected_type_hints": 1, "expected_error_handling": 1},
            dataset_id=dataset.id,
            metadata={"id": b["id"], "difficulty": b["difficulty"]}
        )
        print(f"   + Added: {b['id']} ({b['difficulty']})")

    print(f"\n✅ Dataset ready — {len(benchmarks)} examples uploaded")
    print(f"   View at: https://smith.langchain.com")
    return dataset

def upload_eval_results():
    """Upload existing eval results to LangSmith for tracking."""
    results_file = "eval/eval_results.json"
    if not os.path.exists(results_file):
        print("⚠️  No eval_results.json found — run run_eval.py first")
        return

    client = Client()
    with open(results_file) as f:
        data = json.load(f)

    results  = data.get("results", [])
    summary  = data.get("summary", {})

    print(f"\n📊 Eval Results Summary:")
    print(f"   Difficulty    : {summary.get('difficulty', 'N/A')}")
    print(f"   Tasks Run     : {summary.get('total_tasks', 0)}")
    print(f"   Average Score : {summary.get('average_score', 0)}%")
    print(f"   Tests Passed  : {summary.get('tests_passed', 0)}/{summary.get('total_tasks', 0)}")
    print(f"\n   Per-task breakdown:")
    for r in results:
        score = r["scores"].get("total", 0)
        tests = "✅" if r["scores"].get("test_pass_rate", 0) == 1 else "❌"
        print(f"   {r['task_id']:<25} {score:>5.1f}%  {tests}")

if __name__ == "__main__":
    print("=== LangSmith Dataset Setup ===\n")
    create_dataset()
    upload_eval_results()
    print("\n Done! Open smith.langchain.com → Datasets to see your benchmark set.")