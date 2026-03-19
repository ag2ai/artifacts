"""AG2 multi-agent team: planner, coder, reviewer.

The team uses a RoundRobin pattern so each agent contributes in sequence.
Agent responses are collected via a callback and returned to the caller.
"""

from __future__ import annotations

from autogen import AssistantAgent, LLMConfig
from autogen.agentchat.group import run_group_chat
from autogen.agentchat.group.patterns.pattern import RoundRobinPattern

config = LLMConfig(api_type="openai", model="gpt-4o")

with config:
    planner = AssistantAgent(
        name="planner",
        system_message=(
            "You are a planning agent. Given a user request, break it into clear, "
            "numbered steps. Be specific about what needs to happen at each step. "
            "Do not write code — only produce the plan."
        ),
    )

    coder = AssistantAgent(
        name="coder",
        system_message=(
            "You are a coding agent. Given a plan from the planner, implement "
            "the solution step by step. Write clean, well-documented code. "
            "If something is ambiguous, state your assumption and proceed."
        ),
    )

    reviewer = AssistantAgent(
        name="reviewer",
        system_message=(
            "You are a code review agent. Review the coder's implementation for "
            "correctness, edge cases, security issues, and clarity. Provide "
            "specific, actionable feedback. If the code is good, say so briefly."
        ),
    )

AGENTS = [planner, coder, reviewer]
AGENT_NAMES = [a.name for a in AGENTS]

pattern = RoundRobinPattern(
    initial_agent=planner,
    agents=AGENTS,
)


async def run_team(message: str) -> list[dict[str, str]]:
    """Run the multi-agent team on a user message.

    Returns a list of {"agent": name, "content": text} dicts.
    """
    result = await run_group_chat(
        pattern=pattern,
        messages=message,
        max_rounds=6,
    )

    messages: list[dict[str, str]] = []
    for msg in result.messages:
        if hasattr(msg, "source") and hasattr(msg, "content") and msg.content:
            messages.append({"agent": msg.source, "content": msg.content})

    return messages
