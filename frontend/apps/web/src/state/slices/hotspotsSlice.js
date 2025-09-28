import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { hotspotsAPI } from '../../api/apiService';

// Async thunks
export const fetchHotspots = createAsyncThunk(
  'hotspots/fetchHotspots',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await hotspotsAPI.getHotspots(filters);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch hotspots');
    }
  }
);

export const fetchHotspotById = createAsyncThunk(
  'hotspots/fetchHotspotById',
  async (hotspotId, { rejectWithValue }) => {
    try {
      const response = await hotspotsAPI.getHotspotById(hotspotId);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch hotspot');
    }
  }
);

// Initial state
const initialState = {
  hotspots: [],
  currentHotspot: null,
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    pages: 0,
  },
  filters: {
    status: null,
    event_type: null,
    min_intensity: null,
    latitude: null,
    longitude: null,
    radius: null,
  },
  isLoading: false,
  error: null,
};

// Hotspots slice
const hotspotsSlice = createSlice({
  name: 'hotspots',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = initialState.filters;
    },
    setCurrentHotspot: (state, action) => {
      state.currentHotspot = action.payload;
    },
    clearCurrentHotspot: (state) => {
      state.currentHotspot = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch hotspots
      .addCase(fetchHotspots.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchHotspots.fulfilled, (state, action) => {
        state.isLoading = false;
        state.hotspots = action.payload.items || action.payload;
        if (action.payload.pagination) {
          state.pagination = action.payload.pagination;
        }
        state.error = null;
      })
      .addCase(fetchHotspots.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      // Fetch hotspot by ID
      .addCase(fetchHotspotById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchHotspotById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentHotspot = action.payload;
        state.error = null;
      })
      .addCase(fetchHotspotById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { 
  setFilters, 
  clearFilters, 
  setCurrentHotspot, 
  clearCurrentHotspot, 
  clearError 
} = hotspotsSlice.actions;
export default hotspotsSlice.reducer;
