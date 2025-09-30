import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { reportsAPI } from '../services/apiService';

export default function ViewReportsScreen() {
  const [reports, setReports] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setIsLoading(true);
      const data = await reportsAPI.getPublicReports({ limit: 50 });
      setReports(data);
    } catch (error) {
      console.error('Error loading reports:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadReports();
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'VERIFIED': return '#10b981';
      case 'PENDING': return '#f59e0b';
      case 'REJECTED': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const renderReport = ({ item: report }) => (
    <View style={styles.reportCard}>
      <View style={styles.reportHeader}>
        <Text style={styles.hazardIcon}>
          {getHazardIcon(report.hazard_type)}
        </Text>
        <View style={styles.reportInfo}>
          <Text style={styles.hazardType}>
            {report.hazard_type.replace('_', ' ')}
          </Text>
          <Text style={styles.reportDate}>
            {new Date(report.created_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        </View>
        <View style={styles.badges}>
          <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(report.severity_level) }]}>
            <Text style={styles.severityText}>Level {report.severity_level}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(report.status) }]}>
            <Text style={styles.statusText}>{report.status}</Text>
          </View>
        </View>
      </View>

      {report.description && (
        <Text style={styles.reportDescription}>
          {report.description}
        </Text>
      )}

      <View style={styles.reportFooter}>
        <View style={styles.locationInfo}>
          <Ionicons name="location" size={16} color="#6b7280" />
          <Text style={styles.locationText}>
            {report.latitude?.toFixed(4)}, {report.longitude?.toFixed(4)}
          </Text>
        </View>
        
        {report.media_url && (
          <View style={styles.mediaInfo}>
            <Ionicons name="image" size={16} color="#6b7280" />
            <Text style={styles.mediaText}>Has media</Text>
          </View>
        )}
      </View>

      {report.user && (
        <View style={styles.userInfo}>
          <Ionicons name="person" size={16} color="#6b7280" />
          <Text style={styles.userText}>
            Reported by {report.user.full_name || 'Anonymous'}
          </Text>
        </View>
      )}
    </View>
  );

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="document-text-outline" size={64} color="#d1d5db" />
      <Text style={styles.emptyTitle}>No Reports Available</Text>
      <Text style={styles.emptySubtitle}>
        Check back later for new hazard reports
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Hazard Reports</Text>
        <Text style={styles.subtitle}>Community-reported ocean hazards</Text>
      </View>

      <FlatList
        data={reports}
        renderItem={renderReport}
        keyExtractor={(item, index) => `${item.id || index}`}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={!isLoading ? renderEmpty : null}
        showsVerticalScrollIndicator={false}
      />

      {isLoading && (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading reports...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#3b82f6',
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#dbeafe',
  },
  listContainer: {
    padding: 16,
    flexGrow: 1,
  },
  reportCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  reportHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  hazardIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  reportInfo: {
    flex: 1,
  },
  hazardType: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    textTransform: 'capitalize',
    marginBottom: 4,
  },
  reportDate: {
    fontSize: 14,
    color: '#6b7280',
  },
  badges: {
    alignItems: 'flex-end',
    gap: 4,
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
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  reportDescription: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
    marginBottom: 12,
  },
  reportFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  locationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  locationText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 4,
  },
  mediaInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  mediaText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 4,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  userText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 4,
    fontStyle: 'italic',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#6b7280',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#9ca3af',
    textAlign: 'center',
    lineHeight: 24,
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(248, 250, 252, 0.8)',
  },
  loadingText: {
    fontSize: 16,
    color: '#6b7280',
  },
});
