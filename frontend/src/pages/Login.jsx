import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  const setDemoCredentials = (u, p) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-5 col-lg-4">
          <div className="card p-4 shadow-sm border-0 bg-white rounded-3">
            <div className="text-center mb-3">
              <i className="bi bi-kanban-fill text-primary display-5"></i>
              <h3 className="fw-bold mt-2">TaskFlow</h3>
              <p className="text-muted small">Sign in to collaborate on your team tasks</p>
            </div>

            {error && (
              <div className="alert alert-danger py-2 small" role="alert">
                <i className="bi bi-exclamation-triangle-fill me-1"></i> {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label small fw-semibold">Username</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div className="mb-3">
                <label className="form-label small fw-semibold">Password</label>
                <div className="input-group">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-control"
                    placeholder="Enter password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => setShowPassword(!showPassword)}
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    <i className={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}`}></i>
                  </button>
                </div>
              </div>

              <button type="submit" className="btn btn-primary w-100 py-2 fw-semibold" disabled={loading}>
                {loading ? (
                  <span>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Signing in...
                  </span>
                ) : (
                  <span>
                    <i className="bi bi-box-arrow-in-right me-1"></i> Sign In
                  </span>
                )}
              </button>
            </form>

            <div className="text-center mt-3 small text-muted">
              Don't have an account? <Link to="/register" className="text-primary text-decoration-none fw-semibold">Register here</Link>
            </div>

            {/* Demo Logins Box */}
            <div className="card bg-light mt-4 p-3 border-0 small">
              <div className="fw-bold text-dark mb-1">
                <i className="bi bi-magic me-1 text-primary"></i> Click Demo Account to Fill:
              </div>
              <div className="d-flex justify-content-between align-items-center py-1 border-bottom">
                <span>Admin:</span>
                <button type="button" className="btn btn-sm btn-outline-primary py-0 px-2" onClick={() => setDemoCredentials('admin', 'admin123')}>
                  admin
                </button>
              </div>
              <div className="d-flex justify-content-between align-items-center py-1 border-bottom">
                <span>Manager:</span>
                <button type="button" className="btn btn-sm btn-outline-secondary py-0 px-2" onClick={() => setDemoCredentials('manager1', 'manager123')}>
                  manager1
                </button>
              </div>
              <div className="d-flex justify-content-between align-items-center pt-1">
                <span>Member:</span>
                <button type="button" className="btn btn-sm btn-outline-secondary py-0 px-2" onClick={() => setDemoCredentials('member1', 'member123')}>
                  member1
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
