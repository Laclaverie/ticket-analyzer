import type { ReactNode } from 'react';

interface ShellProps {
  children: ReactNode;
}

export function Shell({ children }: ShellProps) {
  return (
    <div className="shell">
      <div className="backdrop backdrop-a" />
      <div className="backdrop backdrop-b" />
      {children}
    </div>
  );
}