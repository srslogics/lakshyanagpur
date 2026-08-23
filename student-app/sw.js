const CACHE = "lakshya-student-v38";
const ASSETS = ["./", "../portal-shared.css?v=5", "./styles.css?v=17", "../auth-shared.css?v=12", "./app.js?v=24", "./manifest.webmanifest", "../lakshya-logo-576.png?v=20260804-no-tm", "../pwa-icon-192.png?v=20260804-no-tm"];
self.addEventListener("install", event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener("activate", event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE && key.startsWith("lakshya-student-")).map(key => caches.delete(key))))); self.clients.claim(); });
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.pathname.startsWith("/api/")) return;
  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request, {cache:"no-cache"}).then(response => {
      if (response.ok && response.type === "basic") caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
      return response;
    }).catch(() => url.pathname.startsWith("/student-app/") ? caches.match("./") : Response.error()));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok && response.type === "basic") caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
    return response;
  })));
});
