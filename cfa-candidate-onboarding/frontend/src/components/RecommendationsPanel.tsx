import type { Recommendation, WorkflowResult } from "../types";

function Group({ title, items }: { title: string; items: Recommendation[] }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <ul className="plain">
        {items.map((item) => (
          <li key={item.title}>
            <strong>{item.title}</strong>
            <br />
            <span className="muted">{item.reason}</span>
          </li>
        ))}
        {items.length === 0 && <li className="muted">No recommendations.</li>}
      </ul>
    </div>
  );
}

export default function RecommendationsPanel({ result }: { result: WorkflowResult }) {
  const { recommendations, profile } = result;
  return (
    <>
      <Group title="Recommended learning" items={recommendations.learning} />
      <Group title="Events and society activity" items={recommendations.events} />
      <Group title="Career and volunteering" items={recommendations.career} />
      <div className="card">
        <h2>Reference tracking</h2>
        <table>
          <thead><tr><th>Name</th><th>Relationship</th><th>Status</th><th>Member</th></tr></thead>
          <tbody>
            {profile.references.map((ref) => (
              <tr key={ref.name}>
                <td>{ref.name}</td>
                <td>{ref.relationship}</td>
                <td><span className={`badge ${ref.status}`}>{ref.status.replace(/_/g, " ")}</span></td>
                <td>{ref.is_member ? "Yes" : "No"}</td>
              </tr>
            ))}
            {profile.references.length === 0 && (
              <tr><td colSpan={4} className="muted">No references identified yet.</td></tr>
            )}
          </tbody>
        </table>
        <h3>Supporting documents (local storage via MCP)</h3>
        <ul className="plain">
          {profile.documents.map((doc) => <li key={doc} className="mono">{doc}</li>)}
          {profile.documents.length === 0 && <li className="muted">No documents.</li>}
        </ul>
      </div>
    </>
  );
}
