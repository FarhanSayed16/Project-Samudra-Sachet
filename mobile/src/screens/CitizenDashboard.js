import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { reportsAPI, socialMediaAPI } from '../services/apiService';

export default function CitizenDashboard() {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [socialPosts, setSocialPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [reportsData, socialData] = await Promise.all([
        reportsAPI.getPublicReports({ limit: 5 }),
        socialMediaAPI.getPublicPosts({ limit: 5 }),
      ]);
      
      setReports(reportsData);
      setSocialPosts(socialData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const getHazardIcon = (hazardType) => {
    switch (hazardType) {
      case 'HIGH_WAVES': return '🌊';
      case 'STORM_SURGE': return '⛈️';
      case 'TSUNAMI': return '🌊';
      case 'FLOODING': return '🌧️';
      case 'EROSION': return '🏖️';
      default: return '⚠️';
    }
  };

  const getSeverityColor = (severity) => {
    if (severity >= 4) return '#ef4444';
    if (severity >= 3) return '#f59e0b';
    return '#10b981';
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.greeting}>Welcome back, {user?.full_name}!</Text>
        <Text style={styles.subtitle}>Stay informed about ocean hazards</Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{reports.length}</Text>
          <Text style={styles.statLabel}>Recent Reports</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{socialPosts.length}</Text>
          <Text style={styles.statLabel}>Social Updates</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Hazard Reports</Text>
        {isLoading ? (
          <Text style={styles.loadingText}>Loading reports...</Text>
        ) : reports.length > 0 ? (
          reports.map((report, index) => (
            <View key={index} style={styles.reportCard}>
              <View style={styles.reportHeader}>
                <Text style={styles.hazardIcon}>
                  {getHazardIcon(report.hazard_type)}
                </Text>
                <View style={styles.reportInfo}>
                  <Text style={styles.hazardType}>{report.hazard_type.replace('_', ' ')}</Text>
                  <Text style={styles.reportDate}>
                    {new Date(report.created_at).toLocaleDateString()}
                  </Text>
                </View>
                <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(report.severity_level) }]}>
                  <Text style={styles.severityText}>Level {report.severity_level}</Text>
                </View>
              </View>
              {report.description && (
                <Text style={styles.reportDescription} numberOfLines={2}>
                  {report.description}
                </Text>
              )}
              <View style={styles.reportFooter}>
                <Text style={styles.reportStatus}>
                  Status: {report.status}
                </Text>
                <Text style={styles.reportLocation}>
                  📍 {report.latitude?.toFixed(4)}, {report.longitude?.toFixed(4)}
                </Text>
              </View>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>No recent reports available</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Social Media Updates</Text>
        {isLoading ? (
          <Text style={styles.loadingText}>Loading updates...</Text>
        ) : socialPosts.length > 0 ? (
          socialPosts.map((post, index) => (
            <View key={index} style={styles.socialCard}>
              <View style={styles.socialHeader}>
                <Text style={styles.socialIcon}>
                  {post.source === 'TWITTER' ? '🐦' : 
                   post.source === 'FACEBOOK' ? '📘' : 
                   post.source === 'INSTAGRAM' ? '📷' : '📱'}
                </Text>
                <View style={styles.socialInfo}>
                  <Text style={styles.socialAuthor}>{post.author_username}</Text>
                  <Text style={styles.socialDate}>
                    {new Date(post.post_timestamp).toLocaleDateString()}
                  </Text>
                </View>
                <View style={styles.relevanceBadge}>
                  <Text style={styles.relevanceText}>
                    {Math.round(post.relevance_score * 100)}% relevant
                  </Text>
                </View>
              </View>
              <Text style={styles.socialText} numberOfLines={3}>
                {post.post_text}
              </Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>No social updates available</Text>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 20,
    backgroundColor: '#3b82f6',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#dbeafe',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  statLabel: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 4,
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 16,
  },
  loadingText: {
    textAlign: 'center',
    color: '#64748b',
    fontStyle: 'italic',
  },
  emptyText: {
    textAlign: 'center',
    color: '#64748b',
    fontStyle: 'italic',
    padding: 20,
  },
  reportCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  reportHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  hazardIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  reportInfo: {
    flex: 1,
  },
  hazardType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    textTransform: 'capitalize',
  },
  reportDate: {
    fontSize: 12,
    color: '#64748b',
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  severityText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  reportDescription: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 8,
    lineHeight: 20,
  },
  reportFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  reportStatus: {
    fontSize: 12,
    color: '#64748b',
    textTransform: 'capitalize',
  },
  reportLocation: {
    fontSize: 12,
    color: '#64748b',
  },
  socialCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  socialHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  socialIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  socialInfo: {
    flex: 1,
  },
  socialAuthor: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
  },
  socialDate: {
    fontSize: 12,
    color: '#64748b',
  },
  relevanceBadge: {
    backgroundColor: '#dbeafe',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  relevanceText: {
    color: '#3b82f6',
    fontSize: 12,
    fontWeight: '600',
  },
  socialText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
});
