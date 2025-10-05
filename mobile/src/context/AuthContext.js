import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { setAuthToken } from '../services/apiService';
import { authAPI } from '../services/apiService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('authToken');
      const storedUser = await AsyncStorage.getItem('user');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        setAuthToken(storedToken);
      }
    } catch (error) {
      console.error('Error loading stored auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user: userData } = response;
      
      // Store auth data
      await AsyncStorage.setItem('authToken', access_token);
      await AsyncStorage.setItem('user', JSON.stringify(userData));
      
      // Set in state
      setToken(access_token);
      setUser(userData);
      setAuthToken(access_token);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Login failed' 
      };
    }
  };

  const logout = async () => {
    try {
      // Clear stored data
      await AsyncStorage.removeItem('authToken');
      await AsyncStorage.removeItem('user');
      
      // Clear state
      setToken(null);
      setUser(null);
      
      // Clear API service token
      setAuthToken(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const value = {
    user,
    token,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
