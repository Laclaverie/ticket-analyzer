export interface ReceiptSummary {
  id: string;
  store: string | null;
  purchase_date: string | null;
  total_amount: string | number | null;
  currency: string;
  created_at: string;
}

export interface ReceiptListResponse {
  items: ReceiptSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReceiptImage {
  id: string;
  file_path: string;
  file_hash: string;
  created_at: string;
}

export interface ReceiptDetail extends ReceiptSummary {
  images: ReceiptImage[];
}

export interface NormalizedItem {
  id: string;
  receipt_item_raw_id: string;
  normalized_name: string;
  quantity: string | number | null;
  unit_price: string | number | null;
  line_total: string | number | null;
  category_id: string | null;
  confidence: number;
  classification_origin: string;
  created_at: string;
}

export interface CategorySpend {
  category_id: string;
  total_spend: string | number;
}

export interface MonthlySpend {
  year: number;
  month: number;
  total_spend: string | number;
}

export interface TopItem {
  normalized_name: string;
  total_spend: string | number;
  occurrence_count: number;
}

export interface MonthlyReceiptCount {
  year: number;
  month: number;
  receipt_count: number;
}

export interface ReceiptItemsResponse {
  receipt_id: string;
  items: NormalizedItem[];
}

export interface DashboardSnapshot {
  receipts: ReceiptListResponse;
  categorySpend: CategorySpend[];
  monthlySpend: MonthlySpend[];
  topItems: TopItem[];
  receiptsByMonth: MonthlyReceiptCount[];
  source: 'api' | 'mock';
}

export interface ReceiptDetailSnapshot {
  receipt: ReceiptDetail;
  items: NormalizedItem[];
  source: 'api' | 'mock';
}