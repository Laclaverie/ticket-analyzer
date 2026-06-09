import { test, expect } from '@playwright/test';

test('should upload a receipt and see it in the list', async ({ page }) => {
  // Wait for the page to load
  await page.goto('http://localhost:4173');

  // Verify we are on the dashboard
  await expect(page.locator('h1')).toContainText('Desktop-first receipt analysis');

  // Check if we are connected to the API (status pill)
  // Note: Since this is a clean DB, there might be 0 receipts initially.
  const statusPill = page.locator('.status-pill');
  await expect(statusPill).toContainText('Connected to API');

  // Upload the file
  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: /Upload receipt/i }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles('test-receipt.jpg');

  // Verify the upload starts
  await expect(page.getByRole('button', { name: /Uploading.../i })).toBeVisible();

  // Wait for the upload to complete and list to refresh
  // We expect at least one receipt in the list now
  await expect(page.locator('.receipt-row')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('.receipt-store').first()).toContainText('Unknown store');
});
