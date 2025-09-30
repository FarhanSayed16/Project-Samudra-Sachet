import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiService = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiService.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiService.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.log('❌ API Error:', error.response?.status, error.config?.url, error.message);
    
    // Handle 401 errors
    if (error.response?.status === 401) {
      console.log('🔒 Unauthorized - token may be expired');
      // You can add token refresh logic here if needed
    }
    
    return Promise.reject(error);
  }
);

// API functions
export const authAPI = {
  login: async (credentials) => {
    const response = await apiService.post('/auth/login', credentials);
    return response.data;
  },
};

export const reportsAPI = {
  getPublicReports: async (params = {}) => {
    const response = await apiService.get('/reports/public', { params });
    return response.data;
  },
  
  submitReport: async (reportData) => {
    const response = await apiService.post('/reports/', reportData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const socialMediaAPI = {
  getPublicPosts: async (params = {}) => {
    const response = await apiService.get('/social-media/public', { params });
    return response.data;
  },
};

export default apiService;
