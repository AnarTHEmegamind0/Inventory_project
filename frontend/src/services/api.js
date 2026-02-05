import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Detection APIs
export const detectProducts = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  const res = await api.post('/detection/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const getDetectionHistory = async (limit = 20) => {
  const res = await api.get(`/detection/history?limit=${limit}`);
  return res.data;
};

// Audit APIs
export const runAudit = async (auditData) => {
  const res = await api.post('/audit/run', auditData);
  return res.data;
};

export const getAuditHistory = async (limit = 20) => {
  const res = await api.get(`/audit/history?limit=${limit}`);
  return res.data;
};

export const getAuditStats = async () => {
  const res = await api.get('/audit/stats');
  return res.data;
};

// Product APIs
export const getProducts = async (limit = 50) => {
  const res = await api.get(`/products/?limit=${limit}`);
  return res.data;
};

export const createProduct = async (product) => {
  const res = await api.post('/products/', product);
  return res.data;
};

export const deleteProduct = async (name) => {
  const res = await api.delete(`/products/${name}`);
  return res.data;
};

export default api;
