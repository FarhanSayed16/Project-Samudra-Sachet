import React from 'react';
import PropTypes from 'prop-types';

const cn = (...classes) => classes.filter(Boolean).join(' ');

const Input = ({ 
  type = 'text',
  className = '',
  error = false,
  ...rest 
}) => {
  const baseStyles = 'flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50';
  const errorStyles = error ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary-500';

  return (
    <input
      type={type}
      className={cn(baseStyles, errorStyles, className)}
      {...rest}
    />
  );
};

Input.propTypes = {
  type: PropTypes.string,
  className: PropTypes.string,
  error: PropTypes.bool,
};

export default Input;
export { Input };
