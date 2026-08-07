-- =====================================================================
-- CFA Candidate-to-Member Onboarding POC - schema DDL
-- Target: PostgreSQL 14+
-- Usage:  psql -U onboarding -d onboarding -f db/ddl.sql
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS onboarding;
SET search_path TO onboarding, public;

-- ---------------------------------------------------------------------
-- Enumerations
-- ---------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE lifecycle_stage AS ENUM ('candidate', 'membership_applicant', 'member');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE requirement_status AS ENUM
        ('complete', 'in_progress', 'partially_complete', 'not_started', 'pending');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE reference_status AS ENUM
        ('not_started', 'identified', 'requested', 'submitted', 'verified');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE run_status AS ENUM ('running', 'completed', 'failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------------------------------------------------------------------
-- Candidate / member profiles
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidate (
    candidate_id            TEXT PRIMARY KEY,
    full_name               TEXT        NOT NULL,
    email                   TEXT        NOT NULL,
    persona                 TEXT,
    stage                   lifecycle_stage NOT NULL DEFAULT 'candidate',
    country                 TEXT,
    local_society           TEXT,
    professional_conduct_declared BOOLEAN NOT NULL DEFAULT FALSE,
    membership_application_started BOOLEAN NOT NULL DEFAULT FALSE,
    dues_paid               BOOLEAN NOT NULL DEFAULT FALSE,
    source_file             TEXT,
    profile_json            JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS exam_record (
    id              BIGSERIAL PRIMARY KEY,
    candidate_id    TEXT NOT NULL REFERENCES candidate(candidate_id) ON DELETE CASCADE,
    level           TEXT NOT NULL,
    status          TEXT NOT NULL,
    result_date     DATE,
    scheduled_date  DATE,
    UNIQUE (candidate_id, level)
);

CREATE TABLE IF NOT EXISTS work_experience (
    id                    BIGSERIAL PRIMARY KEY,
    candidate_id          TEXT NOT NULL REFERENCES candidate(candidate_id) ON DELETE CASCADE,
    job_title             TEXT NOT NULL,
    employer              TEXT NOT NULL,
    employer_type         TEXT,
    role_description      TEXT,
    activities            JSONB NOT NULL DEFAULT '[]'::jsonb,
    start_date            DATE NOT NULL,
    end_date              DATE,
    months                INTEGER NOT NULL CHECK (months >= 0),
    investment_time_pct   INTEGER NOT NULL CHECK (investment_time_pct BETWEEN 0 AND 100),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS candidate_reference (
    id              BIGSERIAL PRIMARY KEY,
    candidate_id    TEXT NOT NULL REFERENCES candidate(candidate_id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    relationship    TEXT,
    is_member       BOOLEAN NOT NULL DEFAULT FALSE,
    status          reference_status NOT NULL DEFAULT 'not_started',
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- Agentic workflow state
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS workflow_run (
    run_id          UUID PRIMARY KEY,
    candidate_id    TEXT REFERENCES candidate(candidate_id) ON DELETE SET NULL,
    source_file     TEXT,
    status          run_status NOT NULL DEFAULT 'running',
    readiness_score INTEGER CHECK (readiness_score BETWEEN 0 AND 100),
    llm_used        BOOLEAN NOT NULL DEFAULT FALSE,
    question        TEXT,
    answer          TEXT,
    result_json     JSONB,
    error           TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_workflow_run_candidate ON workflow_run (candidate_id, started_at DESC);

-- Checkpoint of LangGraph state after every node, for replay and debugging.
CREATE TABLE IF NOT EXISTS workflow_state (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES workflow_run(run_id) ON DELETE CASCADE,
    node_name       TEXT NOT NULL,
    sequence        INTEGER NOT NULL,
    state_json      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, sequence)
);

CREATE INDEX IF NOT EXISTS ix_workflow_state_run ON workflow_state (run_id, sequence);

-- Append-only audit trail for every agent / node / LLM / MCP / A2A interaction.
CREATE TABLE IF NOT EXISTS agent_audit_log (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL,
    candidate_id    TEXT,
    event_type      TEXT NOT NULL,
    node_name       TEXT,
    agent_name      TEXT,
    status          TEXT NOT NULL DEFAULT 'ok',
    message         TEXT,
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    duration_ms     INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_audit_run       ON agent_audit_log (run_id, id);
CREATE INDEX IF NOT EXISTS ix_audit_candidate ON agent_audit_log (candidate_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_audit_event     ON agent_audit_log (event_type);

-- ---------------------------------------------------------------------
-- Capability outputs
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS readiness_assessment (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES workflow_run(run_id) ON DELETE CASCADE,
    candidate_id    TEXT,
    score           INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    highest_priority_action TEXT,
    rule_breakdown  JSONB NOT NULL DEFAULT '{}'::jsonb,
    requirements    JSONB NOT NULL DEFAULT '[]'::jsonb,
    narrative       TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS work_experience_evaluation (
    id                  BIGSERIAL PRIMARY KEY,
    run_id              UUID NOT NULL REFERENCES workflow_run(run_id) ON DELETE CASCADE,
    candidate_id        TEXT,
    qualifying_months   NUMERIC(6,1) NOT NULL DEFAULT 0,
    completion_pct      INTEGER NOT NULL DEFAULT 0,
    confidence          NUMERIC(3,2) NOT NULL DEFAULT 0,
    escalation_recommended BOOLEAN NOT NULL DEFAULT FALSE,
    evaluation_json     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS action_plan (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES workflow_run(run_id) ON DELETE CASCADE,
    candidate_id    TEXT,
    horizon_days    INTEGER NOT NULL DEFAULT 90,
    summary         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS action_item (
    id              BIGSERIAL PRIMARY KEY,
    plan_id         BIGINT NOT NULL REFERENCES action_plan(id) ON DELETE CASCADE,
    external_id     TEXT NOT NULL,
    month           INTEGER NOT NULL CHECK (month BETWEEN 1 AND 3),
    title           TEXT NOT NULL,
    detail          TEXT,
    category        TEXT,
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (plan_id, external_id)
);

CREATE TABLE IF NOT EXISTS recommendation (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES workflow_run(run_id) ON DELETE CASCADE,
    candidate_id    TEXT,
    kind            TEXT NOT NULL,
    title           TEXT NOT NULL,
    reason          TEXT,
    url             TEXT
);

-- ---------------------------------------------------------------------
-- Convenience view: latest run per candidate
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_latest_run AS
SELECT DISTINCT ON (candidate_id)
       run_id, candidate_id, source_file, status, readiness_score, started_at, completed_at
FROM   workflow_run
ORDER  BY candidate_id, started_at DESC;
