import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../src/App';

function okJsonResponse<T>(payload: T): Response {
  return {
    ok: true,
    status: 200,
    json: async () => payload,
  } as Response;
}

describe('DashboardPage integration', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();

    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);

      if (url.includes('/receipts?page=1&page_size=10')) {
        return okJsonResponse({
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
        });
      }

      if (url.includes('/analytics/spending/by-category')) {
        return okJsonResponse([{ category_id: 'food', total_spend: '75.90' }]);
      }

      if (url.includes('/analytics/spending/by-month')) {
        return okJsonResponse([{ year: 2026, month: 6, total_spend: '75.90' }]);
      }

      if (url.includes('/analytics/top-items?limit=5')) {
        return okJsonResponse([{ normalized_name: 'milk', total_spend: '12.50', occurrence_count: 2 }]);
      }

      if (url.includes('/analytics/receipts/by-month')) {
        return okJsonResponse([{ year: 2026, month: 6, receipt_count: 2 }]);
      }

      if (url.includes('/receipts/receipt-1/items')) {
        return okJsonResponse({
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
        });
      }

      if (url.includes('/receipts/receipt-2/items')) {
        return okJsonResponse({
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
        });
      }

      if (url.includes('/receipts/receipt-1')) {
        return okJsonResponse({
          id: 'receipt-1',
          store: 'Carrefour',
          purchase_date: '2026-06-05T18:40:00Z',
          total_amount: '46.72',
          currency: 'EUR',
          created_at: '2026-06-05T18:42:00Z',
          images: [],
        });
      }

      if (url.includes('/receipts/receipt-2')) {
        return okJsonResponse({
          id: 'receipt-2',
          store: 'Lidl',
          purchase_date: '2026-06-03T12:15:00Z',
          total_amount: '29.18',
          currency: 'EUR',
          created_at: '2026-06-03T12:17:00Z',
          images: [],
        });
      }

      throw new Error(`Unhandled request in test: ${url}`);
    });

    vi.stubGlobal('fetch', fetchMock);
  });

  it('loads from API and updates receipt detail when another receipt is selected', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Connected to API')).toBeTruthy();
    });

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Carrefour/i })).toBeTruthy();
      expect(screen.getAllByText('milk').length).toBeGreaterThan(0);
    });

    fireEvent.click(screen.getByRole('button', { name: /Lidl/i }));

    await waitFor(() => {
      expect(screen.getByText('dish soap')).toBeTruthy();
    });
  });
});