---
## Document Governance

**Status:** Living Document
**Purpose:** Compressed working memory for AI coding sessions. Provides fast project context without requiring full document reads.
**Owner:** AI (with human oversight)
**AI May Modify:** Yes — when a phase changes, a significant engineering decision is made, or architectural clarification occurs.

**Update Policy:**
- Read this file first, every session, before anything else.
- Update when the current implementation phase changes.
- Update when a significant engineering decision, blocker, or architectural clarification occurs.
- Do not store complete project history here. That belongs in Git.
- Do not duplicate information already stable in other documents.
- Keep this document under approximately 10 KB.
- Older implementation notes should be removed as the project progresses.

**Modification Checklist (run before editing):**
> Did the implementation phase change? → Update phase status.
> Was a significant engineering decision made? → Add to Current Decisions.
> Did the architecture change? → Update Architecture Snapshot and notify human.
> Is this document approaching 10 KB? → Trim older, resolved entries.
> For anything else → Do not modify.

**Global Documentation Rule (applies to ALL project documents):**
Before modifying any document in this project, evaluate:
1. Did the product philosophy change? → If NO, do not touch PRODUCT_PRINCIPLES.md.
2. Did the product scope or MVP change? → If NO, do not touch PRODUCT_SPEC.md.
3. Did the architecture actually change? → If NO, do not touch ARCHITECTURE.md.
4. Was a phase completed or reprioritized? → If YES, update IMPLEMENTATION_PLAN.md.
5. Was a significant engineering decision made? → If YES, update CODEBASE_MEMORY.md.

---

# CODEBASE_MEMORY.md

# Project Memory

This document is the primary context file for AI coding assistants.

Read this file first, before any other project document.

It is intentionally concise. It is a compressed snapshot of the project state, not full documentation.

Do not store implementation details here.

Update only when architecture, scope, or phase changes.

---

# Project Status

**Current Phase:** Phase 9 — Polish

**Overall Progress:** Phase 8 Completed (Dashboard built with React/Vite, Vanilla CSS Neural Cortex theme, 8 views, and God Mode)

**Last Updated:** 2026-07-02

---

# Product Mission

Build a local-first AI memory layer that continuously understands software projects,
preserves project knowledge over time using Cognee, and makes that understanding
instantly available to both developers and AI assistants.

Memory is the product.

Continuity is the goal.

---

# Core Problem

Developers repeatedly lose project understanding because knowledge becomes fragmented across:

- AI conversations
- Development sessions
- Time gaps
- Different AI assistants and tools

The goal is not better code generation.

The goal is continuity.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Memory engine | Cognee |
| LLM provider | Nvidia nemotron-3-super-120b-a12b and nv-embed-v1 (via local proxy gateway) |
| File watching | watchdog |
| Git operations | gitpython |
| Observer state | SQLite via aiosqlite |
| CLI | Typer |
| MCP server | mcp Python SDK (SSE transport) |
| Frontend | React + Vite |
| Styling | Vanilla CSS |

---

# Architecture Snapshot

```
Developer
  │
  ├── Works normally
  │       │
  │   Observer Service
  │       │
  │   Event Intelligence (filters noise)
  │       │
  │   Memory Pipeline
  │   (Normalizer → Deduplicator → LLM Extraction → remember())
  │       │
  │     Cognee
  │   (remember / recall / improve / forget)
  │       │
  │   Memory Orchestrator
  │   (orchestrates retrieval, returns normalized output)
  │      / \
  │     /   \
  │ Dashboard  MCP Server
  │ (human)    (AI assistants)
  │
  └── Writes manual note
          │
      Memory Pipeline (direct entry, bypasses Observer)
          │
        Cognee
```

---

## Phase 7: Decision Capture (Tier 2 bypass) [COMPLETED]
**Goal:** Expose endpoints for the explicit decision recording workflows.

**Steps:**
1. ✅ **Implement REST API:** Created `POST /api/notes` in `backend/api/routes.py` and `GET /api/health/nudges` to surface queue.
2. ✅ **Handle MANUAL_NOTE events:** Handled in `backend/pipeline/normalizer.py` to correctly wrap them into `StructuredEvent`. Updated `processor.py` to change `GIT_COMMIT` to `GIT_COMMIT_WITH_REASON` to accurately log them.
3. ✅ **Implement CLI command:** Built `cli/main.py` using `typer` to send notes to `POST /api/notes`.
4. ✅ **Implement Git hook installer:** Added `memory install-hook` in `cli/main.py`.
5. ✅ **Add MCP `add_decision` tool:** Added to `backend/mcp_server.py`.
6. ✅ **Finalize Nudge Queue Suppression:** Updated `has_recent_decision` in `backend/db/state.py` to suppress nudges if any `MANUAL_NOTE` or `GIT_COMMIT_WITH_REASON` was logged in the last 24 hours.

**Key Design Decisions:**
- Manual notes are normalized directly as `MANUAL_NOTE` events, bypassing the file observer, to ensure accurate decision capture.
- Nudge suppression checks globally across all paths for recent manual decisions, offering a better developer experience (i.e. "I already explained my reasoning today").
- Memory Pipeline stages: Normalizer → Deduplicator → two paths:
  - Reasoning to extract (reasoning language or Tier 2 note) → LLM Interpretation → `cognee.remember()` node_set="decisions"
  - Structural change only → `cognee.remember()` directly, no LLM, correct node_set
- Deduplicator prevents redundant `remember()` calls using content hashing + SQLite log.
- Initial indexing runs on first project registration: backfills last 50 commits and existing docs/deps.

## Phase 8: Advanced Cognee Integrations & Dashboard [COMPLETED]
**Goal:** Deep mathematical exploitation of the graph + Visual project understanding.

**Steps:**
1. ✅ **Advanced Endpoints:** Exposed `/api/memory/improve` (Dream Cycle), `/api/memory/root-cause` (Multi-hop), and `/api/memory/prune` (Surgical debt deletion).
2. ✅ **Matrix Vision:** Implemented lightweight Regex Dependency Extractor in `normalizer.py` to ingest structural AST edges automatically on commit.
3. ✅ **Ticking Time Bomb Debt:** Updated `extractor.py` and `state.py` to parse and track `#expires:YYYY-MM-DD` tags for instantaneous pruning.
4. ✅ **UI Shell:** React + Vite initialized. Vanilla CSS with "Neural Cortex" aesthetic.
5. ✅ **Components:** GlassCard and Sidebar components built.
6. ✅ **API Integration:** Created `api/client.js` wrapping all endpoints.
7. ✅ **Core Views:** `ProjectOverview`, `AskYourProject` (Command Palette), `RecentDecisions`, `ArchitectureEvolution`, `CurrentFocus`, `MemoryTimeline` built to render data from `/api/query`.
8. ✅ **Advanced Views:** `MemorySummaryGraph` built using `d3-force` for a dynamic network visualization. `MemoryHealth` built with God Mode controls (Improve, Prune, Root Cause).
9. ✅ **Hackathon Visualizations:** Added the `/api/graph/summary` deterministic subgraph endpoint. Implemented the staggered Zero-Load Reasoning Trace animation in the frontend.

**Key Design Decisions:**
- Pure Vanilla CSS used to maintain ultimate control over the glassmorphism and glow effects.
- d3-force physics simulation is used to provide the "Crazy Cognee" vibe for the graph without interactive dependencies. The graph relies on `/api/graph/summary`, which deterministically builds a fast subgraph from the SQLite `memories_log` (last 30 organic modifications) to completely avoid browser lockups and heavy backend load.
- Zero technical debt approach to AST parsing: used standard regex string formatting (`File A imports File B`) to naturally teach Cognee the edges without external parsers.
- **Theater Effect over SSE:** To showcase multi-hop reasoning without rewriting the backend to support SSE streaming, the backend `AskYourProject` endpoint returns an explicit `reasoning_path` array. The frontend (`AskYourProject.jsx`) staggers the visual rendering of these nodes artificially to create a real-time "thinking" animation with exactly zero backend processing cost.

---

# Current Decisions

## Memory Architecture
- Cognee is the source of truth. Nothing else owns memory.
- Two-tier capture: Tier 1 automatic observation, Tier 2 manual decision notes only.
- Observer is passive. It never interprets.
- Manual notes bypass the Observer entirely. They enter at the Memory Pipeline.
- Memory Pipeline stages: Normalizer → Deduplicator → two paths:
  - Reasoning to extract (reasoning language or Tier 2 note) → LLM Interpretation → `cognee.remember()` node_set="decisions"
  - Structural change only → `cognee.remember()` directly, no LLM, correct node_set
- Deduplicator prevents redundant `remember()` calls using content hashing + SQLite log.
- Initial indexing runs on first project registration: backfills last 50 commits and existing docs/deps.

## Why Capture
- Commit messages with explicit reasoning language are extracted as confirmed decision notes. No fabrication.
- Commit messages without reasoning produce structural change records only. No "why" claim made.
- Nudge queue triggers on high-signal events (dep changes, config changes, module creation/deletion)
  with no confirmed reason — not only on bad commit messages.
- Confirmed reason check: SQLite lookup (Tier 2 notes or commit extractions for same path, last 24h). No `recall()`.
- README and docs changes are NOT nudge triggers — they are the recorded reason, processed as Tier 1.
- Unconfirmed inferences never enter Cognee. Uncertain data stays in SQLite only.
- Optional git commit hook (`memory install-hook`) prompts at commit time. Never required.

## Retrieval Architecture
- Memory Orchestrator owns query construction and output formatting. Cognee owns retrieval and ranking.
- `recall()` returns results pre-ranked by `importance_weight`. Memory Orchestrator does NOT re-rank.
- `recall()` uses `node_set` for category scoping and `query_type` for strategy selection.
- Dashboard formats for humans. MCP Server formats for AI assistants.
- One retrieval system. Two interaction surfaces.

## Cognee Usage Rules
- Unified Dataset Rule: Every project uses exactly ONE unified dataset to ensure a connected knowledge graph. Do not fracture datasets.
- Every `remember()` call's `data_id` UUID (extracted from the awaited `RememberResult`) must be stored in SQLite log immediately. (Note: `node_set` parameter was removed from Cognee 1.2.2 API, so we rely on Semantic Normalizer tags).
- `improve()` runs globally on the unified dataset. Triggered explicitly only: once after initial indexing + every 60 min. Never automatic.
- `forget()` targets by `data_id` UUID from SQLite log. Cascades automatically.
- Bulk forget: query SQLite by metadata → iterate UUIDs. Batch deletions — race condition risk on rapid re-ingest.
- Cognee local backend: SQLite (relational) + LanceDB (vector) + KuzuDB (graph). All embedded, no Docker.
- Memory Health stats come from application SQLite log only. Never query Cognee's internal databases directly.

## Trust and Explainability
- Retrieved facts and AI interpretations must always be visually distinguished.
- Never present synthesized summaries as historical facts.
- Every memory must be traceable to its origin source.
- LLM Extraction never fabricates a "why" not present in available signals.

## Cross-Tool Continuity
- MCP Server is the universal AI interface. No per-tool integrations.
- Any MCP-compatible AI assistant connects to the same project memory.

## Infrastructure
- Local-first. Project data stays on the developer's machine.
- External calls only for LLM processing (Nvidia models). Cognee also makes LLM calls during remember() and improve() — same quota.
- Zero cost constraint. No paid APIs during development or demo.
- One Cognee dataset per project, keyed by project directory path.
- Pipeline failures write to a SQLite retry queue. Three retries with backoff. Skip counts in Memory Health.

## Dashboard
- Dashboard is read-only. It never edits memory.
- Visual graph exploration is achieved via the `MemorySummaryGraph` using D3 force simulation pulling from the optimized `/api/graph/summary` endpoint.
- Reasoning traces in the UI use a "theater effect" (staggered local animation) to parse the `reasoning_path` array from the backend, simulating SSE without backend load.
- Memory Health shows: indexing status, skip counts, nudge queue, last improve() timestamp.

---

# Current Scope

## MVP Includes

- Background observer service
- Memory pipeline with deduplication
- Cognee memory integration
- MCP server (four tools)
- Manual decision notes (CLI + API)
- Dashboard (eight views)

## Out of Scope

- IDE extensions
- Team collaboration
- Cloud sync
- Visual graph exploration
- Advanced authentication
- Multi-project UI management (architecture supports it, UI does not)
- Enterprise features

---

# Implementation Phase Order

```
Phase 0 — Validate Foundation       (spikes only, no production code)
Phase 1 — Project Foundation
Phase 2 — Observer Service
Phase 3 — Memory Pipeline
Phase 4 — Cognee Integration
Phase 5 — Memory Orchestrator
Phase 6 — MCP Server                (before Dashboard — core differentiator) (COMPLETED)
Phase 7 — Decision Capture          (CLI note + git hook + nudge queue)
Phase 8 — Dashboard                 (last — depends on full data layer)
Phase 9 — Polish
```

---

# Coding Principles

- Simplicity over cleverness.
- Small modules with single responsibility.
- No premature optimization.
- Avoid unnecessary abstractions.
- Prefer readable code over compact code.
- Every component has one clear purpose and does not cross its boundary.

---

# AI Assistant Instructions

## Reading Order

Read this file first. Always.

Read other documents only when you need deeper context on a specific topic:

| Document | When to read it |
|---|---|
| `PRODUCT_PRINCIPLES.md` | When making product or UX decisions |
| `ARCHITECTURE.md` | When working on system design or component boundaries |
| `PRODUCT_SPEC.md` | When implementing a specific feature |
| `IMPLEMENTATION_PLAN.md` | When starting or continuing a phase |

## Before Implementing Anything

1. Confirm which phase is currently active.
2. Confirm the component you are working on.
3. Confirm that the component's responsibility is understood.
4. Do not cross component boundaries.
5. Do not introduce dependencies not listed in the technology stack.

## Never Do This

- Do not store memory outside of Cognee.
- Do not make the Dashboard edit memory.
- Do not make the Observer interpret events.
- Do not make the Memory Orchestrator store or re-rank results.
- Do not introduce paid LLM APIs. Use the provided Nvidia API endpoints only.
- Do not skip the Deduplicator stage in the Memory Pipeline.
- Do not call `remember()` without `self_improvement=False` and `node_set`.
- Do not call `improve()` automatically — explicit schedule only.
- Do not query Cognee's internal databases (SQLite/.cognee_system, LanceDB, KuzuDB) directly.
- Do not forget() and immediately re-ingest overlapping vectors — race condition risk.
- Do not use `external_metadata` alone for categorisation — use `node_set`.

---

# Updating This File

Update this file when any of these change:

- Current implementation phase
- Major architectural decision
- Product scope
- Technology stack

Do NOT update after every commit.

This is long-term memory, not a changelog.
