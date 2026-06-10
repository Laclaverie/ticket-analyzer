import React, { useState, useEffect, useRef } from 'react';
import { uploadReceipt, getJobStatus, getReceiptItems } from '../api';
import { UploadReceiptResponse, JobStatus, NormalizedItem } from '../types';

export const DebugPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadResponse, setUploadResponse] = useState<UploadReceiptResponse | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [extractedItems, setExtractedItems] = useState<NormalizedItem[]>([]);
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
    setExtractedItems([]);

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
        if (status.status === 'completed') {
          if (pollingIntervalRef.current) {
            window.clearInterval(pollingIntervalRef.current);
          }
          // Fetch the results
          const itemsResp = await getReceiptItems(status.receipt_id);
          setExtractedItems(itemsResp.items);
        } else if (status.status === 'failed') {
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
    <div style={{
      padding: '20px',
      maxWidth: '1000px',
      margin: '20px auto',
      fontFamily: 'sans-serif',
      color: '#333',
      backgroundColor: '#fff',
      borderRadius: '12px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
    }}>
      <h1 style={{ color: '#000' }}>Phone Simulator (Debug)</h1>
      <p>Use this page to simulate a mobile phone uploading a receipt photo and see how the backend processes it.</p>

      <section style={{ marginBottom: '30px', padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h2 style={{ color: '#000' }}>1. Upload Receipt</h2>
        <form onSubmit={handleUpload}>
          <div style={{ marginBottom: '10px' }}>
            <input type="file" onChange={handleFileChange} accept="image/*" />
          </div>
          <button type="submit" disabled={!file || loading} style={{
            padding: '8px 16px',
            cursor: 'pointer',
            backgroundColor: '#007bff',
            color: '#fff',
            border: 'none',
            borderRadius: '4px'
          }}>
            {loading ? 'Uploading...' : 'Send to API'}
          </button>
        </form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          {rawRequest && (
            <section style={{ marginBottom: '30px' }}>
              <h2 style={{ color: '#000' }}>Raw Request Overview</h2>
              <pre style={{ backgroundColor: '#f4f4f4', padding: '10px', borderRadius: '4px', overflowX: 'auto', color: '#000', border: '1px solid #ddd', fontSize: '12px' }}>
                {rawRequest}
              </pre>
            </section>
          )}

          {uploadResponse && (
            <section style={{ marginBottom: '30px' }}>
              <h2 style={{ color: '#000' }}>API Response</h2>
              <pre style={{ backgroundColor: '#f4f4f4', padding: '10px', borderRadius: '4px', overflowX: 'auto', color: '#000', border: '1px solid #ddd', fontSize: '12px' }}>
                {JSON.stringify(uploadResponse, null, 2)}
              </pre>
            </section>
          )}

          {jobStatus && (
            <section style={{ marginBottom: '30px' }}>
              <h2 style={{ color: '#000' }}>Backend Job Status</h2>
              <div style={{ padding: '15px', backgroundColor: '#eef', borderRadius: '8px', border: '1px solid #ccf' }}>
                <p><strong>Status:</strong> <span style={{
                  fontWeight: 'bold',
                  color: jobStatus.status === 'completed' ? 'green' : jobStatus.status === 'failed' ? 'red' : 'blue'
                }}>{jobStatus.status.toUpperCase()}</span></p>
                <p><strong>Job ID:</strong> {jobStatus.id}</p>
                {jobStatus.error_message && <p style={{ color: 'red' }}><strong>Error:</strong> {jobStatus.error_message}</p>}
                <details>
                  <summary style={{ cursor: 'pointer', color: '#007bff' }}>View Full Job Object</summary>
                  <pre style={{ fontSize: '11px', color: '#000', marginTop: '10px' }}>{JSON.stringify(jobStatus, null, 2)}</pre>
                </details>
              </div>
            </section>
          )}
        </div>

        <div>
          {extractedItems.length > 0 && (
            <section>
              <h2 style={{ color: '#000' }}>Extraction Results</h2>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                      <th style={{ padding: '8px', textAlign: 'left' }}>Raw Text</th>
                      <th style={{ padding: '8px', textAlign: 'left' }}>Normalized Name</th>
                      <th style={{ padding: '8px', textAlign: 'right' }}>Qty</th>
                      <th style={{ padding: '8px', textAlign: 'right' }}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {extractedItems.map((item) => (
                      <tr key={item.id} style={{ borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '8px', fontStyle: 'italic', color: '#666' }}>{item.raw_text}</td>
                        <td style={{ padding: '8px', fontWeight: 'bold' }}>{item.normalized_name}</td>
                        <td style={{ padding: '8px', textAlign: 'right' }}>{item.quantity}</td>
                        <td style={{ padding: '8px', textAlign: 'right' }}>{item.line_total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
};
