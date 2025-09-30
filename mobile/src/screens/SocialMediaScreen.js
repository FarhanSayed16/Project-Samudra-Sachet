import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { socialMediaAPI } from '../services/apiService';

export default function SocialMediaScreen() {
  const [posts, setPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      setIsLoading(true);
      const data = await socialMediaAPI.getPublicPosts({ limit: 50 });
      setPosts(data);
    } catch (error) {
      console.error('Error loading social media posts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadPosts();
    setRefreshing(false);
  };

  const getPlatformIcon = (source) => {
    switch (source) {
      case 'TWITTER': return '🐦';
      case 'FACEBOOK': return '📘';
      case 'INSTAGRAM': return '📷';
      case 'YOUTUBE': return '📺';
      case 'TIKTOK': return '🎵';
      default: return '📱';
    }
  };

  const getPlatformColor = (source) => {
    switch (source) {
      case 'TWITTER': return '#1da1f2';
      case 'FACEBOOK': return '#1877f2';
      case 'INSTAGRAM': return '#e4405f';
      case 'YOUTUBE': return '#ff0000';
      case 'TIKTOK': return '#000000';
      default: return '#6b7280';
    }
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

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'POSITIVE': return '#10b981';
      case 'NEGATIVE': return '#ef4444';
      case 'CONCERN': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const openPost = async (postUrl) => {
    try {
      await Linking.openURL(postUrl);
    } catch (error) {
      console.error('Error opening URL:', error);
    }
  };

  const renderPost = ({ item: post }) => (
    <TouchableOpacity 
      style={styles.postCard}
      onPress={() => post.post_url && openPost(post.post_url)}
    >
      <View style={styles.postHeader}>
        <View style={styles.platformInfo}>
          <Text style={styles.platformIcon}>
            {getPlatformIcon(post.source)}
          </Text>
          <View style={styles.authorInfo}>
            <Text style={styles.authorName}>{post.author_username}</Text>
            <Text style={styles.postDate}>
              {new Date(post.post_timestamp).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>
          </View>
        </View>
        
        <View style={styles.badges}>
          <View style={[styles.relevanceBadge, { backgroundColor: getPlatformColor(post.source) }]}>
            <Text style={styles.relevanceText}>
              {Math.round(post.relevance_score * 100)}%
            </Text>
          </View>
        </View>
      </View>

      <Text style={styles.postText}>{post.post_text}</Text>

      {post.hazard_type && (
        <View style={styles.hazardInfo}>
          <Text style={styles.hazardIcon}>
            {getHazardIcon(post.hazard_type)}
          </Text>
          <Text style={styles.hazardType}>
            {post.hazard_type.replace('_', ' ')}
          </Text>
        </View>
      )}

      <View style={styles.postFooter}>
        <View style={styles.metrics}>
          <View style={styles.metric}>
            <Ionicons name="trending-up" size={16} color="#6b7280" />
            <Text style={styles.metricText}>
              {post.relevance_score?.toFixed(2)} relevance
            </Text>
          </View>
          
          {post.sentiment && (
            <View style={styles.metric}>
              <View style={[styles.sentimentDot, { backgroundColor: getSentimentColor(post.sentiment) }]} />
              <Text style={styles.metricText}>
                {post.sentiment.toLowerCase()}
              </Text>
            </View>
          )}
        </View>

        {post.location && (
          <View style={styles.locationInfo}>
            <Ionicons name="location" size={16} color="#6b7280" />
            <Text style={styles.locationText}>
              {post.latitude?.toFixed(2)}, {post.longitude?.toFixed(2)}
            </Text>
          </View>
        )}
      </View>

      {post.post_url && (
        <View style={styles.linkInfo}>
          <Ionicons name="link" size={16} color="#3b82f6" />
          <Text style={styles.linkText}>Tap to view original post</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="people-outline" size={64} color="#d1d5db" />
      <Text style={styles.emptyTitle}>No Social Media Updates</Text>
      <Text style={styles.emptySubtitle}>
        Check back later for new social media posts about ocean hazards
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Social Media Updates</Text>
        <Text style={styles.subtitle}>Latest posts about ocean hazards</Text>
      </View>

      <FlatList
        data={posts}
        renderItem={renderPost}
        keyExtractor={(item, index) => `${item.source_id || index}`}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={!isLoading ? renderEmpty : null}
        showsVerticalScrollIndicator={false}
      />

      {isLoading && (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading posts...</Text>
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
  postCard: {
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
  postHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  platformInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  platformIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  authorInfo: {
    flex: 1,
  },
  authorName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 2,
  },
  postDate: {
    fontSize: 14,
    color: '#6b7280',
  },
  badges: {
    alignItems: 'flex-end',
  },
  relevanceBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  relevanceText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  postText: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
    marginBottom: 12,
  },
  hazardInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3f4f6',
    padding: 8,
    borderRadius: 8,
    marginBottom: 12,
  },
  hazardIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  hazardType: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    textTransform: 'capitalize',
  },
  postFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  metrics: {
    flexDirection: 'row',
    gap: 16,
  },
  metric: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metricText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 4,
  },
  sentimentDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 4,
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
  linkInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  linkText: {
    fontSize: 14,
    color: '#3b82f6',
    marginLeft: 4,
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
