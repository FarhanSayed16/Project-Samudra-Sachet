import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiService = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let authToken = null;

export const setAuthToken = (token) => {
  authToken = token;
  if (token) {
    apiService.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiService.defaults.headers.common['Authorization'];
  }
};

export const getAuthToken = () => authToken;

// Request interceptor to add auth token
apiService.interceptors.request.use(
  async (config) => {
    console.log('📤 API Request:', config.method?.toUpperCase(), config.url);
    
    // Add auth token if available
    if (!authToken) {
      try {
        authToken = await AsyncStorage.getItem('authToken');
        if (authToken) {
          config.headers.Authorization = `Bearer ${authToken}`;
        }
      } catch (error) {
        console.log('Error getting auth token:', error);
      }
    }
    
    return config;
  },
  (error) => {
    console.log('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiService.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  async (error) => {
    console.log('❌ API Error:', error.response?.status, error.config?.url, error.message);
    
    // Handle 401 errors - clear token and redirect to login
    if (error.response?.status === 401) {
      console.log('🔒 Unauthorized - clearing auth token');
      authToken = null;
      await AsyncStorage.removeItem('authToken');
      await AsyncStorage.removeItem('user');
      // You can dispatch a logout action here if using Redux
    }
    
    // Handle network errors
    if (!error.response) {
      error.message = 'Network error. Please check your internet connection.';
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
