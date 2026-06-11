# api-service

HTTP API for ingestion and analytics reads.

Responsibilities:
- Upload endpoints
- Query endpoints for analytics
- Validation and orchestration
- Async job scheduling

Planned stack:
- Python
- FastAPI

Run it 
```
uv run --package api-service uvicorn api_service.main:app --reload
```