import React from 'react';
import PropTypes from 'prop-types';

// Loading spinner component
export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  return (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-primary-600 ${sizeClasses[size]} ${className}`} />
  );
};

// Loading overlay component
export const LoadingOverlay = ({ isLoading, children, message = 'Loading...' }) => {
  if (!isLoading) return children;

  return (
    <div className="relative">
      {children}
      <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mx-auto mb-4" />
          <p className="text-gray-600">{message}</p>
        </div>
      </div>
    </div>
  );
};

// Loading button component
export const LoadingButton = ({ 
  isLoading, 
  loadingText = 'Loading...', 
  children, 
  disabled,
  className = '',
  ...props 
}) => {
  return (
    <button
      disabled={disabled || isLoading}
      className={`relative ${className}`}
      {...props}
    >
      {isLoading && (
        <LoadingSpinner size="sm" className="absolute left-3 top-1/2 transform -translate-y-1/2" />
      )}
      <span className={isLoading ? 'ml-6' : ''}>
        {isLoading ? loadingText : children}
      </span>
    </button>
  );
};

// Skeleton loading components
export const SkeletonCard = () => (
  <div className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
    <div className="flex items-center space-x-4 mb-4">
      <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
      <div className="flex-1">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>
    <div className="space-y-2">
      <div className="h-3 bg-gray-200 rounded"></div>
      <div className="h-3 bg-gray-200 rounded w-5/6"></div>
      <div className="h-3 bg-gray-200 rounded w-4/6"></div>
    </div>
  </div>
);

export const SkeletonTable = ({ rows = 5, columns = 4 }) => (
  <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
    <div className="px-6 py-4 border-b border-gray-200">
      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
    </div>
    <div className="divide-y divide-gray-200">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="px-6 py-4 animate-pulse">
          <div className="flex space-x-4">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <div key={colIndex} className="flex-1">
                <div className="h-3 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Loading states for different scenarios
export const LoadingStates = {
  // Page loading
  PageLoading: ({ message = 'Loading page...' }) => (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <LoadingSpinner size="xl" className="mx-auto mb-4" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  ),

  // Data loading
  DataLoading: ({ message = 'Loading data...' }) => (
    <div className="flex items-center justify-center py-8">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mx-auto mb-2" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  ),

  // Empty state
  EmptyState: ({ 
    icon, 
    title = 'No data available', 
    description = 'There is no data to display at the moment.',
    action 
  }) => (
    <div className="text-center py-12">
      {icon && (
        <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      {action && action}
    </div>
  ),

  // Error state
  ErrorState: ({ 
    title = 'Something went wrong', 
    description = 'An error occurred while loading data.',
    onRetry,
    error 
  }) => (
    <div className="text-center py-12">
      <div className="mx-auto h-12 w-12 text-red-400 mb-4">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Try Again
        </button>
      )}
      {error && process.env.NODE_ENV === 'development' && (
        <details className="mt-4 text-left">
          <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
            Error Details
          </summary>
          <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded overflow-auto">
            {error.toString()}
          </pre>
        </details>
      )}
    </div>
  )
};

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(['sm', 'md', 'lg', 'xl']),
  className: PropTypes.string
};

LoadingOverlay.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  children: PropTypes.node.isRequired,
  message: PropTypes.string
};

LoadingButton.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  loadingText: PropTypes.string,
  children: PropTypes.node.isRequired,
  disabled: PropTypes.bool,
  className: PropTypes.string
};

SkeletonTable.propTypes = {
  rows: PropTypes.number,
  columns: PropTypes.number
};

LoadingStates.PageLoading.propTypes = {
  message: PropTypes.string
};

LoadingStates.DataLoading.propTypes = {
  message: PropTypes.string
};

LoadingStates.EmptyState.propTypes = {
  icon: PropTypes.node,
  title: PropTypes.string,
  description: PropTypes.string,
  action: PropTypes.node
};

LoadingStates.ErrorState.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  onRetry: PropTypes.func,
  error: PropTypes.instanceOf(Error)
};

