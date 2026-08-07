import type { Readiness } from "../types";

export default function ReadinessPanel({ readiness }: { readiness: Readiness }) {
  return (
    <>
      <div className="card">
        <h2>Membership readiness assessment</h2>
        <div className="metric" style={{ maxWidth: 220 }}>
          <div className="label">Readiness score (rule-based)</div>
          <div className="value">{readiness.score}%</div>
          <div className="progress"><div style={{ width: `${readiness.score}%` }} /></div>
        </div>
        <p className="notice" style={{ marginTop: 14 }}>{readiness.narrative}</p>
      </div>

      <div className="card">
        <h2>Requirement checklist</h2>
        <table>
          <thead><tr><th>Requirement</th><th>Status</th><th>Explanation</th><th>Weight</th><th>Complete</th></tr></thead>
          <tbody>
            {readiness.requirements.map((req) => (
              <tr key={req.name}>
                <td>{req.name}</td>
                <td><span className={`badge ${req.status}`}>{req.status.replace(/_/g, " ")}</span></td>
                <td>{req.explanation}</td>
                <td>{Math.round(req.weight * 100)}%</td>
                <td>{req.completion_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Transparent rule breakdown</h2>
        <table>
          <thead><tr><th>Rule</th><th>Completion</th></tr></thead>
          <tbody>
            {Object.entries(readiness.rule_breakdown).map(([key, value]) => (
              <tr key={key}><td>{key.replace(/_/g, " ")}</td><td>{Math.round(value * 100)}%</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
