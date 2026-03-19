---
name: fullstack-architecture
description: Architecture, directory layout, communication protocol, and conventions for the full-stack multi-agent application
license: Apache-2.0
---

# Full-Stack Multi-Agent Architecture

## Directory layout

```
backend/
├── app/
│   ├── main.py       # FastAPI app — REST endpoints + WebSocket handler
│   ├── agents.py     # AG2 agent team definition and run_team() entry point
│   └── schemas.py    # Pydantic models shared between endpoints and agents
└── tests/
    └── test_api.py

frontend/
├── src/
│   ├── main.tsx          # React entry point
│   ├── App.tsx           # Root component
│   └── components/
│       └── Chat.tsx      # WebSocket chat UI
├── index.html
├── vite.config.ts        # Vite config with API/WS proxy to backend
└── package.json
```

## Tech stack

- **Backend:** FastAPI, AG2 (multi-agent orchestration), Pydantic, uvicorn
- **Frontend:** React 19, TypeScript, Vite
- **Communication:** WebSocket for real-time agent messages, REST for health/metadata

## Communication protocol

The frontend and backend communicate over a single WebSocket at `/ws/chat`.

### Message format (JSON over WebSocket)

Client → Server:
```json
{"message": "user text here"}
```

Server → Client (one per agent response):
```json
{"agent": "planner", "content": "...", "type": "agent_message"}
```

Server → Client (when all agents finish):
```json
{"agent": "", "content": "", "type": "done"}
```

Message types: `agent_message`, `status`, `error`, `done`.

### REST endpoints

- `GET /api/health` — returns `{"status": "ok", "agents": ["planner", "coder", "reviewer"]}`

## Agent team

The backend runs a 3-agent team using AG2's `RoundRobinPattern`:

1. **planner** — breaks user requests into numbered steps
2. **coder** — implements the plan in code
3. **reviewer** — reviews for correctness and security

The `run_team(message)` function in `agents.py` is the single entry point. It returns a list of `{"agent": name, "content": text}` dicts.

## Key conventions

- All API models live in `schemas.py` — import from there, never define inline
- Agent definitions stay in `agents.py` — main.py only imports `run_team` and `AGENT_NAMES`
- The frontend Vite config proxies `/api` and `/ws` to the backend in dev — no hardcoded URLs in components
- Pydantic models use `model_dump_json()` for serialization (v2 API)
