import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchReports } from '../state/slices/reportsSlice';
import { fetchHotspots } from '../state/slices/hotspotsSlice';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { MapPin, FileText, AlertTriangle, Users } from 'lucide-react';

const DashboardPage = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { reports, isLoading: reportsLoading } = useSelector((state) => state.reports);
  const { hotspots, isLoading: hotspotsLoading } = useSelector((state) => state.hotspots);

  useEffect(() => {
    dispatch(fetchReports({ limit: 5 }));
    dispatch(fetchHotspots({ limit: 5 }));
  }, [dispatch]);

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
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-primary-100">
          Monitor coastal hazards and manage reports from your dashboard.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{reports.length}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Hotspots</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{hotspots.length}</div>
            <p className="text-xs text-muted-foreground">
              +8% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Verification</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {reports.filter(r => r.status === 'pending').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Requires attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Verified Reports</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {reports.filter(r => r.status === 'verified').length}
            </div>
            <p className="text-xs text-muted-foreground">
              +15% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Reports */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {reportsLoading ? (
                <div className="text-center py-4">Loading reports...</div>
              ) : reports.length > 0 ? (
                reports.slice(0, 5).map((report) => (
                  <div key={report.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <Badge variant={getHazardTypeColor(report.hazard_type)}>
                          {report.hazard_type}
                        </Badge>
                        <Badge variant={getStatusColor(report.status)}>
                          {report.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">
                        Severity: {report.severity_level}/10
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(report.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-500">
                  No reports available
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Recent Hotspots */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Hotspots</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {hotspotsLoading ? (
                <div className="text-center py-4">Loading hotspots...</div>
              ) : hotspots.length > 0 ? (
                hotspots.slice(0, 5).map((hotspot) => (
                  <div key={hotspot.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <Badge variant="warning">
                          {hotspot.event_type}
                        </Badge>
                        <Badge variant={hotspot.status === 'active' ? 'success' : 'default'}>
                          {hotspot.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">
                        Intensity: {hotspot.intensity}/10
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(hotspot.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-500">
                  No hotspots available
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
