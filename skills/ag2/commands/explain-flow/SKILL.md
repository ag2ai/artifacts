---
name: explain-flow
description: Trace and explain message flow in a multi-agent AG2 conversation
license: Apache-2.0
---

# Explain Flow

Trace the message flow in an AG2 multi-agent conversation. Use this command when you need to understand how messages move between agents, debug unexpected routing, or document a conversation pattern.

## How to Trace

### 1. Identify the entry point

Find where the conversation starts. Look for:
- `run_group_chat(pattern=..., messages="...")` -- group chat entry
- `agent.initiate_chat(recipient, message="...")` -- two-agent entry

### 2. Determine the pattern

Check the pattern type to understand routing:
- **DefaultPattern with handoffs**: Follow the `Handoff` list to see allowed transitions. The LLM picks from allowed targets based on the conversation.
- **AutoPattern**: The group manager LLM selects the next speaker each turn. Check `group_manager_args` for the model used.
- **RoundRobinPattern**: Agents speak in list order, cycling back to the start.

### 3. Trace each turn

For each message in the conversation:

```
Turn 1: [initial_agent] receives the user message
Turn 2: [initial_agent] replies -> routed to [next_agent] via handoff/pattern
Turn 3: [next_agent] replies -> ...
...
Turn N: [final_agent] replies with TERMINATE -> conversation ends
```

### 4. Tool call detours

When an agent makes a tool call, the flow is:
```
caller_agent -> [tool call: function_name(args)] -> executor_agent
executor_agent -> [tool result: return_value] -> caller_agent
caller_agent -> continues conversation
```

Tool calls add two extra turns (call + result) before the conversation resumes.

### 5. Identify termination

The conversation ends when:
- An agent's reply contains `TERMINATE`
- `max_rounds` is reached (if configured)
- No valid next speaker is found

## Checklist

When explaining a flow, cover each of these:

- [ ] Entry point and initial message
- [ ] Pattern type and routing logic
- [ ] Each agent's role in the conversation
- [ ] Handoff transitions (who can speak to whom)
- [ ] Tool calls and their effect on flow
- [ ] Termination condition
- [ ] Total expected turns for a typical run

## Example Output

```
Flow: Research and Summarize

1. User message -> researcher (initial_agent)
2. researcher -> [tool: web_search("quantum error correction")] -> executor
3. executor -> [result: "...search results..."] -> researcher
4. researcher -> [handoff] -> writer
5. writer -> [summary text + TERMINATE] -> END

Pattern: DefaultPattern
Handoffs: researcher -> writer
Tools: web_search (caller=researcher, executor=executor)
Termination: writer replies with TERMINATE
```
