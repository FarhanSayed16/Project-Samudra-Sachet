import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage/index.js';

import authReducer from './slices/authSlice';
import reportsReducer from './slices/reportsSlice';
import hotspotsReducer from './slices/hotspotsSlice';
import adminReducer from './slices/adminSlice';

// Persist configuration for auth
const authPersistConfig = {
  key: 'auth',
  storage,
  whitelist: ['user', 'token', 'refreshToken', 'isAuthenticated', 'userRole'],
};

const persistedAuthReducer = persistReducer(authPersistConfig, authReducer);

// Configure store
export const store = configureStore({
  reducer: {
    auth: persistedAuthReducer,
    reports: reportsReducer,
    hotspots: hotspotsReducer,
    admin: adminReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export const persistor = persistStore(store);
