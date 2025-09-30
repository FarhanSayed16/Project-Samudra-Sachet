import React from 'react';
import PropTypes from 'prop-types';

const cn = (...classes) => classes.filter(Boolean).join(' ');

const Label = ({ 
  children, 
  className = '',
  htmlFor,
  ...rest 
}) => {
  return (
    <label
      htmlFor={htmlFor}
      className={cn(
        'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
        className
      )}
      {...rest}
    >
      {children}
    </label>
  );
};

Label.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  htmlFor: PropTypes.string,
};

export default Label;
export { Label };
