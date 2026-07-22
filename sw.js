const CACHE_NAME = "lakshya-erp-app-v33";
const ASSETS = [
  "./",
  "./styles.css?v=20",
  "./auth-shared.css?v=4",
  "./app.js?v=22",
  "./manifest.webmanifest",
  "./lakshya-logo.png",
  "./share-card.png",
  "./apple-touch-icon.png",
  "./pwa-icon-192.png",
  "./pwa-icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(key => key !== CACHE_NAME && key.startsWith("lakshya-erp-app-")).map(key => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);

  // Authenticated API responses must always come from the backend.
  if (url.origin === self.location.origin && url.pathname.startsWith("/api/")) return;

  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request, { cache: "no-store" })
        .then(response => {
          if (response && response.status === 200 && response.type === "basic") {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          }
          return response;
        })
        .catch(async () => {
          return (await caches.match(event.request)) || (await caches.match("./"));
        })
    );
    return;
  }

  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response && response.status === 200 && response.type === "basic") {
      const responseClone = response.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
    }
    return response;
  })));
});
