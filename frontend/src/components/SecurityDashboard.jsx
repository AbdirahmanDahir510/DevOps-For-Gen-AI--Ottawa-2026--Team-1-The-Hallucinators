import { useState, useEffect } from "react";
import Chatbot from "./Chatbot";
import DocumentUpload from "./DocumentUpload";
import SecurityScore from "./SecurityScore";
import TestResults from "./TestResults";
import "./SecurityDashboard.css";

const API = "http://localhost:5000";

const TABS = [
  { id: "chat",     label: "Chat",      icon: "🤖" },
  { id: "security", label: "Security",  icon: "🛡️" },
];

export default function SecurityDashboard() {
  const [tab, setTab] = useState("chat");
  const [docsOpen, setDocsOpen] = useState(true);
  const [docCount, setDocCount] = useState(0);

  // Test state — lifted here so score persists across tab switches
  const [testResults, setTestResults] = useState([]);
  const [testRunning, setTestRunning] = useState(false);
  const [testScores, setTestScores] = useState(null);
  const [testMeta, setTestMeta] = useState({ total: 0, passed: 0, failed: 0, duration: null });

  // Poll document count so the chatbot header badge stays current
  useEffect(() => {
    const refresh = () =>
      fetch(`${API}/api/documents`)
        .then((r) => r.json())
        .then((d) => setDocCount(d.total ?? 0))
        .catch(() => {});
    refresh();
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, []);

  const runTests = async (suite = "all") => {
    setTestRunning(true);
    try {
      const res = await fetch(`${API}/api/tests/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ suite }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Test run failed.");

      setTestResults(data.results || []);
      setTestScores(data.scores || null);
      setTestMeta({
        total:    data.total    ?? 0,
        passed:   data.passed   ?? 0,
        failed:   data.failed   ?? 0,
        duration: data.duration_seconds ?? null,
      });
    } catch (err) {
      console.error("Test run error:", err);
    } finally {
      setTestRunning(false);
    }
  };

  return (
    <div className="dashboard">
      {/* Top bar */}
      <header className="dashboard__topbar">
        <div className="dashboard__brand">
          <span className="dashboard__brand-icon">🤖</span>
          <div>
            <h1 className="dashboard__title">AI Security Chatbot</h1>
            <p className="dashboard__subtitle">React · Flask · Ollama · RAG · Chaos Testing</p>
          </div>
        </div>

        {testScores?.overall != null && (
          <div className="dashboard__score-pill">
            <span className="dashboard__score-num">{testScores.overall}%</span>
            <span className="dashboard__score-lbl">Security Score</span>
          </div>
        )}
      </header>

      {/* Tab nav */}
      <nav className="dashboard__tabs" aria-label="Main navigation">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`dashboard__tab${tab === t.id ? " dashboard__tab--active" : ""}`}
            onClick={() => setTab(t.id)}
            aria-current={tab === t.id ? "page" : undefined}
          >
            <span aria-hidden="true">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <main className="dashboard__main">
        {/* Chat tab — split layout: docs panel + chat */}
        {tab === "chat" && (
          <div className="dashboard__chat-split">
            {/* Left: document panel */}
            <div className={`dashboard__doc-panel${docsOpen ? "" : " dashboard__doc-panel--collapsed"}`}>
              <button
                className="dashboard__doc-toggle"
                onClick={() => setDocsOpen((o) => !o)}
                aria-label={docsOpen ? "Collapse document panel" : "Expand document panel"}
              >
                {docsOpen ? "◀ Hide" : "▶"}
              </button>
              {docsOpen && <DocumentUpload onDocCountChange={setDocCount} />}
            </div>

            {/* Right: chat */}
            <div className="dashboard__chat-pane">
              <Chatbot docCount={docCount} />
            </div>
          </div>
        )}

        {/* Security tab */}
        {tab === "security" && (
          <div className="dashboard__security-layout">
            <div className="dashboard__security-left">
              <SecurityScore
                scores={testScores}
                total={testMeta.total}
                passed={testMeta.passed}
                failed={testMeta.failed}
              />
            </div>
            <div className="dashboard__security-right">
              <TestResults
                results={testResults}
                running={testRunning}
                onRun={runTests}
                duration={testMeta.duration}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
