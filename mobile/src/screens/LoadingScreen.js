import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';

export default function LoadingScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.logo}>🌊</Text>
        <Text style={styles.title}>Samudra Sachet</Text>
        <Text style={styles.subtitle}>Ocean Hazard Reporting</Text>
        <ActivityIndicator size="large" color="#3b82f6" style={styles.loader} />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
  },
  logo: {
    fontSize: 64,
    marginBottom: 16,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: 32,
  },
  loader: {
    marginBottom: 16,
  },
  loadingText: {
    fontSize: 16,
    color: '#6b7280',
  },
});

