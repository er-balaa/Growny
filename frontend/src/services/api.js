import axios from 'axios';
import { getCurrentToken, auth } from '../firebase';

// Determine API base URL:
// - In production: use VITE_API_URL if set, otherwise use same-origin (empty string)
// - In development: use VITE_API_URL if set, otherwise use localhost:8000
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;

  // If VITE_API_URL is explicitly set (even to empty string), use it
  if (envUrl !== undefined) {
    return envUrl;
  }

  // Fallback: production uses same-origin, development uses localhost
  return import.meta.env.PROD ? '' : 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();
console.log('[API] Base URL:', API_BASE_URL || '(same-origin)');

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get a fresh auth token, prioritizing Firebase's current user token
 * Falls back to localStorage if Firebase auth is not ready
 */
const getFreshToken = async () => {
  // Try to get a fresh token from Firebase first
  if (auth?.currentUser) {
    try {
      const token = await getCurrentToken(false);
      if (token) {
        return token;
      }
    } catch (error) {
      console.warn('Failed to get fresh token from Firebase:', error);
    }
  }

  // Fall back to localStorage token
  return localStorage.getItem('authToken');
};

// Request interceptor to add fresh auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await getFreshToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        console.warn('[API] No auth token available');
      }
    } catch (error) {
      console.error('[API] Error getting token:', error);
      // Try localStorage as final fallback
      const fallbackToken = localStorage.getItem('authToken');
      if (fallbackToken) {
        config.headers.Authorization = `Bearer ${fallbackToken}`;
      }
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
  async (error) => {
    const originalRequest = error.config;

    // If we get a 401 and haven't retried yet, try to refresh the token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      console.log('[API] Got 401, attempting token refresh...');

      try {
        // Force a fresh token
        const freshToken = await getCurrentToken(true);

        if (freshToken) {
          console.log('[API] Token refreshed successfully, retrying request...');
          originalRequest.headers.Authorization = `Bearer ${freshToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('[API] Token refresh failed:', refreshError);
      }

      // Token refresh failed - clear auth state
      console.error('[API] Authentication failed - clearing session');
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }

    return Promise.reject(error);
  }
);

export const taskAPI = {
  // Create a new task
  createTask: async (text) => {
    const response = await api.post('/api/tasks', { text });
    return response.data;
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
