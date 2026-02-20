# eval/benchmarks.py

BENCHMARKS = [
    # ── EASY ──────────────────────────────────────────────────────────────
    {
        "id":         "celsius_to_fahrenheit",
        "difficulty": "easy",
        "task": (
            "Write a Python function called celsius_to_fahrenheit that converts "
            "a temperature from Celsius to Fahrenheit. "
            "Formula: fahrenheit = (celsius * 9/5) + 32. "
            "Handle non-numeric input by raising a TypeError."
        ),
    },
    {
        "id":         "is_palindrome",
        "difficulty": "easy",
        "task": (
            "Write a Python function called is_palindrome that checks whether "
            "a given string is a palindrome (reads the same forwards and backwards). "
            "Ignore case and spaces. Return True or False. "
            "Raise TypeError if input is not a string."
        ),
    },
    {
        "id":         "count_words",
        "difficulty": "easy",
        "task": (
            "Write a Python function called count_words that counts the number "
            "of words in a given string. "
            "Words are separated by whitespace. An empty string returns 0. "
            "Raise TypeError if input is not a string."
        ),
    },
    {
        "id":         "factorial",
        "difficulty": "easy",
        "task": (
            "Write a Python function called factorial that computes the factorial "
            "of a non-negative integer n (n!). "
            "Use recursion. factorial(0) = 1. "
            "Raise ValueError if n is negative. Raise TypeError if n is not an integer."
        ),
    },

    # ── MEDIUM ────────────────────────────────────────────────────────────
    {
        "id":         "binary_search",
        "difficulty": "medium",
        "task": (
            "Write a Python function called binary_search that searches for a "
            "target value in a sorted list and returns its index, or -1 if not found. "
            "Use the binary search algorithm (O log n). "
            "Raise TypeError if the list is not a list or target is not an int/float. "
            "Raise ValueError if the list is not sorted."
        ),
    },
    {
        "id":         "flatten_list",
        "difficulty": "medium",
        "task": (
            "Write a Python function called flatten_list that takes a nested list "
            "(lists within lists, any depth) and returns a single flat list "
            "with all values in order. "
            "Example: flatten_list([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]. "
            "Raise TypeError if input is not a list."
        ),
    },
    {
        "id":         "validate_email",
        "difficulty": "medium",
        "task": (
            "Write a Python function called validate_email that checks whether "
            "a string is a valid email address. "
            "Rules: must contain exactly one '@', domain must contain at least one '.', "
            "no spaces allowed, local part must not be empty. "
            "Return True if valid, False otherwise. "
            "Raise TypeError if input is not a string."
        ),
    },
    {
        "id":         "merge_sort",
        "difficulty": "medium",
        "task": (
            "Write a Python function called merge_sort that sorts a list of numbers "
            "using the merge sort algorithm (O n log n). "
            "Return a new sorted list, do not modify the original. "
            "Handle empty list and single-element list as base cases. "
            "Raise TypeError if input is not a list."
        ),
    },

    # ── HARD ──────────────────────────────────────────────────────────────
    {
        "id":         "lru_cache",
        "difficulty": "hard",
        "task": (
            "Write a Python class called LRUCache that implements a "
            "Least Recently Used cache with a fixed capacity. "
            "Methods: __init__(capacity: int), get(key: int) -> int (return -1 if not found), "
            "put(key: int, value: int) -> None. "
            "When capacity is exceeded, evict the least recently used item. "
            "Use collections.OrderedDict internally. "
            "Raise ValueError if capacity is less than 1."
        ),
    },
    {
        "id":         "rate_limiter",
        "difficulty": "hard",
        "task": (
            "Write a Python class called RateLimiter that limits how many times "
            "a function can be called within a time window. "
            "Methods: __init__(max_calls: int, period_seconds: float), "
            "is_allowed(identifier: str) -> bool. "
            "is_allowed returns True if the identifier has made fewer than max_calls "
            "in the last period_seconds, False otherwise. "
            "Use a dict to track call timestamps per identifier. "
            "Raise ValueError if max_calls < 1 or period_seconds <= 0."
        ),
    },
]


def get_benchmarks(difficulty: str = "all") -> list:
    """Return benchmarks filtered by difficulty level.

    Args:
        difficulty: 'easy', 'medium', 'hard', or 'all'.

    Returns:
        List of benchmark dicts.
    """
    if difficulty == "all":
        return BENCHMARKS
    return [b for b in BENCHMARKS if b["difficulty"] == difficulty]


if __name__ == "__main__":
    for level in ["easy", "medium", "hard"]:
        tasks = get_benchmarks(level)
        print(f"\n{level.upper()} ({len(tasks)} tasks):")
        for t in tasks:
            print(f"  • {t['id']}")