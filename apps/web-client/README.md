# web-client

Desktop-first browser client for Ticket Analyzer.

Stack:
- React
- TypeScript
- Vite

Responsibilities:
- Receipt list and detail inspection
- Category and monthly analytics views
- CSV export workflows

Local development:
1. Install Node dependencies from `apps/web-client`.
2. Start the API service.
3. Run `npm run dev`.

Optional env var:
- `VITE_API_BASE_URL` points to the FastAPI backend, defaulting to `http://localhost:8000`.
