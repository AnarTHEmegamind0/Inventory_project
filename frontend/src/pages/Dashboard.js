import React, { useState, useEffect } from 'react';
import { getAuditStats, getDetectionHistory } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentDetections, setRecentDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsData, detectionsData] = await Promise.all([
        getAuditStats(),
        getDetectionHistory(5),
      ]);
      setStats(statsData);
      setRecentDetections(detectionsData.results || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="card">Loading...</div>;

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="value">{stats?.total_audits || 0}</div>
          <div className="label">Total Audits</div>
        </div>
        <div className="stat-card">
          <div className="value" style={{ color: '#27ae60' }}>
            {stats?.passed || 0}
          </div>
          <div className="label">Passed</div>
        </div>
        <div className="stat-card">
          <div className="value" style={{ color: '#e74c3c' }}>
            {stats?.failed || 0}
          </div>
          <div className="label">Failed</div>
        </div>
        <div className="stat-card">
          <div className="value" style={{ color: '#f39c12' }}>
            {stats?.warnings || 0}
          </div>
          <div className="label">Warnings</div>
        </div>
      </div>

      <div className="card">
        <h2>Recent Detections</h2>
        {recentDetections.length === 0 ? (
          <p>No detections yet. Upload an image to get started.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Products Found</th>
                <th>Processing Time</th>
              </tr>
            </thead>
            <tbody>
              {recentDetections.map((det, i) => (
                <tr key={i}>
                  <td>{new Date(det.timestamp).toLocaleString()}</td>
                  <td>{det.total_products}</td>
                  <td>{det.processing_time_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
