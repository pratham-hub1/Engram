# Memory AI

> A local-first AI memory layer that never lets project understanding disappear.

---

## The Problem

Every time you start a new AI session, you explain your project from scratch.

Every time you switch from Claude to Cursor to ChatGPT, context is lost.

Every time you return after three weeks, the reasoning behind your decisions has vanished.

AI tools remember conversations.

They do not remember projects.

---

## What This Is

A background service that silently observes your project as you work — git commits, file changes, documentation updates, dependency changes — and builds a persistent, structured understanding of your project using Cognee.

When you need context, it is already there.

When you switch AI tools, they all share the same project memory.

When you return after weeks away, your project remembers itself.

---

## How It Works

```
You work normally
      │
Observer Service detects meaningful changes
      │
Memory Pipeline structures the knowledge
      │
Cognee stores and evolves the memory graph
      │
      ├── Dashboard       — you understand your project instantly
      └── MCP Server      — any AI assistant understands it too
```

Two ways knowledge enters memory:

**Automatic (Tier 1)** — Git commits, file changes, documentation updates, dependency and config changes. No user action required.

**Manual (Tier 2)** — Decisions that no machine can infer.

```bash
memory note "Chose JWT over Firebase because pricing scales poorly at volume."
```

---

## Key Features

- **Passive observation** — works without changing how you develop
- **Decision memory** — preserves the *why*, not just the *what*
- **MCP server** — any MCP-compatible AI assistant gets project context automatically
- **Recall interface** — ask your project questions in plain language
- **Local-first** — your code never leaves your machine (except LLM API calls)
- **Zero documentation burden** — memory builds from natural development activity

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for dashboard)
- A Gemini API key (free tier)

### Installation

```bash
git clone https://github.com/your-username/memory-ai.git
cd memory-ai
```

```bash
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

```bash
pip install -e .
```

### Start the Service

```bash
# Register a project and start observing
memory start --project /path/to/your/project
```

### Start the Dashboard

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at `http://localhost:5173`

### Connect an AI Assistant via MCP

Add the following to your AI assistant's MCP configuration:

```json
{
  "mcpServers": {
    "memory-ai": {
      "url": "http://localhost:8001/mcp"
    }
  }
}
```

Your AI assistant now has access to your project memory.

---

## CLI Reference

```bash
# Record an architectural decision
memory note "Reason for a technical choice"

# Query project memory from the terminal
memory recall "Why did we choose this approach?"

# Check observer and memory status
memory status

# Run improve pass manually
memory improve

# Forget a specific memory
memory forget "<memory-id>"
```

---

## MCP Tools

When connected via MCP, AI assistants have access to:

| Tool | Description |
|---|---|
| `recall_context` | Retrieve relevant project memories for a query |
| `get_project_summary` | Get current project state and architecture |
| `add_decision` | Store a decision note directly from the AI assistant |
| `get_recent_changes` | Get a timeline of recent project changes |

---

## Dashboard Views

| View | Purpose |
|---|---|
| Project Overview | Current project state at a glance |
| Ask Your Project | Plain-language recall interface |
| Recent Decisions | Architectural decisions and their reasoning |
| Architecture Evolution | How the project changed over time |
| Current Focus | What is actively being worked on |
| Memory Timeline | Chronological feed of all captured events |
| Memory Summary Graph | Entity and relationship visualization |
| Memory Health | Observer status and indexing metrics |

---

## Documentation

| Document | Purpose |
|---|---|
| [`CODEBASE_MEMORY.md`](./CODEBASE_MEMORY.md) | AI assistant context — read this first |
| [`PRODUCT_PRINCIPLES.md`](./PRODUCT_PRINCIPLES.md) | Non-negotiable product principles |
| [`PRODUCT_SPEC.md`](./PRODUCT_SPEC.md) | Feature specification |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System design and component responsibilities |
| [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) | Build phases and progress |

---

## Technology

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Memory | Cognee |
| LLM | Gemini Free Tier |
| File watching | watchdog |
| Git | gitpython |
| MCP | mcp Python SDK |
| Frontend | React + Vite |
| CLI | Typer |

---

## What This Is Not

- Not a chatbot
- Not a documentation generator
- Not a code editor
- Not a note-taking app
- Not a project management tool

Memory is the product.

Everything else is a surface for accessing it.

---

## License

MIT
