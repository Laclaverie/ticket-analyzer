import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ReceiptListPanel } from '../src/components/dashboard/ReceiptListPanel';

describe('ReceiptListPanel', () => {
  it('renders receipts and emits selection events', () => {
    const onSelectReceipt = vi.fn();

    render(
      <ReceiptListPanel
        receipts={[
          {
            id: 'receipt-1',
            store: 'Carrefour',
            purchase_date: '2026-06-05T18:40:00Z',
            total_amount: '46.72',
            currency: 'EUR',
            created_at: '2026-06-05T18:42:00Z',
          },
        ]}
        total={1}
        selectedReceiptId={null}
        loading={false}
        onSelectReceipt={onSelectReceipt}
      />,
    );

    expect(screen.getByText('Carrefour')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /Carrefour/i }));
    expect(onSelectReceipt).toHaveBeenCalledWith('receipt-1');
  });
});