import type { AuditEntry } from "../types";

export default function AuditPanel({ entries, runId }: { entries: AuditEntry[]; runId: string }) {
  return (
    <div className="card">
      <h2>Agent execution audit log</h2>
      <p className="muted mono">run_id: {runId}</p>
      <table>
        <thead>
          <tr><th>#</th><th>Event</th><th>Node</th><th>Agent</th><th>Status</th><th>ms</th><th>Message</th></tr>
        </thead>
        <tbody>
          {entries.map((entry, index) => (
            <tr key={`${entry.id}-${index}`}>
              <td>{index + 1}</td>
              <td className="mono">{entry.event_type}</td>
              <td>{entry.node_name ?? "-"}</td>
              <td>{entry.agent_name ?? "-"}</td>
              <td><span className={`badge ${entry.status}`}>{entry.status}</span></td>
              <td>{entry.duration_ms ?? "-"}</td>
              <td>
                {entry.message ?? "-"}
                {Object.keys(entry.payload ?? {}).length > 0 && (
                  <div className="mono muted">{JSON.stringify(entry.payload)}</div>
                )}
              </td>
            </tr>
          ))}
          {entries.length === 0 && <tr><td colSpan={7} className="muted">No audit events yet.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}
