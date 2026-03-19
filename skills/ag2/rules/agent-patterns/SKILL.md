---
name: agent-patterns
description: Patterns for creating and configuring AG2 agents correctly
license: Apache-2.0
---

# Agent Patterns

## Creating Agents with LLMConfig

Always use the `LLMConfig` context manager. Agents created inside its scope inherit the configuration automatically.

```python
from ag2 import LLMConfig
from ag2.agentchat import AssistantAgent, UserProxyAgent

with LLMConfig(api_type="openai", model="gpt-4o"):
    planner = AssistantAgent(
        name="planner",
        system_message="You are a project planner. Break tasks into steps.",
    )
    reviewer = AssistantAgent(
        name="reviewer",
        system_message="You review plans for completeness and correctness.",
    )

executor = UserProxyAgent(
    name="executor",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "workspace"},
)
```

Agents that do not need an LLM (e.g., pure code executors) should be created outside the context manager.

## System Message Best Practices

1. **Be specific about the role.** State what the agent does, not what it is.
2. **Define boundaries.** Tell the agent what it should NOT do.
3. **Keep it short.** Aim for 2-4 sentences. Long prompts dilute focus.
4. **Use second person.** Write "You analyze data" not "This agent analyzes data".

```python
# Good
system_message = (
    "You are a SQL analyst. Write SQL queries to answer user questions. "
    "Only use SELECT statements. Never modify data."
)

# Bad -- too vague
system_message = "You are a helpful assistant."
```

## Agent Naming Conventions

- Use lowercase snake_case: `data_analyst`, `code_reviewer`.
- Names must be unique within a group chat.
- Names appear in conversation logs, so make them descriptive.
- Avoid generic names like `assistant` or `agent1`.

## Tool Registration

Register tools on the agents that should be able to call and execute them:

```python
from ag2.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the database and return matching rows."""
    # implementation
    return results

analyst = AssistantAgent(name="analyst", system_message="...")
executor = UserProxyAgent(name="executor", human_input_mode="NEVER")

# Register: analyst decides when to call, executor runs the function
analyst.register_tool(search_database, caller=analyst, executor=executor)
```

## Human Input Modes

- `"ALWAYS"` -- Ask for human input on every turn.
- `"TERMINATE"` -- Ask only when the agent wants to terminate.
- `"NEVER"` -- Fully autonomous, no human input.

```python
# Autonomous executor
executor = UserProxyAgent(name="executor", human_input_mode="NEVER")

# Human-in-the-loop
user = UserProxyAgent(name="user", human_input_mode="TERMINATE")
```

## Termination

Agents stop when a reply contains `"TERMINATE"`. Configure this in the system message:

```python
system_message = (
    "You solve math problems. When you have the final answer, "
    "reply with TERMINATE."
)
```
