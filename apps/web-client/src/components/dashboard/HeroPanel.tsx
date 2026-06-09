import { useRef, useState } from 'react';
import { ActionButton } from '../ui/ActionButton';
import { StatusPill } from '../ui/StatusPill';
import { uploadReceipt } from '../../api';

interface HeroPanelProps {
  statusLabel: string;
  isLive: boolean;
  onExport: () => void;
  onRefresh: () => void;
}

export function HeroPanel({ statusLabel, isLive, onExport, onRefresh }: HeroPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setUploading(true);
    try {
      await uploadReceipt(file);
      onRefresh();
    } catch (error) {
      console.error('Upload failed', error);
      alert('Failed to upload receipt. Please check the backend connection.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

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
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          style={{ display: 'none' }}
          aria-label="Upload receipt image"
        />
        <ActionButton variant="ghost" onClick={handleUploadClick} disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload receipt'}
        </ActionButton>
        <ActionButton variant="ghost" onClick={onExport}>
          Export receipts CSV
        </ActionButton>
        <ActionButton onClick={onRefresh}>Refresh</ActionButton>
      </div>
    </section>
  );
}