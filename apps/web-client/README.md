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

Testing:
1. Unit/integration tests: `npm run test`
2. Watch mode: `npm run test:watch`
3. Browser E2E tests: `npm run test:e2e`
4. First-time Playwright browser install: `npx playwright install chromium`

Optional env var:
- `VITE_API_BASE_URL` points to the FastAPI backend, defaulting to `http://localhost:8000`.
