importScripts("/push-service-worker.js?v=1");
const CACHE = "lakshya-attendance-v28";
const ASSETS = [
  "./",
  "./styles.css?v=9",
  "../auth-shared.css?v=9",
  "../push-shared.css?v=1",
  "../runtime-config.js?v=1",
  "../push-client.js?v=2",
  "./app.js?v=25",
  "./manifest.webmanifest",
  "../lakshya-logo-576.png?v=20260804-no-tm",
  "../pwa-icon-192.png?v=20260804-no-tm"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(key => key.startsWith("lakshya-attendance-") && key !== CACHE).map(key => caches.delete(key))
  )));
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.pathname.startsWith("/api/")) return;
  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request, {cache:"no-cache"}).then(response => {
      if (response.ok && response.type === "basic") caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
      return response;
    }).catch(() => url.pathname.startsWith("/attendance-app/") ? caches.match("./") : Response.error()));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok && response.type === "basic") caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
    return response;
  })));
});
