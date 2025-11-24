import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { username: email, password }),
  register: (userData: { name: string; email: string; password: string }) =>
    api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/me'),
};

export const promptsAPI = {
  create: (promptData: { prompt_text: string }) =>
    api.post('/prompts/', promptData),
  getAll: (params?: { skip?: number; limit?: number }) =>
    api.get('/prompts/', { params }),
  getById: (id: number) => api.get(`/prompts/${id}`),
  delete: (id: number) => api.delete(`/prompts/${id}`),
  generateContent: (data: { prompt: string; platforms: string[] }) =>
    api.post('/prompts/generate', data),
  generateContentWithFiles: (formData: FormData) =>
    api.post('/prompts/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  regenerateContent: (id: number, platforms: string[]) =>
    api.post(`/prompts/${id}/regenerate`, { platforms }),
};

export const postsAPI = {
  getAll: (params?: { skip?: number; limit?: number; platform?: string; status?: string }) =>
    api.get('/posts/', { params }),
  getById: (id: number) => api.get(`/posts/${id}`),
  update: (id: number, content: string) =>
    api.put(`/posts/${id}`, { content }),
  approve: (id: number) => api.patch(`/posts/${id}/approve`),
  reject: (id: number) => api.patch(`/posts/${id}/reject`),
  improve: (id: number, feedback: string) =>
    api.post(`/posts/${id}/improve`, { feedback }),
  delete: (id: number) => api.delete(`/posts/${id}`),
};

export const scheduleAPI = {
  schedule: (data: { generated_post_id: number; platform: string; scheduled_time: string }) =>
    api.post('/schedule/', data),
  getAll: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/schedule/', { params }),
  getById: (id: number) => api.get(`/schedule/${id}`),
  update: (id: number, scheduled_time: string) =>
    api.put(`/schedule/${id}`, { scheduled_time }),
  cancel: (id: number) => api.delete(`/schedule/${id}`),
  getUpcoming: (limit?: number) => api.get('/schedule/upcoming', { params: { limit } }),
};

export const publishAPI = {
  publish: (data: { generated_post_id: number; platform: string; schedule_time?: string }) =>
    api.post('/publish/', data),
  getConnections: () => api.get('/publish/connections'),
  addConnection: (data: { platform: string; access_token: string; platform_username?: string }) =>
    api.post('/publish/connections', data),
  removeConnection: (id: number) => api.delete(`/publish/connections/${id}`),
  testConnection: (platform: string) => api.post('/publish/test-connection', { platform }),
};

export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getPlatformStats: (days?: number) => api.get('/analytics/platform-stats', { params: { days } }),
  getTimeline: (days?: number) => api.get('/analytics/timeline', { params: { days } }),
  getPerformance: () => api.get('/analytics/performance'),
  getScheduledOverview: () => api.get('/analytics/scheduled-overview'),
};
