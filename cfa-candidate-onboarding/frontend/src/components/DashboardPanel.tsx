import type { WorkflowResult } from "../types";

export default function DashboardPanel({ result }: { result: WorkflowResult }) {
  const { dashboard, readiness, work_experience: we } = result;
  return (
    <>
      <div className="card">
        <h2>Lifecycle-aware dashboard</h2>
        <p className="notice">{dashboard.headline}</p>
        <div className="metrics">
          <div className="metric">
            <div className="label">Lifecycle stage</div>
            <div className="value" style={{ fontSize: 18 }}>{dashboard.lifecycle_stage.replace("_", " ")}</div>
          </div>
          <div className="metric">
            <div className="label">Membership readiness</div>
            <div className="value">{dashboard.membership_readiness_pct}%</div>
            <div className="progress"><div style={{ width: `${dashboard.membership_readiness_pct}%` }} /></div>
          </div>
          <div className="metric">
            <div className="label">Work experience</div>
            <div className="value">{dashboard.work_experience_pct}%</div>
            <div className="progress"><div style={{ width: `${dashboard.work_experience_pct}%` }} /></div>
          </div>
          <div className="metric">
            <div className="label">Next exam milestone</div>
            <div className="value" style={{ fontSize: 18 }}>{dashboard.next_exam_milestone ?? "All levels passed"}</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Exam progression</h2>
        <table>
          <thead><tr><th>Level</th><th>Status</th><th>Result date</th><th>Scheduled</th></tr></thead>
          <tbody>
            {dashboard.exam_progression.map((exam) => (
              <tr key={exam.level}>
                <td>{exam.level}</td>
                <td><span className={`badge ${exam.status === "passed" ? "complete" : "in_progress"}`}>{exam.status}</span></td>
                <td>{exam.result_date ?? "-"}</td>
                <td>{exam.scheduled_date ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Outstanding actions and next best actions</h2>
        <h3>Outstanding</h3>
        <ul className="plain">
          {dashboard.outstanding_actions.length === 0 && <li>Nothing outstanding.</li>}
          {dashboard.outstanding_actions.map((action) => <li key={action}>{action}</li>)}
        </ul>
        <h3>AI-generated next best actions</h3>
        <ul className="plain">
          {dashboard.next_best_actions.map((action) => <li key={action}>{action}</li>)}
        </ul>
        <p className="muted">
          Highest priority: {readiness.highest_priority_action}. Estimated qualifying hours:{" "}
          {we.qualifying_hours_estimate.toLocaleString()}.
        </p>
      </div>

      {dashboard.member_benefits.length > 0 && (
        <div className="card">
          <h2>Member dashboard</h2>
          <ul className="plain">
            {dashboard.member_benefits.map((benefit) => <li key={benefit}>{benefit}</li>)}
          </ul>
        </div>
      )}
    </>
  );
}
