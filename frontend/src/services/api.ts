import axios from "axios";

export const api = axios.create({
  baseURL: '', // Vite proxy forwards /api → http://localhost:8000
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT if available
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('jwt_token');

    if (token){
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor: handle 401 globally (Phase 2)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Optional: trigger logout or redirect to login
      console.warn('Auth error: token expired or invalid');
    }
    return Promise.reject(error);
  }
);