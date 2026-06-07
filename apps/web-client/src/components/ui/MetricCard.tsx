import type { ReactNode } from 'react';

interface MetricCardProps {
  label: string;
  value: ReactNode;
  footnote: ReactNode;
  className?: string;
}

export function MetricCard({ label, value, footnote, className = '' }: MetricCardProps) {
  return (
    <article className={`panel metric-card ${className}`.trim()}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-footnote">{footnote}</div>
    </article>
  );
}