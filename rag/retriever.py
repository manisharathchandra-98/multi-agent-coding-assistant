# rag/retriever.py
import json
import math
import re
from collections import Counter

from qdrant_client import QdrantClient

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


def tokenize(text: str) -> list:
    words = re.findall(r'\b[a-zA-Z][a-zA-Z_]*\b', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def vectorize_query(query: str, vocab_data: dict) -> list:
    """Convert a query string into the same TF-IDF vector space as the index."""
    vocab_index = vocab_data["vocab_index"]
    doc_freq    = vocab_data["doc_freq"]
    num_docs    = vocab_data["num_docs"]
    dimension   = vocab_data["dimension"]

    tokens = tokenize(query)
    tf     = Counter(tokens)
    total  = len(tokens) or 1

    vector = [0.0] * dimension
    for word, count in tf.items():
        if word in vocab_index:
            tf_score  = count / total
            idf_score = math.log((num_docs + 1) / (doc_freq.get(word, 0) + 1)) + 1
            vector[vocab_index[word]] = tf_score * idf_score

    return vector


def query_docs(query: str, n_results: int = 3) -> str:
    """Search Qdrant for documents most relevant to the query.

    Args:
        query: Natural language search query.
        n_results: Number of top results to return.

    Returns:
        Formatted string of the most relevant knowledge snippets.
    """
    try:
        with open(VOCAB_PATH, "r", encoding="utf-8") as f:
            vocab_data = json.load(f)
    except FileNotFoundError:
        return "Knowledge base not found. Run: python rag/indexer.py"

    query_vector = vectorize_query(query, vocab_data)

    if all(v == 0.0 for v in query_vector):
        return "No known terms found in query — try different wording."

    try:
        client  = QdrantClient(path=QDRANT_PATH)
        results = client.query_points(
            collection_name=COLLECTION,
            query=query_vector,
            limit=n_results,
        ).points
    except Exception as e:
        return f"Qdrant search failed: {e}"

    if not results:
        return "No relevant documents found."

    snippets = []
    for i, hit in enumerate(results):
        topic   = hit.payload.get("topic",   "general")
        content = hit.payload.get("content", "")
        score   = round(hit.score, 3)
        snippets.append(f"[Snippet {i+1} — {topic} (score: {score})]\n{content}")

    return "\n\n".join(snippets)


if __name__ == "__main__":
    test_queries = [
        "write a recursive fibonacci function",
        "how to sort a list in python",
        "validate email address format",
        "convert celsius to fahrenheit",
        "handle errors and exceptions",
    ]
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        print("-" * 60)
        print(query_docs(q, n_results=2))