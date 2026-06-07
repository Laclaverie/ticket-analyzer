import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface ActionButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'solid' | 'ghost';
}

export function ActionButton({ children, variant = 'solid', className = '', ...props }: ActionButtonProps) {
  return (
    <button
      className={`button ${variant === 'ghost' ? 'ghost' : ''} ${className}`.trim()}
      type="button"
      {...props}
    >
      {children}
    </button>
  );
}