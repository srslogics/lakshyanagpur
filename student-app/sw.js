const CACHE = "lakshya-student-v14";
const ASSETS = ["./", "../portal-shared.css?v=3", "./styles.css?v=7", "../auth-shared.css?v=5", "./app.js?v=7", "./manifest.webmanifest", "../lakshya-logo-576.png", "../pwa-icon-192.png"];
self.addEventListener("install", event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener("activate", event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))); self.clients.claim(); });
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.pathname.startsWith("/api/")) return;
  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request, {cache:"no-cache"}).then(response => {
      if (response.ok && response.type === "basic") caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
      return response;
    }).catch(() => caches.match(event.request).then(match => match || caches.match("./"))));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok && response.type === "basic") caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
    return response;
  })));
});
