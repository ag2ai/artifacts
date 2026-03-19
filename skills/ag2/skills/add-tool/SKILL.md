---
name: add-tool
description: How to create and register a tool on an AG2 agent
license: Apache-2.0
---

# Add a Tool to an Agent

## Step 1: Define the Tool

Use the `@tool` decorator. The function's docstring becomes the tool description the LLM sees. Use type annotations for all parameters.

```python
from ag2.tools import tool

@tool
def get_weather(city: str, units: str = "celsius") -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city to look up.
        units: Temperature units, either 'celsius' or 'fahrenheit'.
    """
    # Your implementation here
    return f"The weather in {city} is 22 {units}"
```

## Step 2: Create the Agents

You need two agents:
- A **caller** agent (LLM-powered) that decides when to invoke the tool.
- An **executor** agent that actually runs the tool function.

```python
from ag2 import LLMConfig
from ag2.agentchat import AssistantAgent, UserProxyAgent

with LLMConfig(api_type="openai", model="gpt-4o"):
    assistant = AssistantAgent(
        name="weather_assistant",
        system_message="You help users check the weather. Use the get_weather tool.",
    )

executor = UserProxyAgent(
    name="executor",
    human_input_mode="NEVER",
)
```

## Step 3: Register the Tool

```python
assistant.register_tool(get_weather, caller=assistant, executor=executor)
```

This tells AG2:
- `assistant` can generate tool-call requests for `get_weather`.
- `executor` runs the actual function and returns the result.

## Type Annotations Matter

The `@tool` decorator inspects type annotations to build the JSON schema sent to the LLM. Always annotate parameters.

Supported types:
- Primitives: `str`, `int`, `float`, `bool`
- Collections: `list[str]`, `dict[str, int]`
- Optional: `Optional[str]`, or `str | None`
- Enums: `Literal["option_a", "option_b"]`

```python
from typing import Literal

@tool
def query_db(
    table: str,
    columns: list[str],
    limit: int = 100,
    order: Literal["asc", "desc"] = "asc",
) -> str:
    """Query a database table and return results."""
    # implementation
    return "results"
```

## Complete Example

```python
from ag2 import LLMConfig
from ag2.agentchat import AssistantAgent, UserProxyAgent
from ag2.tools import tool

@tool
def search_docs(query: str, top_k: int = 5) -> str:
    """Search the documentation index.

    Args:
        query: The search query string.
        top_k: Number of results to return.
    """
    # Replace with real search logic
    return f"Found {top_k} results for '{query}'"

@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file.

    Args:
        path: File path to write to.
        content: Content to write.
    """
    with open(path, "w") as f:
        f.write(content)
    return f"Wrote {len(content)} chars to {path}"

with LLMConfig(api_type="openai", model="gpt-4o"):
    assistant = AssistantAgent(
        name="doc_writer",
        system_message=(
            "You help write documentation. Use search_docs to find relevant info, "
            "then use write_file to save the output. Reply TERMINATE when done."
        ),
    )

executor = UserProxyAgent(name="executor", human_input_mode="NEVER")

# Register both tools
assistant.register_tool(search_docs, caller=assistant, executor=executor)
assistant.register_tool(write_file, caller=assistant, executor=executor)

# Start the conversation
result = assistant.initiate_chat(
    executor,
    message="Write a summary of the authentication module to docs/auth.md",
)
```
