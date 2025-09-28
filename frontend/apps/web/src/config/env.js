// Environment configuration for Project Samudra Sachet Dashboard
export const config = {
  API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  APP_NAME: 'Project Samudra Sachet',
  APP_VERSION: '1.0.0',
  ENVIRONMENT: import.meta.env.MODE || 'development',
};
