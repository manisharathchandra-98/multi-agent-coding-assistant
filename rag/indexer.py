# rag/indexer.py
import json
import math
import os
import re
from collections import Counter

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_PATH = "qdrant_db"
VOCAB_PATH  = "rag/vocab.json"
COLLECTION  = "coding_knowledge"

STOP_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "is", "are", "was", "be", "by", "it", "this", "that", "with", "use",
    "can", "will", "not", "from", "has", "have", "its", "as", "but", "if",
    "each", "all", "any", "both", "how", "what", "when", "where", "which",
    "using", "used", "also", "into", "than", "then", "so", "do",
}

DOCUMENTS = [
    {
        "id": "type_hints",
        "content": (
            "Python type hints best practices: Always annotate function parameters and return types. "
            "Use -> to annotate return type. Use Optional[X] for values that can be None. "
            "Use List[X], Dict[K,V], Tuple[X,Y] from typing for collections. "
            "Example: def add(a: int, b: int) -> int: return a + b"
        ),
        "metadata": {"topic": "type_hints"}
    },
    {
        "id": "docstrings",
        "content": (
            "Python docstring conventions: Every function must have a docstring. "
            "Use triple double-quotes. Include Args, Returns, Raises sections. "
            "Example: def divide(a: float, b: float) -> float: "
            '"""Divide a by b. Args: a: Numerator. b: Denominator. '
            "Returns: Result of a / b. Raises: ValueError: If b is zero.\"\"\""
        ),
        "metadata": {"topic": "docstrings"}
    },
    {
        "id": "error_handling",
        "content": (
            "Python error handling best practices: Use specific exception types, not bare except. "
            "Raise ValueError for invalid inputs, TypeError for wrong types, RuntimeError for unexpected states. "
            "Always validate inputs at the top of the function. "
            "Example: if not isinstance(n, int): raise TypeError('Expected int') "
            "if n < 0: raise ValueError('n must be non-negative')"
        ),
        "metadata": {"topic": "error_handling"}
    },
    {
        "id": "naming_conventions",
        "content": (
            "Python naming conventions PEP 8: Use snake_case for functions and variables. "
            "Use UPPER_CASE for constants. Use PascalCase for class names. "
            "Function names should be verbs: calculate_total, get_user, is_valid, convert_celsius. "
            "Variable names should be descriptive: user_count not uc, total_price not tp."
        ),
        "metadata": {"topic": "naming"}
    },
    {
        "id": "list_operations",
        "content": (
            "Python list operations and patterns: Use list comprehensions for transformations. "
            "[x*2 for x in items if x > 0]. Use enumerate() when you need index and value. "
            "Use zip() to iterate multiple lists together. Use sorted() with key= for custom sort. "
            "Sort by length: sorted(words, key=len). Use any() and all() for boolean checks on lists."
        ),
        "metadata": {"topic": "lists"}
    },
    {
        "id": "recursion",
        "content": (
            "Python recursion patterns: Always define a base case first to stop recursion. "
            "Fibonacci: if n <= 1: return n; return fib(n-1) + fib(n-2). "
            "Factorial: if n == 0: return 1; return n * factorial(n-1). "
            "Use memoization with @functools.lru_cache to avoid recomputation. "
            "Python default recursion limit is 1000 calls deep."
        ),
        "metadata": {"topic": "recursion"}
    },
    {
        "id": "string_operations",
        "content": (
            "Python string operations: Use f-strings for formatting: f'Hello {name}'. "
            "Use .strip() to remove whitespace. Use .split() and .join() for parsing. "
            "Use .lower() and .upper() for case-insensitive comparisons. "
            "Palindrome check: s == s[::-1]. Count words: len(text.split()). "
            "Reverse a string: s[::-1]. Check substring: 'hello' in text."
        ),
        "metadata": {"topic": "strings"}
    },
    {
        "id": "sorting_algorithms",
        "content": (
            "Python sorting algorithms: Bubble sort O(n^2): compare adjacent elements swap if out of order. "
            "Merge sort O(n log n): divide list in half sort each half then merge sorted halves. "
            "Binary search O(log n) requires sorted input: compare middle element go left or right. "
            "Python built-in sort() uses Timsort O(n log n). "
            "Selection sort: find minimum element swap to front repeat."
        ),
        "metadata": {"topic": "algorithms"}
    },
    {
        "id": "data_structures",
        "content": (
            "Python data structures: Use dict for O(1) lookup by key. "
            "Use set for O(1) membership testing and deduplication. "
            "Use collections.defaultdict to avoid KeyError on missing keys. "
            "Use collections.Counter to count occurrences of elements. "
            "Use collections.deque for O(1) append and pop from both ends. "
            "Stack uses append() and pop(). Queue uses append() and popleft()."
        ),
        "metadata": {"topic": "data_structures"}
    },
    {
        "id": "testing_patterns",
        "content": (
            "Python pytest best practices: Test function names start with test_. "
            "Use assert statements for checks: assert add(2,3) == 5. "
            "Test edge cases: empty input, None, negative numbers, zero, large values. "
            "Use pytest.raises to test exceptions: with pytest.raises(ValueError): func(-1). "
            "Test boundary values: test with 0, 1, -1 and large numbers. "
            "Each test should test one thing only."
        ),
        "metadata": {"topic": "testing"}
    },
    {
        "id": "math_operations",
        "content": (
            "Python math operations: Use math module for sqrt, floor, ceil, pi, e. "
            "Integer division: use // operator. Modulo: use % operator. Power: use ** operator. "
            "GCD: use math.gcd(a, b). Check prime: trial division up to sqrt(n). "
            "Celsius to Fahrenheit: fahrenheit = (celsius * 9/5) + 32. "
            "Fahrenheit to Celsius: celsius = (fahrenheit - 32) * 5/9."
        ),
        "metadata": {"topic": "math"}
    },
    {
        "id": "validation_patterns",
        "content": (
            "Python input validation: Validate at function entry point before any logic. "
            "Email validation: check '@' present, domain has dot, no spaces in address. "
            "Phone validation: strip non-digits, check length is 10 or 11 digits. "
            "Range validation: if not min_val <= value <= max_val: raise ValueError. "
            "Type validation: if not isinstance(value, expected_type): raise TypeError."
        ),
        "metadata": {"topic": "validation"}
    },
    {
        "id": "classes_oop",
        "content": (
            "Python OOP class patterns: Define __init__ with self and parameters. "
            "Use @property for computed attributes. Use @staticmethod for utility methods. "
            "Use __repr__ for debugging string representation of object. "
            "Stack class methods: push(), pop(), peek(), is_empty(), size(). "
            "Queue class methods: enqueue(), dequeue(), front(), is_empty()."
        ),
        "metadata": {"topic": "oop"}
    },
    {
        "id": "functional_patterns",
        "content": (
            "Python functional programming: Use map() to transform: list(map(str, numbers)). "
            "Use filter() to select: list(filter(lambda x: x > 0, numbers)). "
            "Use functools.reduce() for accumulation across a list. "
            "Lambda functions: lambda x: x * 2 for simple one-line transforms. "
            "Use zip() to pair elements from two lists together."
        ),
        "metadata": {"topic": "functional"}
    },
    {
        "id": "file_operations",
        "content": (
            "Python file operations: Always use 'with open()' context manager. "
            "Read text: with open(path, 'r') as f: content = f.read(). "
            "Write text: with open(path, 'w') as f: f.write(content). "
            "Read lines: with open(path) as f: lines = f.readlines(). "
            "Check exists: Path(path).exists(). Create dirs: Path(path).mkdir(parents=True, exist_ok=True)."
        ),
        "metadata": {"topic": "file_io"}
    },
]


def tokenize(text: str) -> list:
    words = re.findall(r'\b[a-zA-Z][a-zA-Z_]*\b', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def build_index():
    print("Building RAG index with Qdrant...")

    # ── Step 1: Tokenize all documents ────────────────────────────────────
    all_tokens = [tokenize(d["content"]) for d in DOCUMENTS]

    # ── Step 2: Build vocabulary (every unique word = one dimension) ──────
    vocabulary  = sorted(set(t for tokens in all_tokens for t in tokens))
    vocab_index = {word: i for i, word in enumerate(vocabulary)}
    dimension   = len(vocabulary)
    print(f"Vocabulary size: {dimension} unique terms")

    # ── Step 3: Compute document frequencies (how many docs contain word) ─
    doc_freq: Counter = Counter()
    for tokens in all_tokens:
        doc_freq.update(set(tokens))

    num_docs = len(DOCUMENTS)

    # ── Step 4: TF-IDF vectorizer ──────────────────────────────────────────
    def vectorize(tokens: list) -> list:
        """Convert a token list into a fixed-length TF-IDF vector."""
        vector = [0.0] * dimension
        tf     = Counter(tokens)
        total  = len(tokens) or 1
        for word, count in tf.items():
            if word in vocab_index:
                tf_score  = count / total
                idf_score = math.log((num_docs + 1) / (doc_freq[word] + 1)) + 1
                vector[vocab_index[word]] = tf_score * idf_score
        return vector

    # ── Step 5: Save vocabulary for query-time use ─────────────────────────
    os.makedirs("rag", exist_ok=True)
    with open(VOCAB_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "vocabulary":  vocabulary,
            "vocab_index": vocab_index,
            "doc_freq":    dict(doc_freq),
            "num_docs":    num_docs,
            "dimension":   dimension,
        }, f)
    print(f"Vocabulary saved to {VOCAB_PATH}")

    # ── Step 6: Store vectors in Qdrant ────────────────────────────────────
    client = QdrantClient(path=QDRANT_PATH)

    # Delete and recreate the collection fresh
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
    )

    points = [
        PointStruct(
            id=i,
            vector=vectorize(tokens),
            payload={
                "doc_id":  doc["id"],
                "content": doc["content"],
                "topic":   doc["metadata"]["topic"],
            },
        )
        for i, (doc, tokens) in enumerate(zip(DOCUMENTS, all_tokens))
    ]

    client.upsert(collection_name=COLLECTION, points=points)

    print(f"\n✅ Indexed {len(points)} documents into Qdrant")
    print(f"   Vector dimension : {dimension}")
    print(f"   Similarity metric: Cosine")
    print(f"   Persisted to     : {QDRANT_PATH}/")
    print("\nTopics indexed:")
    for t in sorted(set(d["metadata"]["topic"] for d in DOCUMENTS)):
        print(f"   • {t}")


if __name__ == "__main__":
    build_index()