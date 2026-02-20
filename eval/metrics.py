# eval/metrics.py
import ast
import re


def score_code(code: str, test_results: str) -> dict:
    """Score generated code on 5 quality dimensions.

    Args:
        code: The generated Python source code.
        test_results: Output string from pytest execution.

    Returns:
        Dict with individual scores and a total percentage.
    """
    scores = {}

    # ── 1. Syntax valid (can Python parse it?) ─────────────────────────────
    try:
        ast.parse(code)
        scores["syntax_valid"] = 1
    except SyntaxError:
        scores["syntax_valid"] = 0

    # ── 2. Has type hints (-> and : annotations) ───────────────────────────
    has_return_hint = bool(re.search(r'->\s*[\w\[\], |\'\"]+', code))
    has_param_hint  = bool(re.search(r'\w+\s*:\s*[\w\[\], |\'\"]+', code))
    scores["has_type_hints"] = 1 if (has_return_hint and has_param_hint) else 0

    # ── 3. Has docstring ───────────────────────────────────────────────────
    scores["has_docstring"] = 1 if ('"""' in code or "'''" in code) else 0

    # ── 4. Has error handling (raise or try/except) ────────────────────────
    has_raise = bool(re.search(r'\braise\s+\w+', code))
    has_try   = bool(re.search(r'\btry\s*:', code))
    scores["has_error_handling"] = 1 if (has_raise or has_try) else 0

    # ── 5. Tests passed ────────────────────────────────────────────────────
    if not test_results or test_results.strip() in ["", "(no output)"]:
        scores["test_pass_rate"] = 1.0   # ran but no output — partial credit
    elif any(kw in test_results.lower() for kw in ["failed", "error", "exception"]):
        scores["test_pass_rate"] = 0
    elif any(kw in test_results.lower() for kw in ["passed", "ok", "."]):
        scores["test_pass_rate"] = 1
    else:
        scores["test_pass_rate"] = 0.5   # unknown output — partial credit

    # ── Total score ────────────────────────────────────────────────────────
    total = (
        scores["syntax_valid"]      * 25 +
        scores["has_type_hints"]    * 20 +
        scores["has_docstring"]     * 20 +
        scores["has_error_handling"]* 20 +
        scores["test_pass_rate"]    * 15
    )
    scores["total"] = round(total, 1)

    return scores


def format_score_report(task: str, scores: dict, time_taken: float) -> str:
    """Format a score dict into a readable report string."""
    bars = {
        "syntax_valid":       ("Syntax Valid",       scores["syntax_valid"]       * 100),
        "has_type_hints":     ("Type Hints",         scores["has_type_hints"]     * 100),
        "has_docstring":      ("Docstring",          scores["has_docstring"]      * 100),
        "has_error_handling": ("Error Handling",     scores["has_error_handling"] * 100),
        "test_pass_rate":     ("Tests Passed",       scores["test_pass_rate"]     * 100),
    }
    lines = [f"Task: {task}", "-" * 45]
    for key, (label, pct) in bars.items():
        icon  = "✅" if pct == 100 else ("⚠️ " if pct > 0 else "❌")
        lines.append(f"  {icon}  {label:<20} {pct:.0f}%")
    lines.append("-" * 45)
    lines.append(f"  TOTAL SCORE: {scores['total']:.1f} / 100   ({time_taken:.1f}s)")
    return "\n".join(lines)