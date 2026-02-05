import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import AuditReport from './pages/AuditReport';
import Products from './pages/Products';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <h1 className="logo">Inventory Audit System</h1>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/upload">Detection</Link>
            <Link to="/audit">Audit</Link>
            <Link to="/products">Products</Link>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/audit" element={<AuditReport />} />
            <Route path="/products" element={<Products />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
