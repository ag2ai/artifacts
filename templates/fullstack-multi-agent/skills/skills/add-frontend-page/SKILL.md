---
name: add-frontend-page
description: Step-by-step guide to add a new page or component to the React frontend
license: Apache-2.0
---

# Add a Frontend Page or Component

## Adding a new component

### 1. Create the component file

Create `frontend/src/components/MyComponent.tsx`:

```typescript
import { useState } from "react";

interface Props {
  title: string;
}

export function MyComponent({ title }: Props) {
  const [data, setData] = useState<string>("");

  return (
    <div>
      <h2>{title}</h2>
      <p>{data || "No data yet."}</p>
    </div>
  );
}
```

Rules:
- Export named components, not default exports (except `App.tsx`)
- Define a `Props` interface for all component props
- Place in `frontend/src/components/`

### 2. Use the component in App.tsx

```typescript
import { MyComponent } from "./components/MyComponent";

export default function App() {
  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1>Project Name</h1>
      <MyComponent title="Dashboard" />
      <Chat />
    </div>
  );
}
```

## Connecting to the backend

### REST call

```typescript
import { useEffect, useState } from "react";

export function Dashboard() {
  const [health, setHealth] = useState<{ status: string; agents: string[] } | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth);
  }, []);

  if (!health) return <p>Loading...</p>;

  return (
    <div>
      <p>Status: {health.status}</p>
      <ul>
        {health.agents.map((a) => (
          <li key={a}>{a}</li>
        ))}
      </ul>
    </div>
  );
}
```

### WebSocket connection

Use the same pattern as `Chat.tsx`:

```typescript
const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`);

ws.onopen = () => ws.send(JSON.stringify({ message: text }));
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // Handle msg.type: "agent_message", "status", "error", "done"
};
```

## Styling conventions

This template uses inline styles for simplicity. When adding styles:

- Use inline `style={{}}` for one-off styling
- Keep colors consistent with existing agent colors
- Use the same layout pattern: `maxWidth: 800, margin: "0 auto"` for content sections
- For complex components, extract a CSS module: `MyComponent.module.css`

## Checklist

- [ ] Component in `frontend/src/components/` with typed Props
- [ ] Named export (not default)
- [ ] Imported and rendered in `App.tsx`
- [ ] API calls use `/api/` or `/ws/` prefix (Vite proxies to backend)
- [ ] Loading and error states handled
