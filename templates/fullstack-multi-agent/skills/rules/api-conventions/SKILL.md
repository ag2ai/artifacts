---
name: api-conventions
description: REST and WebSocket endpoint patterns, error handling, and Pydantic schema conventions for the backend
license: Apache-2.0
---

# API Conventions

## Adding a REST endpoint

All REST endpoints go in `backend/app/main.py` under the `/api` prefix.

```python
from .schemas import MyRequest, MyResponse

@app.post("/api/my-endpoint", response_model=MyResponse)
async def my_endpoint(req: MyRequest) -> MyResponse:
    # Business logic here
    return MyResponse(...)
```

Rules:
- Always use a Pydantic `response_model` — never return raw dicts
- Define request/response models in `schemas.py`, not inline
- Use async endpoints — the agent team is async
- Prefix all REST routes with `/api/`

## Pydantic schema conventions

```python
from pydantic import BaseModel

class MyResponse(BaseModel):
    """Docstring explains what this response represents."""
    field_name: str
    optional_field: str | None = None
    items: list[str] = []
```

Rules:
- Use Pydantic v2 API: `model_dump()`, `model_dump_json()`, `model_validate()`
- Provide defaults for optional fields
- Add docstrings — they appear in the auto-generated OpenAPI docs

## WebSocket message handling

The WebSocket handler in `main.py` follows this pattern:

```python
@app.websocket("/ws/my-feature")
async def my_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            # Process and send responses
            await websocket.send_text(response.model_dump_json())
    except WebSocketDisconnect:
        pass
```

Rules:
- Always wrap the receive loop in `try/except WebSocketDisconnect`
- Send structured JSON using Pydantic `model_dump_json()`, not hand-built strings
- Send a `{"type": "done"}` message to signal completion to the frontend
- Send `{"type": "error"}` for recoverable errors instead of closing the connection

## Error handling

- REST: let FastAPI's built-in validation handle 422s; raise `HTTPException` for business errors
- WebSocket: send an error message over the socket, don't close it — the frontend stays connected
- Agent errors: catch exceptions from `run_team()`, send as `{"type": "error"}` to the client

## CORS

CORS is configured in `main.py` for `http://localhost:5173` (Vite dev server). For production, replace with the actual frontend origin.
