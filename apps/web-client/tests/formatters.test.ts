import { describe, expect, it } from 'vitest';
import { formatDate, formatMonth, toMoney } from '../src/lib/formatters';

describe('formatters', () => {
  it('formats money values', () => {
    const formatted = toMoney('12.5', 'EUR');

    expect(formatted).toContain('12');
    expect(formatted).toContain('€');
  });

  it('formats dates and months', () => {
    expect(formatDate('2026-06-07T10:20:30Z')).not.toBe('2026-06-07T10:20:30Z');
    expect(formatMonth(2026, 6)).toContain('2026');
  });
});