import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../src/App';

const { exportReceiptsCsvMock, refreshDashboardMock, setSelectedReceiptIdMock } = vi.hoisted(() => ({
  exportReceiptsCsvMock: vi.fn(),
  refreshDashboardMock: vi.fn(),
  setSelectedReceiptIdMock: vi.fn(),
}));

vi.mock('../src/api', () => ({
  exportReceiptsCsv: exportReceiptsCsvMock,
}));

vi.mock('../src/hooks/useDashboardData', () => ({
  useDashboardData: () => ({
    dashboard: {
      receipts: {
        items: [
          {
            id: 'receipt-1',
            store: 'Carrefour',
            purchase_date: '2026-06-05T18:40:00Z',
            total_amount: '46.72',
            currency: 'EUR',
            created_at: '2026-06-05T18:42:00Z',
          },
        ],
        total: 1,
        page: 1,
        page_size: 10,
      },
      categorySpend: [{ category_id: 'food', total_spend: '46.72' }],
      monthlySpend: [{ year: 2026, month: 6, total_spend: '46.72' }],
      topItems: [{ normalized_name: 'milk', total_spend: '12.50', occurrence_count: 1 }],
      receiptsByMonth: [{ year: 2026, month: 6, receipt_count: 1 }],
      source: 'mock',
    },
    selectedReceiptId: 'receipt-1',
    selectedReceipt: {
      receipt: {
        id: 'receipt-1',
        store: 'Carrefour',
        purchase_date: '2026-06-05T18:40:00Z',
        total_amount: '46.72',
        currency: 'EUR',
        created_at: '2026-06-05T18:42:00Z',
        images: [],
      },
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
      source: 'mock',
    },
    loadingDashboard: false,
    loadingReceipt: false,
    setSelectedReceiptId: setSelectedReceiptIdMock,
    refreshDashboard: refreshDashboardMock,
  }),
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    exportReceiptsCsvMock.mockClear();
    refreshDashboardMock.mockClear();
    setSelectedReceiptIdMock.mockClear();
  });

  it('renders the main dashboard sections', () => {
    render(<App />);

    expect(screen.getByText('Category spend')).toBeTruthy();
    expect(screen.getByText('Receipt detail')).toBeTruthy();
    expect(screen.getAllByText('Receipts').length).toBeGreaterThan(1);
  });

  it('uses the mocked export handler', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Export receipts CSV/i }));

    expect(exportReceiptsCsvMock).toHaveBeenCalledTimes(1);
    expect(exportReceiptsCsvMock).toHaveBeenCalledWith({
      items: [
        {
          id: 'receipt-1',
          store: 'Carrefour',
          purchase_date: '2026-06-05T18:40:00Z',
          total_amount: '46.72',
          currency: 'EUR',
          created_at: '2026-06-05T18:42:00Z',
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
    });
  });
});