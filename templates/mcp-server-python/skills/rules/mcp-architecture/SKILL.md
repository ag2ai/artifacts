---
name: mcp-architecture
description: Architecture overview and conventions for this MCP server project
license: Apache-2.0
---

# MCP Server Architecture

This project implements a Model Context Protocol (MCP) server using the FastMCP framework.

## Core concepts

- **MCP** is a protocol that lets LLMs call "tools" exposed by a server. The server communicates over stdio (or SSE) and the LLM client sends JSON-RPC requests to invoke tools.
- **FastMCP** is the high-level Python SDK from the `mcp` package. It handles protocol framing, schema generation, and transport so you only write plain Python functions.

## Project layout

```
src/
  __init__.py
  server.py        # FastMCP instance and all tool definitions
tests/
  test_tools.py    # Unit tests that call tool functions directly
pyproject.toml     # Project metadata and dependencies
```

## How tools work

Tools are regular Python functions decorated with `@mcp.tool()` on the shared `FastMCP` instance defined in `src/server.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description visible to the LLM."""
    return "result"
```

Key rules:

1. **One `FastMCP` instance** -- created at module level in `src/server.py`. All tools register on this instance.
2. **Docstrings are the tool description** -- the first line of the docstring is what the LLM sees when listing available tools. Write it as a clear, imperative sentence.
3. **Type annotations generate the schema** -- parameter types (`str`, `int`, `float`, `bool`, `list[str]`, etc.) are converted to JSON Schema automatically. Always annotate every parameter.
4. **Return a string** -- tool return values are sent back to the LLM as text content. Return `str` for simple results. For structured data, return JSON via `json.dumps()`.
5. **Keep tools pure when possible** -- tools that are pure functions (no side effects) are easier to test. When side effects are needed (HTTP calls, file I/O), isolate them so the core logic is testable.

## Running the server

- **Development** (interactive inspector UI): `mcp dev src/server.py`
- **Production** (stdio transport): `mcp run src/server.py`
- **Tests**: `uv run pytest`

## Adding resources and prompts

FastMCP also supports `@mcp.resource()` and `@mcp.prompt()` decorators. These follow the same pattern as tools -- decorate a function in `src/server.py` and FastMCP handles the rest. Refer to the MCP Python SDK documentation for details.
