"use strict";

self.addEventListener("push", event => {
  let payload = {};
  try { payload = event.data?.json() || {}; } catch { payload = {}; }
  event.waitUntil(self.registration.showNotification(
    payload.title || "New Lakshya announcement",
    {
      body:payload.body || "Tap to open the app and view it securely.",
      icon:"/pwa-icon-192.png?v=20260804-no-tm",
      badge:"/pwa-icon-192.png?v=20260804-no-tm",
      tag:`lakshya-notice-${payload.noticeId || "new"}`,
      data:{url:payload.url || "/", noticeId:payload.noticeId || ""},
      renotify:false
    }
  ));
});

self.addEventListener("notificationclick", event => {
  event.notification.close();
  const destination = new URL(event.notification.data?.url || "/", self.location.origin).href;
  event.waitUntil(self.clients.matchAll({type:"window", includeUncontrolled:true}).then(async clients => {
    const targetPath = new URL(destination).pathname;
    const existing = clients.find(client => new URL(client.url).pathname.startsWith(targetPath.split("/").slice(0, 2).join("/") || "/"));
    if (existing) {
      await existing.navigate(destination);
      return existing.focus();
    }
    return self.clients.openWindow(destination);
  }));
});
