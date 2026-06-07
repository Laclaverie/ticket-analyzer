import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useDashboardData } from '../src/hooks/useDashboardData';
import type { DashboardSnapshot, ReceiptDetailSnapshot } from '../src/types';

const { loadDashboardMock, loadReceiptDetailMock } = vi.hoisted(() => ({
  loadDashboardMock: vi.fn(),
  loadReceiptDetailMock: vi.fn(),
}));

vi.mock('../src/api', () => ({
  loadDashboard: loadDashboardMock,
  loadReceiptDetail: loadReceiptDetailMock,
}));

const baseDashboard: DashboardSnapshot = {
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
  },
  categorySpend: [{ category_id: 'food', total_spend: '46.72' }],
  monthlySpend: [{ year: 2026, month: 6, total_spend: '75.90' }],
  topItems: [{ normalized_name: 'milk', total_spend: '12.50', occurrence_count: 1 }],
  receiptsByMonth: [{ year: 2026, month: 6, receipt_count: 2 }],
  source: 'api',
};

const baseReceiptDetail: ReceiptDetailSnapshot = {
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
  source: 'api',
};

describe('useDashboardData', () => {
  beforeEach(() => {
    loadDashboardMock.mockReset();
    loadReceiptDetailMock.mockReset();
  });

  it('loads dashboard and then first receipt detail', async () => {
    loadDashboardMock.mockResolvedValue(baseDashboard);
    loadReceiptDetailMock.mockResolvedValue(baseReceiptDetail);

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.loadingDashboard).toBe(true);

    await waitFor(() => {
      expect(result.current.loadingDashboard).toBe(false);
    });

    expect(result.current.dashboard?.source).toBe('api');
    expect(result.current.selectedReceiptId).toBe('receipt-1');

    await waitFor(() => {
      expect(result.current.loadingReceipt).toBe(false);
      expect(result.current.selectedReceipt?.receipt.id).toBe('receipt-1');
    });

    expect(loadDashboardMock).toHaveBeenCalledTimes(1);
    expect(loadReceiptDetailMock).toHaveBeenCalledWith('receipt-1');
  });

  it('does not request receipt detail when dashboard has no receipts', async () => {
    const emptyDashboard: DashboardSnapshot = {
      ...baseDashboard,
      receipts: {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
      },
    };
    loadDashboardMock.mockResolvedValue(emptyDashboard);

    const { result } = renderHook(() => useDashboardData());

    await waitFor(() => {
      expect(result.current.loadingDashboard).toBe(false);
    });

    expect(result.current.dashboard?.receipts.total).toBe(0);
    expect(result.current.selectedReceiptId).toBeNull();
    expect(loadReceiptDetailMock).not.toHaveBeenCalled();
  });

  it('refreshes dashboard without overriding an explicit selection', async () => {
    loadDashboardMock.mockResolvedValue(baseDashboard);
    loadReceiptDetailMock.mockResolvedValue(baseReceiptDetail);

    const { result } = renderHook(() => useDashboardData());

    await waitFor(() => {
      expect(result.current.loadingDashboard).toBe(false);
      expect(result.current.selectedReceiptId).toBe('receipt-1');
    });

    const refreshedDashboard: DashboardSnapshot = {
      ...baseDashboard,
      receipts: {
        ...baseDashboard.receipts,
        items: [
          {
            id: 'receipt-3',
            store: 'Monoprix',
            purchase_date: '2026-06-07T10:00:00Z',
            total_amount: '61.90',
            currency: 'EUR',
            created_at: '2026-06-07T10:02:00Z',
          },
        ],
      },
    };
    loadDashboardMock.mockResolvedValueOnce(refreshedDashboard);

    await act(async () => {
      result.current.setSelectedReceiptId('manual-selection');
    });

    await act(async () => {
      await result.current.refreshDashboard();
    });

    expect(result.current.dashboard?.receipts.items[0]?.id).toBe('receipt-3');
    expect(result.current.selectedReceiptId).toBe('manual-selection');
  });
});