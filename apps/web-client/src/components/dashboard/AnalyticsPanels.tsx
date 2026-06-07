import type { CategorySpend, MonthlyReceiptCount, MonthlySpend, TopItem } from '../../types';
import { formatMonth, toMoney } from '../../lib/formatters';

interface AnalyticsPanelsProps {
  categorySpend: CategorySpend[];
  monthlySpend: MonthlySpend[];
  topItems: TopItem[];
  receiptsByMonth: MonthlyReceiptCount[];
  currency: string;
  onExportWorkflowStub: () => void;
}

function maxSpendValue(rows: Array<{ total_spend: string | number }>): number {
  return Math.max(...rows.map((item) => Number.parseFloat(String(item.total_spend))), 1);
}

export function AnalyticsPanels({
  categorySpend,
  monthlySpend,
  topItems,
  receiptsByMonth,
  currency,
  onExportWorkflowStub,
}: AnalyticsPanelsProps) {
  return (
    <section className="analytics-grid">
      <article className="panel chart-panel">
        <div className="panel-header">
          <div>
            <div className="section-title">Category spend</div>
            <div className="section-subtitle">Backend aggregation by category.</div>
          </div>
        </div>
        <div className="bar-list">
          {categorySpend.map((entry) => {
            const width = `${(Number.parseFloat(String(entry.total_spend)) / maxSpendValue(categorySpend)) * 100}%`;

            return (
              <div key={entry.category_id} className="bar-row">
                <div className="bar-label">{entry.category_id}</div>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width }} />
                </div>
                <div className="bar-value">{toMoney(entry.total_spend, currency)}</div>
              </div>
            );
          })}
        </div>
      </article>

      <article className="panel chart-panel">
        <div className="panel-header">
          <div>
            <div className="section-title">Monthly spend</div>
            <div className="section-subtitle">Receipt totals grouped by month.</div>
          </div>
        </div>
        <div className="bar-list">
          {monthlySpend.map((entry) => {
            const width = `${(Number.parseFloat(String(entry.total_spend)) / maxSpendValue(monthlySpend)) * 100}%`;

            return (
              <div key={`${entry.year}-${entry.month}`} className="bar-row">
                <div className="bar-label">{formatMonth(entry.year, entry.month)}</div>
                <div className="bar-track">
                  <div className="bar-fill alt" style={{ width }} />
                </div>
                <div className="bar-value">{toMoney(entry.total_spend, currency)}</div>
              </div>
            );
          })}
        </div>
      </article>

      <article className="panel chart-panel">
        <div className="panel-header">
          <div>
            <div className="section-title">Top items</div>
            <div className="section-subtitle">Most frequent normalized products.</div>
          </div>
        </div>
        <div className="top-item-list">
          {topItems.map((item) => (
            <div key={item.normalized_name} className="top-item-row">
              <div>
                <div className="item-name">{item.normalized_name}</div>
                <div className="item-origin">{item.occurrence_count} occurrences</div>
              </div>
              <div className="item-money">{toMoney(item.total_spend, currency)}</div>
            </div>
          ))}
        </div>
      </article>

      <article className="panel chart-panel">
        <div className="panel-header">
          <div>
            <div className="section-title">Receipt volume</div>
            <div className="section-subtitle">Counts by month for quick activity checks.</div>
          </div>
        </div>
        <div className="top-item-list">
          {receiptsByMonth.map((entry) => (
            <div key={`${entry.year}-${entry.month}`} className="top-item-row">
              <div>
                <div className="item-name">{formatMonth(entry.year, entry.month)}</div>
                <div className="item-origin">Monthly activity</div>
              </div>
              <div className="item-money">{entry.receipt_count}</div>
            </div>
          ))}
        </div>
        <button className="button ghost export-button" onClick={onExportWorkflowStub} type="button">
          Export workflow stub
        </button>
      </article>
    </section>
  );
}