import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import * as Location from 'expo-location';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { reportsAPI } from '../services/apiService';

const HAZARD_TYPES = [
  { value: 'HIGH_WAVES', label: 'High Waves', icon: '🌊' },
  { value: 'STORM_SURGE', label: 'Storm Surge', icon: '⛈️' },
  { value: 'TSUNAMI', label: 'Tsunami', icon: '🌊' },
  { value: 'FLOODING', label: 'Flooding', icon: '🌧️' },
  { value: 'EROSION', label: 'Erosion', icon: '🏖️' },
];

const SEVERITY_LEVELS = [
  { value: 1, label: 'Low', color: '#10b981' },
  { value: 2, label: 'Moderate', color: '#f59e0b' },
  { value: 3, label: 'High', color: '#f59e0b' },
  { value: 4, label: 'Severe', color: '#ef4444' },
  { value: 5, label: 'Critical', color: '#dc2626' },
];

export default function SubmitReportScreen() {
  const { user } = useAuth();
  const [selectedHazard, setSelectedHazard] = useState('');
  const [severity, setSeverity] = useState(3);
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const getCurrentLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Location permission is required to submit reports');
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setLatitude(location.coords.latitude.toString());
      setLongitude(location.coords.longitude.toString());
    } catch (error) {
      Alert.alert('Error', 'Failed to get current location');
    }
  };

  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Camera roll permission is required');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled) {
        setSelectedImage(result.assets[0]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const takePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Camera permission is required');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled) {
        setSelectedImage(result.assets[0]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take photo');
    }
  };

  const submitReport = async () => {
    if (!selectedHazard) {
      Alert.alert('Error', 'Please select a hazard type');
      return;
    }

    if (!latitude || !longitude) {
      Alert.alert('Error', 'Please provide location coordinates');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('hazard_type', selectedHazard);
      formData.append('latitude', parseFloat(latitude));
      formData.append('longitude', parseFloat(longitude));
      formData.append('description', description);
      formData.append('severity_level', severity);

      if (selectedImage) {
        formData.append('media_file', {
          uri: selectedImage.uri,
          type: 'image/jpeg',
          name: 'report_image.jpg',
        });
      }

      await reportsAPI.submitReport(formData);
      
      Alert.alert('Success', 'Report submitted successfully!', [
        { text: 'OK', onPress: () => {
          // Reset form
          setSelectedHazard('');
          setSeverity(3);
          setDescription('');
          setLatitude('');
          setLongitude('');
          setSelectedImage(null);
        }}
      ]);
    } catch (error) {
      console.error('Error submitting report:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to submit report');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Submit Hazard Report</Text>
          <Text style={styles.subtitle}>Help keep the community safe</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Hazard Type *</Text>
          <View style={styles.hazardGrid}>
            {HAZARD_TYPES.map((hazard) => (
              <TouchableOpacity
                key={hazard.value}
                style={[
                  styles.hazardButton,
                  selectedHazard === hazard.value && styles.hazardButtonSelected
                ]}
                onPress={() => setSelectedHazard(hazard.value)}
              >
                <Text style={styles.hazardIcon}>{hazard.icon}</Text>
                <Text style={[
                  styles.hazardLabel,
                  selectedHazard === hazard.value && styles.hazardLabelSelected
                ]}>
                  {hazard.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Severity Level</Text>
          <View style={styles.severityContainer}>
            {SEVERITY_LEVELS.map((level) => (
              <TouchableOpacity
                key={level.value}
                style={[
                  styles.severityButton,
                  { borderColor: level.color },
                  severity === level.value && { backgroundColor: level.color }
                ]}
                onPress={() => setSeverity(level.value)}
              >
                <Text style={[
                  styles.severityText,
                  severity === level.value && styles.severityTextSelected
                ]}>
                  {level.value}
                </Text>
                <Text style={[
                  styles.severityLabel,
                  severity === level.value && styles.severityLabelSelected
                ]}>
                  {level.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Location</Text>
          <View style={styles.locationRow}>
            <View style={styles.locationInput}>
              <Text style={styles.inputLabel}>Latitude</Text>
              <TextInput
                style={styles.input}
                value={latitude}
                onChangeText={setLatitude}
                placeholder="e.g., 19.0760"
                keyboardType="numeric"
              />
            </View>
            <View style={styles.locationInput}>
              <Text style={styles.inputLabel}>Longitude</Text>
              <TextInput
                style={styles.input}
                value={longitude}
                onChangeText={setLongitude}
                placeholder="e.g., 72.8777"
                keyboardType="numeric"
              />
            </View>
          </View>
          <TouchableOpacity style={styles.locationButton} onPress={getCurrentLocation}>
            <Ionicons name="location" size={20} color="#3b82f6" />
            <Text style={styles.locationButtonText}>Use Current Location</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Description</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={description}
            onChangeText={setDescription}
            placeholder="Describe the hazard in detail..."
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Photo (Optional)</Text>
          {selectedImage ? (
            <View style={styles.imagePreview}>
              <Text style={styles.imagePreviewText}>Image selected</Text>
              <TouchableOpacity
                style={styles.removeImageButton}
                onPress={() => setSelectedImage(null)}
              >
                <Ionicons name="close-circle" size={24} color="#ef4444" />
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.imageButtons}>
              <TouchableOpacity style={styles.imageButton} onPress={pickImage}>
                <Ionicons name="image" size={24} color="#3b82f6" />
                <Text style={styles.imageButtonText}>Gallery</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.imageButton} onPress={takePhoto}>
                <Ionicons name="camera" size={24} color="#3b82f6" />
                <Text style={styles.imageButtonText}>Camera</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        <TouchableOpacity
          style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
          onPress={submitReport}
          disabled={isLoading}
        >
          <Text style={styles.submitButtonText}>
            {isLoading ? 'Submitting...' : 'Submit Report'}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
  },
  hazardGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  hazardButton: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: '45%',
    borderWidth: 2,
    borderColor: '#e5e7eb',
  },
  hazardButtonSelected: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  },
  hazardIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  hazardLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    textAlign: 'center',
  },
  hazardLabelSelected: {
    color: '#3b82f6',
  },
  severityContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  severityButton: {
    flex: 1,
    backgroundColor: 'white',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 2,
  },
  severityText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
  },
  severityTextSelected: {
    color: 'white',
  },
  severityLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 2,
  },
  severityLabelSelected: {
    color: 'white',
  },
  locationRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  locationInput: {
    flex: 1,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 4,
  },
  input: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  locationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#eff6ff',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#3b82f6',
  },
  locationButtonText: {
    color: '#3b82f6',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
  },
  imageButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  imageButton: {
    flex: 1,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d1d5db',
  },
  imageButtonText: {
    color: '#3b82f6',
    fontSize: 14,
    fontWeight: '500',
    marginTop: 8,
  },
  imagePreview: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#d1d5db',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  imagePreviewText: {
    color: '#10b981',
    fontSize: 14,
    fontWeight: '500',
  },
  removeImageButton: {
    padding: 4,
  },
  submitButton: {
    backgroundColor: '#3b82f6',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
  },
  submitButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
