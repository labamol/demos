import type { ActionItem, ActionPlan } from "../types";

interface Props {
  plan: ActionPlan;
  onToggle: (itemId: string) => void;
  onRegenerate: () => void;
  busy: boolean;
}

const MONTHS: Array<1 | 2 | 3> = [1, 2, 3];

export default function ActionPlanPanel({ plan, onToggle, onRegenerate, busy }: Props) {
  return (
    <div className="card">
      <h2>Personalized 90-day plan</h2>
      <p className="notice">{plan.summary}</p>
      <div className="month-grid" style={{ marginTop: 14 }}>
        {MONTHS.map((month) => (
          <div key={month}>
            <h3>Month {month}</h3>
            {plan.items
              .filter((item: ActionItem) => item.month === month)
              .map((item) => (
                <div key={item.id} className={`action${item.completed ? " done" : ""}`}>
                  <input
                    id={item.id}
                    type="checkbox"
                    checked={item.completed}
                    onChange={() => onToggle(item.id)}
                  />
                  <label htmlFor={item.id}>
                    {item.title}
                    {item.detail && <small>{item.detail}</small>}
                  </label>
                </div>
              ))}
          </div>
        ))}
      </div>
      <button className="secondary" onClick={onRegenerate} disabled={busy} style={{ marginTop: 10 }}>
        {busy ? "Regenerating..." : "Regenerate plan from completed actions"}
      </button>
    </div>
  );
}
