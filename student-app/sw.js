const CACHE = "lakshya-student-v13";
const ASSETS = ["./", "../portal-shared.css?v=2", "./styles.css?v=7", "../auth-shared.css?v=5", "./app.js?v=6", "./manifest.webmanifest", "../lakshya-logo.png", "../pwa-icon-192.png", "../pwa-icon-512.png", "../share-card.png"];
self.addEventListener("install", event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener("activate", event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))); self.clients.claim(); });
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.pathname.startsWith("/api/")) return;
  event.respondWith(fetch(event.request).then(response => { if (response.ok && response.type === "basic") caches.open(CACHE).then(cache => cache.put(event.request, response.clone())); return response; }).catch(() => caches.match(event.request).then(match => match || caches.match("./"))));
});
