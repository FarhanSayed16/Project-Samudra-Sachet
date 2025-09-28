import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { reportsAPI } from '../../api/apiService';

// Async thunks
export const fetchReports = createAsyncThunk(
  'reports/fetchReports',
  async (filters = {}, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getReports(filters);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch reports');
    }
  }
);

export const fetchReportById = createAsyncThunk(
  'reports/fetchReportById',
  async (reportId, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getReportById(reportId);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch report');
    }
  }
);

export const createReport = createAsyncThunk(
  'reports/createReport',
  async (reportData, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.createReport(reportData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create report');
    }
  }
);

export const voteOnReport = createAsyncThunk(
  'reports/voteOnReport',
  async ({ reportId, voteType }, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.voteOnReport(reportId, voteType);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to vote on report');
    }
  }
);

// Initial state
const initialState = {
  reports: [],
  currentReport: null,
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    pages: 0,
  },
  filters: {
    status: null,
    hazard_type: null,
    severity_level: null,
    latitude: null,
    longitude: null,
    radius: null,
    start_date: null,
    end_date: null,
  },
  isLoading: false,
  error: null,
};

// Reports slice
const reportsSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = initialState.filters;
    },
    setCurrentReport: (state, action) => {
      state.currentReport = action.payload;
    },
    clearCurrentReport: (state) => {
      state.currentReport = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch reports
      .addCase(fetchReports.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchReports.fulfilled, (state, action) => {
        state.isLoading = false;
        state.reports = action.payload.items || action.payload;
        if (action.payload.pagination) {
          state.pagination = action.payload.pagination;
        }
        state.error = null;
      })
      .addCase(fetchReports.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      // Fetch report by ID
      .addCase(fetchReportById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchReportById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentReport = action.payload;
        state.error = null;
      })
      .addCase(fetchReportById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      // Create report
      .addCase(createReport.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createReport.fulfilled, (state, action) => {
        state.isLoading = false;
        state.reports.unshift(action.payload);
        state.error = null;
      })
      .addCase(createReport.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      // Vote on report
      .addCase(voteOnReport.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(voteOnReport.fulfilled, (state, action) => {
        state.isLoading = false;
        const report = state.reports.find(r => r.id === action.payload.id);
        if (report) {
          report.upvote_count = action.payload.upvote_count;
          report.downvote_count = action.payload.downvote_count;
        }
        if (state.currentReport && state.currentReport.id === action.payload.id) {
          state.currentReport.upvote_count = action.payload.upvote_count;
          state.currentReport.downvote_count = action.payload.downvote_count;
        }
        state.error = null;
      })
      .addCase(voteOnReport.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { 
  setFilters, 
  clearFilters, 
  setCurrentReport, 
  clearCurrentReport, 
  clearError 
} = reportsSlice.actions;
export default reportsSlice.reducer;
