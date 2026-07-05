import asyncio
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from backend.config import settings

app = FastAPI()
chat_semaphore = asyncio.Semaphore(3) # Your rate-limit bouncer for heavy reasoning
embed_semaphore = asyncio.Semaphore(100) # Fast lane for embeddings, bumped to 100 to prevent internal queue timeouts

# Model Translation Map (The "Hack" made elegant)
MODEL_MAP = {
    "gpt-4o": "nvidia/nemotron-3-super-120b-a12b",
    "text-embedding-3-large": "nvidia/nv-embed-v1"
}

@app.post("/v1/{path:path}")
async def nvidia_gateway(path: str, request: Request):
    payload = await request.json()
    
    import json
    with open("debug_payload.log", "a", encoding="utf-8") as f:
        f.write(f"\n--- INCOMING PATH: {path} ---\n{json.dumps(payload, indent=2)}\n")
        
    # 1. Translate the dummy models to Nvidia's real models
    if payload.get("model") in MODEL_MAP:
        payload["model"] = MODEL_MAP[payload["model"]]
        
    # 2. Strip the leaky OpenAI abstractions
    requested_dimensions = payload.pop("dimensions", 3072)
    payload.pop("encoding_format", None)
    
    # Inject input_type for asymmetric models (Embeddings only)
    if "embeddings" in path and "input_type" not in payload:
        payload["input_type"] = "query"
        
    # Truncate oversized chunks to fit strict 4096 token limit
    if "input" in payload:
        inputs = payload["input"]
        if isinstance(inputs, list):
            payload["input"] = [text[:10000] if isinstance(text, str) else text for text in inputs]
        elif isinstance(inputs, str):
            payload["input"] = inputs[:10000]
    
    clean_headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length", "content-encoding", "authorization"]}
    
    # Secure API Key Injection
    if settings.app_llm_api_key:
        clean_headers["authorization"] = f"Bearer {settings.app_llm_api_key}"
    
    # 3. Route to Nvidia securely
    semaphore = embed_semaphore if "embeddings" in path else chat_semaphore
    async with semaphore:
        async with httpx.AsyncClient() as client:
            # Simple retry loop for 429 Too Many Requests
            for attempt in range(3):
                # Log outgoing request
                with open("debug_out.log", "a", encoding="utf-8") as f:
                    f.write(f"\n--- OUTGOING to {path} ---\n{json.dumps(payload, indent=2)}\n")
                    
                resp = await client.post(
                    f"https://integrate.api.nvidia.com/v1/{path}",
                    json=payload, headers=clean_headers, timeout=600.0
                )
                if resp.status_code in [429, 502, 503, 504]:
                    await asyncio.sleep(2)
                    continue
                
                # Log response for debugging
                with open("debug_payload.log", "a", encoding="utf-8") as f:
                    f.write(f"\n--- NVIDIA RESPONSE {resp.status_code} ---\n{resp.text}\n")
                break
            
    # 4. If it's an embeddings response, truncate the vectors to 3072 dimensions!
    if resp.status_code == 200 and "embeddings" in path:
        try:
            response_data = resp.json()
            if "data" in response_data:
                for item in response_data["data"]:
                    if "embedding" in item:
                        item["embedding"] = item["embedding"][:requested_dimensions]
            return JSONResponse(content=response_data, status_code=resp.status_code)
        except Exception:
            pass # fallback to returning raw if json parsing fails
            
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
