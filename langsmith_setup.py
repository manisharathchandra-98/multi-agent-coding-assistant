# langsmith_setup.py
import os
from dotenv import load_dotenv

load_dotenv()

def verify_langsmith():
    api_key = os.getenv("LANGCHAIN_API_KEY", "")
    tracing = os.getenv("LANGCHAIN_TRACING_V2", "false")
    project = os.getenv("LANGCHAIN_PROJECT", "default")

    if tracing == "true" and api_key:
        print(f"✅ LangSmith tracing enabled — project: '{project}'")
    else:
        print("⚠️  LangSmith tracing disabled — check LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY in .env")


if __name__ == "__main__":
    verify_langsmith()