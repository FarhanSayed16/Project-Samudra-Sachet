import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { notificationsAPI } from '../api/apiService';

// Async thunks
export const fetchNotifications = createAsyncThunk(
  'notifications/fetchNotifications',
  async (params = {}) => {
    const response = await notificationsAPI.getNotifications(params);
    return response;
  }
);

export const markNotificationAsRead = createAsyncThunk(
  'notifications/markAsRead',
  async (notificationId) => {
    const response = await notificationsAPI.markAsRead(notificationId);
    return response;
  }
);

export const markAllAsRead = createAsyncThunk(
  'notifications/markAllAsRead',
  async () => {
    const response = await notificationsAPI.markAllAsRead();
    return response;
  }
);

const notificationsSlice = createSlice({
  name: 'notifications',
  initialState: {
    notifications: [],
    unreadCount: 0,
    isLoading: false,
    error: null,
  },
  reducers: {
    addNotification: (state, action) => {
      state.notifications.unshift(action.payload);
      if (!action.payload.isRead) {
        state.unreadCount += 1;
      }
    },
    removeNotification: (state, action) => {
      const index = state.notifications.findIndex(n => n.id === action.payload);
      if (index !== -1) {
        if (!state.notifications[index].isRead) {
          state.unreadCount -= 1;
        }
        state.notifications.splice(index, 1);
      }
    },
    clearNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch notifications
      .addCase(fetchNotifications.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.isLoading = false;
        state.notifications = action.payload.notifications || [];
        state.unreadCount = action.payload.unread_count || 0;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message;
      })
      // Mark as read
      .addCase(markNotificationAsRead.fulfilled, (state, action) => {
        const notification = state.notifications.find(n => n.id === action.payload.id);
        if (notification && !notification.isRead) {
          notification.isRead = true;
          state.unreadCount -= 1;
        }
      })
      // Mark all as read
      .addCase(markAllAsRead.fulfilled, (state) => {
        state.notifications.forEach(notification => {
          notification.isRead = true;
        });
        state.unreadCount = 0;
      });
  },
});

export const { addNotification, removeNotification, clearNotifications } = notificationsSlice.actions;
export default notificationsSlice.reducer;

