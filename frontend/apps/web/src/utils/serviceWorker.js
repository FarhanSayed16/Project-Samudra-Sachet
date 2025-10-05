// Service Worker registration and management
class ServiceWorkerManager {
  constructor() {
    this.registration = null;
    this.isSupported = 'serviceWorker' in navigator;
  }

  async register() {
    if (!this.isSupported) {
      console.log('Service Worker not supported');
      return false;
    }

    try {
      this.registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registered successfully:', this.registration);

      // Handle updates
      this.registration.addEventListener('updatefound', () => {
        const newWorker = this.registration.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New content is available, show update notification
            this.showUpdateNotification();
          }
        });
      });

      return true;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return false;
    }
  }

  async unregister() {
    if (this.registration) {
      const success = await this.registration.unregister();
      console.log('Service Worker unregistered:', success);
      return success;
    }
    return false;
  }

  showUpdateNotification() {
    // Show update notification to user
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification('Update Available', {
        body: 'A new version of Samudra Sachet is available. Click to update.',
        icon: '/favicon.ico',
        tag: 'update-available'
      });

      notification.onclick = () => {
        window.location.reload();
        notification.close();
      };
    } else {
      // Fallback to custom notification
      this.showCustomUpdateNotification();
    }
  }

  showCustomUpdateNotification() {
    // Create custom update notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50 max-w-sm';
    notification.innerHTML = `
      <div class="flex items-center justify-between">
        <div>
          <h3 class="font-semibold">Update Available</h3>
          <p class="text-sm opacity-90">A new version is ready to install.</p>
        </div>
        <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
      <div class="mt-3 flex space-x-2">
        <button onclick="window.location.reload()" class="bg-white text-blue-600 px-3 py-1 rounded text-sm font-medium hover:bg-gray-100">
          Update Now
        </button>
        <button onclick="this.parentElement.parentElement.remove()" class="text-white hover:text-gray-200 text-sm">
          Later
        </button>
      </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 10 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 10000);
  }

  async requestNotificationPermission() {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
      return permission === 'granted';
    }
    return false;
  }

  getStatus() {
    return {
      isSupported: this.isSupported,
      isRegistered: !!this.registration,
      isActive: !!navigator.serviceWorker.controller,
      scope: this.registration?.scope
    };
  }
}

// Create singleton instance
const serviceWorkerManager = new ServiceWorkerManager();

// Initialize service worker when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
  await serviceWorkerManager.register();
  await serviceWorkerManager.requestNotificationPermission();
});

// Export for use in other modules
export default serviceWorkerManager;

