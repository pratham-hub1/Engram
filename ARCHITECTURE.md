---
## Document Governance

**Status:** Mostly Immutable
**Purpose:** Defines the system architecture, component responsibilities, data flows, and architectural rules.
**Owner:** Human (architecture decisions only)
**AI May Modify:** No — never automatically. Only if explicitly instructed after a real architectural change.

**Update Policy:**
- Read every session before working on any component.
- Never modify because implementation details or code changed.
- Never modify to reflect refactors that preserve the existing architecture.
- Only update if a component is added, removed, or if a data flow genuinely changes.
- Component boundaries defined here are hard rules, not suggestions.

**Modification Checklist (run before editing):**
> Did the actual system architecture change? (new component, removed component, changed data flow)
> If NO — do not touch this document.

---

# ARCHITECTURE.md

# Architecture

## High-Level Vision

The product is a local-first background memory system that continuously builds
an evolving understanding of a developer's project.

The LLM is not the source of truth.

Cognee is the source of truth.

The LLM is only used when structured understanding needs to be extracted from raw signals.

---

# High-Level Architecture

```
                        Developer

                            │
                   Works Normally
                            │
          ┌─────────────────────────────────┐
          │         Observer Service         │
          │   (passive, never interprets)    │
          └─────────────────────────────────┘
                            │
               File Events / Git Events /
               Project Metadata
                            │
          ┌─────────────────────────────────┐
          │        Event Intelligence        │
          │    (filters signal from noise)   │
          └─────────────────────────────────┘
                            │
                  Meaningful Events Only
                            │
          ┌─────────────────────────────────┐       Manual Note
          │        Memory Pipeline           │◀────────────────
          │                                  │  (bypasses Observer)
          │  ┌──────────────────────────┐    │
          │  │    Event Normalizer       │    │
          │  ├──────────────────────────┤    │
          │  │      Deduplicator        │    │
          │  ├──────────────────────────┤    │
          │  │    LLM Extraction        │    │
          │  ├──────────────────────────┤    │
          │  │   cognee.remember()      │    │
          │  └──────────────────────────┘    │
          └─────────────────────────────────┘
                            │
                      LLM Provider
                  (Nvidia nemotron-3-super-120b-a12b default)
                            │
          ┌─────────────────────────────────┐
          │         Cognee Memory            │
          │                                  │
          │  remember() / recall()           │
          │  improve()  / forget()           │
          │                                  │
          │  Knowledge Graph + Vector Memory │
          └─────────────────────────────────┘
                            │
               improve() runs on schedule
               forget() runs on request
                            │
          ┌─────────────────────────────────┐
          │       Memory Orchestrator        │
          │                                  │
          │  Builds retrieval requests       │
          │  Calls cognee.recall()           │
          │  Merges + ranks results          │
          │  Returns normalized output       │
          └─────────────────────────────────┘
                    │               │
                    │               │
             ┌──────┴──┐      ┌────┴──────┐
             │Dashboard│      │ MCP Server│
             │         │      │           │
             │Formats  │      │Formats    │
             │for human│      │for AI     │
             └─────────┘      └───────────┘
```

---

# Component Responsibilities

## 1. Observer Service

Runs continuously in the background.

Responsible for detecting meaningful project activity.

Observed signals:

- Git commits
- File creation and deletion
- File modifications
- Documentation updates
- Dependency changes
- Configuration updates

The Observer never understands anything.

It only observes.

Manual notes bypass this component entirely.

---

## 2. Event Intelligence

Not every filesystem event deserves memory.

This component filters signals before they reach the pipeline.

### Ignore

- Build folders (`dist/`, `build/`)
- Caches (`__pycache__/`, `.cache/`)
- Temporary files
- `node_modules/`
- Generated files
- Formatter-only changes (whitespace, style)

### Keep

- README and documentation updates
- Architecture-level file changes
- New feature implementation
- Config modifications
- Dependency additions or removals
- Git commits

Only meaningful events move forward.

---

## 3. Memory Pipeline

Transforms raw events into structured knowledge.

Responsibilities:

- Normalize events into a standard format
- Deduplicate events (prevent redundant `remember()` calls for repeated saves)
- Extract metadata
- Decide whether LLM processing is required
- Call `cognee.remember()`

### Pipeline Stages

The pipeline has two paths after deduplication. LLM is only invoked when reasoning extraction is the goal.

```
                    Event
                      │
                Normalizer
                      │
                Deduplicator
                      │
         Has reasoning to extract?
         (reasoning language in commit,
          or Tier 2 manual note)
                      │
          YES ─────────────────── NO
          │                        │
   LLM Interpretation        cognee.remember()
   (extract why + summary)   directly, no LLM
          │                        │
   cognee.remember()         cognee.remember()
```

**Event Normalizer** — standardizes raw events into a uniform internal format. For structural changes, it wraps raw git diffs in natural language templates.
- **Matrix Vision (AST Dependency Extractor):** For modified `.py`, `.js`, and `.ts` files on Git Commits, it uses lightweight regex to extract `import/require` statements and injects them as English structural edges (e.g., "File auth.py imports database.py"). Cognee natively translates this into physical graph edges without needing heavy AST parsers.

**Deduplicator / State Manager** — prevents redundant ingestion. 
- Uses content hashing to drop duplicate saves.
- **CRITICAL:** When a file changes, it looks up the old `data_id` in SQLite, and calls `cognee.forget()` on the old state *before* allowing the new state into the pipeline. This prevents stale state accumulation in the graph.

**LLM Interpretation** — runs ONLY when reasoning extraction is the goal:
- Commit message contains explicit reasoning language, or event is a Tier 2 manual decision note. 
- **Ticking Time Bomb Debt:** If a `#expires:YYYY-MM-DD` tag is detected in a manual note or commit, it is parsed and stored in the SQLite metadata column. This powers the `/prune` capability.
For structural changes (dependency added, config modified, module deleted), the structured event from the Normalizer is passed directly to `cognee.remember()`. Cognee's own internal LLM handles entity extraction during ingestion. No double-processing. 
The event's type is preserved via metadata to allow filtering during retrieval.

**cognee.remember()** — the final stage. Structured knowledge enters the graph.

Raw events never enter memory directly.

Only structured knowledge enters memory.

### Why Capture — Reasoning Extraction Rule

During LLM Extraction, one additional rule applies to every git commit:

**If the commit message contains explicit reasoning language** — "because," "since,"
"instead of," "replace," "migrate," "avoid," "due to" — extract it as a
high-confidence decision note and store via `cognee.remember()` with decision metadata.

**If no reasoning language is present**, record only the structural change.
Make no "why" claim. Never fabricate intent.

**Nudge Queue — Expanded Trigger:**

The nudge queue triggers on any high-signal project event with no confirmed reason,
not only on bad commit messages. A confirmed reason exists if a Tier 2 note
or commit message extraction for the same file path or module was recorded within
the last 24 hours (checked via SQLite — no `recall()` required).

High-signal event types that trigger the nudge queue:
- Dependency file changes (`package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, etc.)
- Configuration file changes (`docker-compose.yml`, CI/CD files, auth config, environment config)
- Module or directory creation or deletion

Not in scope for nudge triggering:
- README or documentation updates (these ARE the recorded reason — processed as Tier 1 signal)
- Large diff size (threshold is subjective and unreliable)

The Memory Health view surfaces nudge queue items as a single non-blocking count.
No inference is stored. No confirmation is required. The developer may respond or ignore.

**Optional git commit hook** — developers may install a lightweight hook that prompts
for a reason immediately after committing, when the decision is fresh:

```bash
$ git commit -m "Switch auth to JWT"
Engram: Architectural change detected. Reason? (Enter to skip):
> Chose JWT because Firebase has no offline mode
✓ Decision captured.
```

If skipped, normal Tier 1 processing continues unchanged.
The hook is never required. The product functions fully without it.

---

## 4. LLM Provider Layer

Responsible only for extracting understanding from raw content.

Extracted concepts:

- Entities
- Relationships
- Intent
- Architectural changes
- Decision summaries

The provider is an abstraction.

Business logic never depends on a specific model.

### Supported Providers

| Provider | Model | Status |
|---|---|---|
| Nvidia | nemotron-3-super-120b-a12b | Default (via AI Gateway) |
| Cognee Cloud (included models) | — | Available if included |
| OpenAI | — | Supported |
| Ollama | — | Future (offline/local) |

The default model is **nemotron-3-super-120b-a12b**, accessed via our local proxy gateway.
Flash has significantly higher free-tier rate limits.
Cognee makes its own LLM calls during `remember()` and `improve()`.
Those calls share the same Nvidia quota as our pipeline's extraction calls.
Using Flash minimises quota exhaustion risk.

No LLM costs should be incurred during development or demo.

---

## 5. Cognee Memory Layer

The permanent memory. The source of truth.

### Local Backend (default, no extra setup required)

| Store | Backend | Purpose |
|---|---|---|
| Relational | SQLite (embedded) | Document metadata, system state |
| Vector | LanceDB (embedded) | Embeddings, semantic search |
| Graph | KuzuDB (embedded) | Entities and relationships |

All three run inside the Python process. No Docker, no external services.
Data stored in `.cognee_system/` directory.

### API Usage Rules

**Unified Dataset Rule**
- To prevent Knowledge Graph fracturing, **every project uses exactly ONE unified dataset** (e.g., `dataset_name="engram_core"`). 
- Do not split commits and decisions into separate datasets.

**`remember()`**
- Always set `self_improvement=False` — we control improve() timing.
- Run `remember()` inside an application-level async background task. Wait for the `RememberResult` to complete to synchronously extract the generated `data_id`.
- Always set the unified `dataset_name`.
- Store the extracted `data_id` UUID (`result.items[0]['id']`) in our SQLite log immediately.
- Accepts a `List` for bulk ingestion (used during initial indexing).

**`recall()`**
- Results are pre-ranked by `importance_weight` (updated by `improve()`). No re-ranking needed.
- Pass `datasets=["engram_core"]` to query the unified project graph.
- Since `recall()` does not natively filter by category, the Memory Orchestrator filters results post-retrieval based on document prefixes or SQLite metadata mappings.
- Use `query_type` to select retrieval strategy (must pass Enum, e.g., `SearchType.VECTOR`, not strings):

| Query Intent | Strategy | query_type (Enum) |
|---|---|---|
| "Why did we choose X?" | Deep traversal | `SearchType.GRAPH_COMPLETION` |
| "What changed last week?" | Semantic match | `SearchType.VECTOR` |
| General project question | Broad search | `SearchType.HYBRID` (if supported, else VECTOR) |

**`improve()`**
- Runs ONCE globally on the unified dataset, discovering relationships between all categories of data.
- Triggered explicitly only: once after initial indexing + every 60 minutes on schedule.
- Heavy operation (minutes, not milliseconds) — always run as async background task.

**`forget()`**
- Target individual documents by `data_id` UUID (retrieved from our SQLite log).
- Cascades automatically: removes chunks, embeddings, and derived graph nodes/edges for that document without dropping the dataset.
- **Race condition rule:** batch deletions — never immediately re-ingest overlapping vectors after forgetting.

Removing Cognee removes the product.

---

## 6. Memory Orchestrator

The bridge between the application and Cognee's retrieval layer.

Cognee owns retrieval and ranking. The Memory Orchestrator owns query construction and output formatting.

Responsibilities:

- Determine correct `SearchType` enum based on query intent
- Call `cognee.recall()` on the unified dataset
- Filter retrieved results post-retrieval based on query intent (e.g., filtering out commits if the user asked only for decisions)
- Format normalized output for downstream consumers

The Memory Orchestrator does NOT re-rank results.
Cognee returns results pre-ranked by `importance_weight`. Trust that ranking.

The Memory Orchestrator never stores memory.
The Memory Orchestrator never renders UI.
The Memory Orchestrator never generates AI-facing prompts directly.

It provides normalized memory results. Consumers format independently.

---

## 7. Dashboard

Human interface.

Purpose: Allow the developer to understand their project instantly.

The dashboard formats the Memory Orchestrator's normalized output for human consumption.

Views:

- Project Overview
- Ask Your Project (recall interface)
- Recent Decisions
- Architecture Evolution
- Current Focus
- Memory Timeline
- Memory Summary Graph
- Memory Health

The dashboard never edits memory directly.

It only visualizes memory. To achieve real-time streaming effects for the Multi-Hop Detective, the Dashboard utilizes a **staggered UI theater effect**, rendering the static `reasoning_path` array sequentially without backend SSE load. The `MemorySummaryGraph` view uses D3 to visualize the deterministic subgraph provided by `/api/graph/summary`.

**Memory Health data sources:**
- All stats (memory count by node_set, last improve() timestamp, nudge queue, skip counts)
  come from our own SQLite log — not from Cognee's internal databases.
- Cognee's internal stores (SQLite/LanceDB/KuzuDB) are embedded and not queried directly.

---

## 8. MCP Server

Universal AI interface.

Instead of integrating separately with every AI tool,
the product exposes one MCP server.

Compatible AI assistants retrieve project memory automatically
by calling the appropriate MCP tool.

This solves cross-tool context loss.

No manual context transfer.

No copy-paste.

One shared project memory backend.

The MCP Server formats the Memory Orchestrator's normalized output for AI assistant consumption.

### MCP Tools Exposed

| Tool | Input | Returns |
|---|---|---|
| `recall_context` | `query: str` | Relevant memories with sources and timestamps |
| `get_project_summary` | — | Current project state: stack, decisions, recent changes |
| `add_decision` | `text: str` | Stores a Tier 2 decision note, returns confirmation |
| `get_recent_changes` | `days: int` | Timeline of project changes over N days |

---

# Core Data Flows

## Flow 1 — Automatic Tier 1 Capture

```
Developer makes a git commit
  → Observer detects new commit
  → Event Intelligence confirms it is meaningful
  → Memory Pipeline:
      Normalizer produces structured event (type, diff, metadata, evidence)
      Deduplicator confirms it is new
      ─ Reasoning language in commit message?
          YES → LLM Interpretation → cognee.remember() node_set="decisions"
          NO  → cognee.remember() directly  node_set="commits"
  → Knowledge graph evolves
```

## Flow 2 — Manual Tier 2 Decision Note

```
Developer runs: memory note "Chose JWT for offline support"
  → Bypasses Observer and Event Intelligence entirely
  → Enters Memory Pipeline directly
      Normalizer formats as decision record
      Deduplicator confirms it is new
      cognee.remember() stores with decision metadata
  → Returns confirmation
```

## Flow 3 — Recall via Dashboard

```
Developer types: "Why did we choose JWT?"
  → Dashboard sends query to Memory Orchestrator
  → Orchestrator builds retrieval request
  → cognee.recall() traverses knowledge graph
  → Orchestrator returns normalized results
  → Dashboard formats and renders with source labels:
      [Retrieved Fact] vs [AI Interpretation]
```

## Flow 4 — Recall via MCP (AI Assistant)

```
AI assistant needs project context
  → Invokes MCP tool: recall_context("authentication approach")
  → MCP Server calls Memory Orchestrator
  → Orchestrator calls cognee.recall()
  → MCP Server formats result for AI assistant consumption
  → AI assistant uses context without developer intervention
```

## Flow 5 — Scheduled Memory Improvement (The Dream Cycle)

```
Scheduled interval reached (default: every 60 minutes) OR manually triggered via POST /api/memory/improve
  → cognee.improve() runs as background asyncio task
  → Strengthens graph relationships
  → Organizes accumulated knowledge
  → Removes redundancy
  → Does not block API or observer
  → Skipped if a previous improve() is still running
```

## Flow 6 — Why Capture (Commit Reasoning)

```
Commit arrives at Memory Pipeline after Deduplicator
  │
  ├── Reasoning language found in commit message?
  │     YES → LLM Interpretation → cognee.remember() node_set="decisions" (source: commit hash)
  │     NO  → cognee.remember() directly, node_set="commits". No "why" claim made.
  │
  └── High-signal event with no confirmed reason?
        (dep change / config change / module creation or deletion)
        YES → SQLite nudge queue (non-blocking). No inference stored.
        NO  → nothing

Optional git hook path (if installed by developer):
  Developer commits
  → Hook prompts: "Reason? (Enter to skip)"
  → If provided: enters Memory Pipeline as Tier 2 note → LLM Interpretation path
  → If skipped: structural path continues normally
```

## Flow 7 — Multi-Hop Detective (Root Cause Analysis)

```
Developer triggers /api/memory/root-cause with symptom: "auth is failing"
  → Hop 1: Orchestrator calls cognee.recall(SearchType.CHUNKS_ONLY)
      Returns raw code chunks related to "auth"
  → Hop 2: Orchestrator calls cognee.recall(SearchType.GRAPH_COMPLETION) 
      Prompts: "Based on these files, what decisions govern them?"
  → Returns highly contextualized architectural root cause linking code to intent
```

## Flow 8 — Ticking Time Bomb Debt (Surgical Prune)

```
Developer runs /api/memory/prune
  → SQLite queried for all logs where metadata->>'expires_at' is past today
  → For each expired data_id:
      cognee.forget(data_id) executes, purging vector chunks and edges
      SQLite log row is deleted
  → Graph is instantly cleansed of expired technical debt
```

## Flow 9 — Hackathon Deterministic Visualizations

```
Developer requests Memory Summary Graph
  → Dashboard calls /api/graph/summary
  → Backend queries application SQLite log for recent deterministic structural events
  → Builds a fast D3-compatible JSON payload of core nodes + edges
  → Completely bypasses Cognee's internal KuzuDB export (prevents massive payload lockups)
  → Dashboard renders D3 Force simulation in <0.1s
```

---

# Architectural Rules

1. The Observer never interprets. It only observes.

2. Event Intelligence never stores memory. It only filters.

3. The Memory Pipeline never answers questions. It only ingests.

4. Cognee owns memory. Nothing else does.

5. The Memory Orchestrator owns retrieval orchestration. It never stores.

6. The Dashboard only visualizes. It never edits memory.

7. The MCP Server exposes memory to external AI tools. It never owns memory.

8. Manual notes bypass the Observer. They enter at the Memory Pipeline.

9. The Memory Orchestrator returns normalized output. Consumers format independently.

10. The LLM Provider is an abstraction. No business logic depends on a specific model.

11. Unconfirmed inferences never enter Cognee. Uncertain "why" data stages in SQLite until confirmed by the developer or discarded.

12. LLM Extraction never fabricates a "why" that is not present in available signals. If no reasoning is found, none is recorded.

13. The git commit hook is optional. The product functions fully without it. It is never a required step.

14. Every `remember()` call must set `self_improvement=False`. `improve()` is controlled exclusively by the application scheduler.

15. Every project must use exactly ONE unified dataset. Do not fracture the knowledge graph into multiple datasets per project.

16. The `data_id` UUID (extracted from the awaited `RememberResult`) must be stored in the application SQLite log immediately. This is required for `forget()` capability.

17. When using custom OpenAI-compatible models, `LITELLM_TOKENIZER="cl100k_base"` must be set in the environment to prevent tokenizer mapping errors.

18. Memory Health stats are derived from the application's own SQLite log. Cognee's internal embedded databases (SQLite, LanceDB, KuzuDB) are never queried directly.

Every component has exactly one responsibility.

No component may cross its defined boundary.

