// WebSocket connection manager for real-time features
class WebSocketManager {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
    this.isConnected = false;
    this.heartbeatInterval = null;
    this.heartbeatTimeout = null;
  }

  connect(url) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.ws = new WebSocket(url);
      this.setupEventHandlers();
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleReconnect();
    }
  }

  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.isConnected = false;
      this.stopHeartbeat();
      this.emit('disconnected', event);
      
      if (!event.wasClean) {
        this.handleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    };
  }

  handleMessage(data) {
    const { type, payload } = data;
    
    // Handle heartbeat response
    if (type === 'pong') {
      this.handlePong();
      return;
    }

    // Emit message to listeners
    this.emit(type, payload);
  }

  send(type, payload) {
    if (!this.isConnected) {
      console.warn('WebSocket not connected, cannot send message');
      return false;
    }

    try {
      const message = JSON.stringify({ type, payload });
      this.ws.send(message);
      return true;
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      return false;
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  unsubscribe(eventType, callback) {
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket listener:', error);
        }
      });
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('reconnect_failed');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (this.ws && this.ws.readyState === WebSocket.CLOSED) {
        this.connect(this.ws.url);
      }
    }, delay);
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send('ping');
      
      // Set timeout for pong response
      this.heartbeatTimeout = setTimeout(() => {
        console.warn('Heartbeat timeout, reconnecting...');
        this.ws.close();
      }, 10000);
    }, 30000); // Send ping every 30 seconds
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  handlePong() {
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  disconnect() {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.isConnected = false;
  }

  getStatus() {
    return {
      isConnected: this.isConnected,
      readyState: this.ws ? this.ws.readyState : WebSocket.CLOSED,
      reconnectAttempts: this.reconnectAttempts
    };
  }
}

// Real-time event types
export const REALTIME_EVENTS = {
  // Report events
  REPORT_CREATED: 'report_created',
  REPORT_UPDATED: 'report_updated',
  REPORT_VERIFIED: 'report_verified',
  REPORT_REJECTED: 'report_rejected',
  
  // Hotspot events
  HOTSPOT_CREATED: 'hotspot_created',
  HOTSPOT_UPDATED: 'hotspot_updated',
  HOTSPOT_RESOLVED: 'hotspot_resolved',
  
  // Alert events
  ALERT_CREATED: 'alert_created',
  ALERT_UPDATED: 'alert_updated',
  
  // Notification events
  NOTIFICATION_CREATED: 'notification_created',
  
  // System events
  SYSTEM_MAINTENANCE: 'system_maintenance',
  SYSTEM_UPDATE: 'system_update'
};

// Real-time manager
class RealtimeManager {
  constructor() {
    this.wsManager = new WebSocketManager();
    this.isInitialized = false;
    this.eventHandlers = new Map();
  }

  async initialize(wsUrl) {
    if (this.isInitialized) {
      console.log('RealtimeManager already initialized');
      return;
    }

    try {
      // Connect to WebSocket
      this.wsManager.connect(wsUrl);
      
      // Set up event handlers
      this.setupEventHandlers();
      
      this.isInitialized = true;
      console.log('RealtimeManager initialized');
    } catch (error) {
      console.error('Failed to initialize RealtimeManager:', error);
      throw error;
    }
  }

  setupEventHandlers() {
    // Handle connection events
    this.wsManager.subscribe('connected', () => {
      console.log('Real-time connection established');
      this.emit('connection_status', { connected: true });
    });

    this.wsManager.subscribe('disconnected', () => {
      console.log('Real-time connection lost');
      this.emit('connection_status', { connected: false });
    });

    this.wsManager.subscribe('error', (error) => {
      console.error('Real-time connection error:', error);
      this.emit('connection_error', error);
    });

    // Handle real-time events
    Object.values(REALTIME_EVENTS).forEach(eventType => {
      this.wsManager.subscribe(eventType, (data) => {
        this.handleRealtimeEvent(eventType, data);
      });
    });
  }

  handleRealtimeEvent(eventType, data) {
    console.log(`Real-time event received: ${eventType}`, data);
    
    // Emit to registered handlers
    if (this.eventHandlers.has(eventType)) {
      this.eventHandlers.get(eventType).forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in real-time event handler for ${eventType}:`, error);
        }
      });
    }

    // Emit generic real-time event
    this.emit('realtime_event', { type: eventType, data });
  }

  // Subscribe to specific real-time events
  subscribe(eventType, handler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType).push(handler);
  }

  // Unsubscribe from specific real-time events
  unsubscribe(eventType, handler) {
    if (this.eventHandlers.has(eventType)) {
      const handlers = this.eventHandlers.get(eventType);
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  // Send real-time message
  send(eventType, data) {
    return this.wsManager.send(eventType, data);
  }

  // Generic event emitter
  emit(eventType, data) {
    // This could be extended to use a proper event emitter
    window.dispatchEvent(new CustomEvent(eventType, { detail: data }));
  }

  // Get connection status
  getStatus() {
    return this.wsManager.getStatus();
  }

  // Disconnect
  disconnect() {
    this.wsManager.disconnect();
    this.isInitialized = false;
  }
}

// Create singleton instance
const realtimeManager = new RealtimeManager();

export { WebSocketManager, RealtimeManager, realtimeManager };

