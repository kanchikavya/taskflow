/**
 * Centralized API client for TaskFlow DRF backend.
 * Base URL: http://127.0.0.1:8000/api
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export function getAuthToken() {
  return localStorage.getItem('taskflow_token');
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('taskflow_token', token);
  } else {
    localStorage.removeItem('taskflow_token');
  }
}

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Token ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    const errorMsg = data?.error || data?.detail || Object.values(data || {})[0] || 'An error occurred';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }

  return data;
}

export const api = {
  auth: {
    login: (username, password) =>
      request('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      }),
    register: (userData) =>
      request('/auth/register/', {
        method: 'POST',
        body: JSON.stringify(userData),
      }),
    me: () => request('/auth/me/'),
  },
  projects: {
    list: (params = '') => request(`/projects/${params ? `?${params}` : ''}`),
    get: (id) => request(`/projects/${id}/`),
    create: (data) =>
      request('/projects/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  tasks: {
    list: (params = '') => request(`/tasks/${params ? `?${params}` : ''}`),
    get: (id) => request(`/tasks/${id}/`),
    create: (data) =>
      request('/tasks/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    updateStatus: (id, status) =>
      request(`/tasks/${id}/update-status/`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    delete: (id) =>
      request(`/tasks/${id}/`, {
        method: 'DELETE',
      }),
  },
  comments: {
    list: (taskId) => request(`/comments/?task=${taskId}`),
    create: (taskId, content) =>
      request('/comments/', {
        method: 'POST',
        body: JSON.stringify({ task: taskId, content }),
      }),
  },
};
