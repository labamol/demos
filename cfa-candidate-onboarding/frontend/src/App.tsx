import { useCallback, useEffect, useState } from "react";
import ActionPlanPanel from "./components/ActionPlanPanel";
import AuditPanel from "./components/AuditPanel";
import DashboardPanel from "./components/DashboardPanel";
import ExperiencePanel from "./components/ExperiencePanel";
import FileSelector from "./components/FileSelector";
import ReadinessPanel from "./components/ReadinessPanel";
import RecommendationsPanel from "./components/RecommendationsPanel";
import { getAudit, listFiles, runWorkflow, toggleActions } from "./api";
import type { AuditEntry, MockFile, RunResponse } from "./types";

type Tab = "dashboard" | "readiness" | "experience" | "plan" | "recommendations" | "audit";

const TABS: Array<{ id: Tab; label: string }> = [
  { id: "dashboard", label: "Dashboard" },
  { id: "readiness", label: "Readiness" },
  { id: "experience", label: "Work experience" },
  { id: "plan", label: "90-day plan" },
  { id: "recommendations", label: "Recommendations" },
  { id: "audit", label: "Audit log" },
];

export default function App() {
  const [files, setFiles] = useState<MockFile[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [run, setRun] = useState<RunResponse | null>(null);
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [tab, setTab] = useState<Tab>("dashboard");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listFiles()
      .then((result) => {
        setFiles(result);
        if (result.length > 0) setSelected(result[0].name);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const execute = useCallback(
    async (completedIds: string[] = []) => {
      if (!selected) return;
      setBusy(true);
      setError(null);
      try {
        const response = await runWorkflow({
          file_name: selected,
          question: question.trim() ? question.trim() : null,
          completed_action_ids: completedIds,
        });
        setRun(response);
        setAudit(response.audit);
        try {
          setAudit(await getAudit(response.result.run_id));
        } catch {
          /* keep the in-response audit trail if the DB query fails */
        }
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setBusy(false);
      }
    },
    [selected, question]
  );

  const onToggle = async (itemId: string) => {
    if (!run) return;
    const items = run.result.action_plan.items.map((item) =>
      item.id === itemId ? { ...item, completed: !item.completed } : item
    );
    setRun({ ...run, result: { ...run.result, action_plan: { ...run.result.action_plan, items } } });
    try {
      await toggleActions(run.result.run_id, items);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const regenerate = () => {
    const completed = run?.result.action_plan.items.filter((i) => i.completed).map((i) => i.id) ?? [];
    void execute(completed);
  };

  return (
    <>
      <header className="app-header">
        <h1>CFA Candidate-to-Member Onboarding</h1>
        <span>LangGraph + Google A2A + MCP + OpenAI</span>
        {run && <span>{run.result.llm_used ? "LLM: OpenAI" : "LLM: deterministic fallback"}</span>}
      </header>

      <div className="layout">
        <div>
          <FileSelector files={files} selected={selected} onSelect={setSelected} />
          <div className="card">
            <h2>Ask the assistant</h2>
            <textarea
              rows={3}
              placeholder="e.g. Does my equity research experience qualify for membership?"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
            <button style={{ marginTop: 10 }} disabled={!selected || busy} onClick={() => void execute()}>
              {busy ? "Running workflow..." : "Run onboarding workflow"}
            </button>
          </div>
        </div>

        <div>
          {error && <div className="error">{error}</div>}
          {!run && !error && <div className="card">Select a mock candidate file and run the workflow.</div>}
          {run && (
            <>
              {run.answer && (
                <div className="card">
                  <h2>Assistant answer</h2>
                  <p>{run.answer}</p>
                </div>
              )}
              {run.result.transition_ready && (
                <div className="card">
                  <p className="notice">
                    All membership requirements are complete - the simulated member dashboard is active.
                  </p>
                </div>
              )}
              <div className="tabs">
                {TABS.map((item) => (
                  <button
                    key={item.id}
                    className={tab === item.id ? "active" : ""}
                    onClick={() => setTab(item.id)}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
              {tab === "dashboard" && <DashboardPanel result={run.result} />}
              {tab === "readiness" && <ReadinessPanel readiness={run.result.readiness} />}
              {tab === "experience" && <ExperiencePanel evaluation={run.result.work_experience} />}
              {tab === "plan" && (
                <ActionPlanPanel
                  plan={run.result.action_plan}
                  onToggle={(id) => void onToggle(id)}
                  onRegenerate={regenerate}
                  busy={busy}
                />
              )}
              {tab === "recommendations" && <RecommendationsPanel result={run.result} />}
              {tab === "audit" && <AuditPanel entries={audit} runId={run.result.run_id} />}
            </>
          )}
        </div>
      </div>
    </>
  );
}
