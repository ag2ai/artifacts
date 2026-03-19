import { useCallback, useRef, useState } from "react";

interface AgentMessage {
  agent: string;
  content: string;
  type: "agent_message" | "status" | "error" | "done";
}

const AGENT_COLORS: Record<string, string> = {
  planner: "#2563eb",
  coder: "#059669",
  reviewer: "#d97706",
  system: "#6b7280",
};

export function Chat() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const send = useCallback(() => {
    const text = input.trim();
    if (!text) return;

    setInput("");
    setLoading(true);
    setMessages((prev) => [
      ...prev,
      { agent: "you", content: text, type: "agent_message" },
    ]);

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ message: text }));
    };

    ws.onmessage = (event) => {
      const msg: AgentMessage = JSON.parse(event.data);
      if (msg.type === "done") {
        setLoading(false);
        ws.close();
        return;
      }
      setMessages((prev) => [...prev, msg]);
    };

    ws.onerror = () => {
      setMessages((prev) => [
        ...prev,
        { agent: "system", content: "Connection error", type: "error" },
      ]);
      setLoading(false);
    };

    ws.onclose = () => {
      setLoading(false);
    };
  }, [input]);

  return (
    <div>
      <div
        style={{
          border: "1px solid #e5e7eb",
          borderRadius: 8,
          padding: "1rem",
          minHeight: 400,
          maxHeight: 600,
          overflowY: "auto",
          marginBottom: "1rem",
          background: "#fafafa",
        }}
      >
        {messages.length === 0 && (
          <p style={{ color: "#9ca3af", textAlign: "center", marginTop: 160 }}>
            Send a message to start the multi-agent team.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: "0.75rem" }}>
            <strong style={{ color: AGENT_COLORS[msg.agent] ?? "#374151" }}>
              {msg.agent}
            </strong>
            {msg.type === "error" ? (
              <span style={{ color: "#dc2626" }}> {msg.content}</span>
            ) : (
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  margin: "0.25rem 0 0 0",
                  fontFamily: "inherit",
                }}
              >
                {msg.content}
              </pre>
            )}
          </div>
        ))}
        {loading && (
          <p style={{ color: "#9ca3af", fontStyle: "italic" }}>
            Agents are working...
          </p>
        )}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
        style={{ display: "flex", gap: "0.5rem" }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the agent team something..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "0.5rem 0.75rem",
            borderRadius: 6,
            border: "1px solid #d1d5db",
            fontSize: "1rem",
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            padding: "0.5rem 1.5rem",
            borderRadius: 6,
            border: "none",
            background: "#2563eb",
            color: "white",
            fontSize: "1rem",
            cursor: "pointer",
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
