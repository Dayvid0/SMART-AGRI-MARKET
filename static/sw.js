// Smart Agri Market — Service Worker
const CACHE_NAME = 'agrimarket-v1';
const OFFLINE_URL = '/offline/';

// Core assets to pre-cache on install
const PRECACHE_ASSETS = [
    '/',
    OFFLINE_URL,
    '/static/images/icon-192x192.png',
    '/static/images/icon-512x512.png',
    '/static/images/favicon.png',
];

// ─── INSTALL ────────────────────────────────────────────
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Pre-caching core assets');
            return cache.addAll(PRECACHE_ASSETS);
        })
    );
    // Activate immediately, don't wait for old tabs to close
    self.skipWaiting();
});

// ─── ACTIVATE ───────────────────────────────────────────
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        })
    );
    // Take control of all open tabs immediately
    self.clients.claim();
});

// ─── FETCH ──────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
    const { request } = event;

    // Only handle GET requests
    if (request.method !== 'GET') return;

    // Skip cross-origin requests (CDN fonts, Bootstrap, etc.)
    if (!request.url.startsWith(self.location.origin)) return;

    // Strategy: Network-first for HTML pages, Cache-first for static assets
    if (request.mode === 'navigate') {
        // HTML navigation — try network first, fall back to cache, then offline page
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Cache a copy of the page for offline use
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                    return response;
                })
                .catch(() => {
                    return caches.match(request).then((cached) => {
                        return cached || caches.match(OFFLINE_URL);
                    });
                })
        );
    } else if (request.url.match(/\.(css|js|png|jpg|jpeg|webp|svg|ico|woff2?)$/)) {
        // Static assets — cache-first
        event.respondWith(
            caches.match(request).then((cached) => {
                if (cached) return cached;
                return fetch(request).then((response) => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                    return response;
                });
            })
        );
    }
});
