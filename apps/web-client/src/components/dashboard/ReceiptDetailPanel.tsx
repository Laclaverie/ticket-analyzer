import type { ReceiptDetailSnapshot } from '../../types';
import { formatDate, toMoney } from '../../lib/formatters';

interface ReceiptDetailPanelProps {
  selectedReceipt: ReceiptDetailSnapshot | null;
  loading: boolean;
}

export function ReceiptDetailPanel({ selectedReceipt, loading }: ReceiptDetailPanelProps) {
  const activeReceipt = selectedReceipt?.receipt ?? null;

  return (
    <article className="panel detail-panel">
      <div className="panel-header">
        <div>
          <div className="section-title">Receipt detail</div>
          <div className="section-subtitle">Items extracted by the backend pipeline.</div>
        </div>
        <div className="panel-chip">{loading ? 'Loading...' : selectedReceipt?.source ?? 'n/a'}</div>
      </div>

      {activeReceipt ? (
        <>
          <div className="detail-summary">
            <div>
              <div className="detail-store">{activeReceipt.store ?? 'Unknown store'}</div>
              <div className="detail-meta">{formatDate(activeReceipt.purchase_date)}</div>
            </div>
            <div className="detail-total">{toMoney(activeReceipt.total_amount, activeReceipt.currency)}</div>
          </div>

          <div className="item-table">
            <div className="item-table-header">
              <span>Item</span>
              <span>Category</span>
              <span>Total</span>
            </div>
            {selectedReceipt?.items.length ? (
              selectedReceipt.items.map((item) => (
                <div key={item.id} className="item-row">
                  <div>
                    <div className="item-name">{item.normalized_name}</div>
                    <div className="item-origin">
                      {item.classification_origin} · confidence {Math.round(item.confidence * 100)}%
                    </div>
                  </div>
                  <div className="item-category">{item.category_id ?? 'uncategorized'}</div>
                  <div className="item-money">{toMoney(item.line_total, activeReceipt.currency)}</div>
                </div>
              ))
            ) : (
              <div className="empty-state">No items yet for this receipt.</div>
            )}
          </div>
        </>
      ) : (
        <div className="empty-state">Select a receipt to inspect its line items.</div>
      )}
    </article>
  );
}