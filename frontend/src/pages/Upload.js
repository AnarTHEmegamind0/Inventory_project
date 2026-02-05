import React, { useState } from 'react';
import { detectProducts } from '../services/api';

function Upload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const data = await detectProducts(selectedFile);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Detection failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Product Detection</h1>

      <div className="card">
        <h2>Upload Image</h2>
        <div
          className="upload-area"
          onClick={() => document.getElementById('fileInput').click()}
        >
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: '8px' }}
            />
          ) : (
            <div>
              <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                Click to select an image
              </p>
              <p style={{ color: '#999' }}>Supports JPEG, PNG, BMP</p>
            </div>
          )}
          <input
            id="fileInput"
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>

        {selectedFile && (
          <div style={{ marginTop: '1rem', textAlign: 'center' }}>
            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={loading}
            >
              {loading ? 'Detecting...' : 'Detect Products'}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="card" style={{ borderLeft: '4px solid #e74c3c' }}>
          <p style={{ color: '#e74c3c' }}>{error}</p>
        </div>
      )}

      {result && (
        <div className="card">
          <h2>Detection Results</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="value">{result.total_products}</div>
              <div className="label">Products Detected</div>
            </div>
            <div className="stat-card">
              <div className="value">{result.processing_time_ms}ms</div>
              <div className="label">Processing Time</div>
            </div>
          </div>

          {result.detections && result.detections.length > 0 && (
            <table className="table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Confidence</th>
                  <th>Bounding Box</th>
                </tr>
              </thead>
              <tbody>
                {result.detections.map((det, i) => (
                  <tr key={i}>
                    <td>{det.class_name}</td>
                    <td>{(det.confidence * 100).toFixed(1)}%</td>
                    <td>
                      [{det.bbox.map((b) => b.toFixed(0)).join(', ')}]
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

export default Upload;
