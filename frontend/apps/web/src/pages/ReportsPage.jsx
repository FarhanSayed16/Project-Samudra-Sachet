import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchReports, setFilters } from '../state/slices/reportsSlice';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Badge from '../components/ui/Badge';
import { Search, Filter, MapPin, Calendar, AlertTriangle } from 'lucide-react';

const ReportsPage = () => {
  const dispatch = useDispatch();
  const { reports, isLoading, filters, pagination } = useSelector((state) => state.reports);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  useEffect(() => {
    dispatch(fetchReports(filters));
  }, [dispatch, filters]);

  const handleSearch = () => {
    const newFilters = {
      ...filters,
      search: searchTerm,
      status: selectedStatus || null,
    };
    dispatch(setFilters(newFilters));
    dispatch(fetchReports(newFilters));
  };

  const handleStatusFilter = (status) => {
    const newFilters = {
      ...filters,
      status: status === selectedStatus ? null : status,
    };
    setSelectedStatus(status === selectedStatus ? '' : status);
    dispatch(setFilters(newFilters));
    dispatch(fetchReports(newFilters));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'danger';
      default: return 'default';
    }
  };

  const getHazardTypeColor = (type) => {
    switch (type) {
      case 'flood': return 'danger';
      case 'storm': return 'warning';
      case 'erosion': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600">Monitor and manage coastal hazard reports</p>
        </div>
        <Button>
          <MapPin className="h-4 w-4 mr-2" />
          View Map
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-64">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search reports..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="min-w-32">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="verified">Verified</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            <Button onClick={handleSearch}>
              Apply Filters
            </Button>
          </div>

          {/* Status Filter Buttons */}
          <div className="mt-4 flex flex-wrap gap-2">
            {['pending', 'verified', 'rejected'].map((status) => (
              <button
                key={status}
                onClick={() => handleStatusFilter(status)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  selectedStatus === status
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Reports List */}
      <Card>
        <CardHeader>
          <CardTitle>Reports ({pagination.total || reports.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading reports...</p>
            </div>
          ) : reports.length > 0 ? (
            <div className="space-y-4">
              {reports.map((report) => (
                <div key={report.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge variant={getHazardTypeColor(report.hazard_type)}>
                          {report.hazard_type}
                        </Badge>
                        <Badge variant={getStatusColor(report.status)}>
                          {report.status}
                        </Badge>
                        <Badge variant="outline">
                          Severity: {report.severity_level}/10
                        </Badge>
                      </div>
                      
                      {report.description && (
                        <p className="text-gray-700 mb-2">{report.description}</p>
                      )}
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {report.latitude.toFixed(4)}, {report.longitude.toFixed(4)}
                        </div>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {new Date(report.created_at).toLocaleDateString()}
                        </div>
                        <div className="flex items-center">
                          <AlertTriangle className="h-4 w-4 mr-1" />
                          Confidence: {Math.round(report.confidence_score * 100)}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
              <p className="text-gray-600">Try adjusting your filters or check back later.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ReportsPage;
