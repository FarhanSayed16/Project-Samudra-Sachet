// Form validation utilities
export const validators = {
  email: (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value) return 'Email is required';
    if (!emailRegex.test(value)) return 'Please enter a valid email address';
    return null;
  },

  password: (value) => {
    if (!value) return 'Password is required';
    if (value.length < 8) return 'Password must be at least 8 characters long';
    if (!/(?=.*[a-z])/.test(value)) return 'Password must contain at least one lowercase letter';
    if (!/(?=.*[A-Z])/.test(value)) return 'Password must contain at least one uppercase letter';
    if (!/(?=.*\d)/.test(value)) return 'Password must contain at least one number';
    return null;
  },

  confirmPassword: (value, password) => {
    if (!value) return 'Please confirm your password';
    if (value !== password) return 'Passwords do not match';
    return null;
  },

  required: (value, fieldName = 'This field') => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      return `${fieldName} is required`;
    }
    return null;
  },

  minLength: (value, min, fieldName = 'This field') => {
    if (value && value.length < min) {
      return `${fieldName} must be at least ${min} characters long`;
    }
    return null;
  },

  maxLength: (value, max, fieldName = 'This field') => {
    if (value && value.length > max) {
      return `${fieldName} must be no more than ${max} characters long`;
    }
    return null;
  },

  phone: (value) => {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    if (!value) return 'Phone number is required';
    if (!phoneRegex.test(value.replace(/\s/g, ''))) {
      return 'Please enter a valid phone number';
    }
    return null;
  },

  latitude: (value) => {
    const lat = parseFloat(value);
    if (isNaN(lat)) return 'Latitude must be a valid number';
    if (lat < -90 || lat > 90) return 'Latitude must be between -90 and 90';
    return null;
  },

  longitude: (value) => {
    const lng = parseFloat(value);
    if (isNaN(lng)) return 'Longitude must be a valid number';
    if (lng < -180 || lng > 180) return 'Longitude must be between -180 and 180';
    return null;
  },

  severityLevel: (value) => {
    const level = parseInt(value);
    if (isNaN(level)) return 'Severity level must be a number';
    if (level < 1 || level > 10) return 'Severity level must be between 1 and 10';
    return null;
  },

  fileSize: (file, maxSizeMB = 10) => {
    if (!file) return null;
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File size must be less than ${maxSizeMB}MB`;
    }
    return null;
  },

  fileType: (file, allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4']) => {
    if (!file) return null;
    if (!allowedTypes.includes(file.type)) {
      return `File type must be one of: ${allowedTypes.join(', ')}`;
    }
    return null;
  }
};

// Form validation hook
export const useFormValidation = (initialValues = {}, validationRules = {}) => {
  const [values, setValues] = React.useState(initialValues);
  const [errors, setErrors] = React.useState({});
  const [touched, setTouched] = React.useState({});

  const validateField = (name, value) => {
    const rules = validationRules[name];
    if (!rules) return null;

    for (const rule of rules) {
      const error = rule(value, values);
      if (error) return error;
    }
    return null;
  };

  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    Object.keys(validationRules).forEach(field => {
      const error = validateField(field, values[field]);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    
    // Validate field on blur
    const error = validateField(name, values[name]);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const handleSubmit = (onSubmit) => (e) => {
    e.preventDefault();
    setTouched(Object.keys(validationRules).reduce((acc, key) => ({ ...acc, [key]: true }), {}));
    
    if (validateForm()) {
      onSubmit(values);
    }
  };

  const resetForm = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    validateForm,
    resetForm,
    isValid: Object.keys(errors).length === 0 && Object.keys(touched).length > 0
  };
};

// Error message component
export const ErrorMessage = ({ error, touched }) => {
  if (!error || !touched) return null;
  
  return (
    <p className="mt-1 text-sm text-red-600">
      {error}
    </p>
  );
};

// Form field wrapper with validation
export const FormField = ({ 
  name, 
  label, 
  type = 'text', 
  placeholder, 
  value, 
  onChange, 
  onBlur, 
  error, 
  touched, 
  required = false,
  children,
  ...props 
}) => {
  const fieldId = `field-${name}`;
  
  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {children || (
        <input
          id={fieldId}
          type={type}
          name={name}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(name, e.target.value)}
          onBlur={() => onBlur(name)}
          className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm ${
            error && touched ? 'border-red-300' : 'border-gray-300'
          }`}
          {...props}
        />
      )}
      
      <ErrorMessage error={error} touched={touched} />
    </div>
  );
};

