import { expect, test } from '@playwright/test';

test('loads dashboard and updates receipt detail when selecting another receipt', async ({ page }) => {
  await page.route('**/*', async (route) => {
    const url = route.request().url();

    if (url.includes('/receipts?page=1&page_size=10')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'receipt-1',
              store: 'Carrefour',
              purchase_date: '2026-06-05T18:40:00Z',
              total_amount: '46.72',
              currency: 'EUR',
              created_at: '2026-06-05T18:42:00Z',
            },
            {
              id: 'receipt-2',
              store: 'Lidl',
              purchase_date: '2026-06-03T12:15:00Z',
              total_amount: '29.18',
              currency: 'EUR',
              created_at: '2026-06-03T12:17:00Z',
            },
          ],
          total: 2,
          page: 1,
          page_size: 10,
        }),
      });
      return;
    }

    if (url.includes('/analytics/spending/by-category')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify([{ category_id: 'food', total_spend: '75.90' }]),
      });
      return;
    }

    if (url.includes('/analytics/spending/by-month')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify([{ year: 2026, month: 6, total_spend: '75.90' }]),
      });
      return;
    }

    if (url.includes('/analytics/top-items?limit=5')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify([{ normalized_name: 'milk', total_spend: '12.50', occurrence_count: 2 }]),
      });
      return;
    }

    if (url.includes('/analytics/receipts/by-month')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify([{ year: 2026, month: 6, receipt_count: 2 }]),
      });
      return;
    }

    if (url.includes('/receipts/receipt-1/items')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          receipt_id: 'receipt-1',
          items: [
            {
              id: 'item-1',
              receipt_item_raw_id: 'raw-1',
              normalized_name: 'milk',
              quantity: '2',
              unit_price: '2.10',
              line_total: '4.20',
              category_id: 'food',
              confidence: 0.98,
              classification_origin: 'rule',
              created_at: '2026-06-05T18:41:00Z',
            },
          ],
        }),
      });
      return;
    }

    if (url.includes('/receipts/receipt-2/items')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          receipt_id: 'receipt-2',
          items: [
            {
              id: 'item-2',
              receipt_item_raw_id: 'raw-2',
              normalized_name: 'dish soap',
              quantity: '1',
              unit_price: '3.95',
              line_total: '3.95',
              category_id: 'household',
              confidence: 0.93,
              classification_origin: 'rule',
              created_at: '2026-06-03T12:16:00Z',
            },
          ],
        }),
      });
      return;
    }

    if (url.includes('/receipts/receipt-1')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'receipt-1',
          store: 'Carrefour',
          purchase_date: '2026-06-05T18:40:00Z',
          total_amount: '46.72',
          currency: 'EUR',
          created_at: '2026-06-05T18:42:00Z',
          images: [],
        }),
      });
      return;
    }

    if (url.includes('/receipts/receipt-2')) {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'receipt-2',
          store: 'Lidl',
          purchase_date: '2026-06-03T12:15:00Z',
          total_amount: '29.18',
          currency: 'EUR',
          created_at: '2026-06-03T12:17:00Z',
          images: [],
        }),
      });
      return;
    }

    await route.continue();
  });

  await page.goto('/');

  await expect(page.getByText('Connected to API')).toBeVisible();
  await expect(page.getByRole('button', { name: /Carrefour/i })).toBeVisible();
  await expect(page.getByText('milk').first()).toBeVisible();

  await page.getByRole('button', { name: /Lidl/i }).click();
  await expect(page.getByText('dish soap')).toBeVisible();
});