import type { WorkExperienceEvaluation } from "../types";

export default function ExperiencePanel({ evaluation }: { evaluation: WorkExperienceEvaluation }) {
  return (
    <>
      <div className="card">
        <h2>Work-experience evaluator</h2>
        <div className="metrics">
          <div className="metric">
            <div className="label">Qualifying months</div>
            <div className="value">{evaluation.qualifying_months_estimate}</div>
            <div className="muted">of {evaluation.requirement_months} required</div>
          </div>
          <div className="metric">
            <div className="label">Qualifying hours</div>
            <div className="value">{evaluation.qualifying_hours_estimate.toLocaleString()}</div>
          </div>
          <div className="metric">
            <div className="label">Confidence</div>
            <div className="value">{Math.round(evaluation.confidence * 100)}%</div>
          </div>
          <div className="metric">
            <div className="label">Escalation</div>
            <div className="value" style={{ fontSize: 18 }}>
              {evaluation.escalation_recommended ? "Recommended" : "Not needed"}
            </div>
          </div>
        </div>
        <p style={{ marginTop: 12 }}>{evaluation.rationale}</p>
      </div>

      <div className="card">
        <h2>Activity assessment</h2>
        <h3>Likely qualifying activities</h3>
        <ul className="plain">
          {evaluation.likely_qualifying_activities.map((item) => <li key={item}>{item}</li>)}
          {evaluation.likely_qualifying_activities.length === 0 && <li>None identified.</li>}
        </ul>
        <h3>May not qualify independently</h3>
        <ul className="plain">
          {evaluation.non_qualifying_activities.map((item) => <li key={item}>{item}</li>)}
          {evaluation.non_qualifying_activities.length === 0 && <li>None identified.</li>}
        </ul>
        <h3>Missing evidence</h3>
        <ul className="plain">
          {evaluation.missing_evidence.map((item) => <li key={item}>{item}</li>)}
          {evaluation.missing_evidence.length === 0 && <li>Nothing outstanding.</li>}
        </ul>
        <h3>Suggested improved description</h3>
        <p>{evaluation.suggested_description}</p>
        <p className="muted">{evaluation.disclaimer}</p>
      </div>
    </>
  );
}
