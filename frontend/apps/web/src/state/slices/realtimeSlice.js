import { createSlice } from '@reduxjs/toolkit';
import { REALTIME_EVENTS } from '../utils/realtime';

const realtimeSlice = createSlice({
  name: 'realtime',
  initialState: {
    isConnected: false,
    connectionStatus: 'disconnected', // disconnected, connecting, connected, error
    lastEvent: null,
    eventHistory: [],
    error: null,
    stats: {
      totalEvents: 0,
      eventsByType: {},
      lastConnected: null,
      lastDisconnected: null
    }
  },
  reducers: {
    setConnectionStatus: (state, action) => {
      const { status, error } = action.payload;
      state.connectionStatus = status;
      state.isConnected = status === 'connected';
      state.error = error || null;
      
      if (status === 'connected') {
        state.stats.lastConnected = new Date().toISOString();
      } else if (status === 'disconnected') {
        state.stats.lastDisconnected = new Date().toISOString();
      }
    },
    
    addRealtimeEvent: (state, action) => {
      const { type, data, timestamp } = action.payload;
      
      state.lastEvent = { type, data, timestamp };
      state.eventHistory.unshift({ type, data, timestamp });
      
      // Keep only last 100 events
      if (state.eventHistory.length > 100) {
        state.eventHistory = state.eventHistory.slice(0, 100);
      }
      
      // Update stats
      state.stats.totalEvents += 1;
      state.stats.eventsByType[type] = (state.stats.eventsByType[type] || 0) + 1;
    },
    
    clearEventHistory: (state) => {
      state.eventHistory = [];
      state.lastEvent = null;
    },
    
    resetStats: (state) => {
      state.stats = {
        totalEvents: 0,
        eventsByType: {},
        lastConnected: null,
        lastDisconnected: null
      };
    },
    
    setError: (state, action) => {
      state.error = action.payload;
      state.connectionStatus = 'error';
    },
    
    clearError: (state) => {
      state.error = null;
      if (state.connectionStatus === 'error') {
        state.connectionStatus = 'disconnected';
      }
    }
  }
});

export const {
  setConnectionStatus,
  addRealtimeEvent,
  clearEventHistory,
  resetStats,
  setError,
  clearError
} = realtimeSlice.actions;

export default realtimeSlice.reducer;

