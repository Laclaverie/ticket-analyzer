interface StatusPillProps {
  statusLabel: string;
  isLive: boolean;
}

export function StatusPill({ statusLabel, isLive }: StatusPillProps) {
  return (
    <div className={`status-pill ${isLive ? 'live' : 'demo'}`}>
      <span className="status-dot" />
      {statusLabel}
    </div>
  );
}