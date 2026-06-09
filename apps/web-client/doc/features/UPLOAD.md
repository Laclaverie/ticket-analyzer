# Receipt Upload Feature

The Receipt Upload feature allows users to ingest new supermarket receipts into the system from the web dashboard.

## Flow

1.  **Selection**: The user clicks the "Upload receipt" button in the Hero panel.
2.  **File Input**: A native file picker opens, filtered for images (`image/*`).
3.  **Transfer**: The selected file is sent via `POST` to `/receipts/upload` as `multipart/form-data`.
4.  **Backend Ingestion**:
    *   The file is saved to the storage path.
    *   A new `Receipt` record is created.
    *   A `ProcessingJob` is enqueued for the asynchronous worker.
5.  **Feedback**:
    *   During upload, the button text changes to "Uploading..." and is disabled.
    *   On success, the dashboard data is automatically refreshed to show the new receipt (initially with "Unknown store" until processed).
    *   On failure, an alert is shown to the user.

## Implementation Details

*   **API**: `uploadReceipt(file: File)` in `src/api.ts`.
*   **Component**: `HeroPanel.tsx` using a hidden `input[type="file"]`.
*   **State**: Managed via `useDashboardData` hook's `refreshDashboard` method.

## Future Improvements

*   Progress bar for large image uploads.
*   Drag and drop support.
*   Client-side image compression before upload.
