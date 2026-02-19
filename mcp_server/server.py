# mcp_server/server.py — COMPLETE VERSION
import os
import subprocess
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

app = Server("coding-assistant-mcp")


# ─────────────────────────────────────────────────────────────
# TOOL DEFINITIONS — tells the LLM what tools exist
# ─────────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [

        types.Tool(
            name="read_file",
            description="Read the full contents of a file at the given path. Use this to inspect existing code before making changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read, e.g. 'output.py' or 'agents/graph.py'"
                    }
                },
                "required": ["path"]
            }
        ),

        types.Tool(
            name="write_file",
            description="Write or overwrite a file with the given content. Creates parent directories automatically if they don't exist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to write to, e.g. 'output.py'"
                    },
                    "content": {
                        "type": "string",
                        "description": "The full content to write into the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),

        types.Tool(
            name="execute_code",
            description="Execute Python code inside a safe Docker sandbox. Returns stdout and stderr. Use this to test generated code before saving it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Valid Python code to execute"
                    }
                },
                "required": ["code"]
            }
        ),

        types.Tool(
            name="search_github",
            description="Search GitHub for real Python code examples related to a query. Useful for finding implementation patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for, e.g. 'JWT authentication FastAPI'"
                    }
                },
                "required": ["query"]
            }
        ),

        types.Tool(
            name="list_directory",
            description="List all files and folders inside a directory. Useful for understanding the project structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list. Use '.' for current directory."
                    }
                },
                "required": ["path"]
            }
        ),

    ]


# ─────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS — the actual logic for each tool
# ─────────────────────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict):

    # ── TOOL 1: read_file ──────────────────────────────────────
    if name == "read_file":
        path = arguments["path"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return [types.TextContent(
                type="text",
                text=f"Contents of '{path}':\n\n{content}"
            )]
        except FileNotFoundError:
            return [types.TextContent(
                type="text",
                text=f"Error: File '{path}' does not exist."
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error reading '{path}': {str(e)}"
            )]

    # ── TOOL 2: write_file ─────────────────────────────────────
    elif name == "write_file":
        path    = arguments["path"]
        content = arguments["content"]
        try:
            # Create parent folders if they don't exist
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return [types.TextContent(
                type="text",
                text=f"Successfully wrote {len(content)} characters to '{path}'."
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error writing to '{path}': {str(e)}"
            )]

    # ── TOOL 3: execute_code ───────────────────────────────────
    elif name == "execute_code":
        code = arguments["code"]
        try:
            result = subprocess.run(
                [
                    "docker", "run",
                    "--rm",              # Delete container after run
                    "--network", "none", # No internet access (safety)
                    "--memory", "256m",  # Max 256MB RAM
                    "--cpus", "0.5",     # Max 50% of one CPU core
                    "python:3.11-slim",  # Clean Python environment
                    "python", "-c", code # Run the code
                ],
                capture_output=True,
                text=True,
                timeout=30              # Kill after 30 seconds
            )

            output   = result.stdout.strip() if result.stdout.strip() else "(no output)"
            errors   = result.stderr.strip() if result.stderr.strip() else "(no errors)"
            exit_code = result.returncode

            return [types.TextContent(
                type="text",
                text=(
                    f"Exit code: {exit_code}\n\n"
                    f"OUTPUT:\n{output}\n\n"
                    f"ERRORS:\n{errors}"
                )
            )]

        except subprocess.TimeoutExpired:
            return [types.TextContent(
                type="text",
                text="Error: Code execution exceeded the 30-second time limit and was killed."
            )]
        except FileNotFoundError:
            return [types.TextContent(
                type="text",
                text="Error: Docker is not running or not installed. Please start Docker Desktop."
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error executing code: {str(e)}"
            )]

    # ── TOOL 4: search_github ──────────────────────────────────
    elif name == "search_github":
        query = arguments["query"]
        token = os.getenv("GITHUB_TOKEN", "")

        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            response = requests.get(
                "https://api.github.com/search/code",
                params={
                    "q": f"{query} language:python",
                    "per_page": 5,
                    "sort": "indexed"
                },
                headers=headers,
                timeout=10
            )

            if response.status_code == 403:
                return [types.TextContent(
                    type="text",
                    text="GitHub API rate limit hit. Add a GITHUB_TOKEN to your .env file to increase limits."
                )]

            data = response.json()

            if "items" not in data or len(data["items"]) == 0:
                return [types.TextContent(
                    type="text",
                    text=f"No GitHub results found for: '{query}'"
                )]

            results = []
            for item in data["items"][:5]:
                results.append(
                    f"File:   {item['name']}\n"
                    f"Repo:   {item['repository']['full_name']}\n"
                    f"URL:    {item['html_url']}"
                )

            return [types.TextContent(
                type="text",
                text=f"GitHub results for '{query}':\n\n" + "\n\n---\n\n".join(results)
            )]

        except requests.Timeout:
            return [types.TextContent(
                type="text",
                text="Error: GitHub search timed out. Try again."
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error searching GitHub: {str(e)}"
            )]

    # ── TOOL 5: list_directory ─────────────────────────────────
    elif name == "list_directory":
        path = arguments.get("path", ".")
        try:
            if not os.path.isdir(path):
                return [types.TextContent(
                    type="text",
                    text=f"Error: '{path}' is not a directory or does not exist."
                )]

            items = []
            for name_ in sorted(os.listdir(path)):
                full = os.path.join(path, name_)
                if os.path.isdir(full):
                    items.append(f"[DIR]   {name_}/")
                else:
                    size = os.path.getsize(full)
                    items.append(f"[FILE]  {name_}  ({size} bytes)")

            if not items:
                return [types.TextContent(
                    type="text",
                    text=f"Directory '{path}' is empty."
                )]

            return [types.TextContent(
                type="text",
                text=f"Contents of '{path}':\n\n" + "\n".join(items)
            )]

        except PermissionError:
            return [types.TextContent(
                type="text",
                text=f"Error: Permission denied to read '{path}'."
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error listing directory: {str(e)}"
            )]

    # ── Unknown tool ───────────────────────────────────────────
    else:
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'. Available tools: read_file, write_file, execute_code, search_github, list_directory"
        )]


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())