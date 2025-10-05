// Code splitting and lazy loading utilities
import React, { Suspense, lazy } from 'react';

// Lazy load components with error boundaries
export const createLazyComponent = (importFunc, fallback = null) => {
  const LazyComponent = lazy(importFunc);
  
  return (props) => (
    <Suspense fallback={fallback || <div>Loading...</div>}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Lazy load pages
export const LazyPages = {
  DashboardPage: createLazyComponent(() => import('../pages/DashboardPage')),
  ReportsPage: createLazyComponent(() => import('../pages/ReportsPage')),
  HotspotsPage: createLazyComponent(() => import('../pages/HotspotsPage')),
  AdminPage: createLazyComponent(() => import('../pages/AdminPage')),
  ProfilePage: createLazyComponent(() => import('../pages/ProfilePage')),
  LoginPage: createLazyComponent(() => import('../pages/LoginPage')),
  RegisterPage: createLazyComponent(() => import('../pages/RegisterPage'))
};

// Lazy load components
export const LazyComponents = {
  NotificationBell: createLazyComponent(() => import('../components/NotificationBell')),
  ConnectionStatus: createLazyComponent(() => import('../components/ConnectionStatus')),
  ErrorBoundary: createLazyComponent(() => import('../components/ErrorBoundary')),
  LoadingStates: createLazyComponent(() => import('../components/LoadingStates'))
};

// Route-based code splitting
export const withCodeSplitting = (importFunc) => {
  return createLazyComponent(importFunc, (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading page...</p>
      </div>
    </div>
  ));
};

// Dynamic import with retry
export const dynamicImport = (importFunc, retries = 3) => {
  return new Promise((resolve, reject) => {
    const attemptImport = (attempt) => {
      importFunc()
        .then(resolve)
        .catch((error) => {
          if (attempt < retries) {
            console.warn(`Import attempt ${attempt} failed, retrying...`, error);
            setTimeout(() => attemptImport(attempt + 1), 1000 * attempt);
          } else {
            reject(error);
          }
        });
    };
    
    attemptImport(1);
  });
};

// Preload components
export const preloadComponent = (importFunc) => {
  const componentPromise = importFunc();
  
  // Preload the component
  componentPromise.catch(() => {
    // Ignore preload errors
  });
  
  return componentPromise;
};

// Preload multiple components
export const preloadComponents = (importFuncs) => {
  return Promise.allSettled(importFuncs.map(preloadComponent));
};

// Route preloading
export const preloadRoute = (routePath, importFunc) => {
  // Preload on hover
  const preloadOnHover = () => {
    preloadComponent(importFunc);
  };
  
  // Preload on focus
  const preloadOnFocus = () => {
    preloadComponent(importFunc);
  };
  
  return {
    onMouseEnter: preloadOnHover,
    onFocus: preloadOnFocus
  };
};

// Bundle analyzer helper
export const analyzeBundle = () => {
  if (process.env.NODE_ENV === 'development') {
    console.log('Bundle analysis available in development mode');
    console.log('Use webpack-bundle-analyzer or similar tools for detailed analysis');
  }
};

// Performance monitoring for lazy loading
export const trackLazyLoadPerformance = (componentName, loadTime) => {
  if (typeof window !== 'undefined' && window.performance) {
    const entry = {
      name: `lazy-load-${componentName}`,
      startTime: performance.now() - loadTime,
      duration: loadTime,
      entryType: 'measure'
    };
    
    performance.mark(`lazy-load-${componentName}-end`);
    performance.measure(`lazy-load-${componentName}`, `lazy-load-${componentName}-start`, `lazy-load-${componentName}-end`);
    
    console.log(`Lazy load performance for ${componentName}:`, entry);
  }
};

// Lazy load with performance tracking
export const createTrackedLazyComponent = (importFunc, componentName) => {
  const LazyComponent = lazy(() => {
    const startTime = performance.now();
    performance.mark(`${componentName}-start`);
    
    return importFunc().then(module => {
      const loadTime = performance.now() - startTime;
      trackLazyLoadPerformance(componentName, loadTime);
      return module;
    });
  });
  
  return (props) => (
    <Suspense fallback={<div>Loading {componentName}...</div>}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Export utilities
export default {
  createLazyComponent,
  LazyPages,
  LazyComponents,
  withCodeSplitting,
  dynamicImport,
  preloadComponent,
  preloadComponents,
  preloadRoute,
  analyzeBundle,
  trackLazyLoadPerformance,
  createTrackedLazyComponent
};

