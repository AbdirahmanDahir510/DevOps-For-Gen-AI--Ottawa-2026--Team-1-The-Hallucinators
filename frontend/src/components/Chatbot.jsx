import { useState, useRef, useEffect } from "react";
import "./Chatbot.css";

const API = "http://localhost:5000";

export default function Chatbot({ docCount = 0 }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! I'm your local AI security assistant. Upload a PDF in the panel on the left, then ask me anything about it.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Request failed.");
      }

      const sources = data.sources?.length
        ? `\n\n*Sources: ${data.sources.map((s) => s.filename).join(", ")}*`
        : "";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.response + sources,
          contextUsed: data.context_used,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Error: ${err.message}`, isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="chatbot">
      <div className="chatbot__header">
        <span className="chatbot__icon">🤖</span>
        <h2>AI Security Chatbot</h2>
        <span className="chatbot__badge">Llama 3.2 · Ollama</span>
        {docCount > 0 ? (
          <span className="chatbot__doc-badge" title="Documents loaded — answers will use RAG">
            📄 {docCount} doc{docCount !== 1 ? "s" : ""} loaded
          </span>
        ) : (
          <span className="chatbot__doc-badge chatbot__doc-badge--empty" title="No documents uploaded yet">
            📄 No docs
          </span>
        )}
      </div>

      <div className="chatbot__messages" aria-live="polite" aria-label="Chat messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chatbot__msg chatbot__msg--${msg.role}${msg.isError ? " chatbot__msg--error" : ""}`}
          >
            <span className="chatbot__avatar">
              {msg.role === "user" ? "👤" : "🤖"}
            </span>
            <div className="chatbot__bubble">
              {msg.contextUsed && (
                <span className="chatbot__rag-badge">📄 RAG</span>
              )}
              <p>{msg.text}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="chatbot__msg chatbot__msg--assistant">
            <span className="chatbot__avatar">🤖</span>
            <div className="chatbot__bubble chatbot__bubble--thinking">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chatbot__input-row">
        <textarea
          className="chatbot__textarea"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask something… (Enter to send, Shift+Enter for new line)"
          rows={3}
          disabled={loading}
          aria-label="Chat input"
        />
        <button
          className="chatbot__send"
          onClick={send}
          disabled={loading || !input.trim()}
          aria-label="Send message"
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
