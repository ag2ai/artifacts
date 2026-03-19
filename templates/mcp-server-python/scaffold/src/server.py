"""MCP server with example tools.

Run with:
    mcp dev src/server.py
    mcp run src/server.py
"""

from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("{{ project_name }}")


@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: The name of the person to greet.

    Returns:
        A friendly greeting message.
    """
    return f"Hello, {name}! Welcome to {{ project_name }}."


@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Supports basic arithmetic: addition, subtraction, multiplication,
    division, and exponentiation. No imports or function calls allowed.

    Args:
        expression: A mathematical expression to evaluate (e.g. "2 + 3 * 4").

    Returns:
        The result of the evaluation, or an error message.
    """
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        return f"Error: expression contains disallowed characters. Only digits and +-*/.() are permitted."

    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
    except Exception as exc:
        return f"Error: {exc}"

    return str(result)


@mcp.tool()
def get_time(timezone_name: str = "UTC") -> str:
    """Get the current date and time.

    Args:
        timezone_name: Currently only "UTC" is supported.

    Returns:
        The current date and time as an ISO-8601 string.
    """
    now = datetime.now(timezone.utc)
    return now.isoformat()


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
