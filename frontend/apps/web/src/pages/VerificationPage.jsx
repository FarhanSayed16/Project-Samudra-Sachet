import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchReports } from '../state/slices/reportsSlice';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { CheckCircle, XCircle, Clock, AlertTriangle, MapPin, Calendar } from 'lucide-react';

const VerificationPage = () => {
  const dispatch = useDispatch();
  const { reports, isLoading } = useSelector((state) => state.reports);
  const [selectedReport, setSelectedReport] = useState(null);
  const [verificationData, setVerificationData] = useState({
    status: 'pending',
    notes: '',
    confidence_score: 0.5
  });

  useEffect(() => {
    // Fetch only pending reports for verification
    dispatch(fetchReports({ status: 'pending' }));
  }, [dispatch]);

  const handleVerification = async (reportId, status) => {
    try {
      // This would call the verification API
      console.log('Verifying report:', reportId, 'with status:', status);
      // await dispatch(verifyReport({ reportId, verificationData })).unwrap();
      
      // For now, just update the local state
      const updatedReports = reports.map(report => 
        report.id === reportId 
          ? { ...report, status }
          : report
      );
      
      setSelectedReport(null);
      setVerificationData({
        status: 'pending',
        notes: '',
        confidence_score: 0.5
      });
    } catch (error) {
      console.error('Verification failed:', error);
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

  const getSeverityColor = (severity) => {
    if (severity >= 8) return 'danger';
    if (severity >= 6) return 'warning';
    if (severity >= 4) return 'secondary';
    return 'default';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Report Verification</h1>
          <p className="text-gray-600">Review and verify coastal hazard reports</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="warning">
            <Clock className="h-3 w-3 mr-1" />
            {reports.filter(r => r.status === 'pending').length} Pending
          </Badge>
        </div>
      </div>

      {/* Verification Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Verification</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {reports.filter(r => r.status === 'pending').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Awaiting review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Verified Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {reports.filter(r => r.status === 'verified').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Successfully verified
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected Today</CardTitle>
            <XCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {reports.filter(r => r.status === 'rejected').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Rejected reports
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Reports List */}
      <Card>
        <CardHeader>
          <CardTitle>Reports Awaiting Verification</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading reports...</p>
            </div>
          ) : reports.filter(r => r.status === 'pending').length > 0 ? (
            <div className="space-y-4">
              {reports.filter(r => r.status === 'pending').map((report) => (
                <div key={report.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge variant={getHazardTypeColor(report.hazard_type)}>
                          {report.hazard_type}
                        </Badge>
                        <Badge variant={getSeverityColor(report.severity_level)}>
                          Severity: {report.severity_level}/10
                        </Badge>
                        <Badge variant="warning">
                          Confidence: {Math.round(report.confidence_score * 100)}%
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
                          Votes: {report.upvote_count} ↑ {report.downvote_count} ↓
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4 flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setSelectedReport(report)}
                      >
                        Review
                      </Button>
                      <Button 
                        variant="success" 
                        size="sm"
                        onClick={() => handleVerification(report.id, 'verified')}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Verify
                      </Button>
                      <Button 
                        variant="danger" 
                        size="sm"
                        onClick={() => handleVerification(report.id, 'rejected')}
                      >
                        <XCircle className="h-4 w-4 mr-1" />
                        Reject
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">All caught up!</h3>
              <p className="text-gray-600">No reports are currently pending verification.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Verification Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4">
            <CardHeader>
              <CardTitle>Verify Report</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Report Details</h3>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge variant={getHazardTypeColor(selectedReport.hazard_type)}>
                        {selectedReport.hazard_type}
                      </Badge>
                      <Badge variant={getSeverityColor(selectedReport.severity_level)}>
                        Severity: {selectedReport.severity_level}/10
                      </Badge>
                    </div>
                    {selectedReport.description && (
                      <p className="text-gray-700 mb-2">{selectedReport.description}</p>
                    )}
                    <p className="text-sm text-gray-500">
                      Location: {selectedReport.latitude.toFixed(4)}, {selectedReport.longitude.toFixed(4)}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Verification Notes
                  </label>
                  <textarea
                    value={verificationData.notes}
                    onChange={(e) => setVerificationData({...verificationData, notes: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={3}
                    placeholder="Add verification notes..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Confidence Score: {Math.round(verificationData.confidence_score * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={verificationData.confidence_score}
                    onChange={(e) => setVerificationData({...verificationData, confidence_score: parseFloat(e.target.value)})}
                    className="w-full"
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <Button 
                    variant="outline"
                    onClick={() => setSelectedReport(null)}
                  >
                    Cancel
                  </Button>
                  <Button 
                    variant="danger"
                    onClick={() => handleVerification(selectedReport.id, 'rejected')}
                  >
                    <XCircle className="h-4 w-4 mr-1" />
                    Reject
                  </Button>
                  <Button 
                    variant="success"
                    onClick={() => handleVerification(selectedReport.id, 'verified')}
                  >
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Verify
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default VerificationPage;
