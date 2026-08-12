const CACHE_NAME = "lakshya-erp-app-v87";
const ASSETS = [
  "/operations",
  "/styles.css?v=54",
  "/auth-shared.css?v=8",
  "/app.js?v=67",
  "/manifest.webmanifest",
  "/lakshya-logo-576.png?v=20260804-no-tm",
  "/pwa-icon-192.png?v=20260804-no-tm"
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
  // Each portal owns its own navigation and offline shell. Never replace it
  // with the Operations shell when this root worker is still controlling a tab.
  if (/^\/(?:student-app|parent-app|faculty-app|attendance-app)(?:\/|$)/.test(url.pathname)) return;

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
          return (await caches.match(event.request)) || (await caches.match("/operations"));
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
