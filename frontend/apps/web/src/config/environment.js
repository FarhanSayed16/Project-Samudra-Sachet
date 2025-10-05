// Environment configuration for production deployment
const environments = {
  development: {
    API_BASE_URL: 'http://localhost:8000/api/v1',
    WS_URL: 'ws://localhost:8000/ws',
    VAPID_PUBLIC_KEY: 'your-vapid-public-key-dev',
    ENABLE_ANALYTICS: false,
    ENABLE_PERFORMANCE_MONITORING: true,
    ENABLE_DEBUG_LOGS: true,
    CACHE_TTL: 300000, // 5 minutes
    RATE_LIMIT_CALLS: 100,
    RATE_LIMIT_WINDOW: 60000, // 1 minute
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_FILE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'video/mp4'],
    SENTRY_DSN: null,
    GOOGLE_ANALYTICS_ID: null
  },
  
  staging: {
    API_BASE_URL: 'https://staging-api.samudra-sachet.com/api/v1',
    WS_URL: 'wss://staging-api.samudra-sachet.com/ws',
    VAPID_PUBLIC_KEY: 'your-vapid-public-key-staging',
    ENABLE_ANALYTICS: true,
    ENABLE_PERFORMANCE_MONITORING: true,
    ENABLE_DEBUG_LOGS: true,
    CACHE_TTL: 600000, // 10 minutes
    RATE_LIMIT_CALLS: 200,
    RATE_LIMIT_WINDOW: 60000, // 1 minute
    MAX_FILE_SIZE: 20 * 1024 * 1024, // 20MB
    ALLOWED_FILE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'application/pdf'],
    SENTRY_DSN: 'your-sentry-dsn-staging',
    GOOGLE_ANALYTICS_ID: 'GA-STAGING-ID'
  },
  
  production: {
    API_BASE_URL: 'https://api.samudra-sachet.com/api/v1',
    WS_URL: 'wss://api.samudra-sachet.com/ws',
    VAPID_PUBLIC_KEY: 'your-vapid-public-key-production',
    ENABLE_ANALYTICS: true,
    ENABLE_PERFORMANCE_MONITORING: false,
    ENABLE_DEBUG_LOGS: false,
    CACHE_TTL: 1800000, // 30 minutes
    RATE_LIMIT_CALLS: 500,
    RATE_LIMIT_WINDOW: 60000, // 1 minute
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_FILE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'application/pdf', 'text/plain'],
    SENTRY_DSN: 'your-sentry-dsn-production',
    GOOGLE_ANALYTICS_ID: 'GA-PRODUCTION-ID'
  }
};

// Get current environment
const getCurrentEnvironment = () => {
  const env = import.meta.env.MODE || 'development';
  return environments[env] || environments.development;
};

// Environment configuration
export const config = {
  ...getCurrentEnvironment(),
  
  // Override with environment variables if available
  API_BASE_URL: import.meta.env.VITE_API_URL || getCurrentEnvironment().API_BASE_URL,
  WS_URL: import.meta.env.VITE_WS_URL || getCurrentEnvironment().WS_URL,
  VAPID_PUBLIC_KEY: import.meta.env.VITE_VAPID_PUBLIC_KEY || getCurrentEnvironment().VAPID_PUBLIC_KEY,
  SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN || getCurrentEnvironment().SENTRY_DSN,
  GOOGLE_ANALYTICS_ID: import.meta.env.VITE_GA_ID || getCurrentEnvironment().GOOGLE_ANALYTICS_ID,
  
  // App metadata
  APP_NAME: 'Project Samudra Sachet',
  APP_VERSION: '1.0.0',
  APP_DESCRIPTION: 'Comprehensive platform for crowdsourced ocean hazard reporting and social media analytics',
  
  // Feature flags
  FEATURES: {
    OFFLINE_SUPPORT: true,
    PUSH_NOTIFICATIONS: true,
    REAL_TIME_UPDATES: true,
    FILE_UPLOADS: true,
    SOCIAL_MEDIA_INTEGRATION: true,
    AI_ANALYSIS: true,
    MAP_INTEGRATION: true,
    EXPORT_DATA: true
  },
  
  // Security settings
  SECURITY: {
    CSP_REPORT_URI: '/api/v1/security/csp-violation',
    SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
    MAX_LOGIN_ATTEMPTS: 5,
    LOCKOUT_DURATION: 15 * 60 * 1000, // 15 minutes
    PASSWORD_MIN_LENGTH: 8,
    PASSWORD_REQUIRE_UPPERCASE: true,
    PASSWORD_REQUIRE_LOWERCASE: true,
    PASSWORD_REQUIRE_NUMBERS: true,
    PASSWORD_REQUIRE_SPECIAL_CHARS: true
  },
  
  // Performance settings
  PERFORMANCE: {
    LAZY_LOAD_THRESHOLD: 100, // pixels
    DEBOUNCE_DELAY: 300, // milliseconds
    THROTTLE_DELAY: 1000, // milliseconds
    MAX_CONCURRENT_REQUESTS: 5,
    REQUEST_TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000 // 1 second
  },
  
  // UI settings
  UI: {
    THEME: 'light', // light, dark, auto
    LANGUAGE: 'en',
    TIMEZONE: 'UTC',
    DATE_FORMAT: 'YYYY-MM-DD',
    TIME_FORMAT: 'HH:mm:ss',
    CURRENCY: 'USD',
    UNITS: 'metric' // metric, imperial
  },
  
  // API settings
  API: {
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
    MAX_RETRY_DELAY: 10000,
    BACKOFF_MULTIPLIER: 2
  }
};

// Validate configuration
export const validateConfig = () => {
  const errors = [];
  
  if (!config.API_BASE_URL) {
    errors.push('API_BASE_URL is required');
  }
  
  if (!config.WS_URL) {
    errors.push('WS_URL is required');
  }
  
  if (config.FEATURES.PUSH_NOTIFICATIONS && !config.VAPID_PUBLIC_KEY) {
    errors.push('VAPID_PUBLIC_KEY is required for push notifications');
  }
  
  if (errors.length > 0) {
    console.error('Configuration validation errors:', errors);
    throw new Error(`Configuration validation failed: ${errors.join(', ')}`);
  }
  
  return true;
};

// Get feature flag
export const isFeatureEnabled = (feature) => {
  return config.FEATURES[feature] === true;
};

// Get environment-specific setting
export const getSetting = (key, defaultValue = null) => {
  return config[key] !== undefined ? config[key] : defaultValue;
};

// Check if running in production
export const isProduction = () => {
  return import.meta.env.MODE === 'production';
};

// Check if running in development
export const isDevelopment = () => {
  return import.meta.env.MODE === 'development';
};

// Check if running in staging
export const isStaging = () => {
  return import.meta.env.MODE === 'staging';
};

// Export default config
export default config;

