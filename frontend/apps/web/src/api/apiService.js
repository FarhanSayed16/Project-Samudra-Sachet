import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to get token from localStorage (for interceptors)
const getToken = () => {
  try {
    const persistedState = localStorage.getItem('persist:auth');
    if (persistedState) {
      const parsed = JSON.parse(persistedState);
      const authState = JSON.parse(parsed.auth || '{}');
      return authState.token;
    }
  } catch (error) {
    console.error('Error getting token from localStorage:', error);
  }
  return null;
};

// Function to get refresh token from localStorage
const getRefreshToken = () => {
  try {
    const persistedState = localStorage.getItem('persist:auth');
    if (persistedState) {
      const parsed = JSON.parse(persistedState);
      const authState = JSON.parse(parsed.auth || '{}');
      return authState.refreshToken;
    }
  } catch (error) {
    console.error('Error getting refresh token from localStorage:', error);
  }
  return null;
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = getRefreshToken();

        if (refreshToken) {
          const response = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {
            refresh_token: refreshToken
          });

          const { access_token } = response.data;
          
          // Update token in localStorage
          try {
            const persistedState = localStorage.getItem('persist:auth');
            if (persistedState) {
              const parsed = JSON.parse(persistedState);
              const authState = JSON.parse(parsed.auth || '{}');
              authState.token = access_token;
              parsed.auth = JSON.stringify(authState);
              localStorage.setItem('persist:auth', JSON.stringify(parsed));
            }
          } catch (updateError) {
            console.error('Error updating token in localStorage:', updateError);
          }

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Clear auth data and redirect to login
        localStorage.removeItem('persist:auth');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  refresh: async (refreshToken) => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.patch('/users/me', userData);
    return response.data;
  },

  changePassword: async (passwordData) => {
    const response = await api.post('/users/me/password', passwordData);
    return response.data;
  }
};

// Reports API
export const reportsAPI = {
  getReports: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.hazard_type) params.append('hazard_type', filters.hazard_type);
    if (filters.severity_level) params.append('severity_level', filters.severity_level);
    if (filters.latitude && filters.longitude && filters.radius) {
      params.append('latitude', filters.latitude);
      params.append('longitude', filters.longitude);
      params.append('radius', filters.radius);
    }
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await api.get(`/reports?${params.toString()}`);
    return response.data;
  },

  getReportById: async (reportId) => {
    const response = await api.get(`/reports/${reportId}`);
    return response.data;
  },

  createReport: async (reportData) => {
    const formData = new FormData();
    formData.append('hazard_type', reportData.hazard_type);
    formData.append('latitude', reportData.latitude);
    formData.append('longitude', reportData.longitude);
    formData.append('severity_level', reportData.severity_level);
    if (reportData.description) formData.append('description', reportData.description);
    if (reportData.media_file) {
      formData.append('media_file', reportData.media_file);
    }

    const response = await api.post('/reports', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  voteOnReport: async (reportId, voteType) => {
    const response = await api.post(`/reports/${reportId}/vote`, { vote_type: voteType });
    return response.data;
  }
};

// Verification API
export const verificationAPI = {
  verifyReport: async (reportId, verificationData) => {
    const response = await api.post(`/reports/${reportId}/verification`, verificationData);
    return response.data;
  },

  getVerificationHistory: async (reportId) => {
    const response = await api.get(`/reports/${reportId}/verifications`);
    return response.data;
  }
};

// Social Media API
export const socialMediaAPI = {
  getSocialMediaPosts: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.platform) params.append('platform', filters.platform);
    if (filters.hazard_type) params.append('hazard_type', filters.hazard_type);
    if (filters.sentiment) params.append('sentiment', filters.sentiment);
    if (filters.relevance_score) params.append('relevance_score', filters.relevance_score);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await api.get(`/social-media?${params.toString()}`);
    return response.data;
  },

  getSocialMediaPostById: async (postId) => {
    const response = await api.get(`/social-media/${postId}`);
    return response.data;
  }
};

// Analysis API
export const analysisAPI = {
  analyzeImage: async (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await api.post('/analysis/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  analyzeText: async (textData) => {
    const response = await api.post('/analysis/text', textData);
    return response.data;
  },

  getAnalysisById: async (analysisId) => {
    const response = await api.get(`/analysis/${analysisId}`);
    return response.data;
  }
};

// Hotspots API
export const hotspotsAPI = {
  getHotspots: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.event_type) params.append('event_type', filters.event_type);
    if (filters.min_intensity) params.append('min_intensity', filters.min_intensity);
    if (filters.latitude && filters.longitude && filters.radius) {
      params.append('latitude', filters.latitude);
      params.append('longitude', filters.longitude);
      params.append('radius', filters.radius);
    }
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await api.get(`/hotspots?${params.toString()}`);
    return response.data;
  },

  getHotspotById: async (hotspotId) => {
    const response = await api.get(`/hotspots/${hotspotId}`);
    return response.data;
  }
};

// Admin API
export const adminAPI = {
  getDashboard: async () => {
    const response = await api.get('/admin/dashboard');
    return response.data;
  },

  getUsers: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.role) params.append('role', filters.role);
    if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
    if (filters.is_verified !== undefined) params.append('is_verified', filters.is_verified);
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await api.get(`/admin/users?${params.toString()}`);
    return response.data;
  },

  updateUserRole: async (userId, roleData) => {
    const response = await api.patch(`/admin/users/${userId}/role`, roleData);
    return response.data;
  }
};

// Alerts API
export const alertsAPI = {
  createAlert: async (alertData) => {
    const response = await api.post('/alerts', alertData);
    return response.data;
  },

  getAlerts: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.alert_type) params.append('alert_type', filters.alert_type);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.status) params.append('status', filters.status);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await api.get(`/alerts?${params.toString()}`);
    return response.data;
  }
};

export default api;
