import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mydost2-production.up.railway.app';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/signin';
    }
    return Promise.reject(error);
  }
);

// Chat API
export const chatAPI = {
  send: (data, token) => apiClient.post('/api/chat', data),
  listConversations: (userId) => apiClient.get('/api/conversations', { params: { user_id: userId } }),
  getConversation: (conversationId) => apiClient.get(`/api/conversations/${conversationId}`),
  deleteConversation: (conversationId) => apiClient.delete(`/api/conversations/${conversationId}`),
  deleteAll: (userId) => apiClient.delete('/api/conversations', { params: { user_id: userId, confirm: true } }),
  updateProfile: (payload) => apiClient.put('/api/profile', payload, { params: { user_id: payload.user_id } }),
  deleteMemories: (userId) => apiClient.delete('/api/memories', { params: { user_id: userId, confirm: true } }),
};

// OCR API
export const ocrAPI = {
  processImage: (formData) => apiClient.post('/api/ocr', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getLanguages: () => apiClient.get('/api/ocr/languages'),
};

// PDF API
export const pdfAPI = {
  uploadPDF: (formData) => apiClient.post('/api/pdf/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getInfo: () => apiClient.get('/api/pdf/info'),
};

// Image Editing API
export const imageAPI = {
  crop: (formData) => apiClient.post('/api/image/crop', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  enhance: (formData) => apiClient.post('/api/image/enhance', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  annotate: (formData) => apiClient.post('/api/image/annotate', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getOperations: () => apiClient.get('/api/image/info'),
};

// Admin API
export const adminAPI = {
  login: (password) => apiClient.post('/api/admin/login', { password }),
  getConfig: () => apiClient.get('/api/admin/config'),
  updateConfig: (config) => apiClient.post('/api/admin/config', config),
  toggleModule: (feature, enabled) => apiClient.post('/api/admin/module/toggle', { feature, enabled }),
  getStats: () => apiClient.get('/api/admin/stats'),
  clearCache: () => apiClient.post('/api/admin/cache/clear'),
  reindex: () => apiClient.post('/api/admin/reindex'),
  listModules: () => apiClient.get('/api/admin/modules'),
  getSystemPrompt: () => apiClient.get('/api/admin/system-prompt'),
  updateSystemPrompt: (prompt) => apiClient.post('/api/admin/system-prompt/update', { prompt }),
  updateAPIKeys: (keys) => apiClient.post('/api/admin/api-keys/update', keys),
  addTeerResult: (result) => apiClient.post('/api/admin/data/add-teer-result', result),
  getTeerStats: (days) => apiClient.get('/api/admin/data/teer-stats', { params: { days } }),
};

// Memories API
export const memoryAPI = {
  list: (userId, limit = 10) => apiClient.get('/api/memories', { params: { user_id: userId, limit } }),
  search: (userId, query, limit = 5) =>
    apiClient.get('/api/memories/search', { params: { user_id: userId, query, limit } }),
  create: (payload) => apiClient.post('/api/memories', payload),
  update: (memoryId, payload) => apiClient.put(`/api/memories/${memoryId}`, payload),
  remove: (memoryId, userId) => apiClient.delete(`/api/memories/${memoryId}`, { params: { user_id: userId } }),
  removeAll: (userId) => apiClient.delete('/api/memories', { params: { user_id: userId, confirm: true } }),
};

export default apiClient;
