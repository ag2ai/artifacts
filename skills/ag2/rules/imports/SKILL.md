---
name: ag2-imports
description: Correct import paths and module structure for the AG2 framework
license: Apache-2.0
---

# AG2 Imports

The package name is `ag2`, not `autogen`. All imports use the `ag2` namespace.

## Core Agents

```python
from ag2.agentchat import AssistantAgent, UserProxyAgent, ConversableAgent
```

- `AssistantAgent` -- LLM-powered agent that generates replies.
- `UserProxyAgent` -- Proxy for human input; can also execute code.
- `ConversableAgent` -- Base class for all conversable agents.

## LLM Configuration

```python
from ag2 import LLMConfig
```

Use `LLMConfig` as a context manager to bind a model configuration to agents created within its scope:

```python
with LLMConfig(api_type="openai", model="gpt-4o"):
    agent = AssistantAgent(name="assistant")
```

## Group Chat

```python
from ag2.agentchat.group import run_group_chat
from ag2.agentchat.group import DefaultPattern, AutoPattern, RoundRobinPattern
```

- `run_group_chat` -- Orchestrates a multi-agent conversation.
- `DefaultPattern` -- LLM-based speaker selection with optional handoffs.
- `AutoPattern` -- Automatic orchestration; the LLM decides flow.
- `RoundRobinPattern` -- Agents speak in fixed round-robin order.

## Tools

```python
from ag2.tools import tool
```

The `@tool` decorator converts a plain function into a tool that agents can call.

## Nested Chats and Advanced Patterns

```python
from ag2.agentchat import initiate_chats          # Sequential multi-conversation
from ag2.agentchat import register_hand_off        # Handoff registration
from ag2.agentchat.group import Handoff            # Explicit handoff target
```

## Common Mistakes

- Do NOT use `import autogen` -- the package was renamed to `ag2`.
- Do NOT import `GroupChat` or `GroupChatManager` -- use `run_group_chat` with a pattern instead.
- Do NOT use `config_list` dicts -- use `LLMConfig` objects.
