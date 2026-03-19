"""FastAPI application with REST and WebSocket endpoints.

Run with:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import json
import traceback

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .agents import AGENT_NAMES, run_team
from .schemas import AgentMessage, HealthResponse

app = FastAPI(title="{{ project_name }}", description="{{ description }}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check — returns status and available agent names."""
    return HealthResponse(status="ok", agents=AGENT_NAMES)


@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time multi-agent chat.

    Protocol:
        Client sends: {"message": "user text"}
        Server sends: {"agent": "name", "content": "...", "type": "agent_message"}
        Server sends: {"agent": "", "content": "", "type": "done"} when finished
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_message = payload.get("message", "")

            if not user_message:
                await websocket.send_text(
                    AgentMessage(agent="system", content="Empty message", type="error").model_dump_json()
                )
                continue

            # Notify client that processing has started
            await websocket.send_text(
                AgentMessage(agent="system", content="Agents are working...", type="status").model_dump_json()
            )

            # Run the agent team
            try:
                responses = await run_team(user_message)
            except Exception:
                await websocket.send_text(
                    AgentMessage(
                        agent="system",
                        content=f"Agent error: {traceback.format_exc()}",
                        type="error",
                    ).model_dump_json()
                )
                continue

            # Stream each agent response
            for resp in responses:
                msg = AgentMessage(agent=resp["agent"], content=resp["content"])
                await websocket.send_text(msg.model_dump_json())

            # Signal completion
            await websocket.send_text(
                AgentMessage(agent="", content="", type="done").model_dump_json()
            )

    except WebSocketDisconnect:
        pass
