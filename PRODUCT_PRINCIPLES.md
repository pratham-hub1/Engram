---
## Document Governance

**Status:** Immutable
**Purpose:** Defines the product philosophy and non-negotiable principles that govern every decision made on this project.
**Owner:** Human (product decisions only)
**AI May Modify:** No — never automatically. Only if explicitly instructed after a fundamental product vision change.

**Update Policy:**
- Read every session before making any product or UX decision.
- Do not modify during normal development.
- Do not modify because implementation details changed.
- Only modify if the core product vision or philosophy fundamentally changes.
- Treat every principle here as a hard constraint, not a guideline.

**Modification Checklist (run before editing):**
> Did the product philosophy change at a fundamental level?
> If NO — do not touch this document.

---

# PRODUCT_PRINCIPLES.md

# Project Principles

This document defines the non-negotiable principles for the product.
Every architecture decision, feature, and implementation must align with these principles.

---

# Vision

Build a developer memory system that never lets project understanding disappear.

The product should preserve the reasoning, evolution, and current state of a software project across:

- AI assistants
- Development sessions
- Time
- Different tools
- Different teammates (future)

The goal is NOT documentation.

The goal is continuity.

---

# Core Problem

Developers repeatedly lose project understanding.

Examples:

- Starting a new AI chat
- Switching from ChatGPT to Claude
- Returning after several weeks
- Forgetting why an architecture decision was made
- AI suggesting solutions that were already rejected
- Repeating the same explanations to different tools

Today's AI remembers conversations.

It does NOT remember projects.

This product solves project continuity.

---

# Product Philosophy

The developer should almost never think about maintaining memory.

Memory should build itself.

The product should observe the project passively, understand important changes, organize them,
and make them instantly available whenever needed.

Manual work should only exist when absolutely necessary.

---

# Design Principles

## Automatic First

Everything that can be captured automatically should be.

Examples:

- Git commits
- Code structure
- Dependency changes
- Documentation changes
- Project configuration
- Folder evolution

The user should never need to manually keep memory updated.

---

## Manual Only For Decisions

Some knowledge cannot be inferred.

Examples:

- "We rejected Firebase because of pricing."
- "JWT was selected for offline compatibility."
- "Redis caused deployment issues."

These represent reasoning rather than observable changes.

The product provides an extremely lightweight way to record these decisions.

Decision records are optional, not required.

---

## Memory Is The Product

The dashboard is NOT the product.

The UI is NOT the product.

The memory system is the product.

Everything else simply visualizes it.

---

## Cognee Is Essential

Removing Cognee must fundamentally reduce the product's value.

Cognee is responsible for:

- Remembering
- Recalling
- Improving memory
- Forgetting stale knowledge
- Graph relationships

Without Cognee the system becomes a simple file scanner.

Therefore Cognee must remain central to every important workflow.

---

## Universal AI Access

Project memory should be accessible to any compatible AI assistant through a standard protocol (MCP),
without the developer acting as a synchronization layer.

The product exposes a single MCP server.

Any tool that connects to it gains immediate project understanding.

This is how cross-tool context loss is solved — not through per-tool integrations,
but through one shared interface.

Removing the MCP server removes cross-tool continuity from the product.

---

## Local-First

The product runs locally.

Project data does not leave the developer's machine except for LLM API calls
required for memory processing.

This is not a limitation.

It is a trust guarantee.

The observer service, project scanning, indexing, and memory generation all run locally.
External calls are only made where technically necessary.

---

## Zero Documentation Burden

Developers should never feel they are writing documentation.

Memory must emerge naturally from development.

If users feel they are maintaining another Notion workspace, the product has failed.

---

## Explainability

Every retrieved memory should answer:

- Why was this retrieved?
- Which source produced it?
- When was it created?
- Why is it relevant?

Memory should never feel like a black box.

---

## Trust Over Intelligence

Incorrect memory is worse than missing memory.

Never fabricate project history.

Prefer uncertainty over hallucination.

Every important memory should be traceable back to its origin.

Synthesized summaries must be visually distinguishable from retrieved facts.
When the system infers or summarizes, that must be communicated clearly to the user.

Retrieved facts and AI interpretations are never presented as the same thing.

---

# Two-Tier Memory Model

## Tier 1 — Passive Observation

Captured automatically.

Examples:

- Git commits
- File changes
- Dependency updates
- README changes
- Documentation
- Project structure
- Configs

No user action required.

---

## Tier 2 — Decision Memory

Captured only when developers want to preserve reasoning.

Example:

```
memory note "We chose JWT because Firebase pricing scales poorly."
```

This represents architectural intent, not documentation.

---

# Core User Experience

The user should experience three moments.

## Moment 1

The product begins understanding the project immediately after one-time setup:
select a project directory and provide the required API key.

No further manual configuration is required.

---

## Moment 2

After weeks away, the user instantly regains complete project understanding.

No searching.

No reading dozens of files.

No remembering manually.

---

## Moment 3

Any AI assistant immediately understands the project without the user re-explaining everything.

This is the signature experience of the product.

---

# Scope

The hackathon version focuses on one primary workflow: Project Continuity.

Everything else is secondary.

We are NOT building:

- Another IDE
- Another AI chatbot
- Another documentation platform
- Another project management tool
- Another note-taking application

---

# Success Metric

A successful demo should make the audience say:

> "I no longer need to explain my project every time I switch AI tools."

If we achieve that, the product has succeeded.

---

# Engineering Principles

- Build the smallest architecture that demonstrates the vision.
- Prefer reliability over feature count.
- Prefer automation over configuration.
- Prefer passive observation over manual input.
- Prefer clarity over complexity.
- Every feature must reduce developer cognitive load.
- If a feature requires developers to think about the memory system, it is probably wrong.

---

# One Sentence Product Definition

A passive project memory layer that continuously understands how a project evolves,
preserves architectural decisions, and gives any AI assistant instant project understanding
through Cognee-powered memory.
