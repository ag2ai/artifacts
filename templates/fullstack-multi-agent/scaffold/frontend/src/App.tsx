import { Chat } from "./components/Chat";

export default function App() {
  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1>{{ project_name }}</h1>
      <p style={{ color: "#666" }}>{{ description }}</p>
      <Chat />
    </div>
  );
}
