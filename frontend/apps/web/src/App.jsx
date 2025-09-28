import React, { useEffect } from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { RouterProvider } from 'react-router-dom';
import router from './router';
import { ErrorBoundary } from './components';
import { store, persistor } from './state/store';
import AuthInitializer from './AuthInitializer';

export default function App() {
  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    console.log('🌊 Project Samudra Sachet Dashboard - API Base:', apiBase);
  }, []);

  return (
    <Provider store={store}>
      <PersistGate loading={<div>Loading...</div>} persistor={persistor}>
        <ErrorBoundary>
          <AuthInitializer>
            <RouterProvider router={router} />
          </AuthInitializer>
        </ErrorBoundary>
      </PersistGate>
    </Provider>
  );
}
