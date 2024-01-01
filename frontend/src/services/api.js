import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const taskAPI = {
  // Create a new task
  createTask: async (text) => {
    try {
      console.log('Creating task with text:', text);
      const response = await api.post('/api/tasks', { text });
      console.log('Task creation response:', response.data);
      return response.data;
    } catch (error) {
      console.error('API Error in createTask:', error);
      console.error('Error response:', error.response?.data);
      throw error;
    }
  },

  // Get all tasks for the user
  getTasks: async () => {
    const response = await api.get('/api/tasks');
    return response.data;
  },

  // Search tasks
  searchTasks: async (query) => {
    const response = await api.post('/api/search', { query });
    return response.data;
  },

  // Delete a task
  deleteTask: async (taskId) => {
    const response = await api.delete(`/api/tasks/${taskId}`);
    return response.data;
  },
};

export default api;
