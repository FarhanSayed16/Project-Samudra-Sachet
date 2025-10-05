import React, { useEffect } from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { RouterProvider } from 'react-router-dom';
import router from './router';
import { ErrorBoundary } from './components';
import { ToastProvider } from './components/Toast';
import { store, persistor } from './state/store';
import AuthInitializer from './AuthInitializer';
import serviceWorkerManager from './utils/serviceWorker';
import { offlineStorage, networkManager } from './utils/offlineStorage';
import { performanceMonitor } from './utils/performance';
import { securityManager } from './utils/security';

export default function App() {
  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    console.log('🌊 Project Samudra Sachet Dashboard - API Base:', apiBase);

    // Initialize all capabilities
    const initializeApp = async () => {
      try {
        // Initialize security
        securityManager.init();
        console.log('✅ Security manager initialized');

        // Initialize performance monitoring
        performanceMonitor.init();
        console.log('✅ Performance monitoring initialized');

        // Initialize offline storage
        await offlineStorage.init();
        console.log('✅ Offline storage initialized');

        // Register service worker
        await serviceWorkerManager.register();
        console.log('✅ Service worker registered');

        // Set up network status monitoring
        networkManager.addListener((status) => {
          console.log('🌐 Network status changed:', status);
          
          // Show offline notification
          if (status === 'offline') {
            console.log('📱 App is now offline');
          } else if (status === 'online') {
            console.log('📱 App is back online');
            // Trigger sync of offline actions
            window.dispatchEvent(new CustomEvent('online-sync'));
          }
        });

        console.log('🌊 All capabilities initialized successfully');
      } catch (error) {
        console.error('❌ Failed to initialize app capabilities:', error);
      }
    };

    initializeApp();
  }, []);

  return (
    <Provider store={store}>
      <PersistGate loading={<div>Loading...</div>} persistor={persistor}>
        <ErrorBoundary>
          <ToastProvider>
            <AuthInitializer>
              <RouterProvider router={router} />
            </AuthInitializer>
          </ToastProvider>
        </ErrorBoundary>
      </PersistGate>
    </Provider>
  );
}
