---
name: add-api-endpoint
description: Step-by-step guide to add a new REST or WebSocket endpoint to the backend
license: Apache-2.0
---

# Add an API Endpoint

## Adding a REST endpoint

### 1. Define the request/response models in `backend/app/schemas.py`

```python
class SummarizeRequest(BaseModel):
    """Request to summarize a conversation."""
    conversation_id: str

class SummarizeResponse(BaseModel):
    """Summary of a conversation."""
    summary: str
    message_count: int
```

### 2. Add the endpoint in `backend/app/main.py`

```python
from .schemas import SummarizeRequest, SummarizeResponse

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest) -> SummarizeResponse:
    # Call the agent team or implement logic
    responses = await run_team(f"Summarize conversation {req.conversation_id}")
    return SummarizeResponse(
        summary=responses[-1]["content"] if responses else "",
        message_count=len(responses),
    )
```

### 3. Add a test in `backend/tests/test_api.py`

```python
@pytest.mark.asyncio
async def test_summarize(client: AsyncClient) -> None:
    resp = await client.post("/api/summarize", json={"conversation_id": "abc"})
    assert resp.status_code == 200
    body = resp.json()
    assert "summary" in body
```

### 4. Call from the frontend

```typescript
const resp = await fetch("/api/summarize", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ conversation_id: id }),
});
const data = await resp.json();
```

The Vite proxy forwards `/api` requests to the backend automatically.

## Adding a WebSocket endpoint

### 1. Add the handler in `backend/app/main.py`

```python
@app.websocket("/ws/stream")
async def stream_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            # Process and stream responses
            await websocket.send_text(
                AgentMessage(agent="system", content="...", type="status").model_dump_json()
            )
    except WebSocketDisconnect:
        pass
```

### 2. Connect from the frontend

```typescript
const ws = new WebSocket(`${protocol}//${window.location.host}/ws/stream`);
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // Handle message
};
```

The Vite proxy handles `/ws` paths — add the new path to `vite.config.ts` if using a different prefix.

## Checklist

- [ ] Request/response Pydantic models in `schemas.py`
- [ ] Endpoint in `main.py` with `response_model` (REST) or structured JSON (WS)
- [ ] Test in `tests/test_api.py`
- [ ] Frontend call uses `/api/` or `/ws/` prefix (proxied by Vite)
