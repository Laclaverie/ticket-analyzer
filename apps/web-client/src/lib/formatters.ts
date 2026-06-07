export function toMoney(value: string | number | null | undefined, currency = 'EUR'): string {
  const numeric = typeof value === 'number' ? value : Number.parseFloat(value ?? '0');
  if (Number.isNaN(numeric)) {
    return '-';
  }

  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency,
  }).format(numeric);
}

export function formatMonth(year: number, month: number): string {
  return new Intl.DateTimeFormat('fr-FR', {
    month: 'short',
    year: 'numeric',
  }).format(new Date(year, month - 1, 1));
}

export function formatDate(value: string | null | undefined): string {
  if (!value) {
    return '-';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date);
}