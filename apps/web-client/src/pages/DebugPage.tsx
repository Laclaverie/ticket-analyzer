import React, { useState, useEffect, useRef } from 'react';
import { uploadReceipt, getJobStatus } from '../api';
import { UploadReceiptResponse, JobStatus } from '../types';

export const DebugPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadResponse, setUploadResponse] = useState<UploadReceiptResponse | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rawRequest, setRawRequest] = useState<string | null>(null);

  const pollingIntervalRef = useRef<number | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setUploadResponse(null);
    setJobStatus(null);

    // Simulate raw request view
    setRawRequest(`POST /receipts/upload\nContent-Type: multipart/form-data\n\nFile: ${file.name} (${file.size} bytes)`);

    try {
      const response = await uploadReceipt(file);
      setUploadResponse(response);
      startPolling(response.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const startPolling = (jobId: string) => {
    if (pollingIntervalRef.current) {
      window.clearInterval(pollingIntervalRef.current);
    }

    const poll = async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);
        if (status.status === 'completed' || status.status === 'failed') {
          if (pollingIntervalRef.current) {
            window.clearInterval(pollingIntervalRef.current);
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    poll();
    pollingIntervalRef.current = window.setInterval(poll, 2000);
  };

  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        window.clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h1>Phone Simulator (Debug)</h1>
      <p>Use this page to simulate a mobile phone uploading a receipt photo.</p>

      <section style={{ marginBottom: '30px', padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h2>1. Upload Receipt</h2>
        <form onSubmit={handleUpload}>
          <div style={{ marginBottom: '10px' }}>
            <input type="file" onChange={handleFileChange} accept="image/*" />
          </div>
          <button type="submit" disabled={!file || loading} style={{ padding: '8px 16px', cursor: 'pointer' }}>
            {loading ? 'Uploading...' : 'Send to API'}
          </button>
        </form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </section>

      {rawRequest && (
        <section style={{ marginBottom: '30px' }}>
          <h2>Raw Request Overview</h2>
          <pre style={{ backgroundColor: '#f4f4f4', padding: '10px', borderRadius: '4px', overflowX: 'auto' }}>
            {rawRequest}
          </pre>
        </section>
      )}

      {uploadResponse && (
        <section style={{ marginBottom: '30px' }}>
          <h2>API Response</h2>
          <pre style={{ backgroundColor: '#f4f4f4', padding: '10px', borderRadius: '4px', overflowX: 'auto' }}>
            {JSON.stringify(uploadResponse, null, 2)}
          </pre>
        </section>
      )}

      {jobStatus && (
        <section style={{ marginBottom: '30px' }}>
          <h2>Backend Processing Status</h2>
          <div style={{ padding: '15px', backgroundColor: '#eef', borderRadius: '8px' }}>
            <p><strong>Status:</strong> <span style={{
              fontWeight: 'bold',
              color: jobStatus.status === 'completed' ? 'green' : jobStatus.status === 'failed' ? 'red' : 'blue'
            }}>{jobStatus.status.toUpperCase()}</span></p>
            <p><strong>Job ID:</strong> {jobStatus.id}</p>
            <p><strong>Receipt ID:</strong> {jobStatus.receipt_id}</p>
            {jobStatus.error_message && <p style={{ color: 'red' }}><strong>Error:</strong> {jobStatus.error_message}</p>}
            <details>
              <summary>View Full Job Object</summary>
              <pre style={{ fontSize: '12px' }}>{JSON.stringify(jobStatus, null, 2)}</pre>
            </details>
          </div>
        </section>
      )}
    </div>
  );
};
