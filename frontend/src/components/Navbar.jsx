import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
      <div className="container-fluid px-lg-4">
        <Link className="navbar-brand text-primary d-flex align-items-center gap-2" to="/dashboard">
          <i className="bi bi-kanban-fill fs-4"></i>
          <span className="text-white">Task<span className="text-primary">Flow</span></span>
        </Link>

        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#reactNavbar">
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="reactNavbar">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <NavLink className={({ isActive }) => `nav-link ${isActive ? 'active text-white fw-bold' : ''}`} to="/dashboard">
                <i className="bi bi-speedometer2 me-1"></i> Dashboard
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className={({ isActive }) => `nav-link ${isActive ? 'active text-white fw-bold' : ''}`} to="/projects">
                <i className="bi bi-folder me-1"></i> Projects
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className={({ isActive }) => `nav-link ${isActive ? 'active text-white fw-bold' : ''}`} to="/kanban">
                <i className="bi bi-kanban me-1"></i> Kanban
              </NavLink>
            </li>
          </ul>

          <div className="d-flex align-items-center gap-3">
            <div className="text-end text-light">
              <div className="fw-semibold small">{user.first_name ? `${user.first_name} ${user.last_name || ''}` : user.username}</div>
              <span className={`badge ${user.role === 'admin' ? 'bg-danger' : user.role === 'manager' ? 'bg-warning text-dark' : 'bg-info text-dark'}`} style={{ fontSize: '0.7rem' }}>
                {user.role ? user.role.toUpperCase() : 'MEMBER'}
              </span>
            </div>

            <button onClick={handleLogout} className="btn btn-sm btn-outline-danger">
              <i className="bi bi-box-arrow-right me-1"></i> Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
