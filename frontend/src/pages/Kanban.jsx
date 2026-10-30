import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api';

export default function Kanban() {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedProjectId = searchParams.get('project') || '';

  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState('');
  const [draggedTaskId, setDraggedTaskId] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [projectsData, tasksData] = await Promise.all([
          api.projects.list(),
          api.tasks.list(selectedProjectId ? `project=${selectedProjectId}` : ''),
        ]);
        setProjects(projectsData.results || projectsData || []);
        setTasks(tasksData.results || tasksData || []);
      } catch (err) {
        console.error('Failed to load Kanban data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedProjectId]);

  const handleStatusChange = async (taskId, newStatus) => {
    const taskToUpdate = tasks.find((t) => t.id === taskId);
    if (!taskToUpdate || taskToUpdate.status === newStatus) return;

    // Optimistic UI update
    const previousTasks = [...tasks];
    setTasks(tasks.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t)));

    try {
      await api.tasks.updateStatus(taskId, newStatus);
      showToast(`Task "${taskToUpdate.title}" moved to ${newStatus.replace('_', ' ').toUpperCase()}`);
    } catch (err) {
      console.error('Status update failed:', err);
      setTasks(previousTasks); // Revert
      showToast(`Failed to update status: ${err.message}`, true);
    }
  };

  const showToast = (msg, isError = false) => {
    setToastMessage({ text: msg, isError });
    setTimeout(() => setToastMessage(''), 3500);
  };

  const onDragStart = (e, id) => {
    setDraggedTaskId(id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const onDragOver = (e) => {
    e.preventDefault();
  };

  const onDrop = (e, targetStatus) => {
    e.preventDefault();
    if (draggedTaskId) {
      handleStatusChange(draggedTaskId, targetStatus);
      setDraggedTaskId(null);
    }
  };

  const columns = [
    { key: 'todo', label: 'To Do', color: 'secondary', icon: 'bi-circle' },
    { key: 'in_progress', label: 'In Progress', color: 'warning', icon: 'bi-hourglass-split' },
    { key: 'done', label: 'Done', color: 'success', icon: 'bi-check2-circle' },
  ];

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status"></div>
        <div className="text-muted mt-2">Loading Kanban Board...</div>
      </div>
    );
  }

  return (
    <div className="container-fluid px-lg-4 py-4">
      {/* Header & Project Selector */}
      <div className="card p-4 bg-white shadow-sm border-0 mb-4">
        <div className="d-flex flex-wrap justify-content-between align-items-center gap-3">
          <div>
            <h2 className="fw-bold mb-1 d-flex align-items-center gap-2">
              <i className="bi bi-kanban text-primary"></i> Kanban Board
            </h2>
            <p className="text-muted small mb-0">
              Drag and drop cards or use quick-action buttons. State updates via DRF REST API without page reload.
            </p>
          </div>

          <div className="d-flex align-items-center gap-2">
            <span className="small fw-semibold text-muted">Filter by Project:</span>
            <select
              className="form-select form-select-sm"
              style={{ width: '220px' }}
              value={selectedProjectId}
              onChange={(e) => setSearchParams(e.target.value ? { project: e.target.value } : {})}
            >
              <option value="">All Projects</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Kanban 3-Column Grid */}
      <div className="row g-4">
        {columns.map((col) => {
          const colTasks = tasks.filter((t) => t.status === col.key);

          return (
            <div key={col.key} className="col-lg-4">
              <div
                className="card h-100 bg-light border-0 shadow-sm"
                onDragOver={onDragOver}
                onDrop={(e) => onDrop(e, col.key)}
                style={{ minHeight: '600px' }}
              >
                {/* Column Header */}
                <div className={`card-header bg-white border-bottom border-3 border-${col.color} d-flex justify-content-between align-items-center py-3`}>
                  <div className="d-flex align-items-center gap-2">
                    <i className={`bi ${col.icon} text-${col.color}`}></i>
                    <span className="fw-bold text-dark">{col.label}</span>
                  </div>
                  <span className={`badge bg-${col.color} text-${col.key === 'in_progress' ? 'dark' : 'white'} rounded-pill`}>
                    {colTasks.length}
                  </span>
                </div>

                {/* Tasks List */}
                <div className="card-body p-3 d-flex flex-column gap-3">
                  {colTasks.map((task) => (
                    <div
                      key={task.id}
                      draggable
                      onDragStart={(e) => onDragStart(e, task.id)}
                      className="card p-3 bg-white border shadow-sm"
                      style={{ cursor: 'grab' }}
                    >
                      <div className="d-flex justify-content-between align-items-start gap-2 mb-2">
                        <h6 className="fw-bold text-dark mb-0">{task.title}</h6>

                        {/* Move Actions Dropdown */}
                        <div className="dropdown">
                          <button className="btn btn-sm btn-light border-0 p-0 text-muted" type="button" data-bs-toggle="dropdown">
                            <i className="bi bi-three-dots-vertical"></i>
                          </button>
                          <ul className="dropdown-menu dropdown-menu-end shadow-sm small py-1">
                            <li className="dropdown-header text-muted py-1" style={{ fontSize: '0.7rem' }}>MOVE TO</li>
                            {col.key !== 'todo' && (
                              <li>
                                <button className="dropdown-item py-1" onClick={() => handleStatusChange(task.id, 'todo')}>
                                  <i className="bi bi-circle me-1 text-secondary"></i> To Do
                                </button>
                              </li>
                            )}
                            {col.key !== 'in_progress' && (
                              <li>
                                <button className="dropdown-item py-1" onClick={() => handleStatusChange(task.id, 'in_progress')}>
                                  <i className="bi bi-hourglass-split me-1 text-warning"></i> In Progress
                                </button>
                              </li>
                            )}
                            {col.key !== 'done' && (
                              <li>
                                <button className="dropdown-item py-1" onClick={() => handleStatusChange(task.id, 'done')}>
                                  <i className="bi bi-check2-circle me-1 text-success"></i> Done
                                </button>
                              </li>
                            )}
                          </ul>
                        </div>
                      </div>

                      <p className="text-muted small mb-2 text-truncate">{task.description || 'No description provided'}</p>

                      <div className="d-flex flex-wrap align-items-center gap-1 mb-2">
                        <span className={`badge ${task.priority === 'urgent' ? 'bg-danger' : task.priority === 'high' ? 'bg-warning text-dark' : 'bg-info text-dark'}`} style={{ fontSize: '0.68rem' }}>
                          {task.priority?.toUpperCase()}
                        </span>
                        {task.due_date && (
                          <span className={`badge ${task.is_overdue ? 'bg-danger' : 'bg-light text-muted border'}`} style={{ fontSize: '0.68rem' }}>
                            <i className="bi bi-calendar3 me-1"></i> {task.due_date}
                          </span>
                        )}
                        <span className="badge bg-secondary-subtle text-secondary ms-auto" style={{ fontSize: '0.68rem' }}>
                          {task.project_name}
                        </span>
                      </div>

                      <div className="d-flex justify-content-between align-items-center pt-2 border-top small text-muted">
                        <div>
                          <i className="bi bi-person-circle text-primary me-1"></i>
                          <span>{task.assigned_to_username || 'Unassigned'}</span>
                        </div>
                        <span style={{ fontSize: '0.7rem' }}>#{task.id}</span>
                      </div>
                    </div>
                  ))}

                  {colTasks.length === 0 && (
                    <div className="text-center py-5 text-muted fst-italic">
                      Drop tasks here
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="position-fixed bottom-0 end-0 p-3" style={{ zIndex: 1100 }}>
          <div className={`toast show align-items-center text-white ${toastMessage.isError ? 'bg-danger' : 'bg-success'} border-0 shadow`}>
            <div className="d-flex">
              <div className="toast-body">
                <i className={`bi ${toastMessage.isError ? 'bi-exclamation-triangle' : 'bi-check-circle'} me-2`}></i>
                {toastMessage.text}
              </div>
              <button type="button" className="btn-close btn-close-white me-2 m-auto" onClick={() => setToastMessage('')}></button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
