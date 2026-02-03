import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

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

apiClient.interceptors.response.use(
  (response) => {
    if (response.config.responseType === 'blob') {
      return response;
    }
    return response.data;
  },
  (error) => {
    const status = error.response?.status;
    const errorData = error.response?.data;

    if (status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('lastLoginEmail');
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }

    const customError = {
      status,
      message: errorData?.message || errorData?.detail || error.message || "An unexpected error occurred",
      data: errorData,
      originalError: error
    };

    return Promise.reject(customError);
  }
);

export default apiClient;