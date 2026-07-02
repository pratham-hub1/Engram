---
## Document Governance

**Status:** Living Document
**Purpose:** Tracks implementation progress, phase status, and build priorities across all development sessions.
**Owner:** AI (with human oversight)
**AI May Modify:** Yes — AI may update this document when a phase starts, is completed, or when priorities are officially reprioritized.

**Update Policy:**
- Read every session before writing any code.
- Update the phase status when a phase begins or completes.
- Update priorities if officially reprioritized by the human.
- Do not add new phases without human approval.
- Do not remove phases or success criteria without human approval.
- This is the single source of truth for implementation progress.

**Modification Checklist (run before editing):**
> Was a development phase started, completed, or officially reprioritized?
> If YES — update this document.
> If NO — do not touch this document.

---

# IMPLEMENTATION_PLAN.md

# Implementation Plan

## Objective

Build the product incrementally.

Every phase must produce a working, testable system.

No future phase should begin before the current phase is complete and verified.

Features are layered on top of stable foundations, never built in parallel.

---

# Implementation Principles

- Build foundations before interfaces.
- Working software is preferred over incomplete features.
- Every phase must end in a testable state.
- Avoid premature optimization.
- Do not build placeholder implementations.
- If a dependency is not ready, mock it cleanly instead of blocking progress.
- The MCP Server is a core deliverable, not a bonus feature.
- The Dashboard is built last. It depends on a complete data layer.

---

# Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| Backend runtime | Python 3.11+ | Cognee is Python |
| API framework | FastAPI | Async-native, SSE support |
| ASGI server | Uvicorn | FastAPI standard |
| File watching | watchdog | Cross-platform, mature |
| Git operations | gitpython | Clean Python API |
| Scheduling | asyncio + APScheduler | Lightweight, no broker needed |
| Observer state | SQLite via aiosqlite | Local, zero-setup, persistent |
| CLI | Typer | Thin wrapper over REST API |
| MCP server | mcp Python SDK (SSE) | Standard protocol, multi-client |
| Frontend | React + Vite | Fast to build |
| Styling | Vanilla CSS | No framework overhead |
| LLM provider | Gemini Flash (gemini-1.5-flash) | Zero cost, higher free-tier limits than Pro |
| Memory engine | Cognee | Core dependency |

---

# Phase 0 — Validate the Foundation

## Goal

Verify that all external dependencies work before writing production code.

## No production code in this phase. Spike scripts only.

## Spikes

1. Verify Cognee local or Cloud setup
2. Verify `cognee.remember()` ingests and persists data correctly
3. Verify `cognee.recall()` retrieves relevant results
4. Verify MCP SDK connectivity and tool invocation

## Success Criteria

All four spikes pass.

If any spike fails, resolve the dependency before proceeding.

Do not move to Phase 1 until this phase is complete.

---

# Phase 1 — Project Foundation

## Goal

Establish the project structure and development environment.

## Deliverables

- Project directory structure
- Configuration management (`config.py`, `.env.example`)
- Environment variable loading
- Structured logging
- Shared error handling utilities
- SQLite database initialization for observer state
- Development scripts (`start`, `reset`, `logs`)

## Project Structure

```
memory-ai/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── observer/
│   │   ├── watcher.py
│   │   ├── git_monitor.py
│   │   └── filters.py
│   ├── pipeline/
│   │   ├── normalizer.py
│   │   ├── deduplicator.py
│   │   ├── extractor.py
│   │   └── ingestor.py
│   ├── memory/
│   │   └── cognee_client.py
│   ├── orchestrator/
│   │   └── memory_orchestrator.py
│   ├── mcp_server/
│   │   └── server.py
│   ├── api/
│   │   └── routes/
│   │       ├── status.py
│   │       ├── memories.py
│   │       ├── notes.py
│   │       ├── timeline.py
│   │       └── context.py
│   └── db/
│       └── state.py
├── cli/
│   └── main.py
├── frontend/
│   └── src/
├── pyproject.toml
├── .env.example
└── README.md
```

## Success Criteria

A new contributor can clone the repository and start the project without modifying source code.

---

# Phase 2 — Observer Service

## Goal

Continuously detect meaningful project activity without interpreting it.

## Observed Signals

| Signal | Method | Trigger |
|---|---|---|
| Git commits | watchdog `.git/logs/HEAD` | File modified |
| `.md` file changes | watchdog | Write event after debounce |
| Dependency files | watchdog | `package.json`, `requirements.txt`, `pyproject.toml`, etc. |
| Config files | watchdog | `docker-compose.yml`, `.env.example`, root `*.yml` |
| Structural changes | watchdog | Directory/file creation or deletion |

## Hard Ignore List

```
node_modules/    .git/objects/    __pycache__/
dist/            build/           .venv/
*.pyc            *.log            .DS_Store
```

## Deliverables

- Background file watcher (watchdog integration)
- Git commit monitor (watchdog handler for `.git/logs/HEAD`)
- Event filter (ignore rules)
- Async event queue
- Event logging to SQLite

## Batching Rules

- Git commits: processed immediately (discrete, intentional events)
- File system events: batched in 30-second rolling windows before forwarding

## Success Criteria

Meaningful events are detected reliably.

Noisy events are ignored.

No memory is created in this phase.

The Observer only observes.

---

# Phase 3 — Memory Pipeline

## Goal

Convert raw project events into structured knowledge candidates.

## Pipeline Stages

Two paths after deduplication. LLM only invoked when reasoning extraction is the goal.

```
Event Normalizer → Deduplicator → Reasoning to extract?
                                         │
                              YES ───────── NO
                              │              │
                    LLM Interpretation   cognee.remember()
                              │          directly (no LLM)
                    cognee.remember()    node_set by event type
                    node_set="decisions"
```

**Event Normalizer** — converts all event types into a standard internal format.
Produces a structured event: `{ type, diff, metadata, evidence }`. No AI.

**Deduplicator** — compares content hash against recent ingestion log.
Prevents redundant `remember()` calls for repeated saves of the same content.
Persists the deduplication log across restarts using SQLite. No AI.

**LLM Interpretation** — runs ONLY when reasoning extraction is the goal:
- Commit message contains explicit reasoning language ("because," "since," "instead of,"
  "replace," "migrate," "avoid," "due to") — extract as high-confidence decision note,
  store via `cognee.remember()` with `node_set="decisions"`. Source: commit hash.
- Event is a Tier 2 manual decision note — LLM summarises and stores as decision.

**Direct path (no LLM)** — for all structural events:
- Dependency change → `node_set="dependencies"`
- Config change → `node_set="config"`
- Module creation/deletion → `node_set="modules"`
- Commit with no reasoning → `node_set="commits"`, no "why" claim made

For structural events, the structured output from the Normalizer is passed directly
to `cognee.remember()`. Cognee's own internal LLM handles entity extraction.
No double-processing. No fabrication risk.

**Nudge queue** — if a high-signal event (dep change, config change, module creation/deletion)
has no confirmed reason (SQLite check: last 24h for same path), write to nudge queue in SQLite.
Surface in Memory Health as a non-blocking count.

## Deliverables

- Event normalizer (structured event: type, diff, metadata, evidence)
- Deduplicator with SQLite-backed hash log
- LLM Interpretation stage (Gemini Flash, only for reasoning extraction)
- Direct-path builder for structural events (no LLM)
- Nudge queue writer (SQLite)
- Dry-run mode for testing pipeline output without calling `remember()`

## Pipeline Error Strategy

Failed pipeline events must never cause silent data loss or crash the observer.

- Failed events are written to a SQLite retry queue with failure reason and timestamp.
- The pipeline retries with exponential backoff, up to three attempts.
- After three failures, the event is logged as skipped. Development continues uninterrupted.
- Skip counts are surfaced in the Dashboard's Memory Health view.
- LLM rate limit errors are treated as transient failures and retried with a longer backoff.

## Success Criteria

Every important event becomes a clean structured memory candidate.

The dry-run output can be inspected to verify pipeline correctness without storage.

Deduplication prevents redundant ingestion on repeated file saves.

Commit messages with explicit reasoning produce decision-type memories automatically.

Pipeline failures do not crash the observer or lose events permanently.

---

# Phase 4 — Cognee Integration

## Goal

Persist project knowledge using Cognee.

## Cognee API Configuration

All `remember()` calls must use these parameters without exception:

```python
await cognee.remember(
    data,                          # text, List[str], or DataItem
    dataset_name="<project-id>",   # project-keyed, derived from directory path
    node_set="<category>",         # see node_set taxonomy below
    self_improvement=False,        # explicit improve() control only
    run_in_background=True         # non-blocking
)
# Immediately store returned data_id UUID in SQLite log
```

**node_set taxonomy:**

| Event Type | node_set |
|---|---|
| Architectural decisions | `"decisions"` |
| Git commit changes | `"commits"` |
| Dependency file changes | `"dependencies"` |
| Config file changes | `"config"` |
| Module/directory creation or deletion | `"modules"` |

## Deliverables

- Cognee client wrapper (`cognee_client.py`)
- `remember()` — structured ingestion with node_set, self_improvement=False, run_in_background=True
- `recall()` — knowledge retrieval with node_set scoping and query_type routing
- `improve()` — explicitly scheduled (never automatic); triggered once post-indexing then every 60 min
- `forget()` — targeted deletion by data_id UUID retrieved from SQLite log
- SQLite log table: stores `data_id`, `node_set`, `dataset`, `timestamp` per remember() call

## Dataset Strategy

Each project is assigned a unique dataset ID derived from its directory path.
This isolates project memories and prepares the architecture for future multi-project support
without requiring schema changes.

## Initial Indexing

When a developer first registers a project, the system must backfill existing knowledge.
The observer only captures future changes. Without initial indexing, a project registered
today has zero memory of its past.

Initial indexing runs as a background asyncio task immediately after project registration.
It does not block the observer or API.

**Backfill uses bulk ingestion:** Pass all 50 commits as a single `List` to `remember()`.
Do not iterate with 50 individual calls — one bulk call is more efficient.

**Backfill scope:**
- Last 50 git commits (configurable via environment variable)
- Existing `README.md` and documentation files
- Current `package.json`, `requirements.txt`, `pyproject.toml`, or equivalent
- Existing config files (`.env.example`, `docker-compose.yml`, root-level `*.yml`)

**After backfill completes:** trigger `improve()` explicitly once. It is heavy (takes minutes).
Show progress in Memory Health: "Improving memory graph… this takes a few minutes."

**Progress:** surfaced in the Memory Health dashboard view during indexing.

**Duplicate safety:** the Deduplicator prevents re-ingestion if the project is re-registered.
Cognee also performs structural deduplication internally (merges overlapping graph nodes).

## Success Criteria

Project knowledge persists across application restarts.

Restarting the application does not lose memory.

`improve()` runs on explicit schedule only — never fires automatically.

Initial indexing completes in the background without blocking service startup.

Every `remember()` call's `data_id` is stored in the SQLite log before the call returns.

---

# Phase 5 — Memory Orchestrator

## Goal

Bridge the application and Cognee's retrieval layer.

## Responsibilities

- Determine correct `node_set` and `query_type` based on query intent
- Call `cognee.recall()` with constructed parameters
- Format normalized output for downstream consumers

Cognee returns results pre-ranked by `importance_weight`. The Orchestrator does NOT re-rank.

## Query Routing Table

| Query Intent | node_set | query_type |
|---|---|---|
| "Why did we choose X?" | `"decisions"` | graph-completion |
| "What changed last week?" | `"commits"` | vector |
| General project question | unscoped | hybrid |
| MCP `get_project_summary` | unscoped | hybrid |
| MCP `get_recent_changes` | `"commits"` | vector |
| Dashboard "Recent Decisions" | `"decisions"` | graph-completion |

## Deliverables

- Memory Orchestrator service
- Query builder (intent → node_set + query_type)
- Normalized response formatter

## Success Criteria

The application retrieves relevant project knowledge consistently.

The Orchestrator never stores memory.

Cognee remains the source of truth.

Downstream consumers (Dashboard, MCP) format independently.

---

# Phase 6 — MCP Server

## Goal

Expose project memory to any MCP-compatible AI assistant.

## Rationale for Early Placement

The MCP Server is a core product differentiator.
It is simpler to build than the Dashboard.
If development time runs short, the product must have a working MCP Server.
A product with memory + MCP but no polished dashboard is still a complete product.
A product with a dashboard but no MCP has lost its primary differentiator.

## MCP Tools

| Tool | Input | Returns |
|---|---|---|
| `recall_context` | `query: str` | Relevant memories with sources and timestamps |
| `get_project_summary` | — | Project state: stack, decisions, recent changes |
| `add_decision` | `text: str` | Stores Tier 2 note, returns confirmation |
| `get_recent_changes` | `days: int` | Timeline of changes over N days |

## Transport

SSE (Server-Sent Events) — allows multiple AI clients to connect simultaneously.

## Deliverables

- MCP server (SSE transport)
- Four tool definitions
- Connection to Memory Orchestrator
- Context formatting for AI consumption

## Success Criteria

An AI assistant can retrieve project understanding without any manual context sharing.

All four tools respond correctly.

---

# Phase 7 — Decision Capture

## Goal

Provide every mechanism for capturing architectural decisions that automatic
observation alone cannot reliably infer.

This phase delivers the complete Tier 2 capture surface.

## Tier 2 Mechanisms

### Mechanism 1 — CLI Decision Note

```
Developer runs: memory note "Chose JWT for offline support"
  → Bypasses Observer entirely
  → Enters Memory Pipeline directly
  → cognee.remember() with decision metadata
  → Returns confirmation in under 15 seconds
```

### Mechanism 2 — Optional Git Commit Hook

A lightweight shell hook that prompts for a reason immediately after committing,
when the decision context is freshest.

```bash
$ git commit -m "Switch auth to JWT"
Memory AI: Architectural change detected. Reason? (Enter to skip):
> Chose JWT because Firebase has no offline mode
✓ Decision captured.
```

- Installed once via `memory install-hook` (or manually)
- Completely optional. Product functions fully without it.
- If the developer presses Enter, normal Tier 1 processing continues unchanged.
- Captured reason enters the Memory Pipeline as a Tier 2 decision note.

### Mechanism 3 — Nudge Queue (Memory Health)

The nudge queue triggers on any high-signal project event with no confirmed reason —
not only when commit messages are vague.

**High-signal event types:**
- Dependency file changes (`package.json`, `requirements.txt`, `pyproject.toml`, etc.)
- Configuration file changes (`docker-compose.yml`, CI/CD files, auth/env config)
- Module or directory creation or deletion

**Confirmed reason check (SQLite only, no `recall()`):**
A reason is considered confirmed if a Tier 2 note or commit message extraction
for the same file path or module was recorded in the last 24 hours.
If confirmed: no nudge. If not confirmed: add one item to the nudge queue.

The Memory Health view surfaces the queue as a single non-blocking count:

```
3 significant changes this week with no recorded reason.
Run 'memory notes' to review, or ignore.
```

No inference is stored. No confirmation is required. The developer may respond or ignore.

## Deliverables

- CLI command: `memory note "..."`
- REST endpoint: `POST /api/notes`
- Pipeline integration (enters at normalizer, bypasses deduplicator)
- Cognee ingestion with decision-type metadata
- Git commit hook installer: `memory install-hook`
- Hook script (shell, cross-platform)
- Nudge queue writer in Memory Pipeline
- Nudge queue reader for Memory Health view

## Success Criteria

A developer can record an architectural decision in under 15 seconds via CLI.

The git hook prompts correctly and accepts or skips without error.

Decision notes appear in the Dashboard's "Recent Decisions" view.

Decision notes are retrievable via MCP.

Nudge queue surfaces correctly in Memory Health when high-signal events have no reason.

---

# Phase 8 — Dashboard

## Goal

Allow developers to understand their project instantly through a visual interface.

## Rationale for Late Placement

The Dashboard is the most complex deliverable.
It depends on a complete data layer (Phases 2–7).
Building it last ensures all views have real data to display.

## Dashboard Views

| View | Data Source |
|---|---|
| Project Overview | Memory Orchestrator — hybrid recall, unscoped |
| Ask Your Project | Memory Orchestrator — hybrid recall, user query |
| Recent Decisions | Memory Orchestrator — graph-completion, node_set="decisions" |
| Architecture Evolution | Memory Orchestrator — graph-completion, node_set="commits" |
| Current Focus | Memory Orchestrator — vector recall, node_set="commits" (last 7 days) |
| Memory Timeline | Application SQLite event log (chronological, no recall() needed) |
| Memory Summary Graph | Memory Orchestrator — entity data from Cognee |
| Memory Health | Application SQLite log only — no recall(), no Cognee internal DB queries |

## UI Rules

- Retrieved facts and AI interpretations are always visually distinguished
- Dashboard never edits memory directly
- All views are read-only

## Deliverables

- React + Vite frontend
- All eight dashboard views
- "Ask Your Project" search interface
- REST API integration
- Real-time updates via WebSocket or polling

## Success Criteria

A developer can understand complete project state without opening source code.

---

# Phase 9 — Polish

## Goal

Prepare the product for demonstration.

## Demo Dataset Strategy

> The product's own development history will serve as the primary demo dataset.
> The product will have observed itself being built.
> This is self-demonstrating: the memory system built memory of the product that built it.

## Deliverables

- UI refinement and visual polish
- Empty states for all views
- Loading states and error messages
- Performance improvements where needed
- Documentation cleanup
- End-to-end demo walkthrough script

## Success Criteria

The product feels stable, understandable, and reliable during a live demonstration.

---

# Phase Summary

| Phase | Name | Core Output | Status |
|---|---|---|---|
| 0 | Validate Foundation | All spikes pass | ✅ Complete |
| 1 | Project Foundation | Runnable project scaffold | ✅ Complete |
| 2 | Observer Service | Events detected, noise filtered | 🔄 In Progress |
| 3 | Memory Pipeline | Events → structured memory candidates | ⏳ Pending |
| 4 | Cognee Integration | Memory persists across restarts | ⏳ Pending |
| 5 | Memory Orchestrator | Retrieval working, normalized output | ⏳ Pending |
| 6 | MCP Server | AI assistants retrieve project context | ⏳ Pending |
| 7 | Manual Decision Notes | Decisions captured in under 15 seconds | ⏳ Pending |
| 8 | Dashboard | Visual project understanding | ⏳ Pending |
| 9 | Polish | Demo-ready product | ⏳ Pending |

---

# Out of Scope

Intentionally excluded from the hackathon MVP:

- Multi-user collaboration
- Team workspaces
- Cloud synchronization
- Advanced graph exploration
- Mobile applications
- IDE extensions
- Plugin marketplace
- Authentication platform
- Enterprise RBAC
- Distributed deployments

---

# Definition of Done

The implementation is complete when:

- ✓ Project activity is automatically observed
- ✓ Important events become structured memory
- ✓ Cognee stores and evolves project knowledge
- ✓ Developers can ask questions about their own project
- ✓ AI assistants retrieve the same project understanding through MCP
- ✓ The dashboard clearly explains project evolution
- ✓ The developer never has to manually reconstruct project context
