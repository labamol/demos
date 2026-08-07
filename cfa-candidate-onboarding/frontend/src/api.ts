import type { ActionItem, AuditEntry, MockFile, RunResponse } from "./types";

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${detail}`);
  }
  return (await response.json()) as T;
}

export const listFiles = () => request<MockFile[]>("/api/files");

export const runWorkflow = (payload: {
  file_name: string;
  question?: string | null;
  completed_action_ids?: string[];
}) => request<RunResponse>("/api/workflow/run", { method: "POST", body: JSON.stringify(payload) });

export const getAudit = (runId: string) =>
  request<AuditEntry[]>(`/api/audit?run_id=${encodeURIComponent(runId)}`);

export const toggleActions = (runId: string, items: ActionItem[]) =>
  request<{ completed: number }>("/api/action-plan/toggle", {
    method: "POST",
    body: JSON.stringify({ run_id: runId, items }),
  });
