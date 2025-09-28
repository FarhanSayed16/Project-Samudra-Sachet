import React from 'react';
import PropTypes from 'prop-types';

const cn = (...classes) => classes.filter(Boolean).join(' ');

const Card = ({ children, className = '', ...rest }) => {
  return (
    <div
      className={cn(
        'rounded-lg border border-gray-200 bg-white shadow-sm',
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
};

const CardHeader = ({ children, className = '', ...rest }) => {
  return (
    <div
      className={cn('flex flex-col space-y-1.5 p-6', className)}
      {...rest}
    >
      {children}
    </div>
  );
};

const CardTitle = ({ children, className = '', ...rest }) => {
  return (
    <h3
      className={cn('text-lg font-semibold leading-none tracking-tight', className)}
      {...rest}
    >
      {children}
    </h3>
  );
};

const CardDescription = ({ children, className = '', ...rest }) => {
  return (
    <p
      className={cn('text-sm text-gray-500', className)}
      {...rest}
    >
      {children}
    </p>
  );
};

const CardContent = ({ children, className = '', ...rest }) => {
  return (
    <div className={cn('p-6 pt-0', className)} {...rest}>
      {children}
    </div>
  );
};

const CardFooter = ({ children, className = '', ...rest }) => {
  return (
    <div className={cn('flex items-center p-6 pt-0', className)} {...rest}>
      {children}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

CardHeader.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

CardTitle.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

CardDescription.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

CardContent.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

CardFooter.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };
