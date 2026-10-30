import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [tasksData, projectsData] = await Promise.all([
          api.tasks.list(),
          api.projects.list(),
        ]);
        setTasks(tasksData.results || tasksData || []);
        setProjects(projectsData.results || projectsData || []);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status"></div>
        <div className="text-muted mt-2">Loading your TaskFlow dashboard...</div>
      </div>
    );
  }

  // Compute metrics
  const todoCount = tasks.filter((t) => t.status === 'todo').length;
  const inProgressCount = tasks.filter((t) => t.status === 'in_progress').length;
  const doneCount = tasks.filter((t) => t.status === 'done').length;
  const overdueTasks = tasks.filter((t) => t.is_overdue);
  const myTasks = tasks.filter((t) => t.assigned_to === user?.id);

  return (
    <div className="container-fluid px-lg-4 py-4">
      {/* Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-2">
        <div>
          <h2 className="fw-bold mb-1">Hello, {user?.first_name || user?.username}! 👋</h2>
          <p className="text-muted mb-0">Live team task and project overview.</p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/kanban" className="btn btn-outline-primary">
            <i className="bi bi-kanban me-1"></i> Kanban Board
          </Link>
          <Link to="/projects" className="btn btn-primary">
            <i className="bi bi-folder me-1"></i> View Projects
          </Link>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger py-2 small mb-4">
          <i className="bi bi-exclamation-triangle me-1"></i> {error}
        </div>
      )}

      {/* Overdue Alert Banner */}
      {overdueTasks.length > 0 && (
        <div className="alert alert-danger d-flex align-items-center justify-content-between shadow-sm mb-4">
          <div>
            <i className="bi bi-alarm-fill fs-5 me-2"></i>
            <strong>Attention needed:</strong> You have <strong>{overdueTasks.length}</strong> overdue task(s) requiring updates!
          </div>
          <Link to="/kanban" className="btn btn-sm btn-outline-danger">Review in Kanban &rarr;</Link>
        </div>
      )}

      {/* Metrics Row */}
      <div className="row g-3 mb-4">
        <div className="col-6 col-md-3">
          <div className="card p-3 border-start border-primary border-4 bg-white shadow-sm">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small fw-semibold text-uppercase">Projects</div>
                <div className="fs-3 fw-bold text-dark">{projects.length}</div>
              </div>
              <div className="bg-primary-subtle text-primary p-3 rounded-circle">
                <i className="bi bi-folder2-open fs-4"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-6 col-md-3">
          <div className="card p-3 border-start border-secondary border-4 bg-white shadow-sm">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small fw-semibold text-uppercase">To Do</div>
                <div className="fs-3 fw-bold text-secondary">{todoCount}</div>
              </div>
              <div className="bg-secondary-subtle text-secondary p-3 rounded-circle">
                <i className="bi bi-list-task fs-4"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-6 col-md-3">
          <div className="card p-3 border-start border-warning border-4 bg-white shadow-sm">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small fw-semibold text-uppercase">In Progress</div>
                <div className="fs-3 fw-bold text-warning">{inProgressCount}</div>
              </div>
              <div className="bg-warning-subtle text-warning p-3 rounded-circle">
                <i className="bi bi-hourglass-split fs-4"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-6 col-md-3">
          <div className="card p-3 border-start border-success border-4 bg-white shadow-sm">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <div className="text-muted small fw-semibold text-uppercase">Done</div>
                <div className="fs-3 fw-bold text-success">{doneCount}</div>
              </div>
              <div className="bg-success-subtle text-success p-3 rounded-circle">
                <i className="bi bi-check2-circle fs-4"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main 2-Column Section */}
      <div className="row g-4">
        {/* Left Column: Assigned Tasks */}
        <div className="col-lg-8">
          <div className="card p-4 h-100 bg-white shadow-sm border-0">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="fw-bold mb-0">
                <i className="bi bi-person-check text-primary me-2"></i> My Assigned Tasks ({myTasks.length})
              </h5>
              <Link to="/kanban" className="small text-decoration-none">Open Board &rarr;</Link>
            </div>

            {myTasks.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light small">
                    <tr>
                      <th>Task Title</th>
                      <th>Project</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Due Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {myTasks.map((t) => (
                      <tr key={t.id}>
                        <td className="fw-semibold text-dark">{t.title}</td>
                        <td>
                          <span className="badge bg-secondary-subtle text-secondary">{t.project_name}</span>
                        </td>
                        <td>
                          <span className={`badge ${t.priority === 'urgent' ? 'bg-danger' : t.priority === 'high' ? 'bg-warning text-dark' : 'bg-info text-dark'}`}>
                            {t.priority?.toUpperCase()}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${t.status === 'done' ? 'bg-success' : t.status === 'in_progress' ? 'bg-warning text-dark' : 'bg-secondary'}`}>
                            {t.status === 'in_progress' ? 'IN PROGRESS' : t.status?.toUpperCase()}
                          </span>
                        </td>
                        <td className={`small ${t.is_overdue ? 'text-danger fw-bold' : 'text-muted'}`}>
                          {t.due_date || '—'}
                          {t.is_overdue && <i className="bi bi-exclamation-circle ms-1" title="Overdue"></i>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-5 text-muted">
                <i className="bi bi-check2-circle display-4 text-success opacity-50 mb-2"></i>
                <p className="mb-0">You currently have no tasks assigned to your account.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Projects Quick List */}
        <div className="col-lg-4">
          <div className="card p-4 bg-white shadow-sm border-0">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="fw-bold mb-0">Active Projects</h5>
              <Link to="/projects" className="small text-decoration-none">View All</Link>
            </div>

            <div className="d-flex flex-column gap-3">
              {projects.slice(0, 4).map((p) => (
                <div key={p.id} className="border rounded p-3 bg-light">
                  <div className="d-flex justify-content-between align-items-start">
                    <span className="fw-bold text-dark">{p.name}</span>
                    <span className="badge bg-primary rounded-pill">{p.task_count || 0} tasks</span>
                  </div>
                  <p className="text-muted small mt-1 mb-2 text-truncate">{p.description || 'No description'}</p>
                  <div className="d-flex justify-content-between align-items-center small text-muted">
                    <span><i className="bi bi-people me-1"></i> {p.member_count || 0} members</span>
                    <Link to={`/kanban?project=${p.id}`} className="btn btn-sm btn-link p-0 text-decoration-none">
                      Kanban &rarr;
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
