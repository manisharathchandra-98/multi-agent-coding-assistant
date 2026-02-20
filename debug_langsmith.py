# Save as debug_langsmith.py and run it
import os
from dotenv import load_dotenv

load_dotenv()

print("=== LangSmith Debug ===")
print(f"LANGCHAIN_TRACING_V2 : '{os.getenv('LANGCHAIN_TRACING_V2')}'")
print(f"LANGCHAIN_API_KEY    : '{os.getenv('LANGCHAIN_API_KEY', '')[:20]}...'")
print(f"LANGCHAIN_PROJECT    : '{os.getenv('LANGCHAIN_PROJECT')}'")
print(f"LANGCHAIN_ENDPOINT   : '{os.getenv('LANGCHAIN_ENDPOINT')}'")

# Try sending a test trace directly
from langsmith import Client

try:
    client = Client()
    projects = list(client.list_projects())
    print(f"\n✅ Connected to LangSmith! Found {len(projects)} project(s):")
    for p in projects:
        print(f"   - {p.name}")
except Exception as e:
    print(f"\n❌ Connection failed: {e}")