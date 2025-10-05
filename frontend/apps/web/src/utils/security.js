// Security utilities and hardening
class SecurityManager {
  constructor() {
    this.cspViolations = [];
    this.securityHeaders = {
      'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:; frame-ancestors 'none'; base-uri 'self'; form-action 'self';",
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=(), usb=()'
    };
  }

  // Initialize security measures
  init() {
    this.setupCSPViolationReporting();
    this.setupXSSProtection();
    this.setupClickjackingProtection();
    this.setupSecureStorage();
    this.setupInputSanitization();
    
    console.log('Security manager initialized');
  }

  // Setup Content Security Policy violation reporting
  setupCSPViolationReporting() {
    document.addEventListener('securitypolicyviolation', (event) => {
      const violation = {
        blockedURI: event.blockedURI,
        violatedDirective: event.violatedDirective,
        originalPolicy: event.originalPolicy,
        sourceFile: event.sourceFile,
        lineNumber: event.lineNumber,
        columnNumber: event.columnNumber,
        timestamp: Date.now()
      };

      this.cspViolations.push(violation);
      console.warn('CSP Violation:', violation);

      // Report to server in production
      if (process.env.NODE_ENV === 'production') {
        this.reportCSPViolation(violation);
      }
    });
  }

  // Report CSP violation to server
  async reportCSPViolation(violation) {
    try {
      await fetch('/api/v1/security/csp-violation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(violation)
      });
    } catch (error) {
      console.error('Failed to report CSP violation:', error);
    }
  }

  // Setup XSS protection
  setupXSSProtection() {
    // Sanitize user input
    this.sanitizeInput = (input) => {
      if (typeof input !== 'string') return input;
      
      // Remove potentially dangerous characters
      return input
        .replace(/[<>]/g, '') // Remove < and >
        .replace(/javascript:/gi, '') // Remove javascript: protocol
        .replace(/on\w+=/gi, '') // Remove event handlers
        .trim();
    };

    // Escape HTML entities
    this.escapeHtml = (text) => {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    };
  }

  // Setup clickjacking protection
  setupClickjackingProtection() {
    // Check if page is in iframe
    if (window.top !== window.self) {
      console.warn('Page is loaded in iframe - potential clickjacking attempt');
      // In production, you might want to redirect or show warning
    }
  }

  // Setup secure storage
  setupSecureStorage() {
    // Secure localStorage wrapper
    this.secureStorage = {
      setItem: (key, value) => {
        try {
          const encrypted = this.encrypt(value);
          localStorage.setItem(key, encrypted);
        } catch (error) {
          console.error('Failed to store secure data:', error);
        }
      },
      
      getItem: (key) => {
        try {
          const encrypted = localStorage.getItem(key);
          return encrypted ? this.decrypt(encrypted) : null;
        } catch (error) {
          console.error('Failed to retrieve secure data:', error);
          return null;
        }
      },
      
      removeItem: (key) => {
        localStorage.removeItem(key);
      }
    };
  }

  // Simple encryption/decryption (for demo purposes)
  encrypt(text) {
    // In production, use proper encryption libraries
    return btoa(text);
  }

  decrypt(encryptedText) {
    // In production, use proper decryption libraries
    return atob(encryptedText);
  }

  // Setup input sanitization
  setupInputSanitization() {
    // Sanitize form inputs
    this.sanitizeFormData = (formData) => {
      const sanitized = {};
      for (const [key, value] of Object.entries(formData)) {
        sanitized[key] = this.sanitizeInput(value);
      }
      return sanitized;
    };

    // Validate file uploads
    this.validateFileUpload = (file, allowedTypes = [], maxSize = 10 * 1024 * 1024) => {
      const errors = [];

      if (!file) {
        errors.push('No file provided');
        return errors;
      }

      if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
        errors.push(`File type ${file.type} not allowed`);
      }

      if (file.size > maxSize) {
        errors.push(`File size ${file.size} exceeds maximum ${maxSize}`);
      }

      // Check file extension
      const allowedExtensions = allowedTypes.map(type => type.split('/')[1]);
      const fileExtension = file.name.split('.').pop().toLowerCase();
      if (allowedExtensions.length > 0 && !allowedExtensions.includes(fileExtension)) {
        errors.push(`File extension .${fileExtension} not allowed`);
      }

      return errors;
    };
  }

  // Rate limiting for API calls
  setupRateLimiting() {
    const apiCalls = new Map();
    const RATE_LIMIT_WINDOW = 60000; // 1 minute
    const MAX_CALLS_PER_WINDOW = 100;

    return (endpoint) => {
      const now = Date.now();
      const key = `${endpoint}_${Math.floor(now / RATE_LIMIT_WINDOW)}`;
      
      const calls = apiCalls.get(key) || 0;
      if (calls >= MAX_CALLS_PER_WINDOW) {
        throw new Error('Rate limit exceeded');
      }
      
      apiCalls.set(key, calls + 1);
      
      // Clean up old entries
      setTimeout(() => {
        apiCalls.delete(key);
      }, RATE_LIMIT_WINDOW);
    };
  }

  // Validate JWT token
  validateJWTToken(token) {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid token format');
      }

      const payload = JSON.parse(atob(parts[1]));
      const now = Math.floor(Date.now() / 1000);

      if (payload.exp && payload.exp < now) {
        throw new Error('Token expired');
      }

      if (payload.iat && payload.iat > now) {
        throw new Error('Token not yet valid');
      }

      return payload;
    } catch (error) {
      console.error('JWT validation error:', error);
      return null;
    }
  }

  // Generate secure random string
  generateSecureRandom(length = 32) {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  // Hash password (client-side, for demo purposes)
  async hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // Check for suspicious activity
  detectSuspiciousActivity() {
    const suspiciousPatterns = [
      /<script/i,
      /javascript:/i,
      /on\w+=/i,
      /eval\(/i,
      /document\.cookie/i,
      /window\.location/i
    ];

    return (input) => {
      if (typeof input !== 'string') return false;
      
      return suspiciousPatterns.some(pattern => pattern.test(input));
    };
  }

  // Get security status
  getSecurityStatus() {
    return {
      cspViolations: this.cspViolations.length,
      isSecureContext: window.isSecureContext,
      hasCrypto: !!window.crypto,
      hasSubtleCrypto: !!window.crypto?.subtle,
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform
    };
  }

  // Clear security data
  clearSecurityData() {
    this.cspViolations = [];
  }
}

// Input validation utilities
export const validators = {
  email: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  password: (password) => {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return {
      isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar,
      errors: [
        password.length < minLength && 'Password must be at least 8 characters long',
        !hasUpperCase && 'Password must contain at least one uppercase letter',
        !hasLowerCase && 'Password must contain at least one lowercase letter',
        !hasNumbers && 'Password must contain at least one number',
        !hasSpecialChar && 'Password must contain at least one special character'
      ].filter(Boolean)
    };
  },

  phone: (phone) => {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
  },

  url: (url) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }
};

// Create singleton instance
const securityManager = new SecurityManager();

export { SecurityManager, securityManager };

