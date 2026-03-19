---
name: build-group-chat
description: Step-by-step workflow for building an AG2 multi-agent group chat
license: Apache-2.0
---

# Build a Group Chat

## Step 1: Imports

```python
from ag2 import LLMConfig
from ag2.agentchat import AssistantAgent, UserProxyAgent
from ag2.agentchat.group import run_group_chat, DefaultPattern, Handoff
```

## Step 2: Create Agents

Define agents inside an `LLMConfig` context manager. Give each agent a distinct role.

```python
with LLMConfig(api_type="openai", model="gpt-4o"):
    planner = AssistantAgent(
        name="planner",
        system_message=(
            "You break down user requests into actionable steps. "
            "Hand off to coder when the plan is ready."
        ),
    )
    coder = AssistantAgent(
        name="coder",
        system_message=(
            "You write Python code based on the plan. "
            "Hand off to reviewer when code is complete."
        ),
    )
    reviewer = AssistantAgent(
        name="reviewer",
        system_message=(
            "You review code for correctness and style. "
            "If changes are needed, hand off to coder. "
            "If the code is correct, reply with TERMINATE."
        ),
    )

executor = UserProxyAgent(
    name="executor",
    human_input_mode="NEVER",
)
```

## Step 3: Choose a Pattern

### DefaultPattern with handoffs (recommended)

Agents explicitly hand off to the next speaker. You define allowed transitions.

```python
pattern = DefaultPattern(
    initial_agent=planner,
    agents=[planner, coder, reviewer, executor],
    handoffs=[
        Handoff(source=planner, target=coder),
        Handoff(source=coder, target=reviewer),
        Handoff(source=reviewer, target=coder),
    ],
    group_manager_args={"llm_config": LLMConfig(api_type="openai", model="gpt-4o")},
)
```

### AutoPattern

The LLM decides who speaks next. No explicit handoffs needed.

```python
from ag2.agentchat.group import AutoPattern

pattern = AutoPattern(
    initial_agent=planner,
    agents=[planner, coder, reviewer, executor],
    group_manager_args={"llm_config": LLMConfig(api_type="openai", model="gpt-4o")},
)
```

### RoundRobinPattern

Agents speak in the order they are listed. Simple and predictable.

```python
from ag2.agentchat.group import RoundRobinPattern

pattern = RoundRobinPattern(
    initial_agent=planner,
    agents=[planner, coder, reviewer],
)
```

## Step 4: Run the Group Chat

```python
result = run_group_chat(
    pattern=pattern,
    messages="Build a CLI tool that converts CSV files to JSON.",
)
```

## Complete Example

```python
from ag2 import LLMConfig
from ag2.agentchat import AssistantAgent, UserProxyAgent
from ag2.agentchat.group import run_group_chat, DefaultPattern, Handoff

with LLMConfig(api_type="openai", model="gpt-4o"):
    planner = AssistantAgent(
        name="planner",
        system_message="You create step-by-step plans. Hand off to coder when ready.",
    )
    coder = AssistantAgent(
        name="coder",
        system_message="You implement code from plans. Hand off to reviewer when done.",
    )
    reviewer = AssistantAgent(
        name="reviewer",
        system_message=(
            "You review code quality. Hand off to coder for fixes. "
            "Reply TERMINATE when approved."
        ),
    )

executor = UserProxyAgent(name="executor", human_input_mode="NEVER")

pattern = DefaultPattern(
    initial_agent=planner,
    agents=[planner, coder, reviewer, executor],
    handoffs=[
        Handoff(source=planner, target=coder),
        Handoff(source=coder, target=reviewer),
        Handoff(source=reviewer, target=coder),
    ],
    group_manager_args={"llm_config": LLMConfig(api_type="openai", model="gpt-4o")},
)

result = run_group_chat(
    pattern=pattern,
    messages="Build a function that merges two sorted lists.",
)
```
