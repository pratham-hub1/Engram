from fastapi import APIRouter, Query, HTTPException
from backend.memory.orchestrator import query_decision, query_history, query_general

router = APIRouter()

import json

def parse_llm_json(raw_text: str):
    try:
        import re
        text = raw_text.strip()
        # Find the first [ or { and the last ] or } to strip all markdown and preamble
        match = re.search(r'([\[\{].*[\]\}])', text, re.DOTALL)
        if match:
            text = match.group(1)
        return json.loads(text)
    except Exception:
        return {"raw_response": raw_text}

from pydantic import BaseModel
from typing import List
from openai import AsyncOpenAI
from backend.config import settings

class TimelineEvent(BaseModel):
    date: str
    event: str

class TimelineResponse(BaseModel):
    events: List[TimelineEvent]

class DecisionEvent(BaseModel):
    decision: str
    reason: str
    source: str
    confidence: str

class DecisionResponse(BaseModel):
    decisions: List[DecisionEvent]

async def strict_parse_llm_json(raw_text: str, intent: str):
    """Guaranteed JSON formatting using OpenAI Structured Outputs"""
    try:
        # Fast path: check if the LLM actually output valid JSON first
        import re
        text = raw_text.strip()
        match = re.search(r'([\[\{].*[\]\}])', text, re.DOTALL)
        if match:
            text = match.group(1)
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        elif "events" in parsed:
            return parsed["events"]
        elif "decisions" in parsed:
            return parsed["decisions"]
        return parsed
    except Exception:
        pass # Fallthrough to strict OpenAI parsing

    try:
        client = AsyncOpenAI(
            api_key=settings.cognee_llm_api_key,
            base_url="http://127.0.0.1:5001/v1"
        )
        response_format = TimelineResponse if intent == "history" else DecisionResponse
        
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a strict data formatter. Extract the events or decisions from the raw text into the exact JSON schema requested. Do not make anything up."},
                {"role": "user", "content": raw_text}
            ],
            response_format=response_format,
            temperature=0
        )
        parsed = completion.choices[0].message.parsed
        if intent == "history":
            return [e.model_dump() for e in parsed.events]
        else:
            return [e.model_dump() for e in parsed.decisions]
    except Exception as e:
        return {"raw_response": raw_text, "error": str(e)}

@router.get("/api/query")
async def query_memory(
    q: str = Query(default="", description="The question to ask the memory engine"),
    intent: str = Query("general", description="The intent of the query: 'decision', 'history', or 'general'")
):
    try:
        if intent == "decision":
            query_str = q if q else "What are the recent architectural decisions?"
            answer_text = await query_decision(query_str)
            parsed_answer = await strict_parse_llm_json(answer_text, intent)
        elif intent == "history":
            query_str = q if q else "What is the recent project history and timeline?"
            import aiosqlite
            import json
            from backend.db.state import DB_PATH
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT event_type, source_path, metadata, timestamp FROM memories_log WHERE event_type IN ('GIT_COMMIT_WITH_REASON', 'GIT_COMMIT', 'MANUAL_NOTE', 'MILESTONE') ORDER BY timestamp DESC LIMIT 8") as cursor:
                    rows = await cursor.fetchall()
            
            parsed_answer = []
            for r in rows:
                ts = r["timestamp"].split(".")[0].replace("T", " ")
                if r["event_type"] == "GIT_COMMIT_WITH_REASON":
                    try:
                        meta = json.loads(r["metadata"] or "{}")
                        msg = meta.get("message", "Commit")
                        parsed_answer.append({"date": ts, "event": f"Git Commit: {msg}"})
                    except Exception:
                        parsed_answer.append({"date": ts, "event": f"Committed {r['source_path']}"})
                elif r["event_type"] == "MANUAL_NOTE":
                    try:
                        meta = json.loads(r["metadata"] or "{}")
                        msg = meta.get("note", "Manual Note")
                        parsed_answer.append({"date": ts, "event": f"Milestone: {msg}"})
                    except Exception:
                        parsed_answer.append({"date": ts, "event": f"Milestone on {r['source_path']}"})
                else:
                    parsed_answer.append({"date": ts, "event": f"Event: {r['source_path']}"})
        else:
            query_str = q if q else "Provide a general summary."
            answer_text = await query_general(query_str)
            parsed_answer = parse_llm_json(answer_text)
            
        return {"query": query_str, "intent": intent, "data": parsed_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
import hashlib
import time
from backend.pipeline.processor import process_event
from backend.observer.queue import RawEvent
from backend.config import settings
from backend.db.state import get_nudges, DB_PATH, get_cache, set_cache
import aiosqlite
from backend.memory.orchestrator import query_onboarding

class NoteRequest(BaseModel):
    text: str

@router.post("/api/notes")
async def add_manual_note(request: NoteRequest):
    """
    Tier 2 Manual Decision Note entry point. Bypasses Observer.
    """
    text = request.text
    content_hash = hashlib.sha256(text.encode()).hexdigest()
    
    event = RawEvent(
        event_type="MANUAL_NOTE",
        path="manual_note", # Pseudo-path for manual notes
        timestamp=time.time(),
        metadata={"message": text, "hash": content_hash, "source": "cli"}
    )
    
    # Process through pipeline
    result = await process_event(event, settings.cognee_dataset_name)
    
    if result.success:
        return {"status": "Decision captured.", "data_id": result.data_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to capture decision note.")

@router.get("/api/health/nudges")
async def get_nudge_queue():
    """
    Returns the current unresolved nudges for Memory Health view.
    """
    nudges = await get_nudges()
    return {"nudges": nudges, "count": len(nudges)}

@router.get("/api/health/stats")
async def get_health_stats():
    """
    Returns the Memory Health metrics: Decisions Captured and Documents Indexed.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM memories_log WHERE event_type IN ('MANUAL_NOTE', 'GIT_COMMIT_WITH_REASON')") as cursor:
                row = await cursor.fetchone()
                decisions_captured = row[0] if row else 0
                
            async with db.execute("SELECT COUNT(*) FROM memories_log WHERE event_type IN ('FILE_CREATED', 'FILE_MODIFIED')") as cursor:
                row = await cursor.fetchone()
                documents_indexed = row[0] if row else 0
                
            # Count architectural changes (events associated with structural nodes)
            async with db.execute("SELECT COUNT(*) FROM memories_log WHERE event_type LIKE '%STRUCTURAL%' OR event_type IN ('FILE_MODIFIED')") as cursor:
                row = await cursor.fetchone()
                architectural_changes = row[0] if row else 0
                
            # Count pending why notes (nudges that have not been resolved)
            nudges = await get_nudges()
            pending_why_notes = len(nudges) if nudges else 0
                
        return {
            "decisions_captured": decisions_captured,
            "documents_indexed": documents_indexed,
            "architectural_changes": architectural_changes,
            "pending_why_notes": pending_why_notes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/graph/summary")
async def get_graph_summary():
    """
    Returns a deterministic, pruned clustered subgraph of the architecture and recent changes.
    """
    try:
        nodes = [
            {"id": "Project Core", "group": 1, "radius": 24},
            {"id": "Backend API", "group": 2, "radius": 16},
            {"id": "Frontend UI", "group": 2, "radius": 16},
            {"id": "Memory Orchestrator", "group": 3, "radius": 12},
            {"id": "Observer Service", "group": 3, "radius": 12},
            {"id": "Cognee Graph", "group": 4, "radius": 20},
            {"id": "LLM Extraction", "group": 3, "radius": 12},
            {"id": "SQLite Log", "group": 4, "radius": 12},
            {"id": "LanceDB", "group": 4, "radius": 12},
            {"id": "KuzuDB", "group": 4, "radius": 12},
            {"id": "Dashboard", "group": 5, "radius": 16},
            {"id": "MCP Server", "group": 5, "radius": 16},
        ]
        links = [
            {"source": "Project Core", "target": "Backend API", "value": 2},
            {"source": "Project Core", "target": "Frontend UI", "value": 2},
            {"source": "Backend API", "target": "Memory Orchestrator", "value": 1},
            {"source": "Backend API", "target": "Observer Service", "value": 1},
            {"source": "Observer Service", "target": "LLM Extraction", "value": 1},
            {"source": "LLM Extraction", "target": "Cognee Graph", "value": 3},
            {"source": "Memory Orchestrator", "target": "Cognee Graph", "value": 3},
            {"source": "Cognee Graph", "target": "SQLite Log", "value": 1},
            {"source": "Cognee Graph", "target": "LanceDB", "value": 1},
            {"source": "Cognee Graph", "target": "KuzuDB", "value": 1},
            {"source": "Frontend UI", "target": "Dashboard", "value": 2},
            {"source": "Dashboard", "target": "Memory Orchestrator", "value": 2},
            {"source": "Backend API", "target": "MCP Server", "value": 2},
            {"source": "MCP Server", "target": "Memory Orchestrator", "value": 2},
        ]
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT DISTINCT source_path FROM memories_log WHERE event_type IN ('FILE_CREATED', 'FILE_MODIFIED') ORDER BY timestamp DESC LIMIT 30") as cursor:
                rows = await cursor.fetchall()
                for idx, row in enumerate(rows):
                    path = row["source_path"]
                    if not path or path == "manual_note": continue
                    
                    filename = path.split("/")[-1].split("\\")[-1]
                    node_id = f"file_{idx}_{filename}"
                    nodes.append({"id": node_id, "label": filename, "group": 6, "radius": 10})
                    
                    if "frontend" in path.lower():
                        links.append({"source": "Frontend UI", "target": node_id, "value": 1})
                    elif "backend" in path.lower():
                        links.append({"source": "Backend API", "target": node_id, "value": 1})
                    else:
                        links.append({"source": "Project Core", "target": node_id, "value": 1})
                        
        return {"nodes": nodes, "links": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/activity")
async def get_activity_feed():
    """
    Returns the 10 most recent activity feed events.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT event_type, source_path, timestamp FROM memories_log ORDER BY timestamp DESC LIMIT 10") as cursor:
                rows = await cursor.fetchall()
                feed = [dict(r) for r in rows]
        return {"feed": feed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/project/onboarding")
async def get_onboarding_summary():
    """
    Returns the high-level project summary for onboarding (cached).
    """
    try:
        cache_key = "onboarding_summary"
        cached = await get_cache(cache_key)
        if cached:
            return json.loads(cached)
            
        # Execute heavy graph search
        raw_text = await query_onboarding()
        parsed = parse_llm_json(raw_text)
        
        # Save to cache
        await set_cache(cache_key, json.dumps(parsed))
        
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from backend.memory.cognee_client import improve_dataset, recall_memory, forget_event
from backend.db.state import get_expired_memories, delete_memory_log

@router.post("/api/memory/improve")
async def improve_memory():
    """Triggers the background optimization of the Cognee graph."""
    try:
        await improve_dataset(settings.cognee_dataset_name)
        return {"status": "Memory optimized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RootCauseRequest(BaseModel):
    symptom: str

@router.post("/api/memory/root-cause")
async def root_cause(request: RootCauseRequest):
    """Multi-Hop Detective: Finds code, then finds the intent."""
    try:
        # Hop 1: Find the code chunks
        chunks = await recall_memory(request.symptom, settings.cognee_dataset_name, query_type="CHUNKS_ONLY")
        
        # Hop 2: Find the architectural decisions
        decisions_prompt = f"Based on these files related to '{request.symptom}', what architectural decisions govern them?"
        decisions = await recall_memory(decisions_prompt + "\n\nContext:\n" + chunks, settings.cognee_dataset_name, query_type="GRAPH_COMPLETION")
        
        return {
            "symptom": request.symptom,
            "hop1_chunks": chunks,
            "hop2_decisions": decisions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/memory/prune")
async def prune_memory():
    """Ticking Time Bomb Debt: Surgically forgets expired memories."""
    try:
        expired = await get_expired_memories()
        forgotten = 0
        for mem in expired:
            await forget_event(mem["data_id"], dataset_name=settings.cognee_dataset_name)
            await delete_memory_log(mem["data_id"])
            forgotten += 1
            
        return {"status": "success", "forgotten_count": forgotten, "details": expired}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

