# run_eval.py
import time
import json
import os
from dotenv import load_dotenv
import langsmith_setup
from langsmith import traceable

load_dotenv()

from agents.graph import run_pipeline
from eval.metrics import score_code, format_score_report
from eval.benchmarks import get_benchmarks

RESULTS_FILE = "eval/eval_results.json"

langsmith_setup.verify_langsmith()

@traceable(name="benchmark-run", tags=["eval"])
def run_benchmark(task_name: str, task_description: str) -> dict:
    """Runs a single benchmark task through the pipeline — traced in LangSmith."""
    return run_pipeline(task_description)

def run_evaluation(difficulty: str = "easy"):
    """Run the pipeline on all benchmarks and score the results.

    Args:
        difficulty: 'easy', 'medium', 'hard', or 'all'
    """
    benchmarks = get_benchmarks(difficulty)
    print(f"\n{'='*60}")
    print(f"  MULTI-AGENT CODING ASSISTANT — EVALUATION")
    print(f"  Running {len(benchmarks)} benchmarks ({difficulty})")
    print(f"{'='*60}\n")

    all_results = []

    for i, benchmark in enumerate(benchmarks, 1):
        task_id = benchmark["id"]
        task    = benchmark["task"]

        print(f"[{i}/{len(benchmarks)}] Running: {task_id} ({benchmark['difficulty']})...")

        start_time = time.time()
        try:
            result     = result = run_benchmark(task_id, task)
            time_taken = round(time.time() - start_time, 1)

            code         = result.get("code", "")
            test_results = result.get("test_results", "")
            iterations   = result.get("iterations", 1)

            scores = score_code(code, test_results)
            if test_results and test_results.strip() not in ["", "(no output)"]:
                preview = test_results.strip()[:300]
                print(f"  Test output: {preview}\n")

            print(format_score_report(task_id, scores, time_taken))
            print(f"  Iterations: {iterations}")
            print()

            all_results.append({
                "task_id":    task_id,
                "difficulty": benchmark["difficulty"],
                "scores":     scores,
                "iterations": iterations,
                "time":       time_taken,
                "code":       code,
            })

        except Exception as e:
            time_taken = round(time.time() - start_time, 1)
            print(f"  ❌ FAILED: {e}\n")
            all_results.append({
                "task_id":    task_id,
                "difficulty": benchmark["difficulty"],
                "scores":     {"total": 0},
                "iterations": 0,
                "time":       time_taken,
                "error":      str(e),
            })

    # ── Summary table ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Task':<25} {'Score':>6}  {'Tests':>6}  {'Time':>6}")
    print(f"  {'-'*50}")

    total_score = 0
    tests_passed = 0

    for r in all_results:
        score      = r["scores"].get("total", 0)
        test_rate  = r["scores"].get("test_pass_rate", 0)
        time_taken = r.get("time", 0)
        test_icon  = "✅" if test_rate == 1 else ("⚠️ " if test_rate > 0 else "❌")

        print(f"  {r['task_id']:<25} {score:>5.1f}%  {test_icon:>5}  {time_taken:>5.1f}s")
        total_score  += score
        tests_passed += (1 if test_rate == 1 else 0)

    avg_score = total_score / len(all_results) if all_results else 0

    print(f"  {'-'*50}")
    print(f"  {'AVERAGE':<25} {avg_score:>5.1f}%  {tests_passed}/{len(all_results)} passed")
    print(f"{'='*60}\n")

    # ── Save results ───────────────────────────────────────────────────────
    os.makedirs("eval", exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "summary": {
                "difficulty":    difficulty,
                "total_tasks":   len(all_results),
                "average_score": round(avg_score, 1),
                "tests_passed":  tests_passed,
            },
            "results": all_results,
        }, f, indent=2)

    print(f"Results saved to {RESULTS_FILE}")
    return avg_score


if __name__ == "__main__":
    # Start with easy tasks only (fastest — ~4 tasks × ~20s = ~2 minutes)
    run_evaluation(difficulty="easy")