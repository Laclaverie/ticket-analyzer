import type { ReceiptSummary } from '../../types';
import { formatDate, toMoney } from '../../lib/formatters';
import { ActionButton } from '../ui/ActionButton';

interface ReceiptListPanelProps {
  receipts: ReceiptSummary[];
  total: number;
  selectedReceiptId: string | null;
  loading: boolean;
  onSelectReceipt: (receiptId: string) => void;
}

export function ReceiptListPanel({ receipts, total, selectedReceiptId, loading, onSelectReceipt }: ReceiptListPanelProps) {
  return (
    <article className="panel list-panel">
      <div className="panel-header">
        <div>
          <div className="section-title">Receipts</div>
          <div className="section-subtitle">Select a receipt to inspect its items.</div>
        </div>
        <div className="panel-chip">{total} total</div>
      </div>

      <div className="receipt-list">
        {loading && <div className="empty-state">Loading receipts...</div>}
        {!loading &&
          receipts.map((receipt) => {
            const selected = receipt.id === selectedReceiptId;
            return (
              <ActionButton
                key={receipt.id}
                className={`receipt-row ${selected ? 'selected' : ''}`}
                onClick={() => onSelectReceipt(receipt.id)}
              >
                <div>
                  <div className="receipt-store">{receipt.store ?? 'Unknown store'}</div>
                  <div className="receipt-meta">
                    {formatDate(receipt.purchase_date)} · {receipt.currency}
                  </div>
                </div>
                <div className="receipt-total">{toMoney(receipt.total_amount, receipt.currency)}</div>
              </ActionButton>
            );
          })}
      </div>
    </article>
  );
}