# Agentic POC Skills — a domain-neutral starter pack

Reusable agent skills and templates for building an **auditable agentic POC** on the stack used by
`../cfa_sdd/` and `../cfa-candidate-onboarding/`: an orchestrated LangGraph workflow, Google A2A
specialist agents, MCP tool-server file access, Pydantic contracts, an optional LLM, PostgreSQL run
auditing, FastAPI and a React client.

Everything here is **domain-independent**. It was extracted from the CFA Candidate-to-Member POC by
stripping the CFA specifics out; those specifics now live in exactly one place per project — the
domain skill you write from `templates/domain-skill-template.md`.

## What's in here

```
agentic-poc-skills/
├── skills/
│   ├── agentic-workflow-langgraph/SKILL.md   # graph wiring, node contract, state, checkpoints
│   ├── a2a-agents/SKILL.md                   # agent cards, JSON-RPC message/send, transport fallback
│   ├── mcp-file-access/SKILL.md              # stdio tool server, path containment, stdout hygiene
│   ├── pydantic-contracts/SKILL.md           # typed contracts and their TypeScript mirrors
│   ├── postgres-run-audit/SKILL.md           # runs, checkpoints, audit events, idempotent DDL
│   ├── llm-narration-boundary/SKILL.md       # deterministic fallback + the rules/generation boundary
│   ├── fastapi-service/SKILL.md              # route surface, error mapping, pydantic-settings
│   ├── react-run-ui/SKILL.md                 # run lifecycle, loading/error/empty states, strict typing
│   └── deployment-config-guard/SKILL.md      # minimal config surface, dependency pinning
├── templates/
│   ├── constitution-template.md              # 5 reusable principles + a stack section to rewrite
│   └── domain-skill-template.md              # the one file you write per project
└── README.md
```

## How to use it for a new POC

1. **Scaffold Spec Kit** in your new project folder:
   ```bash
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.16.0
   specify init . --integration copilot --script sh
   ```
2. **Copy the skills**: `cp -r agentic-poc-skills/skills/* <project>/.github/skills/`
   (or `.claude/skills/` / `.agents/skills/` for other agents).
3. **Write the domain skill** from `templates/domain-skill-template.md` and drop it alongside them.
   This is the only authoring work — it holds the lifecycle, entities, scoring constants,
   classification rules, fixture personas and the advisory boundary.
4. **Write the constitution** from `templates/constitution-template.md`. Keep principles I–V close to
   verbatim; rewrite the Technology Constraints section for your stack. Save it to
   `.specify/memory/constitution.md`.
5. **Adapt the three partially-generic skills** — each carries an explicit `> **Adapt:**` note:
   - `agentic-workflow-langgraph` — record your canonical node sequence.
   - `fastapi-service` — record your concrete route surface.
   - `deployment-config-guard` — record your declared config-file set.
6. **Add a `copilot-instructions.md`** routing agents to the right skill per area, listing your
   features and the quality gates. See `../cfa_sdd/.github/copilot-instructions.md` for a worked
   example.
7. **Write the specs**, then run `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` per feature.

## Reuse map (what came from where)

| Pack skill | Origin in `cfa_sdd/` | Change made |
| --- | --- | --- |
| `pydantic-contracts` | `cfa-pydantic-models` | none beyond naming — was already domain-free |
| `llm-narration-boundary` | `cfa-openai-llm` | generalized "eligibility" to "authoritative determination" |
| `mcp-file-access` | `cfa-mcp-file-access` | tool names shown as a pattern rather than a fixed surface |
| `a2a-agents` | `cfa-a2a-agents` | dropped the three CFA agent names |
| `postgres-run-audit` | `cfa-postgres-audit` | table set reduced to the reusable audit core |
| `agentic-workflow-langgraph` | `cfa-langgraph-workflow` | canonical node list replaced with an adapt note |
| `fastapi-service` | `cfa-fastapi-backend` | CFA route list replaced with a route-shape guideline |
| `react-run-ui` | `cfa-react-ui` | CFA tab list removed; run-consistency rules kept |
| `deployment-config-guard` | `cfa-deployment-config` | the specific three files became a configurable declared set |
| *(not carried over)* | `cfa-poc-domain` | replaced by `templates/domain-skill-template.md` |

## The four ideas worth keeping

If you take nothing else from this pack:

1. **Deterministic rules produce every number; the LLM only narrates.** It makes the product
   reproducible by hand and the AI unambiguously additive rather than load-bearing.
2. **Every node emits audit events and a state checkpoint, and audit failures never fail the run.**
   Retrofitting this is painful; it costs almost nothing up front.
3. **Record the transport actually used on every delegated call.** Without it you cannot distinguish a
   working MCP/A2A integration from one that has silently run on its fallback since day one.
4. **Ship offline-capable from the first commit.** A deterministic fallback for every generated string
   means the demo never depends on an API key, a network, or a rate limit.
