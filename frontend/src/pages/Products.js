import React, { useState, useEffect } from 'react';
import { getProducts, createProduct, deleteProduct } from '../services/api';

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: '',
    category: '',
    expected_count: 0,
    location: '',
    sku: '',
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data.products || []);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createProduct(form);
      setForm({ name: '', category: '', expected_count: 0, location: '', sku: '' });
      setShowForm(false);
      loadProducts();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to create product');
    }
  };

  const handleDelete = async (name) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    try {
      await deleteProduct(name);
      loadProducts();
    } catch (error) {
      alert('Failed to delete product');
    }
  };

  if (loading) return <div className="card">Loading...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1>Products</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Product'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h2>Add New Product</h2>
          <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
            <input
              type="text"
              placeholder="Product Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              style={{ padding: '0.6rem', borderRadius: '6px', border: '1px solid #ddd' }}
            />
            <input
              type="text"
              placeholder="Category"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              required
              style={{ padding: '0.6rem', borderRadius: '6px', border: '1px solid #ddd' }}
            />
            <input
              type="number"
              placeholder="Expected Count"
              value={form.expected_count}
              onChange={(e) => setForm({ ...form, expected_count: parseInt(e.target.value) || 0 })}
              style={{ padding: '0.6rem', borderRadius: '6px', border: '1px solid #ddd' }}
            />
            <input
              type="text"
              placeholder="Location (e.g., Shelf A-1)"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              style={{ padding: '0.6rem', borderRadius: '6px', border: '1px solid #ddd' }}
            />
            <input
              type="text"
              placeholder="SKU"
              value={form.sku}
              onChange={(e) => setForm({ ...form, sku: e.target.value })}
              style={{ padding: '0.6rem', borderRadius: '6px', border: '1px solid #ddd' }}
            />
            <button type="submit" className="btn btn-primary">Save Product</button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Product Inventory ({products.length})</h2>
        {products.length === 0 ? (
          <p>No products yet. Add your first product above.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Expected Count</th>
                <th>Location</th>
                <th>SKU</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p, i) => (
                <tr key={i}>
                  <td>{p.name}</td>
                  <td>{p.category}</td>
                  <td>{p.expected_count}</td>
                  <td>{p.location}</td>
                  <td>{p.sku}</td>
                  <td>
                    <button
                      className="btn btn-danger"
                      style={{ padding: '0.3rem 0.8rem', fontSize: '0.85rem' }}
                      onClick={() => handleDelete(p.name)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Products;
