---
name: add-mcp-tool
description: Step-by-step guide for adding a new tool to this MCP server
license: Apache-2.0
---

# Add a new MCP tool

Follow these steps to add a new tool to the MCP server.

## Steps

### 1. Define the tool function in `src/server.py`

Open `src/server.py` and add a new function decorated with `@mcp.tool()`. Place it after the existing tool definitions, before the `main()` function.

```python
@mcp.tool()
def my_new_tool(param_one: str, param_two: int = 10) -> str:
    """Short description of what the tool does.

    Longer explanation if needed. This docstring is shown to the LLM
    when it lists available tools, so be specific about what the tool
    does and when to use it.

    Args:
        param_one: Describe this parameter.
        param_two: Describe this parameter. Defaults to 10.

    Returns:
        What the tool returns.
    """
    # Implementation here
    result = f"{param_one} processed with {param_two}"
    return result
```

Requirements:
- The function **must** be decorated with `@mcp.tool()` using the module-level `mcp` instance.
- Every parameter **must** have a type annotation. Supported types: `str`, `int`, `float`, `bool`, `list[...]`, `dict[str, ...]`, and `Optional[...]`.
- Provide default values for optional parameters.
- The return type should be `str`. For structured data, use `json.dumps()`.
- Write a clear docstring -- it is the tool's description for the LLM.

### 2. Add tests in `tests/test_tools.py`

Open `tests/test_tools.py` and import the new function, then add a test class.

```python
from src.server import my_new_tool

class TestMyNewTool:
    def test_basic_usage(self) -> None:
        result = my_new_tool("hello", 5)
        assert "hello" in result

    def test_default_param(self) -> None:
        result = my_new_tool("world")
        assert "10" in result

    def test_edge_case(self) -> None:
        result = my_new_tool("", 0)
        assert isinstance(result, str)
```

Tool functions are plain Python, so tests call them directly without needing an MCP client.

### 3. Run the tests

```bash
uv run pytest tests/test_tools.py -v
```

### 4. Manual verification with the MCP inspector

Start the dev server and use the interactive inspector to call the tool:

```bash
mcp dev src/server.py
```

This opens a browser UI where you can see all registered tools, inspect their schemas, and invoke them with test inputs.

## Checklist

- [ ] Function is decorated with `@mcp.tool()` in `src/server.py`
- [ ] All parameters have type annotations
- [ ] Docstring clearly describes the tool's purpose and parameters
- [ ] Unit tests added in `tests/test_tools.py`
- [ ] `uv run pytest` passes
- [ ] Tool appears and works in `mcp dev` inspector
