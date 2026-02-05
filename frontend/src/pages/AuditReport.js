import React, { useState, useEffect } from 'react';
import { getAuditHistory } from '../services/api';

function AuditReport() {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAudits();
  }, []);

  const loadAudits = async () => {
    try {
      const data = await getAuditHistory(20);
      setAudits(data.results || []);
    } catch (error) {
      console.error('Failed to load audits:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const classes = {
      pass: 'badge badge-pass',
      fail: 'badge badge-fail',
      warning: 'badge badge-warning',
    };
    return <span className={classes[status] || 'badge'}>{status.toUpperCase()}</span>;
  };

  if (loading) return <div className="card">Loading...</div>;

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Audit Reports</h1>

      {audits.length === 0 ? (
        <div className="card">
          <p>No audit reports yet. Run an audit from the API or detection page.</p>
        </div>
      ) : (
        audits.map((audit, i) => (
          <div key={i} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div>
                <h3>{audit.audit_id}</h3>
                <p style={{ color: '#666' }}>
                  {audit.location} | {new Date(audit.timestamp).toLocaleString()}
                </p>
              </div>
              {getStatusBadge(audit.status)}
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <div className="value">{audit.total_expected}</div>
                <div className="label">Expected</div>
              </div>
              <div className="stat-card">
                <div className="value">{audit.total_detected}</div>
                <div className="label">Detected</div>
              </div>
              <div className="stat-card">
                <div className="value">
                  {(audit.match_rate * 100).toFixed(1)}%
                </div>
                <div className="label">Match Rate</div>
              </div>
            </div>

            {audit.discrepancies && audit.discrepancies.length > 0 && (
              <div>
                <h4 style={{ marginBottom: '0.5rem' }}>Discrepancies</h4>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Expected</th>
                      <th>Detected</th>
                      <th>Difference</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {audit.discrepancies.map((d, j) => (
                      <tr key={j}>
                        <td>{d.product_name}</td>
                        <td>{d.expected_count}</td>
                        <td>{d.detected_count}</td>
                        <td style={{ color: d.difference < 0 ? '#e74c3c' : '#27ae60' }}>
                          {d.difference > 0 ? '+' : ''}{d.difference}
                        </td>
                        <td>{getStatusBadge(d.status)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default AuditReport;
