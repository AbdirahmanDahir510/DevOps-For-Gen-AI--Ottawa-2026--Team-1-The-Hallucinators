import { useState } from "react";
import "./TestResults.css";

const SEVERITY_ORDER = { HIGH: 0, MEDIUM: 1, LOW: 2 };
const CATEGORY_ICONS = {
  "Prompt Injection": "💉",
  "Data Leakage":     "🔓",
  "RAG Security":     "📄",
  "Chaos":            "⚡",
};

/**
 * TestResults
 *
 * Props:
 *   results:  array of { name, category, status, severity, details }
 *   running:  bool — true while tests are in progress
 *   onRun:    (suite) => void — called when user clicks a run button
 *   duration: number (seconds) | null
 */
export default function TestResults({ results, running, onRun, duration }) {
  const [filter, setFilter] = useState("all");       // all | PASS | FAIL
  const [expanded, setExpanded] = useState(null);    // row index
  const [suite, setSuite] = useState("all");

  const filtered = results.filter((r) => filter === "all" || r.status === filter);

  // Sort: failures first, then by severity
  const sorted = [...filtered].sort((a, b) => {
    if (a.status !== b.status) return a.status === "FAIL" ? -1 : 1;
    return (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9);
  });

  const toggle = (i) => setExpanded(expanded === i ? null : i);

  return (
    <div className="results">
      <div className="results__header">
        <span>🧪</span>
        <h2>Test Results</h2>
        {duration !== null && (
          <span className="results__duration">{duration}s</span>
        )}
      </div>

      {/* Controls */}
      <div className="results__controls">
        <div className="results__suite-row">
          <select
            value={suite}
            onChange={(e) => setSuite(e.target.value)}
            className="results__select"
            disabled={running}
            aria-label="Select test suite"
          >
            <option value="all">All Tests</option>
            <option value="security">Security Tests</option>
            <option value="rag">RAG Tests</option>
            <option value="chaos">Chaos Tests</option>
          </select>
          <button
            className="results__run-btn"
            onClick={() => onRun(suite)}
            disabled={running}
            aria-label="Run selected test suite"
          >
            {running ? (
              <><span className="results__spinner" aria-hidden="true" /> Running…</>
            ) : (
              "▶ Run Tests"
            )}
          </button>
        </div>

        {results.length > 0 && (
          <div className="results__filter" role="group" aria-label="Filter results">
            {["all", "PASS", "FAIL"].map((f) => (
              <button
                key={f}
                className={`results__filter-btn${filter === f ? " active" : ""}`}
                onClick={() => setFilter(f)}
              >
                {f === "all" ? "All" : f}
                <span className="results__filter-count">
                  {f === "all"
                    ? results.length
                    : results.filter((r) => r.status === f).length}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Table */}
      {results.length === 0 ? (
        <p className="results__empty">
          {running ? "Running tests…" : "No results yet. Run a test suite above."}
        </p>
      ) : (
        <div className="results__table-wrap">
          <table className="results__table" aria-label="Test results">
            <thead>
              <tr>
                <th scope="col">Test</th>
                <th scope="col">Category</th>
                <th scope="col">Severity</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r, i) => (
                <>
                  <tr
                    key={i}
                    className={`results__row results__row--${r.status.toLowerCase()}${expanded === i ? " results__row--open" : ""}`}
                    onClick={() => toggle(i)}
                    style={{ cursor: "pointer" }}
                    aria-expanded={expanded === i}
                  >
                    <td className="results__name">
                      <span className="results__expand-icon">{expanded === i ? "▾" : "▸"}</span>
                      {r.name}
                    </td>
                    <td>
                      <span className="results__category">
                        {CATEGORY_ICONS[r.category] || "🔹"} {r.category}
                      </span>
                    </td>
                    <td>
                      <span className={`results__severity results__severity--${r.severity.toLowerCase()}`}>
                        {r.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`results__status results__status--${r.status.toLowerCase()}`}>
                        {r.status === "PASS" ? "✓ PASS" : r.status === "FAIL" ? "✗ FAIL" : r.status}
                      </span>
                    </td>
                  </tr>
                  {expanded === i && (
                    <tr key={`${i}-detail`} className="results__detail-row">
                      <td colSpan={4}>
                        <div className="results__detail">
                          <strong>Details:</strong> {r.details || "No additional details."}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
