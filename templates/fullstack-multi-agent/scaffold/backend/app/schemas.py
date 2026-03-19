"""Pydantic models for API request/response types."""

from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""

    message: str


class AgentMessage(BaseModel):
    """A single message from an agent, sent over WebSocket."""

    agent: str
    content: str
    type: str = "agent_message"  # agent_message | status | error | done


class HealthResponse(BaseModel):
    status: str = "ok"
    agents: list[str] = []
