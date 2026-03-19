---
name: add-agent-to-team
description: Step-by-step guide to add a new agent to the multi-agent team
license: Apache-2.0
---

# Add an Agent to the Team

## Steps

### 1. Define the agent in `backend/app/agents.py`

Add the agent inside the `with config:` block alongside the existing agents:

```python
with config:
    planner = AssistantAgent(...)
    coder = AssistantAgent(...)
    reviewer = AssistantAgent(...)

    # New agent
    tester = AssistantAgent(
        name="tester",
        system_message=(
            "You are a testing agent. Given the coder's implementation, "
            "write comprehensive unit tests covering edge cases and error "
            "conditions. Use pytest conventions."
        ),
    )
```

### 2. Add the agent to the AGENTS list

```python
AGENTS = [planner, coder, reviewer, tester]
```

`AGENT_NAMES` updates automatically since it's derived from `AGENTS`.

### 3. Update the pattern if needed

For `RoundRobinPattern`, agents execute in list order — place the new agent where it should speak in the sequence.

If switching to `AutoPattern` for dynamic routing:

```python
from autogen.agentchat.group.patterns.pattern import AutoPattern

pattern = AutoPattern(
    initial_agent=planner,
    agents=AGENTS,
)
```

### 4. Update `max_rounds` in `run_team()`

Each agent takes one round. If you added an agent, increase `max_rounds` to allow at least 2 full cycles:

```python
result = await run_group_chat(
    pattern=pattern,
    messages=message,
    max_rounds=8,  # was 6 with 3 agents
)
```

### 5. Add the agent color in the frontend

In `frontend/src/components/Chat.tsx`, add a color entry:

```typescript
const AGENT_COLORS: Record<string, string> = {
  planner: "#2563eb",
  coder: "#059669",
  reviewer: "#d97706",
  tester: "#7c3aed",   // new
  system: "#6b7280",
};
```

### 6. Update the test

In `backend/tests/test_api.py`:

```python
async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/api/health")
    body = resp.json()
    assert "tester" in body["agents"]
```

## Checklist

- [ ] Agent defined with a specific, focused system message
- [ ] Added to `AGENTS` list in the correct position
- [ ] `max_rounds` updated to accommodate the new agent
- [ ] Frontend color mapping added
- [ ] Health check test updated
