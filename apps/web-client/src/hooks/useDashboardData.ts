import { useEffect, useState } from 'react';
import { loadDashboard, loadReceiptDetail } from '../api';
import type { DashboardSnapshot, ReceiptDetailSnapshot } from '../types';

export function useDashboardData() {
  const [dashboard, setDashboard] = useState<DashboardSnapshot | null>(null);
  const [selectedReceiptId, setSelectedReceiptId] = useState<string | null>(null);
  const [selectedReceipt, setSelectedReceipt] = useState<ReceiptDetailSnapshot | null>(null);
  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [loadingReceipt, setLoadingReceipt] = useState(false);

  useEffect(() => {
    let active = true;

    loadDashboard()
      .then((snapshot) => {
        if (!active) {
          return;
        }

        setDashboard(snapshot);
        setSelectedReceiptId((current) => current ?? snapshot.receipts.items[0]?.id ?? null);
      })
      .finally(() => {
        if (active) {
          setLoadingDashboard(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedReceiptId) {
      return;
    }

    let active = true;
    setLoadingReceipt(true);

    loadReceiptDetail(selectedReceiptId)
      .then((snapshot) => {
        if (active) {
          setSelectedReceipt(snapshot);
        }
      })
      .finally(() => {
        if (active) {
          setLoadingReceipt(false);
        }
      });

    return () => {
      active = false;
    };
  }, [selectedReceiptId]);

  return {
    dashboard,
    selectedReceiptId,
    selectedReceipt,
    loadingDashboard,
    loadingReceipt,
    setSelectedReceiptId,
    refreshDashboard: async () => {
      const snapshot = await loadDashboard();
      setDashboard(snapshot);
      setSelectedReceiptId((current) => current ?? snapshot.receipts.items[0]?.id ?? null);
      return snapshot;
    },
  };
}