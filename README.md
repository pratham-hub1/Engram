# 🧠 Engram

> A local-first, self-healing Neural Knowledge Graph for your codebase.

---

## 🛑 The Problem

Every time you start a new AI session, you explain your project from scratch.
Every time you switch from Claude to Cursor to ChatGPT, context is lost.
Every time you return after three weeks, the reasoning behind your decisions has vanished.

AI tools remember conversations. **They do not remember projects.**

---

## ⚡ What is Engram?

Engram is a background service that silently observes your project as you work — capturing git commits, file changes, documentation updates, and architectural shifts — and builds a persistent, 4-dimensional understanding of your project using **Cognee 1.2.2**.

When you need context, it is already there.
When a new developer joins, they can instantly interrogate the project's history.
**[Phase 2 Vision] Universal Memory:** We have laid the foundation for an MCP server so that any AI assistant (Claude, Cursor) can eventually share this exact same project memory.

---

## 🚀 How It Works (The Architecture)

```text
[ Developer Works ] ──> [ Background Observer (Watchdog) ]
                               │
                      [ Event Intelligence Pipeline ]
                               │ (Filters noise, extracts topology)
                 [ Decoupled NIM Gateway (Port 5001) ] 👈 (The API Fix)
                               │
                     [ Cognee Neural Graph ]
                               │ (SQLite + LanceDB + KuzuDB)
          ┌────────────────────┴────────────────────┐
          │                                         │
 [ Glassmorphism Dashboard ]               [ MCP Server (Alpha) ]
 (The Multi-Hop Detective)          (AI Assistant Context Provider)
```

**Two ways knowledge enters memory:**

1. **The Observer (Passive):** Instantly captures configuration changes, documentation updates, and Git Commits. Extracts structural relationships (e.g. `auth.js` imports `db.js`) without heavy AST parsers.
2. **The Ledger (Active):** When the system detects a major architectural change without documentation, it sends a "Nudge". The developer can quickly log a human-readable decision that gets bound directly to the code nodes.

---

## 🌟 Hackathon Demo Showcase & Killer Features

- **The Multi-Hop Detective (Zero-Load Reasoning Trace):** An interactive UI that traverses the graph to answer complex architectural questions (e.g., *"Why did we switch to Vite, and what files were affected?"*). The frontend features a highly optimized "theater effect" staggered animation that parses the LLM's explicit `reasoning_path` output in real-time. This perfectly simulates SSE/WebSockets streaming visually, while enforcing exactly **zero added load** or latency on the backend architecture.
- **Deterministic Graph Visualization (`/api/graph/summary`):** Rather than crashing the browser with a massive unstructured graph pull, Engram intelligently constructs a pruned, fast subgraph in `<0.1s`. It dynamically pulls the 30 most recent organic file modifications from the local SQLite `memories_log` and elegantly wires them directly into the core architectural system nodes for D3 to render.
- **Self-Healing Indexing:** The backend utilizes a robust startup verification protocol against Cognee to ensure the Knowledge Graph is perfectly synced, preventing rate-limit flooding on reboot.
- **Ticking Debt Detection:** The system actively monitors "ghost decisions" (code written without recorded intent) and nudges developers before knowledge is lost.
- **Local-First & Fast:** Embeddings and Graph traversal run entirely local (LanceDB + KuzuDB) backed by the Nvidia AI API for reasoning extraction.
- **Decoupled NIM Gateway (Resilient Architecture):** Built a standalone FastAPI sidecar to intercept, sanitize, and translate OpenAI-formatted payloads into strict NVIDIA NIM schemas in real-time. This prevents event-loop deadlocks and ensures lightning-fast graph ingestion without relying on fragile CLI proxies.
- 🚧 **Universal AI Compatibility (Experimental):** Built the foundational MCP (Model Context Protocol) server. Currently undergoing stability testing for V2, which will allow any compatible AI tool to instantly read the project's mind.

---

## 🛠️ Quick Start (Hackathon Demo Setup)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Nvidia API Key

### 1. Setup the Backend
```bash
# Clone and install dependencies
git clone https://github.com/your-username/engram.git
cd engram

# Set your API Key
cp .env.example .env
# Edit .env and add NVIDIA_API_KEY=your_key

# Install the package
pip install -e .
```

### 2. Start the Brain & Gateway (FastAPI + Cognee)
Open two terminal tabs to ensure asynchronous stability:

Terminal 1 (The NIM Gateway):
```bash
uvicorn backend.gateway:app --host 127.0.0.1 --port 5001
```

Terminal 2 (The Main Brain):
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
*Note: On first boot, the system will automatically perform an initial backfill of your codebase. Subsequent boots are instant.*

### 3. Start the Dashboard (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
*The sleek Obsidian/Glassmorphism dashboard will be live at `http://localhost:5173`.*

### 🚧 4. Connect an AI Assistant via MCP (Alpha / Testing Phase)
> **Note:** The MCP integration is structurally built but currently undergoing active stability testing. Feel free to inspect the architecture, but the primary Hackathon demo focuses on the Core Dashboard.

```json
{
  "mcpServers": {
    "engram": {
      "url": "http://localhost:8001/mcp"
    }
  }
}
```

---

## 🧩 The Dashboard Views

| View | Purpose |
|---|---|
| **Mission Control** | High-level architectural synthesis from the neural graph and Activity Ticker. |
| **Ask Your Project** | The "Multi-Hop Detective" for interrogating the graph with live reasoning trace paths. |
| **Neural Ledger** | Human-in-the-loop context backfilling and Neural Decisions Grid. |
| **Evolution** | 4-Dimensional structural morphing over time and dynamic Architecture Graph rendering. |
| **Memory Health** | Real-time extraction of active engineering trajectories and local database sizes. |

---

## 📜 Technology Stack

- **Backend:** Python, FastAPI, Watchdog
- **Neural Graph:** Cognee 1.2.2 (KuzuDB + LanceDB + SQLite embedded)
- **Intelligence:** Nvidia nemotron-3-super-120b-a12b and nv-embed-v1
- **Frontend:** React, Vite, D3.js (Force Simulation), Lucide-React
- **Aesthetic:** Custom CSS Glassmorphism + React Markdown
- **Interoperability:** Model Context Protocol (MCP) Python SDK

---

*Memory is the product. Everything else is a surface for accessing it.*
