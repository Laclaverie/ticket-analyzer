# Web Client

Desktop-first browser client for Ticket Analyzer.

## Tech Stack
- **React 18**
- **TypeScript**
- **Vite**

## Prerequisites
- Node.js (v18 or newer recommended)
- npm or yarn

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configuration**:
   Optionally set `VITE_API_BASE_URL` in your environment (default: `http://localhost:8000`).

3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

## Building for Production

To create a production-ready build:
```bash
npm run build
```
The optimized files will be generated in the `dist/` directory.

To preview the production build locally:
```bash
npm run preview
```

## Testing
- **Unit/Integration**: `npm run test` (Vitest)
- **E2E (Playwright)**: `npm run test:e2e`
- **Install Playwright Browsers**: `npx playwright install chromium` (needed for E2E)
