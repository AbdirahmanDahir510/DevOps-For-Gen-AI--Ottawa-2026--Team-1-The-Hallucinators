import { useState } from "react";
import Chatbot from "./Chatbot";
import DocumentUpload from "./DocumentUpload";
import SecurityScore from "./SecurityScore";
import TestResults from "./TestResults";
import "./SecurityDashboard.css";

const API = "http://localhost:5000";

const TABS = [
  { id: "chat",     label: "Chat",      icon: "🤖" },
  { id: "docs",     label: "Documents", icon: "📄" },
  { id: "security", label: "Security",  icon: "🛡️" },
];

export default function SecurityDashboard() {
  const [tab, setTab] = useState("chat");

  // Test state — lifted here so score persists across tab switches
  const [testResults, setTestResults] = useState([]);
  const [testRunning, setTestRunning] = useState(false);
  const [testScores, setTestScores] = useState(null);
  const [testMeta, setTestMeta] = useState({ total: 0, passed: 0, failed: 0, duration: null });

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
        {/* Chat tab */}
        {tab === "chat" && (
          <div className="dashboard__chat-layout">
            <Chatbot />
          </div>
        )}

        {/* Docs tab */}
        {tab === "docs" && (
          <div className="dashboard__docs-layout">
            <DocumentUpload />
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
