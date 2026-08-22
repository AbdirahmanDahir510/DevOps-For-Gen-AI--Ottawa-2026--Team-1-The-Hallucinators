import "./SecurityScore.css";

/**
 * SecurityScore
 * Displays the overall score ring + three category scores.
 *
 * Props:
 *   scores: { overall, security, rag, chaos }  (all 0-100 or null)
 *   total, passed, failed: integers
 */
export default function SecurityScore({ scores, total, passed, failed }) {
  const overall = scores?.overall ?? null;

  const ringColor = (score) => {
    if (score === null) return "#e5e7eb";
    if (score >= 80) return "#10b981";
    if (score >= 60) return "#f59e0b";
    return "#ef4444";
  };

  const label = (score) => {
    if (score === null) return "N/A";
    if (score >= 80) return "Good";
    if (score >= 60) return "Fair";
    return "Poor";
  };

  // SVG ring parameters
  const R = 54;
  const CIRC = 2 * Math.PI * R;
  const dash = overall !== null ? (overall / 100) * CIRC : 0;

  const categories = [
    { key: "security", label: "Security",   icon: "🔒" },
    { key: "rag",      label: "RAG",        icon: "📄" },
    { key: "chaos",    label: "Chaos",      icon: "⚡" },
  ];

  return (
    <div className="score">
      <div className="score__header">
        <span>🛡️</span>
        <h2>Security Score</h2>
      </div>

      <div className="score__body">
        {/* Ring */}
        <div className="score__ring-wrap">
          <svg viewBox="0 0 128 128" className="score__ring" aria-hidden="true">
            <circle cx="64" cy="64" r={R} fill="none" stroke="#e5e7eb" strokeWidth="12" />
            <circle
              cx="64" cy="64" r={R} fill="none"
              stroke={ringColor(overall)}
              strokeWidth="12"
              strokeDasharray={`${dash} ${CIRC}`}
              strokeLinecap="round"
              transform="rotate(-90 64 64)"
              style={{ transition: "stroke-dasharray 0.6s ease" }}
            />
          </svg>
          <div className="score__ring-text">
            <span className="score__pct" style={{ color: ringColor(overall) }}>
              {overall !== null ? `${overall}%` : "—"}
            </span>
            <span className="score__label">{label(overall)}</span>
          </div>
        </div>

        {/* Stats row */}
        {total > 0 && (
          <div className="score__stats">
            <div className="score__stat score__stat--total">
              <span className="score__stat-val">{total}</span>
              <span className="score__stat-lbl">Total</span>
            </div>
            <div className="score__stat score__stat--pass">
              <span className="score__stat-val">{passed}</span>
              <span className="score__stat-lbl">Passed</span>
            </div>
            <div className="score__stat score__stat--fail">
              <span className="score__stat-val">{failed}</span>
              <span className="score__stat-lbl">Failed</span>
            </div>
          </div>
        )}

        {/* Category bars */}
        <div className="score__categories">
          {categories.map(({ key, label: lbl, icon }) => {
            const val = scores?.[key] ?? null;
            return (
              <div key={key} className="score__cat">
                <div className="score__cat-header">
                  <span>{icon} {lbl}</span>
                  <span style={{ color: ringColor(val) }}>
                    {val !== null ? `${val}%` : "—"}
                  </span>
                </div>
                <div className="score__bar-bg">
                  <div
                    className="score__bar-fill"
                    style={{
                      width: val !== null ? `${val}%` : "0%",
                      background: ringColor(val),
                    }}
                    role="progressbar"
                    aria-valuenow={val ?? 0}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`${lbl} score`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
