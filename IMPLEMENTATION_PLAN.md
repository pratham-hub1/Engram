# Hybrid NIM Architecture Implementation Plan

This plan safely configures the backend to use `nvidia/nv-embed-v1` for embeddings and `nvidia/nemotron-3-super-120b-a12b` for LLM reasoning, while cleanly resolving the empty graph and tokenizer errors.

## Proposed Changes

### 1. The Tokenizer Dictionary Injection
The underlying framework (`tiktoken` via `litellm`) crashes when counting tokens because it doesn't recognize the model string `nvidia/nv-embed-v1`. Monkey-patching environments variables (`LITELLM_TOKENIZER`) clearly fails because abstraction layers bypass them. 
The absolute cleanest fix is to programmatically inject the model into `tiktoken`'s global dictionary before any heavy libraries load.

#### [MODIFY] backend/main.py
- Import `tiktoken`.
- Add `tiktoken.model.MODEL_TO_ENCODING["nvidia/nv-embed-v1"] = "cl100k_base"` at the top of the lifespan function to globally map the custom Nvidia model to standard OpenAI token rules.
- Update `cognee.config.set_embedding_config()` to use `"nvidia/nv-embed-v1"`.

### 2. The Configuration Layer
We will update `config.py` to route embedding requests to the new model.

#### [MODIFY] backend/config.py
- Change `cognee_embedding_model` to `nvidia/nv-embed-v1`.

### 3. The Self-Healing Indexer (Dropping the Split-Brain)
We must remove the fragile SQLite flag that causes the graph to stay empty after a database wipe.

#### [MODIFY] backend/memory/indexer.py
- Remove the `is_project_indexed()` check completely.
- Instead, use `cognee.search()` (or equivalent API) on startup to verify if the graph actually has nodes. If it returns an empty result, trigger the backfill. This makes the architecture mathematically self-healing.

#### [MODIFY] backend/db/state.py
- We will no longer need `is_project_indexed` or `project_settings` table lookups for initialization.

## User Review Required
> [!IMPORTANT]
> To execute this plan, I need you to confirm:
> 1. Is your `NVIDIA_NIM_API_KEY` (or the equivalent `nvapi-...` key) already saved in your root `.env` file under `COGNEE_LLM_API_KEY` and `COGNEE_EMBEDDING_API_KEY`?
> 2. Are you comfortable with me writing a small script to drop the `.cognee_system` directory to force the new self-healing indexer to trigger a massive, pristine backfill?
