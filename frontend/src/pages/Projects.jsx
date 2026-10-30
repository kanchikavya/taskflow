import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';

export default function Projects() {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [error, setError] = useState('');

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await api.projects.list();
      setProjects(data.results || data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch projects.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await api.projects.create(newProject);
      setShowModal(false);
      setNewProject({ name: '', description: '' });
      loadProjects();
    } catch (err) {
      alert(`Error creating project: ${err.message}`);
    }
  };

  const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager';

  return (
    <div className="container-fluid px-lg-4 py-4">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-2">
        <div>
          <h2 className="fw-bold mb-1">Team Projects</h2>
          <p className="text-muted mb-0">Collaborative project workspaces managed via DRF API.</p>
        </div>
        {isManagerOrAdmin && (
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <i className="bi bi-folder-plus me-1"></i> New Project
          </button>
        )}
      </div>

      {error && <div className="alert alert-danger py-2 small">{error}</div>}

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status"></div>
          <div className="text-muted mt-2">Loading projects...</div>
        </div>
      ) : (
        <div className="row g-4">
          {projects.map((p) => (
            <div key={p.id} className="col-md-6 col-lg-4">
              <div className="card h-100 p-4 bg-white shadow-sm border-0 d-flex flex-column justify-content-between">
                <div>
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <h5 className="fw-bold text-dark mb-0">{p.name}</h5>
                    <span className="badge bg-primary-subtle text-primary">
                      {p.task_count || 0} tasks
                    </span>
                  </div>
                  <p className="text-muted small mb-3" style={{ minHeight: '40px' }}>
                    {p.description || 'No description provided.'}
                  </p>
                </div>

                <div className="border-top pt-3">
                  <div className="d-flex justify-content-between align-items-center mb-3 small text-muted">
                    <span><i className="bi bi-people me-1"></i> {p.member_count || 0} member(s)</span>
                    <span><i className="bi bi-person-badge me-1"></i> Lead: {p.created_by?.username}</span>
                  </div>

                  <Link to={`/kanban?project=${p.id}`} className="btn btn-sm btn-outline-primary w-100">
                    <i className="bi bi-kanban me-1"></i> Open Project Kanban
                  </Link>
                </div>
              </div>
            </div>
          ))}

          {projects.length === 0 && (
            <div className="col-12 text-center py-5 text-muted">
              <i className="bi bi-folder2-open display-4 opacity-50 mb-2"></i>
              <p>No projects found.</p>
            </div>
          )}
        </div>
      )}

      {/* Modal for Project Creation */}
      {showModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title fw-bold">Create New Project</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <form onSubmit={handleCreateProject}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label small fw-semibold">Project Name</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g., Mobile App Redesign"
                      value={newProject.name}
                      onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label small fw-semibold">Description</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      placeholder="Project scope and goals..."
                      value={newProject.description}
                      onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    ></textarea>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-outline-secondary" onClick={() => setShowModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Create Project
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
