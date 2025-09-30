import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';

export default function ProfileScreen() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: logout },
      ]
    );
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'citizen': return '👤';
      case 'coastal_volunteer': return '🤝';
      case 'coastal_guard': return '🛡️';
      case 'disaster_manager': return '🚨';
      case 'admin': return '⚙️';
      default: return '👤';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'citizen': return '#3b82f6';
      case 'coastal_volunteer': return '#10b981';
      case 'coastal_guard': return '#f59e0b';
      case 'disaster_manager': return '#ef4444';
      case 'admin': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const formatRole = (role) => {
    return role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarIcon}>
            {getRoleIcon(user?.user_role)}
          </Text>
        </View>
        <Text style={styles.userName}>{user?.full_name}</Text>
        <View style={[styles.roleBadge, { backgroundColor: getRoleColor(user?.user_role) }]}>
          <Text style={styles.roleText}>
            {formatRole(user?.user_role)}
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account Information</Text>
        
        <View style={styles.infoCard}>
          <View style={styles.infoRow}>
            <Ionicons name="mail" size={20} color="#6b7280" />
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>Email</Text>
              <Text style={styles.infoValue}>{user?.email}</Text>
            </View>
          </View>
          
          <View style={styles.infoRow}>
            <Ionicons name="person" size={20} color="#6b7280" />
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>Full Name</Text>
              <Text style={styles.infoValue}>{user?.full_name}</Text>
            </View>
          </View>
          
          <View style={styles.infoRow}>
            <Ionicons name="shield-checkmark" size={20} color="#6b7280" />
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>Account Status</Text>
              <Text style={[styles.infoValue, { color: user?.is_active ? '#10b981' : '#ef4444' }]}>
                {user?.is_active ? 'Active' : 'Inactive'}
              </Text>
            </View>
          </View>
          
          <View style={styles.infoRow}>
            <Ionicons name="checkmark-circle" size={20} color="#6b7280" />
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>Verification Status</Text>
              <Text style={[styles.infoValue, { color: user?.is_verified ? '#10b981' : '#f59e0b' }]}>
                {user?.is_verified ? 'Verified' : 'Pending'}
              </Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>App Information</Text>
        
        <View style={styles.infoCard}>
          <View style={styles.infoRow}>
            <Ionicons name="information-circle" size={20} color="#6b7280" />
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>App Version</Text>
              <Text style={styles.infoValue}>1.0.0</Text>
            </View>
          </View>
          
          <View style={styles.infoRow}>
            <Ionicons name="globe" size={20} color="#6b7280" />
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>Language</Text>
              <Text style={styles.infoValue}>English</Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actions</Text>
        
        <TouchableOpacity style={styles.actionButton} onPress={handleLogout}>
          <Ionicons name="log-out" size={20} color="#ef4444" />
          <Text style={styles.actionButtonText}>Logout</Text>
          <Ionicons name="chevron-forward" size={20} color="#6b7280" />
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>🌊 Samudra Sachet</Text>
        <Text style={styles.footerSubtext}>Ocean Hazard Reporting System</Text>
        <Text style={styles.footerCopyright}>© 2024 All rights reserved</Text>
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
    backgroundColor: '#3b82f6',
    padding: 40,
    paddingTop: 60,
    alignItems: 'center',
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatarIcon: {
    fontSize: 40,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  roleBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  roleText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
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
  infoCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  infoContent: {
    flex: 1,
    marginLeft: 12,
  },
  infoLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1e293b',
  },
  actionButton: {
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionButtonText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
    color: '#ef4444',
    marginLeft: 12,
  },
  footer: {
    alignItems: 'center',
    padding: 40,
    paddingBottom: 60,
  },
  footerText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  footerCopyright: {
    fontSize: 12,
    color: '#9ca3af',
  },
});
