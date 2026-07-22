const CACHE_NAME = "lakshya-erp-app-v32";
const ASSETS = [
  "./",
  "./styles.css?v=20",
  "./auth-shared.css?v=4",
  "./app.js?v=21",
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
      Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;

      return fetch(event.request)
        .then(response => {
          if (!response || response.status !== 200 || response.type !== "basic") {
            return response;
          }

          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          return response;
        })
        .catch(async () => {
          const url = new URL(event.request.url);

          if (event.request.mode === "navigate") {
            const requestedPage =
              (await caches.match(event.request)) ||
              (await caches.match(url.pathname)) ||
              (await caches.match(`.${url.pathname}`));

            if (requestedPage) {
              return requestedPage;
            }
          }

          return caches.match("./");
        });
    })
  );
});
