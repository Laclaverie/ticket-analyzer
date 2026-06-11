import type {
  CategorySpend,
  DashboardSnapshot,
  MonthlyReceiptCount,
  MonthlySpend,
  ReceiptDetailSnapshot,
  ReceiptListResponse,
  ReceiptItemsResponse,
  ReceiptDetail,
  TopItem,
  UploadReceiptResponse,
  JobStatus,
  SystemStatusResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const jsonHeaders = {
  Accept: 'application/json',
};

function buildUrl(path: string): string {
  return new URL(path, API_BASE_URL).toString();
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(buildUrl(path), { headers: jsonHeaders });
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

const mockReceipts: ReceiptListResponse = {
  items: [
    {
      id: 'receipt-demo-1',
      store: 'Carrefour',
      purchase_date: '2026-06-05T18:40:00Z',
      total_amount: '46.72',
      currency: 'EUR',
      created_at: '2026-06-05T18:42:00Z',
    },
    {
      id: 'receipt-demo-2',
      store: 'Lidl',
      purchase_date: '2026-06-03T12:15:00Z',
      total_amount: '29.18',
      currency: 'EUR',
      created_at: '2026-06-03T12:17:00Z',
    },
    {
      id: 'receipt-demo-3',
      store: 'Monoprix',
      purchase_date: '2026-05-29T19:05:00Z',
      total_amount: '61.90',
      currency: 'EUR',
      created_at: '2026-05-29T19:08:00Z',
    },
  ],
  total: 3,
  page: 1,
  page_size: 10,
};

const mockCategorySpend: CategorySpend[] = [
  { category_id: 'food', total_spend: '92.55' },
  { category_id: 'household', total_spend: '27.80' },
  { category_id: 'hygiene', total_spend: '17.45' },
  { category_id: 'drinks', total_spend: '9.99' },
];

const mockMonthlySpend: MonthlySpend[] = [
  { year: 2026, month: 4, total_spend: '135.40' },
  { year: 2026, month: 5, total_spend: '173.20' },
  { year: 2026, month: 6, total_spend: '118.90' },
];

const mockTopItems: TopItem[] = [
  { normalized_name: 'milk', total_spend: '14.40', occurrence_count: 5 },
  { normalized_name: 'eggs', total_spend: '11.95', occurrence_count: 4 },
  { normalized_name: 'bread', total_spend: '10.20', occurrence_count: 4 },
  { normalized_name: 'dish soap', total_spend: '8.75', occurrence_count: 2 },
];

const mockReceiptsByMonth: MonthlyReceiptCount[] = [
  { year: 2026, month: 4, receipt_count: 2 },
  { year: 2026, month: 5, receipt_count: 3 },
  { year: 2026, month: 6, receipt_count: 2 },
];

const mockReceiptDetail = new Map<string, ReceiptDetail>([
  [
    'receipt-demo-1',
    {
      ...mockReceipts.items[0],
      images: [
        {
          id: 'image-demo-1',
          file_path: '/demo/carrefour-receipt.jpg',
          file_hash: 'demo-hash-1',
          created_at: '2026-06-05T18:40:30Z',
        },
      ],
    },
  ],
  [
    'receipt-demo-2',
    {
      ...mockReceipts.items[1],
      images: [
        {
          id: 'image-demo-2',
          file_path: '/demo/lidl-receipt.jpg',
          file_hash: 'demo-hash-2',
          created_at: '2026-06-03T12:15:30Z',
        },
      ],
    },
  ],
  [
    'receipt-demo-3',
    {
      ...mockReceipts.items[2],
      images: [
        {
          id: 'image-demo-3',
          file_path: '/demo/monoprix-receipt.jpg',
          file_hash: 'demo-hash-3',
          created_at: '2026-05-29T19:05:30Z',
        },
      ],
    },
  ],
]);

const mockReceiptItems = new Map<string, ReceiptItemsResponse>([
  [
    'receipt-demo-1',
    {
      receipt_id: 'receipt-demo-1',
      items: [
        {
          id: 'raw-1',
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
        {
          id: 'raw-2',
          receipt_item_raw_id: 'raw-2',
          normalized_name: 'bread',
          quantity: '1',
          unit_price: '1.25',
          line_total: '1.25',
          category_id: 'food',
          confidence: 0.95,
          classification_origin: 'rule',
          created_at: '2026-06-05T18:41:00Z',
        },
      ],
    },
  ],
  [
    'receipt-demo-2',
    {
      receipt_id: 'receipt-demo-2',
      items: [
        {
          id: 'raw-3',
          receipt_item_raw_id: 'raw-3',
          normalized_name: 'dish soap',
          quantity: '1',
          unit_price: '3.95',
          line_total: '3.95',
          category_id: 'household',
          confidence: 0.91,
          classification_origin: 'rule',
          created_at: '2026-06-03T12:16:00Z',
        },
      ],
    },
  ],
  [
    'receipt-demo-3',
    {
      receipt_id: 'receipt-demo-3',
      items: [
        {
          id: 'raw-4',
          receipt_item_raw_id: 'raw-4',
          normalized_name: 'eggs',
          quantity: '6',
          unit_price: '0.89',
          line_total: '5.34',
          category_id: 'food',
          confidence: 0.97,
          classification_origin: 'rule',
          created_at: '2026-05-29T19:06:00Z',
        },
      ],
    },
  ],
]);

async function safeFetchDashboard(): Promise<DashboardSnapshot> {
  try {
    const [receipts, categorySpend, monthlySpend, topItems, receiptsByMonth] = await Promise.all([
      fetchJson<ReceiptListResponse>('/receipts?page=1&page_size=10'),
      fetchJson<CategorySpend[]>('/analytics/spending/by-category'),
      fetchJson<MonthlySpend[]>('/analytics/spending/by-month'),
      fetchJson<TopItem[]>('/analytics/top-items?limit=5'),
      fetchJson<MonthlyReceiptCount[]>('/analytics/receipts/by-month'),
    ]);

    return {
      receipts,
      categorySpend,
      monthlySpend,
      topItems,
      receiptsByMonth,
      source: 'api',
    };
  } catch {
    return {
      receipts: mockReceipts,
      categorySpend: mockCategorySpend,
      monthlySpend: mockMonthlySpend,
      topItems: mockTopItems,
      receiptsByMonth: mockReceiptsByMonth,
      source: 'mock',
    };
  }
}

async function safeFetchReceiptDetail(receiptId: string): Promise<ReceiptDetailSnapshot> {
  try {
    const [receipt, items] = await Promise.all([
      fetchJson<ReceiptDetail>(`/receipts/${receiptId}`),
      fetchJson<ReceiptItemsResponse>(`/receipts/${receiptId}/items`),
    ]);

    return {
      receipt,
      items: items.items,
      source: 'api',
    };
  } catch {
    const receipt = mockReceiptDetail.get(receiptId) ?? (mockReceipts.items[0] as ReceiptDetail);
    const items = mockReceiptItems.get(receiptId)?.items ?? [];

    return {
      receipt,
      items,
      source: 'mock',
    };
  }
}

export async function loadDashboard(): Promise<DashboardSnapshot> {
  return safeFetchDashboard();
}

export async function loadReceiptDetail(receiptId: string): Promise<ReceiptDetailSnapshot> {
  return safeFetchReceiptDetail(receiptId);
}

export async function uploadReceipt(file: File): Promise<UploadReceiptResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(buildUrl('/receipts/upload'), {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }

  return (await response.json()) as UploadReceiptResponse;
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  return fetchJson<JobStatus>(`/jobs/${jobId}`);
}

export async function getReceiptItems(receiptId: string): Promise<ReceiptItemsResponse> {
  return fetchJson<ReceiptItemsResponse>(`/receipts/${receiptId}/items`);
}

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  return fetchJson<SystemStatusResponse>('/system/status');
}

export function exportReceiptsCsv(receipts: ReceiptListResponse): void {
  const rows = [
    ['id', 'store', 'purchase_date', 'total_amount', 'currency', 'created_at'],
    ...receipts.items.map((receipt) => [
      receipt.id,
      receipt.store ?? '',
      receipt.purchase_date ?? '',
      String(receipt.total_amount ?? ''),
      receipt.currency,
      receipt.created_at,
    ]),
  ];

  const csv = rows
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n');

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'ticket-analyzer-receipts.csv';
  anchor.click();
  URL.revokeObjectURL(url);
}
