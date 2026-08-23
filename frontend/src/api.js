const API_BASE = '/api';

export function getAuthToken() {
  return localStorage.getItem('prodexa_token');
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('prodexa_token', token);
  } else {
    localStorage.removeItem('prodexa_token');
  }
}

export async function fetchApi(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers
  };

  const config = {
    ...options,
    headers
  };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `HTTP Error ${response.status}`);
    }
    
    // Return blob for download responses, text for plain text, json for json
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return await response.json();
    } else if (contentType.includes('text/plain')) {
      return await response.text();
    } else if (contentType.includes('octet-stream') || contentType.includes('attachment') || contentType.includes('text/csv')) {
      return await response.blob();
    }
    return await response.text();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Auth
  login: (email, password) => fetchApi('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (email, password, name, role) => fetchApi('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, name, role }) }),
  getMe: () => fetchApi('/auth/me'),

  // Dashboard & Health
  getHealth: () => fetchApi('/health'),
  getDashboardSummary: () => fetchApi('/dashboard/summary'),

  // Products
  getProducts: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/products?${query}`);
  },
  getProductDetail: (id) => fetchApi(`/products/${id}`),

  // Evidence
  getEvidenceList: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/evidence?${query}`);
  },
  getProductEvidence: (id) => fetchApi(`/evidence/${id}`),

  // Validation & Confidence
  getValidationMetrics: () => fetchApi('/validation'),
  getConfidenceMetrics: () => fetchApi('/confidence'),

  // Human Review Queue
  getReviewQueue: (statusFilter) => fetchApi(`/review/queue${statusFilter ? `?status_filter=${statusFilter}` : ''}`),
  getReviewItem: (id) => fetchApi(`/review/${id}`),
  acceptReviewItem: (id, reviewerId, reason) => fetchApi(`/review/${id}/accept`, { method: 'POST', body: JSON.stringify({ reviewer_id: reviewerId, reason }) }),
  editReviewItem: (id, reviewerId, editedValue, reason) => fetchApi(`/review/${id}/edit`, { method: 'POST', body: JSON.stringify({ reviewer_id: reviewerId, edited_value: editedValue, reason }) }),
  rejectReviewItem: (id, reviewerId, reason) => fetchApi(`/review/${id}/reject`, { method: 'POST', body: JSON.stringify({ reviewer_id: reviewerId, reason }) }),
  escalateReviewItem: (id, reviewerId, reason) => fetchApi(`/review/${id}/escalate`, { method: 'POST', body: JSON.stringify({ reviewer_id: reviewerId, reason }) }),

  // Descriptions
  getDescriptions: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/descriptions?${query}`);
  },
  getProductDescription: (id) => fetchApi(`/descriptions/${id}`),

  // Final Outputs & Downloads
  getFinalOutputs: () => fetchApi('/final/outputs'),

  // Reports
  getReportsList: () => fetchApi('/reports'),
  viewReport: (filename) => fetchApi(`/reports/view/${filename}`),

  // Pipeline & Evaluation
  getPipelineStatus: () => fetchApi('/pipeline/status'),
  getEvaluation: () => fetchApi('/evaluation'),

  // Admin Telemetry
  getAdminSystem: () => fetchApi('/admin/system'),
  getAdminUsers: () => fetchApi('/admin/users'),
  getAdminAuditLogs: () => fetchApi('/admin/audit'),

  // Upload & Real-Time Job Processing
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const token = getAuthToken();
    return fetch('/api/jobs', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData
    }).then(res => {
      if (!res.ok) {
        return res.json().then(err => { throw new Error(err.detail || 'Upload failed'); });
      }
      return res.json();
    });
  },
  createJob: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const token = getAuthToken();
    return fetch('/api/jobs', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData
    }).then(res => {
      if (!res.ok) {
        return res.json().then(err => { throw new Error(err.detail || 'Failed to create processing job'); });
      }
      return res.json();
    });
  },
  getJobStatus: (jobId) => fetchApi(`/jobs/${jobId}`),
  getJobResults: (jobId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/jobs/${jobId}/results?${query}`);
  },
  exportJobResults: (jobId) => fetchApi(`/jobs/${jobId}/export`),
  retryJob: (jobId) => fetchApi(`/jobs/${jobId}/retry`, { method: 'POST' })
};
