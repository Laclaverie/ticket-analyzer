import { ActionButton } from '../ui/ActionButton';
import { StatusPill } from '../ui/StatusPill';

interface HeroPanelProps {
  statusLabel: string;
  isLive: boolean;
  onExport: () => void;
  onRefresh: () => void;
}

export function HeroPanel({ statusLabel, isLive, onExport, onRefresh }: HeroPanelProps) {
  return (
    <section className="hero panel">
      <div>
        <div className="eyebrow">Ticket Analyzer</div>
        <h1>Desktop-first receipt analysis, without leaving the browser.</h1>
        <p className="hero-copy">
          Inspect the latest receipts, review category spending, and export visible data from one focused PC
          dashboard.
        </p>
      </div>

      <div className="hero-actions">
        <StatusPill statusLabel={statusLabel} isLive={isLive} />
        <ActionButton variant="ghost" onClick={onExport}>
          Export receipts CSV
        </ActionButton>
        <ActionButton onClick={onRefresh}>Refresh</ActionButton>
      </div>
    </section>
  );
}