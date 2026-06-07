import { exportReceiptsCsv } from '../api';
import { AnalyticsPanels } from '../components/dashboard/AnalyticsPanels';
import { HeroPanel } from '../components/dashboard/HeroPanel';
import { ReceiptDetailPanel } from '../components/dashboard/ReceiptDetailPanel';
import { ReceiptListPanel } from '../components/dashboard/ReceiptListPanel';
import { MetricCard } from '../components/ui/MetricCard';
import { Shell } from '../components/Shell';
import { useDashboardData } from '../hooks/useDashboardData';
import { toMoney } from '../lib/formatters';

function downloadItem(item: string): void {
  const blob = new Blob([item], { type: 'text/plain;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'ticket-analyzer-export.txt';
  anchor.click();
  URL.revokeObjectURL(url);
}

export function DashboardPage() {
  const {
    dashboard,
    selectedReceiptId,
    selectedReceipt,
    loadingDashboard,
    loadingReceipt,
    setSelectedReceiptId,
    refreshDashboard,
  } = useDashboardData();

  const currency = dashboard?.receipts.items[0]?.currency ?? 'EUR';
  const categorySpend = dashboard?.categorySpend ?? [];
  const monthlySpend = dashboard?.monthlySpend ?? [];
  const topItems = dashboard?.topItems ?? [];
  const receiptsByMonth = dashboard?.receiptsByMonth ?? [];
  const totalSpend = categorySpend.reduce((total, row) => total + Number.parseFloat(String(row.total_spend)), 0);
  const receiptCount = dashboard?.receipts.total ?? 0;
  const averageReceipt = receiptCount > 0 ? totalSpend / receiptCount : 0;
  const statusLabel = dashboard?.source === 'api' ? 'Connected to API' : dashboard ? 'Demo data' : 'Loading';
  const topCategory = categorySpend[0]?.category_id ?? 'n/a';
  const topItem = topItems[0]?.normalized_name ?? 'n/a';

  return (
    <Shell>
      <main className="app">
        <HeroPanel
          statusLabel={statusLabel}
          isLive={dashboard?.source === 'api'}
          onExport={() => {
            if (!dashboard) {
              return;
            }

            exportReceiptsCsv(dashboard.receipts);
          }}
          onRefresh={() => {
            void refreshDashboard();
          }}
        />

        <section className="metrics">
          <MetricCard label="Receipts" value={loadingDashboard ? '...' : receiptCount} footnote="Tracked receipts in the current list" />
          <MetricCard
            label="Total spend"
            value={loadingDashboard ? '...' : toMoney(totalSpend, currency)}
            footnote="Sum of the category spending snapshot"
          />
          <MetricCard
            label="Average receipt"
            value={loadingDashboard ? '...' : toMoney(averageReceipt, currency)}
            footnote="Simple overview for quick comparison"
          />
          <MetricCard
            label="Top category"
            value={loadingDashboard ? '...' : topCategory}
            footnote={topItem}
            className="metric-sm"
          />
        </section>

        <section className="dashboard-grid">
          <ReceiptListPanel
            receipts={dashboard?.receipts.items ?? []}
            total={dashboard?.receipts.total ?? 0}
            selectedReceiptId={selectedReceiptId}
            loading={loadingDashboard}
            onSelectReceipt={setSelectedReceiptId}
          />

          <ReceiptDetailPanel selectedReceipt={selectedReceipt} loading={loadingReceipt} />
        </section>

        <AnalyticsPanels
          categorySpend={categorySpend}
          monthlySpend={monthlySpend}
          topItems={topItems}
          receiptsByMonth={receiptsByMonth}
          currency={currency}
          onExportWorkflowStub={() => downloadItem('CSV export placeholder for future detailed export workflow')}
        />
      </main>
    </Shell>
  );
}