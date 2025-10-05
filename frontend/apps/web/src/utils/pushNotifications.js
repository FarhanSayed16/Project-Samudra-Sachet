// Push notification manager
class PushNotificationManager {
  constructor() {
    this.registration = null;
    this.subscription = null;
    this.isSupported = 'PushManager' in window && 'serviceWorker' in navigator;
    this.vapidPublicKey = null;
  }

  async initialize(vapidPublicKey) {
    if (!this.isSupported) {
      console.log('Push notifications not supported');
      return false;
    }

    this.vapidPublicKey = vapidPublicKey;

    try {
      // Get service worker registration
      this.registration = await navigator.serviceWorker.ready;
      
      // Check existing subscription
      this.subscription = await this.registration.pushManager.getSubscription();
      
      console.log('Push notification manager initialized');
      return true;
    } catch (error) {
      console.error('Failed to initialize push notification manager:', error);
      return false;
    }
  }

  async requestPermission() {
    if (!this.isSupported) {
      return 'denied';
    }

    try {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
      return permission;
    } catch (error) {
      console.error('Failed to request notification permission:', error);
      return 'denied';
    }
  }

  async subscribe() {
    if (!this.isSupported || !this.registration) {
      throw new Error('Push notifications not supported or not initialized');
    }

    try {
      // Check if already subscribed
      if (this.subscription) {
        console.log('Already subscribed to push notifications');
        return this.subscription;
      }

      // Create new subscription
      this.subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.vapidPublicKey
      });

      console.log('Subscribed to push notifications:', this.subscription);
      return this.subscription;
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
      throw error;
    }
  }

  async unsubscribe() {
    if (!this.subscription) {
      console.log('Not subscribed to push notifications');
      return false;
    }

    try {
      const success = await this.subscription.unsubscribe();
      if (success) {
        this.subscription = null;
        console.log('Unsubscribed from push notifications');
      }
      return success;
    } catch (error) {
      console.error('Failed to unsubscribe from push notifications:', error);
      return false;
    }
  }

  async sendSubscriptionToServer(subscription) {
    try {
      const response = await fetch('/api/v1/notifications/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subscription: subscription,
          user_agent: navigator.userAgent,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Subscription sent to server:', result);
      return result;
    } catch (error) {
      console.error('Failed to send subscription to server:', error);
      throw error;
    }
  }

  async removeSubscriptionFromServer() {
    try {
      const response = await fetch('/api/v1/notifications/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Subscription removed from server:', result);
      return result;
    } catch (error) {
      console.error('Failed to remove subscription from server:', error);
      throw error;
    }
  }

  // Show local notification
  showNotification(title, options = {}) {
    if (!this.isSupported) {
      console.log('Notifications not supported');
      return;
    }

    const defaultOptions = {
      body: '',
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: 'samudra-sachet',
      requireInteraction: false,
      silent: false,
      ...options
    };

    if (this.registration) {
      this.registration.showNotification(title, defaultOptions);
    } else {
      // Fallback to browser notification
      new Notification(title, defaultOptions);
    }
  }

  // Handle incoming push messages
  handlePushMessage(event) {
    console.log('Push message received:', event);

    const data = event.data ? event.data.json() : {};
    const { title, body, icon, url, actions } = data;

    const options = {
      body,
      icon: icon || '/favicon.ico',
      badge: '/favicon.ico',
      tag: 'samudra-sachet',
      requireInteraction: true,
      actions: actions || []
    };

    // Show notification
    event.waitUntil(
      this.registration.showNotification(title, options)
    );
  }

  // Handle notification click
  handleNotificationClick(event) {
    console.log('Notification clicked:', event);

    event.notification.close();

    const data = event.notification.data;
    const url = data?.url || '/';

    // Focus or open the app
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then(clientList => {
        // Check if app is already open
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
    );
  }

  // Handle notification action click
  handleNotificationActionClick(event) {
    console.log('Notification action clicked:', event);

    const action = event.action;
    const data = event.notification.data;

    event.notification.close();

    // Handle different actions
    switch (action) {
      case 'view':
        // Open the app
        event.waitUntil(
          clients.openWindow(data?.url || '/')
        );
        break;
      case 'dismiss':
        // Just close the notification
        break;
      default:
        console.log('Unknown action:', action);
    }
  }

  // Get subscription info
  getSubscriptionInfo() {
    if (!this.subscription) {
      return null;
    }

    return {
      endpoint: this.subscription.endpoint,
      keys: {
        p256dh: this.subscription.getKey('p256dh'),
        auth: this.subscription.getKey('auth')
      }
    };
  }

  // Check if subscribed
  isSubscribed() {
    return !!this.subscription;
  }

  // Get permission status
  getPermissionStatus() {
    if (!this.isSupported) {
      return 'unsupported';
    }
    return Notification.permission;
  }

  // Get status
  getStatus() {
    return {
      isSupported: this.isSupported,
      isSubscribed: this.isSubscribed(),
      permission: this.getPermissionStatus(),
      hasRegistration: !!this.registration
    };
  }
}

// Notification types
export const NOTIFICATION_TYPES = {
  REPORT_CREATED: 'report_created',
  REPORT_VERIFIED: 'report_verified',
  HOTSPOT_CREATED: 'hotspot_created',
  ALERT_CREATED: 'alert_created',
  SYSTEM_MAINTENANCE: 'system_maintenance',
  GENERAL: 'general'
};

// Notification templates
export const NOTIFICATION_TEMPLATES = {
  [NOTIFICATION_TYPES.REPORT_CREATED]: {
    title: 'New Hazard Report',
    body: 'A new hazard report has been submitted in your area.',
    icon: '/icons/report.svg',
    actions: [
      { action: 'view', title: 'View Report' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  },
  [NOTIFICATION_TYPES.REPORT_VERIFIED]: {
    title: 'Report Verified',
    body: 'Your hazard report has been verified by authorities.',
    icon: '/icons/verified.svg',
    actions: [
      { action: 'view', title: 'View Report' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  },
  [NOTIFICATION_TYPES.HOTSPOT_CREATED]: {
    title: 'New Hotspot Detected',
    body: 'A new hazard hotspot has been detected in your area.',
    icon: '/icons/hotspot.svg',
    actions: [
      { action: 'view', title: 'View Hotspot' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  },
  [NOTIFICATION_TYPES.ALERT_CREATED]: {
    title: 'Emergency Alert',
    body: 'An emergency alert has been issued for your area.',
    icon: '/icons/alert.svg',
    actions: [
      { action: 'view', title: 'View Alert' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  },
  [NOTIFICATION_TYPES.SYSTEM_MAINTENANCE]: {
    title: 'System Maintenance',
    body: 'The system will undergo maintenance. Some features may be unavailable.',
    icon: '/icons/maintenance.svg',
    actions: [
      { action: 'dismiss', title: 'Dismiss' }
    ]
  }
};

// Create singleton instance
const pushNotificationManager = new PushNotificationManager();

export { PushNotificationManager, pushNotificationManager };

