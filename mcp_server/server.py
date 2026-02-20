# mcp_server/server.py
import asyncio
import os
import subprocess
import sys

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Add project root to path so we can import rag/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Server("coding-assistant")

WORKSPACE = "workspace"
os.makedirs(WORKSPACE, exist_ok=True)


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_file",
            description="Read a file from the workspace folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name to read"}
                },
                "required": ["filename"]
            }
        ),
        types.Tool(
            name="write_file",
            description="Write content to a file in the workspace folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name to write"},
                    "content":  {"type": "string", "description": "Content to write"}
                },
                "required": ["filename", "content"]
            }
        ),
        types.Tool(
            name="execute_code",
            description="Execute Python code in a sandboxed Docker container.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="search_github",
            description="Search GitHub for code examples related to a keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Search keyword"}
                },
                "required": ["keyword"]
            }
        ),
        types.Tool(
            name="list_directory",
            description="List all files in the workspace folder.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="query_docs",
            description="Search the RAG knowledge base for relevant Python coding best practices and patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query":     {"type": "string",  "description": "What to search for"},
                    "n_results": {"type": "integer", "description": "Number of results (default 3)", "default": 3}
                },
                "required": ["query"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    # ── read_file ──────────────────────────────────────────────────────────
    if name == "read_file":
        filename = arguments["filename"]
        filepath = os.path.join(WORKSPACE, filename)
        if not os.path.exists(filepath):
            return [types.TextContent(type="text", text=f"Error: {filename} not found.")]
        with open(filepath, "r") as f:
            return [types.TextContent(type="text", text=f.read())]

    # ── write_file ─────────────────────────────────────────────────────────
    elif name == "write_file":
        filename = arguments["filename"]
        content  = arguments["content"]
        filepath = os.path.join(WORKSPACE, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return [types.TextContent(type="text", text=f"Written {len(content)} chars to {filename}")]

    # ── execute_code ───────────────────────────────────────────────────────
    elif name == "execute_code":
        code = arguments["code"]
        try:
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "--network", "none",
                    "--memory", "256m",
                    "--cpus",   "0.5",
                    "-i",
                    "coding-sandbox",
                    "python", "-c", code
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout or result.stderr or "(no output)"
            return [types.TextContent(type="text", text=output)]
        except subprocess.TimeoutExpired:
            return [types.TextContent(type="text", text="Error: Code execution timed out (30s limit).")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error executing code: {e}")]

    # ── search_github ──────────────────────────────────────────────────────
    elif name == "search_github":
        keyword = arguments["keyword"]
        return [types.TextContent(
            type="text",
            text=(
                f"GitHub search results for '{keyword}':\n"
                f"1. github.com/python/cpython — reference implementation examples\n"
                f"2. github.com/TheAlgorithms/Python — algorithm implementations in Python\n"
                f"3. github.com/vinta/awesome-python — curated Python resources\n"
                f"(Tip: search 'site:github.com python {keyword}' in your browser for real results)"
            )
        )]

    # ── list_directory ─────────────────────────────────────────────────────
    elif name == "list_directory":
        files = os.listdir(WORKSPACE)
        if not files:
            return [types.TextContent(type="text", text="workspace/ is empty.")]
        file_list = "\n".join(f"  • {f}" for f in sorted(files))
        return [types.TextContent(type="text", text=f"workspace/ contents:\n{file_list}")]

    # ── query_docs ─────────────────────────────────────────────────────────
    elif name == "query_docs":
        try:
            from rag.retriever import query_docs
            query    = arguments.get("query", "")
            n_results = arguments.get("n_results", 3)
            result   = query_docs(query, n_results)
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"RAG query failed: {e}")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())