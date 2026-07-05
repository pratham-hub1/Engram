# Project Engram Architecture

The Engram project uses a decentralized microservice architecture. 

## Key Components
1. **FastAPI Main Backend**: Runs on Port 8000 and handles all business logic, Observer file watching, and Cognee integration.
2. **Sidecar API Gateway**: Runs on Port 5001. It intercepts all OpenAI-formatted requests from Cognee, strips leaky parameters (like `input_type` for chat completions), and translates the requests to Nvidia's native LLM and Embedding models.
3. **Database**: We use LanceDB under the hood for storing vector embeddings and a SQLite state database.

This architecture was finalized on July 3rd, 2026, just two days before the hackathon deadline.
