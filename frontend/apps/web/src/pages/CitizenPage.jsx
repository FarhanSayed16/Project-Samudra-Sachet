import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { Badge } from '../components/ui/Badge';
import { Separator } from '../components/ui/Separator';
import { apiService } from '../api/apiService';

const CitizenPage = () => {
  const [activeTab, setActiveTab] = useState('reports');
  const [reports, setReports] = useState([]);
  const [socialPosts, setSocialPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newReport, setNewReport] = useState({
    hazard_type: '',
    latitude: '',
    longitude: '',
    description: '',
    severity_level: 3
  });

  // Ocean hazard types
  const hazardTypes = [
    { value: 'tsunami', label: 'Tsunami' },
    { value: 'high_waves', label: 'High Waves' },
    { value: 'swell_surge', label: 'Swell Surge' },
    { value: 'coastal_flooding', label: 'Coastal Flooding' },
    { value: 'storm_surge', label: 'Storm Surge' },
    { value: 'unusual_tide', label: 'Unusual Tide' },
    { value: 'coastal_damage', label: 'Coastal Damage' },
    { value: 'coastal_current', label: 'Coastal Current' },
    { value: 'other', label: 'Other' }
  ];

  // Social media platforms
  const platforms = [
    { value: 'twitter', label: 'Twitter', color: 'bg-blue-500' },
    { value: 'facebook', label: 'Facebook', color: 'bg-blue-600' },
    { value: 'instagram', label: 'Instagram', color: 'bg-pink-500' },
    { value: 'youtube', label: 'YouTube', color: 'bg-red-500' },
    { value: 'telegram', label: 'Telegram', color: 'bg-blue-400' }
  ];

  // Sentiment colors
  const sentimentColors = {
    panic: 'bg-red-500',
    concern: 'bg-orange-500',
    neutral: 'bg-gray-500',
    awareness: 'bg-blue-500',
    relief: 'bg-green-500'
  };

  useEffect(() => {
    if (activeTab === 'reports') {
      fetchReports();
    } else if (activeTab === 'social') {
      fetchSocialPosts();
    }
  }, [activeTab]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/reports/public?limit=20');
      setReports(response.data || []);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSocialPosts = async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/social-media/public?limit=20');
      setSocialPosts(response.data || []);
    } catch (error) {
      console.error('Error fetching social posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReport = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      console.log('📤 Submitting report...');
      const formData = new FormData();
      formData.append('hazard_type', newReport.hazard_type);
      formData.append('latitude', newReport.latitude);
      formData.append('longitude', newReport.longitude);
      formData.append('description', newReport.description);
      formData.append('severity_level', newReport.severity_level);

      const response = await apiService.post('/reports/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('✅ Report submitted:', response.data);

      // Reset form
      setNewReport({
        hazard_type: '',
        latitude: '',
        longitude: '',
        description: '',
        severity_level: 3
      });

      // Refresh reports
      fetchReports();
      
      alert('Report submitted successfully!');
    } catch (error) {
      console.error('❌ Error submitting report:', error);
      console.error('Error details:', error.response?.data);
      alert(`Error submitting report: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSeverityColor = (level) => {
    switch (level) {
      case 1: return 'bg-green-500';
      case 2: return 'bg-yellow-500';
      case 3: return 'bg-orange-500';
      case 4: return 'bg-red-500';
      case 5: return 'bg-red-700';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Ocean Hazard Reporting
          </h1>
          <p className="text-gray-600">
            Report ocean hazards and view social media updates about coastal conditions
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('reports')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'reports'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                View Reports
              </button>
              <button
                onClick={() => setActiveTab('submit')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'submit'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Submit Report
              </button>
              <button
                onClick={() => setActiveTab('social')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'social'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Social Media Updates
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-gray-900">Recent Ocean Hazard Reports</h2>
              <Button onClick={fetchReports} disabled={loading}>
                {loading ? 'Loading...' : 'Refresh'}
              </Button>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading reports...</p>
              </div>
            ) : reports.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-gray-600">No reports available at the moment.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {reports.map((report) => (
                  <Card key={report.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-lg">
                          {hazardTypes.find(h => h.value === report.hazard_type)?.label || report.hazard_type}
                        </CardTitle>
                        <Badge className={`${getSeverityColor(report.severity_level)} text-white`}>
                          Level {report.severity_level}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600 mb-4">{report.description}</p>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Location:</span>
                          <span>{report.latitude?.toFixed(4)}, {report.longitude?.toFixed(4)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Status:</span>
                          <Badge variant="outline">{report.status}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Reported:</span>
                          <span>{formatDate(report.created_at)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Upvotes:</span>
                          <span>{report.upvote_count || 0}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'submit' && (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Submit Ocean Hazard Report</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitReport} className="space-y-6">
                <div>
                  <Label htmlFor="hazard_type">Hazard Type *</Label>
                  <select
                    id="hazard_type"
                    value={newReport.hazard_type}
                    onChange={(e) => setNewReport({ ...newReport, hazard_type: e.target.value })}
                    className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select hazard type</option>
                    {hazardTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="latitude">Latitude *</Label>
                    <Input
                      id="latitude"
                      type="number"
                      step="any"
                      min="-90"
                      max="90"
                      value={newReport.latitude}
                      onChange={(e) => setNewReport({ ...newReport, latitude: e.target.value })}
                      placeholder="e.g., 19.0760"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="longitude">Longitude *</Label>
                    <Input
                      id="longitude"
                      type="number"
                      step="any"
                      min="-180"
                      max="180"
                      value={newReport.longitude}
                      onChange={(e) => setNewReport({ ...newReport, longitude: e.target.value })}
                      placeholder="e.g., 72.8777"
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="severity_level">Severity Level</Label>
                  <select
                    id="severity_level"
                    value={newReport.severity_level}
                    onChange={(e) => setNewReport({ ...newReport, severity_level: parseInt(e.target.value) })}
                    className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={1}>1 - Low</option>
                    <option value={2}>2 - Low-Medium</option>
                    <option value={3}>3 - Medium</option>
                    <option value={4}>4 - High</option>
                    <option value={5}>5 - Critical</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <textarea
                    id="description"
                    value={newReport.description}
                    onChange={(e) => setNewReport({ ...newReport, description: e.target.value })}
                    className="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                    placeholder="Describe the ocean hazard you observed..."
                  />
                </div>

                <Button type="submit" disabled={loading} className="w-full">
                  {loading ? 'Submitting...' : 'Submit Report'}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {activeTab === 'social' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-gray-900">Social Media Ocean Updates</h2>
              <Button onClick={fetchSocialPosts} disabled={loading}>
                {loading ? 'Loading...' : 'Refresh'}
              </Button>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading social media posts...</p>
              </div>
            ) : socialPosts.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-gray-600">No social media posts available at the moment.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {socialPosts.map((post) => (
                  <Card key={post.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start space-x-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium ${platforms.find(p => p.value === post.source)?.color || 'bg-gray-500'}`}>
                          {post.source?.charAt(0).toUpperCase()}
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="font-medium text-gray-900">@{post.author_username}</span>
                            <Badge className={`${platforms.find(p => p.value === post.source)?.color || 'bg-gray-500'} text-white`}>
                              {platforms.find(p => p.value === post.source)?.label || post.source}
                            </Badge>
                            {post.sentiment && (
                              <Badge className={`${sentimentColors[post.sentiment] || 'bg-gray-500'} text-white`}>
                                {post.sentiment}
                              </Badge>
                            )}
                          </div>
                          
                          <p className="text-gray-800 mb-3">{post.post_text}</p>
                          
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>{formatDate(post.post_timestamp || post.created_at)}</span>
                            {post.location && (
                              <span>📍 {post.location.latitude?.toFixed(4)}, {post.location.longitude?.toFixed(4)}</span>
                            )}
                            {post.hazard_type && (
                              <Badge variant="outline">
                                {hazardTypes.find(h => h.value === post.hazard_type)?.label || post.hazard_type}
                              </Badge>
                            )}
                            <span>👍 {post.engagement_count || 0}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CitizenPage;
