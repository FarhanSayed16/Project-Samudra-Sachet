import React from 'react';
import PropTypes from 'prop-types';

const cn = (...classes) => classes.filter(Boolean).join(' ');

const Badge = ({ 
  variant = 'default',
  children, 
  className = '',
  ...rest 
}) => {
  const baseStyles = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium';
  
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    secondary: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    outline: 'border border-gray-300 text-gray-700',
  };

  return (
    <span
      className={cn(baseStyles, variantClasses[variant], className)}
      {...rest}
    >
      {children}
    </span>
  );
};

Badge.propTypes = {
  variant: PropTypes.oneOf(['default', 'secondary', 'success', 'warning', 'danger', 'outline']),
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

export default Badge;
export { Badge };
