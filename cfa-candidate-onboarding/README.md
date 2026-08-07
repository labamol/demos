# CFA Candidate-to-Member Onboarding — Agentic AI POC

An agentic AI proof of concept for the **Candidate-to-Member transition** journey described in
the CFA Booth 1 Guide. A LangGraph workflow orchestrates several agents that read synthetic
candidate profiles from local directory storage over **MCP**, call each other over **Google A2A**,
use **OpenAI** for narrative/judgement, and persist workflow state plus a full agent execution
audit trail in **Postgres**. A **React** UI lets you pick a mock candidate file and inspect every
capability and every audit event.

## POC capabilities

| Capability | Where it lives |
|---|---|
| 1. Lifecycle-aware dashboard (candidate vs member view, exam progression, readiness, outstanding actions, AI next-best actions) | `build_dashboard` node, `frontend/src/components/DashboardPanel.tsx` |
| 2. Membership readiness assessment (rule-based score, LLM narrative, requirement checklist) | `backend/app/agents/rules.py`, `assess_readiness` node |
| 3. Work-experience evaluator (qualifying activities, missing evidence, confidence, improved description, escalation) | `backend/app/agents/work_experience.py` (A2A agent) |
| 4. Personalized 90-day action plan, with completion toggles and regeneration | `backend/app/agents/action_plan.py` (A2A agent) |
| Q&A about exams, work experience and membership | `backend/app/agents/qa.py` |
| Reference and application-readiness tracking | readiness requirements + `RecommendationsPanel` |
| Recommended learning, events, career activities | `backend/app/agents/recommendations.py` (A2A agent) |
| Transition to simulated member dashboard once requirements are met | `transition_ready` rule + dashboard stage switch |

The readiness percentage is computed by transparent deterministic rules
(`backend/app/agents/rules.py`), never by the LLM; the LLM only explains it. Work-experience
output is explicitly labelled as guidance, not an official eligibility determination.

## Architecture

```
React (Vite, :5173)
        │  REST /api/*
FastAPI (:8000)
        ├── LangGraph workflow  backend/app/workflow/graph.py
        │      load_profile → assess_readiness → evaluate_experience
        │      → build_action_plan → recommend → build_dashboard → [answer_question]
        ├── MCP client ──stdio──► candidate-files MCP server ──► data/mock (local directory storage)
        ├── Google A2A client ──JSON-RPC──► /a2a/{agent}  (agent cards at /a2a/{agent}/.well-known/agent.json)
        ├── OpenAI (falls back to deterministic output when OPENAI_API_KEY is empty)
        └── Postgres  workflow_run, workflow_state, agent_audit_log, capability output tables
```

Auditing: every node emits `node_started` / `node_completed` (or `node_failed`), every LLM, MCP
and A2A interaction is logged with latency and transport, and the LangGraph state is checkpointed
after each node into `workflow_state`. If Postgres is unreachable the run still completes and
audit events are buffered in memory.

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## 1. Database

```bash
sudo -u postgres psql -c "CREATE USER onboarding WITH PASSWORD 'onboarding';"
sudo -u postgres psql -c "CREATE DATABASE onboarding OWNER onboarding;"
PGPASSWORD=onboarding psql -h localhost -U onboarding -d onboarding -f db/ddl.sql
```

All objects are created in the `onboarding` schema. The script is idempotent.

## 2. Configuration

```bash
cp .env.example .env
```

Edit `.env`:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Leave empty to run fully offline on deterministic fallbacks; set it to enable OpenAI. |
| `OPENAI_MODEL` | Defaults to `gpt-4o-mini`. |
| `DATABASE_URL` | `postgresql+psycopg://onboarding:onboarding@localhost:5432/onboarding` |
| `DATA_DIR` | Local directory storage root, default `./data/mock`. |
| `MCP_CONFIG_PATH` | Path to `mcp.config.json`. |
| `A2A_BASE_URL` | Base URL the workflow uses to reach the A2A agents (the API itself). |

`mcp.config.json` declares the `candidate-files` MCP server (stdio) over `DATA_DIR`.

## 3. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

API docs: <http://localhost:8000/docs>. Health: `GET /api/health`.

The MCP server is spawned automatically by the API over stdio. To run it standalone:

```bash
python -m backend.app.mcp.file_server
```

## 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` and `/a2a` to `http://localhost:8000`.

## 5. Using the POC

1. Pick a mock candidate file in the left panel.
2. Optionally type a question (e.g. *"Does my equity research experience qualify?"*).
3. Click **Run onboarding workflow**.
4. Browse the tabs: Dashboard, Readiness, Work experience, 90-day plan, Recommendations, Audit log.
5. Tick action items and click **Regenerate plan from completed actions**.

### Mock data (`data/mock/applications`)

| File | Persona | Expected readiness |
|---|---|---|
| `arjun_mehta_candidate.json` | Advanced candidate (Levels I & II, ~30 months experience) | 42% |
| `aisha_khan_applicant.json` | Newly eligible charterholder applicant | 70% |
| `neha_sharma_member.json` | Existing member — switches to the member dashboard | 100% |
| `rohan_patel_early_candidate.json` | Early candidate with non-qualifying operations experience | 15% |

`data/mock/documents/<candidate_id>/` holds supporting documents surfaced over MCP.

## API reference

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Service and database status |
| GET | `/api/files` | Selectable mock profiles (via MCP) |
| POST | `/api/workflow/run` | Run the LangGraph workflow |
| GET | `/api/runs` | Recent workflow runs |
| GET | `/api/runs/{run_id}` | Full stored result |
| GET | `/api/audit?run_id=` | Agent execution audit log |
| POST | `/api/action-plan/toggle` | Persist action completion |
| GET | `/api/agents` | Published A2A agent cards |
| GET | `/a2a/{agent}/.well-known/agent.json` | A2A agent card |
| POST | `/a2a/{agent}` | A2A `message/send` (JSON-RPC 2.0) |

## Inspecting the audit trail

```sql
SELECT event_type, node_name, agent_name, status, duration_ms, message
FROM   onboarding.agent_audit_log
WHERE  run_id = '<run-id>'
ORDER  BY id;

SELECT sequence, node_name, jsonb_pretty(state_json)
FROM   onboarding.workflow_state
WHERE  run_id = '<run-id>'
ORDER  BY sequence;
```

## Notes and limitations

- All candidate data is synthetic; there is no authentication ("log in as a synthetic profile" is
  modelled as selecting a profile file).
- Work-experience output is guidance only and not an official eligibility determination.
- Requirement thresholds (48 qualifying months, 2 references, readiness weights) are constants in
  `backend/app/agents/rules.py` and are illustrative, not authoritative CFA Institute policy.
