---
## Document Governance

**Status:** Mostly Immutable
**Purpose:** Defines what the product is, what features belong in the MVP, and the core user experience.
**Owner:** Human (scope decisions only)
**AI May Modify:** No — never automatically. Only if explicitly instructed after an official product scope or feature change.

**Update Policy:**
- Read every session before implementing any feature.
- Do not update to reflect implementation progress.
- Do not add features without explicit human approval.
- Only modify when the MVP scope or product feature set officially changes.

**Modification Checklist (run before editing):**
> Did the product scope or MVP feature set officially change?
> If NO — do not touch this document.

---

# PRODUCT_SPEC.md

# Product Specification

## Working Name

Engram

---

# One Sentence Product Definition

A local-first AI memory layer that continuously understands the evolution of a software project,
preserves its knowledge over time using Cognee, and makes that understanding instantly available
to both developers and AI assistants.

---

# Core Problem

Developers lose project understanding long before they lose code.

Every new AI session starts from zero.

Every AI tool has isolated context.

Important architectural decisions disappear over time.

Developers repeatedly explain the same project to different AI assistants.

The product eliminates this continuity problem.

---

# Target Users

## Primary

- Solo developers
- Indie hackers
- AI-first developers

## Secondary

- Small engineering teams
- Startup teams
- Open-source contributors

---

# Product Philosophy

The developer should continue working exactly as they do today.

Memory should build automatically.

The developer should never feel like they are maintaining documentation.

The system silently becomes smarter every day.

---

# Core User Journey

## Step 1 — One-Time Setup

User selects a project directory and provides the required API key once.

The background service begins observing meaningful project activity immediately.

No further configuration is required.

---

## Step 2 — Developer Works Normally

The developer works without thinking about memory.

Examples:

- Writing code
- Creating files
- Updating README
- Changing dependencies
- Making commits
- Writing manual decision notes (optional)

The product continuously builds project memory in the background.

---

## Step 3 — Instant Continuity

Weeks later, the developer opens any supported AI assistant.

Instead of explaining the project again, the AI immediately understands:

- Current architecture
- Important decisions
- Recent changes
- Project evolution
- Current direction

---

# Core User Moments

## Moment 1 — "I didn't have to teach it."

The product quietly understands the project without being told.

---

## Moment 2 — "It actually knows why this exists."

The AI answers using historical project knowledge, not just current code.

---

## Moment 3 — "I can continue from anywhere."

Changing AI tools never means losing project understanding.

---

# Product Features

## Automatic Observation

Continuously watches:

- Git commits
- Project structure changes
- Documentation updates
- Configuration changes
- Dependency changes

No manual maintenance required.

---

## Project Memory

Builds and organizes:

- Entities
- Relationships
- Architecture
- Decisions
- Evolution timeline

Powered by Cognee.

---

## Intelligent Recall

Two interaction surfaces for querying project memory:

### Dashboard — Ask Your Project

A search bar in the dashboard labeled "Ask Your Project."

Example queries:

- Why was authentication implemented this way?
- What changed last week?
- Explain the payment flow.
- Where is user onboarding handled?

The dashboard sends the query to the Memory Orchestrator,
which calls `cognee.recall()` and renders the sourced result.
The response includes a `reasoning_path` array, which the Dashboard renders with a zero-load staggered animation (theater effect) to simulate true multi-hop reasoning traces.

### MCP — AI Assistant Access

AI assistants never display a search UI.

They invoke the MCP recall tool automatically when project context is needed.

Humans use the Dashboard.
AI assistants use MCP.

One retrieval system. Two interaction surfaces.

---

## AI Continuity

Every connected AI assistant sees the same project understanding.

No repeated explanations.

No manual context transfer.

---

## Decision Notes

Optional. Extremely lightweight.

Developer records architectural reasoning that automatic observation cannot capture:

```
memory note "Switched from JWT to Better Auth because..."
```

These become first-class project memory, ingested directly into Cognee.

---

## Dashboard

Read-only visualization of project memory.

### Views

**Project Overview**
Current project state at a glance.

**Ask Your Project**
Search interface for querying project memory.
Returns sourced results with clear distinction between retrieved facts and AI interpretations.

**Recent Decisions**
Tier 2 decision notes and inferred decisions from git history.

**Architecture Evolution**
Chronological timeline of significant architectural changes.
Examples: authentication introduced, database changed, dependency migration, module split, API redesign.
Explains how the project evolved over time.

**Current Focus**
Summarizes what the developer is actively working on.
Derived from: recent git commits, recent meaningful file activity, recent decision notes.
Not predictive. Reflects recent development activity only.

**Memory Timeline**
Chronological feed of all captured project events.

**Memory Summary Graph (Hackathon Demo)**
A lightweight, non-interactive D3 force-directed visualization of major project entities and their relationships.
Deterministically powered by the new `/api/graph/summary` endpoint to guarantee <0.1s render times.
Helps users understand how project concepts connect visually. Read-only. Not interactive for exploration.

**Memory Health**
Operational health indicator for the memory system.
Shows: last successful indexing, pending observations, projects being tracked,
memory freshness, indexing status.
Not an AI confidence score.

---

# What We Do NOT Build

We are NOT:

- Another IDE
- Another code editor
- Another documentation platform
- Another note-taking application
- Another chatbot
- Another code generator

Memory is the product.

---

# MVP Scope

The MVP must deliver:

- ✓ Background observation
- ✓ Manual decision notes
- ✓ Cognee memory integration
- ✓ Memory recall
- ✓ MCP server
- ✓ Dashboard

---

# Nice To Have (Post-Hackathon)

- Visual graph exploration (pan, zoom, navigation, filtering)
- Git history timeline
- Advanced search filters
- Architecture snapshots
- AI suggestions
- Multi-project support
- Team workspaces

These are valuable but not required for a successful hackathon demo.

---

# Demo Scenario

The developer works on a project for several days.

The product silently builds memory throughout.

The developer opens a completely new AI session.

Without manually explaining anything, the AI immediately answers:

- What the project is
- Why architectural decisions were made
- What changed recently
- Where important features exist

The audience immediately understands that memory persisted beyond a single AI conversation.

> Note: The product's own development history will serve as the primary demo dataset.
> This makes the demo self-demonstrating — the product built memory of itself.

---

# Success Criteria

The product succeeds if developers stop thinking about preserving project context.

Memory should feel invisible while being continuously useful.

The developer should never think: "I have to explain my project again."

Instead they simply continue building.
