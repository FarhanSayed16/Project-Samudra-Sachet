// Service Worker for offline support
const CACHE_NAME = 'samudra-sachet-v1';
const OFFLINE_URL = '/offline.html';

// Files to cache for offline use
const STATIC_CACHE_URLS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/offline.html'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Install event');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Failed to cache static assets', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activate event');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const { url, method } = request;

  // Only handle GET requests
  if (method !== 'GET') {
    return;
  }

  // Skip cross-origin requests
  if (!url.startsWith(self.location.origin)) {
    return;
  }

  // Handle API requests
  if (url.includes('/api/')) {
    event.respondWith(
      handleApiRequest(request)
    );
    return;
  }

  // Handle page requests
  if (request.mode === 'navigate') {
    event.respondWith(
      handlePageRequest(request)
    );
    return;
  }

  // Handle other requests (static assets)
  event.respondWith(
    handleStaticRequest(request)
  );
});

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // If successful, cache the response
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache for API request');
    
    // Try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for API requests
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: 'You are currently offline. Please check your internet connection.'
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle page requests with cache-first strategy
async function handlePageRequest(request) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Try network
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed for page request');
    
    // Return offline page
    const offlineResponse = await caches.match(OFFLINE_URL);
    if (offlineResponse) {
      return offlineResponse;
    }
    
    // Fallback offline response
    return new Response(
      `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Offline - Samudra Sachet</title>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
          <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
            <h1>You're Offline</h1>
            <p>Please check your internet connection and try again.</p>
            <button onclick="window.location.reload()">Retry</button>
          </div>
        </body>
      </html>
      `,
      {
        status: 200,
        statusText: 'OK',
        headers: { 'Content-Type': 'text/html' }
      }
    );
  }
}

// Handle static asset requests with cache-first strategy
async function handleStaticRequest(request) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Try network
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Failed to fetch static asset');
    return new Response('Asset not available offline', {
      status: 404,
      statusText: 'Not Found'
    });
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync event', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(
      syncOfflineActions()
    );
  }
});

// Sync offline actions when connection is restored
async function syncOfflineActions() {
  try {
    // Get offline actions from IndexedDB
    const offlineActions = await getOfflineActions();
    
    for (const action of offlineActions) {
      try {
        await syncAction(action);
        await removeOfflineAction(action.id);
      } catch (error) {
        console.error('Service Worker: Failed to sync action', action, error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Failed to sync offline actions', error);
  }
}

// Sync individual action
async function syncAction(action) {
  const response = await fetch(action.url, {
    method: action.method,
    headers: action.headers,
    body: action.body
  });
  
  if (!response.ok) {
    throw new Error(`Sync failed: ${response.status}`);
  }
  
  return response;
}

// IndexedDB operations for offline actions
async function getOfflineActions() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('SamudraSachetDB', 1);
    
    request.onerror = () => reject(request.error);
    
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['offlineActions'], 'readonly');
      const store = transaction.objectStore('offlineActions');
      const getAllRequest = store.getAll();
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
    
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains('offlineActions')) {
        db.createObjectStore('offlineActions', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

async function removeOfflineAction(id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('SamudraSachetDB', 1);
    
    request.onerror = () => reject(request.error);
    
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['offlineActions'], 'readwrite');
      const store = transaction.objectStore('offlineActions');
      const deleteRequest = store.delete(id);
      
      deleteRequest.onsuccess = () => resolve();
      deleteRequest.onerror = () => reject(deleteRequest.error);
    };
  });
}

