// Performance monitoring utilities
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      pageLoad: null,
      apiCalls: [],
      renderTimes: [],
      memoryUsage: [],
      errors: []
    };
    this.observers = new Map();
    this.isEnabled = process.env.NODE_ENV === 'development' || 
                     localStorage.getItem('perf-monitoring') === 'true';
  }

  // Initialize performance monitoring
  init() {
    if (!this.isEnabled) return;

    this.measurePageLoad();
    this.setupPerformanceObserver();
    this.setupMemoryMonitoring();
    this.setupErrorTracking();
    
    console.log('Performance monitoring initialized');
  }

  // Measure page load performance
  measurePageLoad() {
    if (typeof window === 'undefined') return;

    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0];
      if (navigation) {
        this.metrics.pageLoad = {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          totalTime: navigation.loadEventEnd - navigation.fetchStart,
          firstPaint: this.getFirstPaint(),
          firstContentfulPaint: this.getFirstContentfulPaint()
        };
        
        console.log('Page load metrics:', this.metrics.pageLoad);
      }
    });
  }

  // Get First Paint metric
  getFirstPaint() {
    const paintEntries = performance.getEntriesByType('paint');
    const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
    return firstPaint ? firstPaint.startTime : null;
  }

  // Get First Contentful Paint metric
  getFirstContentfulPaint() {
    const paintEntries = performance.getEntriesByType('paint');
    const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint');
    return firstContentfulPaint ? firstContentfulPaint.startTime : null;
  }

  // Setup Performance Observer
  setupPerformanceObserver() {
    if (!('PerformanceObserver' in window)) return;

    // Observe navigation timing
    const navObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        if (entry.entryType === 'navigation') {
          this.metrics.pageLoad = {
            domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
            loadComplete: entry.loadEventEnd - entry.loadEventStart,
            totalTime: entry.loadEventEnd - entry.fetchStart
          };
        }
      });
    });

    navObserver.observe({ entryTypes: ['navigation'] });

    // Observe resource timing
    const resourceObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        if (entry.entryType === 'resource') {
          this.trackResourceLoad(entry);
        }
      });
    });

    resourceObserver.observe({ entryTypes: ['resource'] });

    // Observe long tasks
    const longTaskObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        console.warn('Long task detected:', entry.duration, 'ms');
        this.metrics.errors.push({
          type: 'long_task',
          duration: entry.duration,
          timestamp: Date.now()
        });
      });
    });

    longTaskObserver.observe({ entryTypes: ['longtask'] });
  }

  // Track resource load performance
  trackResourceLoad(entry) {
    const resource = {
      name: entry.name,
      duration: entry.duration,
      size: entry.transferSize,
      type: this.getResourceType(entry),
      timestamp: Date.now()
    };

    if (resource.type === 'api') {
      this.metrics.apiCalls.push(resource);
    }
  }

  // Determine resource type
  getResourceType(entry) {
    if (entry.name.includes('/api/')) return 'api';
    if (entry.name.endsWith('.js')) return 'script';
    if (entry.name.endsWith('.css')) return 'style';
    if (entry.name.match(/\.(jpg|jpeg|png|gif|svg|webp)$/)) return 'image';
    if (entry.name.match(/\.(woff|woff2|ttf|eot)$/)) return 'font';
    return 'other';
  }

  // Setup memory monitoring
  setupMemoryMonitoring() {
    if (!('memory' in performance)) return;

    const checkMemory = () => {
      const memory = performance.memory;
      this.metrics.memoryUsage.push({
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit,
        timestamp: Date.now()
      });

      // Keep only last 100 memory measurements
      if (this.metrics.memoryUsage.length > 100) {
        this.metrics.memoryUsage = this.metrics.memoryUsage.slice(-100);
      }
    };

    // Check memory every 30 seconds
    setInterval(checkMemory, 30000);
    checkMemory(); // Initial check
  }

  // Setup error tracking
  setupErrorTracking() {
    window.addEventListener('error', (event) => {
      this.metrics.errors.push({
        type: 'javascript_error',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        timestamp: Date.now()
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.metrics.errors.push({
        type: 'unhandled_promise_rejection',
        reason: event.reason,
        timestamp: Date.now()
      });
    });
  }

  // Track API call performance
  trackApiCall(url, method, duration, status) {
    if (!this.isEnabled) return;

    this.metrics.apiCalls.push({
      url,
      method,
      duration,
      status,
      timestamp: Date.now()
    });

    // Keep only last 100 API calls
    if (this.metrics.apiCalls.length > 100) {
      this.metrics.apiCalls = this.metrics.apiCalls.slice(-100);
    }
  }

  // Track component render time
  trackRenderTime(componentName, renderTime) {
    if (!this.isEnabled) return;

    this.metrics.renderTimes.push({
      component: componentName,
      renderTime,
      timestamp: Date.now()
    });

    // Keep only last 100 render times
    if (this.metrics.renderTimes.length > 100) {
      this.metrics.renderTimes = this.metrics.renderTimes.slice(-100);
    }
  }

  // Get performance summary
  getSummary() {
    const apiCalls = this.metrics.apiCalls;
    const renderTimes = this.metrics.renderTimes;
    const errors = this.metrics.errors;

    return {
      pageLoad: this.metrics.pageLoad,
      apiPerformance: {
        total: apiCalls.length,
        averageDuration: apiCalls.length > 0 ? 
          apiCalls.reduce((sum, call) => sum + call.duration, 0) / apiCalls.length : 0,
        slowestCall: apiCalls.length > 0 ? 
          apiCalls.reduce((max, call) => call.duration > max.duration ? call : max) : null,
        errorRate: apiCalls.length > 0 ? 
          apiCalls.filter(call => call.status >= 400).length / apiCalls.length : 0
      },
      renderPerformance: {
        total: renderTimes.length,
        averageRenderTime: renderTimes.length > 0 ? 
          renderTimes.reduce((sum, render) => sum + render.renderTime, 0) / renderTimes.length : 0,
        slowestComponent: renderTimes.length > 0 ? 
          renderTimes.reduce((max, render) => render.renderTime > max.renderTime ? render : max) : null
      },
      errors: {
        total: errors.length,
        byType: errors.reduce((acc, error) => {
          acc[error.type] = (acc[error.type] || 0) + 1;
          return acc;
        }, {})
      },
      memoryUsage: this.metrics.memoryUsage.length > 0 ? 
        this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1] : null
    };
  }

  // Export metrics for analysis
  exportMetrics() {
    const summary = this.getSummary();
    const dataStr = JSON.stringify(summary, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `performance-metrics-${Date.now()}.json`;
    link.click();
  }

  // Clear metrics
  clearMetrics() {
    this.metrics = {
      pageLoad: null,
      apiCalls: [],
      renderTimes: [],
      memoryUsage: [],
      errors: []
    };
  }

  // Enable/disable monitoring
  setEnabled(enabled) {
    this.isEnabled = enabled;
    localStorage.setItem('perf-monitoring', enabled.toString());
    
    if (enabled) {
      this.init();
    }
  }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor();

// React hook for tracking component render time
export const usePerformanceTracking = (componentName) => {
  const startTime = React.useRef(Date.now());

  React.useEffect(() => {
    const renderTime = Date.now() - startTime.current;
    performanceMonitor.trackRenderTime(componentName, renderTime);
  });

  return {
    trackApiCall: performanceMonitor.trackApiCall.bind(performanceMonitor),
    trackRenderTime: performanceMonitor.trackRenderTime.bind(performanceMonitor)
  };
};

// Higher-order component for performance tracking
export const withPerformanceTracking = (WrappedComponent, componentName) => {
  return React.memo((props) => {
    const { trackRenderTime } = usePerformanceTracking(componentName);
    
    React.useEffect(() => {
      trackRenderTime(componentName, 0); // Track mount time
    }, [trackRenderTime]);

    return <WrappedComponent {...props} />;
  });
};

export { PerformanceMonitor, performanceMonitor };

