# agents/mcp_client.py
import asyncio
import threading
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def _async_call_tool(tool_name: str, arguments: dict) -> str:
    """Async function that connects to MCP server and calls a tool."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            if result.content:
                return result.content[0].text
            return ""


def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """
    Call an MCP tool synchronously from inside a LangGraph agent.
    Runs async MCP client in a dedicated thread to avoid event loop conflicts.
    """
    result = {"value": None, "error": None}

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result["value"] = loop.run_until_complete(
                _async_call_tool(tool_name, arguments)
            )
        except Exception as e:
            result["error"] = str(e)
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=60)

    if thread.is_alive():
        return f"Error: MCP tool '{tool_name}' timed out after 60 seconds"

    if result["error"]:
        return f"Error calling MCP tool '{tool_name}': {result['error']}"

    return result["value"] or ""