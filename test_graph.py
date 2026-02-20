# test_graph.py — run this to verify Day 2 Morning works
from agents.graph import build_graph

graph = build_graph()
print("Graph compiled successfully.")
print("Running a quick test task...\n")

result = graph.invoke({
    "task":         "Write a Python function called add_numbers that takes two integers and returns their sum.",
    "code":         "",
    "review":       "",
    "review_json":  {},
    "tests":        "",
    "test_results": "",
    "iterations":   0,
    "messages":     []
})

print("── Agent Activity ──")
for msg in result["messages"]:
    print(f"  {msg['role']:15} → {msg['content']}")

print("\n── Generated Code ──")
print(result["code"])

print("\n── Review ──")
print(result["review"])

print("\n── Test Results ──")
print(result["test_results"])