export interface MockFile {
  name: string;
  path: string;
  size_bytes: number;
  kind: string;
  candidate_name?: string | null;
  persona?: string | null;
  lifecycle_stage?: string | null;
}

export interface ExamRecord {
  level: string;
  status: string;
  result_date?: string | null;
  scheduled_date?: string | null;
}

export interface Requirement {
  name: string;
  status: string;
  explanation: string;
  weight: number;
  completion_pct: number;
}

export interface Readiness {
  score: number;
  requirements: Requirement[];
  highest_priority_action: string;
  blocking_gaps: string[];
  rule_breakdown: Record<string, number>;
  narrative: string;
}

export interface WorkExperienceEvaluation {
  qualifying_months_estimate: number;
  qualifying_hours_estimate: number;
  requirement_months: number;
  completion_pct: number;
  likely_qualifying_activities: string[];
  non_qualifying_activities: string[];
  missing_evidence: string[];
  confidence: number;
  suggested_description: string;
  escalation_recommended: boolean;
  rationale: string;
  disclaimer: string;
}

export interface ActionItem {
  id: string;
  month: 1 | 2 | 3;
  title: string;
  detail: string;
  category: string;
  completed: boolean;
}

export interface ActionPlan {
  horizon_days: number;
  summary: string;
  items: ActionItem[];
}

export interface Recommendation {
  title: string;
  kind: string;
  reason: string;
  url?: string | null;
}

export interface Dashboard {
  lifecycle_stage: string;
  headline: string;
  exam_progression: ExamRecord[];
  next_exam_milestone?: string | null;
  membership_readiness_pct: number;
  work_experience_pct: number;
  outstanding_actions: string[];
  next_best_actions: string[];
  member_benefits: string[];
}

export interface Reference {
  name: string;
  relationship: string;
  status: string;
  is_member: boolean;
}

export interface Profile {
  candidate_id: string;
  full_name: string;
  email: string;
  persona: string;
  lifecycle_stage: string;
  local_society?: string | null;
  references: Reference[];
  documents: string[];
}

export interface WorkflowResult {
  run_id: string;
  candidate_id: string;
  source_file: string;
  profile: Profile;
  dashboard: Dashboard;
  readiness: Readiness;
  work_experience: WorkExperienceEvaluation;
  action_plan: ActionPlan;
  recommendations: { learning: Recommendation[]; events: Recommendation[]; career: Recommendation[] };
  transition_ready: boolean;
  llm_used: boolean;
  started_at: string;
  completed_at: string;
}

export interface AuditEntry {
  id: number;
  run_id: string;
  candidate_id?: string | null;
  event_type: string;
  node_name?: string | null;
  agent_name?: string | null;
  status: string;
  message?: string | null;
  payload: Record<string, unknown>;
  duration_ms?: number | null;
  created_at: string;
}

export interface RunResponse {
  result: WorkflowResult;
  answer?: string | null;
  audit: AuditEntry[];
}
