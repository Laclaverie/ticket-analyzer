import { beforeEach, describe, expect, it, vi } from 'vitest';
import { loadDashboard, loadReceiptDetail, uploadReceipt } from '../src/api';

function okJsonResponse<T>(payload: T): Response {
  return {
    ok: true,
    status: 200,
    json: async () => payload,
  } as Response;
}

describe('api loaders', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    vi.stubGlobal('fetch', vi.fn());
  });

  it('loads dashboard from API when all requests succeed', async () => {
    const fetchMock = vi
      .mocked(globalThis.fetch)
      .mockResolvedValueOnce(
        okJsonResponse({
          items: [
            {
              id: 'receipt-api-1',
              store: 'API Store',
              purchase_date: '2026-06-01T10:00:00Z',
              total_amount: '10.00',
              currency: 'EUR',
              created_at: '2026-06-01T10:05:00Z',
            },
          ],
          total: 1,
          page: 1,
          page_size: 10,
        }),
      )
      .mockResolvedValueOnce(okJsonResponse([{ category_id: 'food', total_spend: '10.00' }]))
      .mockResolvedValueOnce(okJsonResponse([{ year: 2026, month: 6, total_spend: '10.00' }]))
      .mockResolvedValueOnce(
        okJsonResponse([{ normalized_name: 'milk', total_spend: '10.00', occurrence_count: 1 }]),
      )
      .mockResolvedValueOnce(okJsonResponse([{ year: 2026, month: 6, receipt_count: 1 }]));

    const snapshot = await loadDashboard();

    expect(snapshot.source).toBe('api');
    expect(snapshot.receipts.total).toBe(1);
    expect(snapshot.categorySpend[0]?.category_id).toBe('food');
    expect(fetchMock).toHaveBeenCalledTimes(5);
  });

  it('falls back to mock dashboard data when API fails', async () => {
    vi.mocked(globalThis.fetch).mockRejectedValue(new Error('network down'));

    const snapshot = await loadDashboard();

    expect(snapshot.source).toBe('mock');
    expect(snapshot.receipts.items.length).toBeGreaterThan(0);
    expect(snapshot.topItems.length).toBeGreaterThan(0);
  });

  it('loads receipt detail from API when both requests succeed', async () => {
    const fetchMock = vi
      .mocked(globalThis.fetch)
      .mockResolvedValueOnce(
        okJsonResponse({
          id: 'receipt-api-1',
          store: 'API Store',
          purchase_date: '2026-06-01T10:00:00Z',
          total_amount: '10.00',
          currency: 'EUR',
          created_at: '2026-06-01T10:05:00Z',
          images: [],
        }),
      )
      .mockResolvedValueOnce(
        okJsonResponse({
          receipt_id: 'receipt-api-1',
          items: [
            {
              id: 'item-1',
              receipt_item_raw_id: 'raw-1',
              normalized_name: 'milk',
              quantity: '1',
              unit_price: '2.00',
              line_total: '2.00',
              category_id: 'food',
              confidence: 0.99,
              classification_origin: 'rule',
              created_at: '2026-06-01T10:01:00Z',
            },
          ],
        }),
      );

    const detail = await loadReceiptDetail('receipt-api-1');

    expect(detail.source).toBe('api');
    expect(detail.receipt.id).toBe('receipt-api-1');
    expect(detail.items).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('falls back to mock receipt detail when API fails', async () => {
    vi.mocked(globalThis.fetch).mockRejectedValue(new Error('network down'));

    const detail = await loadReceiptDetail('receipt-demo-2');

    expect(detail.source).toBe('mock');
    expect(detail.receipt.id).toBe('receipt-demo-2');
    expect(detail.items.length).toBeGreaterThan(0);
  });

  it('uploads a receipt file successfully', async () => {
    const fetchMock = vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      okJsonResponse({
        receipt_id: 'receipt-123',
        job_id: 'job-456',
        message: 'Receipt uploaded and queued for processing.',
      }),
    );

    const file = new File(['dummy content'], 'receipt.jpg', { type: 'image/jpeg' });
    const response = await uploadReceipt(file);

    expect(response.receipt_id).toBe('receipt-123');
    expect(response.job_id).toBe('job-456');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/receipts/upload'),
      expect.objectContaining({
        method: 'POST',
        body: expect.any(FormData),
      }),
    );

    const callBody = fetchMock.mock.calls[0]?.[1]?.body as FormData;
    expect(callBody.get('file')).toBe(file);
  });

  it('throws error when upload fails', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce({
      ok: false,
      status: 400,
    } as Response);

    const file = new File(['dummy content'], 'receipt.jpg', { type: 'image/jpeg' });

    await expect(uploadReceipt(file)).rejects.toThrow('Upload failed: 400');
  });
});