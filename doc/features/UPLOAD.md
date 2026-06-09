# Feature: Receipt Upload

Allows users to upload receipt images from their local machine to the Ticket Analyzer system.

## Flow
1. User clicks "Upload Receipt" on the Dashboard.
2. User selects a JPEG/PNG file.
3. Web Client sends a POST request to `/receipts/upload` with the multipart file.
4. API Service saves the file to local storage and creates a processing job.
5. Dashboard polls or refreshes to show the new "Pending" receipt.

## Components
- `HeroPanel.tsx`: Contains the file input and triggers the upload.
- `useDashboardData.ts`: Manages the upload state and triggers a refresh.
- `api.ts`: Performs the `fetch` call to the backend.

## Testing
- **Unit**: `tests/api.test.ts` verifies the service call.
- **Integration**: `tests/dashboard-page.integration.test.tsx` verifies the UI interaction.
- **E2E**: `e2e/upload.spec.ts` verifies the full roundtrip.
