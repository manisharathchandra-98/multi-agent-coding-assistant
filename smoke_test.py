# smoke_test.py
# ─────────────────────────────────────────────────────────────────────────────
# Day 1 Evening — Single Agent Smoke Test
# This agent connects to your MCP server and asks Claude to write a Python
# function to a file. If the file appears on disk, everything is working.
# ─────────────────────────────────────────────────────────────────────────────

import os
import json
from dotenv import load_dotenv
import anthropic
from agents.mcp_client import call_mcp_tool

load_dotenv()

client = anthropic.Anthropic()
MODEL  = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5-20251101")

# ── Tools we expose to Claude ─────────────────────────────────────────────────
# These match exactly what your MCP server implements
TOOLS = [
    {
        "name": "write_file",
        "description": "Write content to a file at the given path. Creates folders automatically.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path":    {"type": "string", "description": "File path to write to"},
                "content": {"type": "string", "description": "Content to write into the file"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Read and return the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"}
            },
            "required": ["path"]
        }
    }
]


def run_agent(task: str) -> str:
    """
    Run a single agent that uses MCP tools to complete a coding task.

    The agent loop:
    1. Send task to Claude
    2. Claude decides to call a tool → we execute it via MCP
    3. We send the tool result back to Claude
    4. Repeat until Claude says it is done (stop_reason = end_turn)
    """
    print(f"\nTask: {task}")
    print("─" * 60)

    messages = [{"role": "user", "content": task}]

    # Agentic loop — keeps running until Claude stops calling tools
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=TOOLS,
            messages=messages
        )

        print(f"\nAgent thinking... (stop_reason: {response.stop_reason})")

        # ── Claude is finished — no more tool calls ──────────────────────────
        if response.stop_reason == "end_turn":
            final_text = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "Task complete."
            )
            return final_text

        # ── Claude wants to use a tool ───────────────────────────────────────
        if response.stop_reason == "tool_use":

            # Add Claude's response (including tool call) to message history
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name  = block.name
                    tool_input = block.input

                    print(f"\n  → Claude is calling tool: [{tool_name}]")
                    print(f"    Arguments: {json.dumps(tool_input, indent=6)}")

                    # Execute the tool via your MCP server
                    result = call_mcp_tool(tool_name, tool_input)

                    preview = result[:120] + "..." if len(result) > 120 else result
                    print(f"    Result: {preview}")

                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result
                    })

            # Send tool results back to Claude and continue the loop
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason — exit loop safely
            print(f"Unexpected stop_reason: {response.stop_reason}")
            break

    return "Agent finished."


# ── Run the smoke test ────────────────────────────────────────────────────────
if __name__ == "__main__":

    task = (
        "Write a Python function called validate_email that takes an email "
        "string and returns True if it is a valid email format, False otherwise. "
        "Use the re module. Include type hints and a docstring with examples. "
        "Save the complete function to workspace/output.py"
    )

    final_response = run_agent(task)

    print("\n── Claude's Final Response ──────────────────────────────────────")
    print(final_response)

    # ── Verify the file was actually created ──────────────────────────────────
    print("\n── Verification ─────────────────────────────────────────────────")

    if os.path.exists("workspace/output.py"):
        print("SUCCESS — workspace/output.py was created!")
        print("\n── File Contents ────────────────────────────────────────────────")
        with open("workspace/output.py", "r") as f:
            print(f.read())
    else:
        print("FAILED — workspace/output.py was not created.")
        print("Check the output above for errors.")