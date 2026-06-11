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
  raw_text?: string;
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

export interface UploadReceiptResponse {
  receipt_id: string;
  job_id: string;
  message: string;
}

export type ProcessingStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface JobStatus {
  id: string;
  receipt_id: string;
  status: ProcessingStatus;
  error_message: string | null;
  retry_count: number;
  max_attempts: number;
  next_retry_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkerStatus {
  worker_id: string;
  processor_kind: string;
  last_heartbeat: string;
  status: 'online' | 'offline';
  is_active: boolean;
}

export interface SystemStatusResponse {
  workers: WorkerStatus[];
  server_time: string;
}
