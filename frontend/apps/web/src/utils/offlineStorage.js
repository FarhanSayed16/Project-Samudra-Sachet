// Offline storage utilities using IndexedDB
class OfflineStorage {
  constructor() {
    this.dbName = 'SamudraSachetDB';
    this.version = 1;
    this.db = null;
  }

  // Initialize IndexedDB
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Create object stores
        if (!db.objectStoreNames.contains('reports')) {
          const reportsStore = db.createObjectStore('reports', { keyPath: 'id' });
          reportsStore.createIndex('status', 'status', { unique: false });
          reportsStore.createIndex('hazard_type', 'hazard_type', { unique: false });
          reportsStore.createIndex('created_at', 'created_at', { unique: false });
        }

        if (!db.objectStoreNames.contains('hotspots')) {
          const hotspotsStore = db.createObjectStore('hotspots', { keyPath: 'id' });
          hotspotsStore.createIndex('status', 'status', { unique: false });
          hotspotsStore.createIndex('event_type', 'event_type', { unique: false });
        }

        if (!db.objectStoreNames.contains('offlineActions')) {
          const actionsStore = db.createObjectStore('offlineActions', { keyPath: 'id', autoIncrement: true });
          actionsStore.createIndex('timestamp', 'timestamp', { unique: false });
          actionsStore.createIndex('type', 'type', { unique: false });
        }

        if (!db.objectStoreNames.contains('userData')) {
          db.createObjectStore('userData', { keyPath: 'key' });
        }

        if (!db.objectStoreNames.contains('cache')) {
          const cacheStore = db.createObjectStore('cache', { keyPath: 'key' });
          cacheStore.createIndex('timestamp', 'timestamp', { unique: false });
          cacheStore.createIndex('expires', 'expires', { unique: false });
        }
      };
    });
  }

  // Generic store method
  async store(storeName, data) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Generic get method
  async get(storeName, key) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Generic getAll method
  async getAll(storeName, indexName = null, range = null) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const target = indexName ? store.index(indexName) : store;
      const request = range ? target.getAll(range) : target.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Generic delete method
  async delete(storeName, key) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // Store offline action
  async storeOfflineAction(action) {
    const offlineAction = {
      ...action,
      timestamp: Date.now(),
      retryCount: 0
    };

    return this.store('offlineActions', offlineAction);
  }

  // Get offline actions
  async getOfflineActions() {
    return this.getAll('offlineActions');
  }

  // Remove offline action
  async removeOfflineAction(id) {
    return this.delete('offlineActions', id);
  }

  // Store reports for offline access
  async storeReports(reports) {
    const promises = reports.map(report => 
      this.store('reports', { ...report, cached_at: Date.now() })
    );
    return Promise.all(promises);
  }

  // Get cached reports
  async getCachedReports(filters = {}) {
    let reports = await this.getAll('reports');

    // Apply filters
    if (filters.status) {
      reports = reports.filter(report => report.status === filters.status);
    }
    if (filters.hazard_type) {
      reports = reports.filter(report => report.hazard_type === filters.hazard_type);
    }
    if (filters.limit) {
      reports = reports.slice(0, filters.limit);
    }

    // Sort by created_at descending
    reports.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    return reports;
  }

  // Store hotspots for offline access
  async storeHotspots(hotspots) {
    const promises = hotspots.map(hotspot => 
      this.store('hotspots', { ...hotspot, cached_at: Date.now() })
    );
    return Promise.all(promises);
  }

  // Get cached hotspots
  async getCachedHotspots(filters = {}) {
    let hotspots = await this.getAll('hotspots');

    // Apply filters
    if (filters.status) {
      hotspots = hotspots.filter(hotspot => hotspot.status === filters.status);
    }
    if (filters.event_type) {
      hotspots = hotspots.filter(hotspot => hotspot.event_type === filters.event_type);
    }
    if (filters.limit) {
      hotspots = hotspots.slice(0, filters.limit);
    }

    // Sort by created_at descending
    hotspots.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    return hotspots;
  }

  // Cache API response
  async cacheResponse(key, data, ttl = 300000) { // 5 minutes default TTL
    const cacheEntry = {
      key,
      data,
      timestamp: Date.now(),
      expires: Date.now() + ttl
    };

    return this.store('cache', cacheEntry);
  }

  // Get cached response
  async getCachedResponse(key) {
    const cacheEntry = await this.get('cache', key);
    
    if (!cacheEntry) return null;
    
    // Check if expired
    if (Date.now() > cacheEntry.expires) {
      await this.delete('cache', key);
      return null;
    }
    
    return cacheEntry.data;
  }

  // Store user data
  async storeUserData(key, data) {
    return this.store('userData', { key, data, timestamp: Date.now() });
  }

  // Get user data
  async getUserData(key) {
    const entry = await this.get('userData', key);
    return entry ? entry.data : null;
  }

  // Clear expired cache entries
  async clearExpiredCache() {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore(storeName);
      const index = store.index('expires');
      const range = IDBKeyRange.upperBound(Date.now());
      const request = index.openCursor(range);

      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        } else {
          resolve();
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  // Get storage usage
  async getStorageUsage() {
    if (!this.db) await this.init();

    const stores = ['reports', 'hotspots', 'offlineActions', 'userData', 'cache'];
    const usage = {};

    for (const storeName of stores) {
      const data = await this.getAll(storeName);
      usage[storeName] = {
        count: data.length,
        size: JSON.stringify(data).length
      };
    }

    return usage;
  }

  // Clear all data
  async clearAll() {
    if (!this.db) await this.init();

    const stores = ['reports', 'hotspots', 'offlineActions', 'userData', 'cache'];
    const transaction = this.db.transaction(stores, 'readwrite');

    const promises = stores.map(storeName => {
      const store = transaction.objectStore(storeName);
      return new Promise((resolve, reject) => {
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    });

    return Promise.all(promises);
  }
}

// Create singleton instance
const offlineStorage = new OfflineStorage();

// Network status detection
class NetworkManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.listeners = [];
    
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));
  }

  handleOnline() {
    this.isOnline = true;
    this.notifyListeners('online');
  }

  handleOffline() {
    this.isOnline = false;
    this.notifyListeners('offline');
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  notifyListeners(event) {
    this.listeners.forEach(listener => listener(event));
  }

  getStatus() {
    return {
      isOnline: this.isOnline,
      connectionType: navigator.connection?.effectiveType || 'unknown'
    };
  }
}

// Create singleton instance
const networkManager = new NetworkManager();

// Offline API wrapper
class OfflineAPI {
  constructor(apiService) {
    this.apiService = apiService;
    this.offlineStorage = offlineStorage;
    this.networkManager = networkManager;
  }

  async request(url, options = {}) {
    const { method = 'GET', data, headers = {} } = options;

    // If online, try network request first
    if (this.networkManager.isOnline) {
      try {
        const response = await this.apiService.request(url, options);
        
        // Cache successful GET requests
        if (method === 'GET' && response.status === 200) {
          await this.offlineStorage.cacheResponse(url, response.data);
        }
        
        return response;
      } catch (error) {
        // If network fails, try cache for GET requests
        if (method === 'GET') {
          const cachedData = await this.offlineStorage.getCachedResponse(url);
          if (cachedData) {
            return { data: cachedData, fromCache: true };
          }
        }
        throw error;
      }
    }

    // If offline, handle based on method
    if (method === 'GET') {
      // Try cache for GET requests
      const cachedData = await this.offlineStorage.getCachedResponse(url);
      if (cachedData) {
        return { data: cachedData, fromCache: true };
      }
      
      // Return offline error
      throw new Error('Offline: No cached data available');
    } else {
      // Store POST/PUT/DELETE requests for later sync
      await this.offlineStorage.storeOfflineAction({
        url,
        method,
        headers,
        data,
        timestamp: Date.now()
      });
      
      // Return success response (will sync later)
      return { 
        data: { message: 'Action queued for sync' }, 
        fromOffline: true 
      };
    }
  }
}

export { offlineStorage, networkManager, OfflineAPI };

