import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';
import { setConnectionStatus, addRealtimeEvent } from '../state/slices/realtimeSlice';
import { realtimeManager } from '../utils/realtime';
import { pushNotificationManager } from '../utils/pushNotifications';

const ConnectionStatus = () => {
  const dispatch = useDispatch();
  const { connectionStatus, isConnected, lastEvent, stats } = useSelector(state => state.realtime);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Set up real-time event listeners
    const handleConnectionStatus = (status) => {
      dispatch(setConnectionStatus({ status: status === 'online' ? 'connected' : 'disconnected' }));
    };

    const handleRealtimeEvent = (event) => {
      dispatch(addRealtimeEvent({
        type: event.type,
        data: event.data,
        timestamp: new Date().toISOString()
      }));
    };

    // Subscribe to real-time events
    realtimeManager.subscribe('connection_status', handleConnectionStatus);
    realtimeManager.subscribe('realtime_event', handleRealtimeEvent);

    // Initialize real-time connection
    const initializeRealtime = async () => {
      try {
        const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
        await realtimeManager.initialize(wsUrl);
      } catch (error) {
        console.error('Failed to initialize real-time connection:', error);
        dispatch(setConnectionStatus({ status: 'error', error: error.message }));
      }
    };

    initializeRealtime();

    return () => {
      realtimeManager.unsubscribe('connection_status', handleConnectionStatus);
      realtimeManager.unsubscribe('realtime_event', handleRealtimeEvent);
    };
  }, [dispatch]);

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'connecting':
        return <Wifi className="h-4 w-4 text-yellow-500 animate-pulse" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <WifiOff className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'error':
        return 'Connection Error';
      default:
        return 'Disconnected';
    }
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-green-600';
      case 'connecting':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const handleReconnect = () => {
    dispatch(setConnectionStatus({ status: 'connecting' }));
    // Reinitialize real-time connection
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    realtimeManager.initialize(wsUrl).catch(error => {
      dispatch(setConnectionStatus({ status: 'error', error: error.message }));
    });
  };

  const handleEnableNotifications = async () => {
    try {
      const permission = await pushNotificationManager.requestPermission();
      if (permission === 'granted') {
        const subscription = await pushNotificationManager.subscribe();
        await pushNotificationManager.sendSubscriptionToServer(subscription);
        console.log('Push notifications enabled');
      }
    } catch (error) {
      console.error('Failed to enable push notifications:', error);
    }
  };

  return (
    <div className="relative">
      {/* Connection Status Indicator */}
      <div 
        className={`flex items-center space-x-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
          isConnected ? 'bg-green-50 hover:bg-green-100' : 'bg-gray-50 hover:bg-gray-100'
        }`}
        onClick={() => setShowDetails(!showDetails)}
      >
        {getStatusIcon()}
        <span className={`text-sm font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
        {lastEvent && (
          <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" />
        )}
      </div>

      {/* Connection Details Panel */}
      {showDetails && (
        <div className="absolute top-full right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border p-4 z-50">
          <div className="space-y-4">
            {/* Status */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Connection Status</h3>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getStatusIcon()}
                  <span className={getStatusColor()}>{getStatusText()}</span>
                </div>
                {!isConnected && (
                  <button
                    onClick={handleReconnect}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Reconnect
                  </button>
                )}
              </div>
            </div>

            {/* Stats */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Statistics</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Total Events:</span>
                  <span className="ml-2 font-medium">{stats.totalEvents}</span>
                </div>
                <div>
                  <span className="text-gray-600">Last Connected:</span>
                  <span className="ml-2 font-medium">
                    {stats.lastConnected ? new Date(stats.lastConnected).toLocaleTimeString() : 'Never'}
                  </span>
                </div>
              </div>
            </div>

            {/* Event Types */}
            {Object.keys(stats.eventsByType).length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Event Types</h3>
                <div className="space-y-1">
                  {Object.entries(stats.eventsByType).map(([type, count]) => (
                    <div key={type} className="flex justify-between text-sm">
                      <span className="text-gray-600 capitalize">{type.replace('_', ' ')}</span>
                      <span className="font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Last Event */}
            {lastEvent && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Last Event</h3>
                <div className="text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium capitalize">{lastEvent.type.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Time:</span>
                    <span className="font-medium">
                      {new Date(lastEvent.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Notifications */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Notifications</h3>
              <div className="text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Push Notifications:</span>
                  <button
                    onClick={handleEnableNotifications}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    Enable
                  </button>
                </div>
              </div>
            </div>

            {/* Close Button */}
            <div className="pt-2 border-t">
              <button
                onClick={() => setShowDetails(false)}
                className="w-full text-sm text-gray-600 hover:text-gray-800"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;

