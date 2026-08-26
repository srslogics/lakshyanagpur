"use strict";

(() => {
  const supported = () => "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
  const decodeKey = value => {
    const padding = "=".repeat((4 - value.length % 4) % 4);
    const raw = atob((value + padding).replace(/-/g, "+").replace(/_/g, "/"));
    return Uint8Array.from([...raw].map(character => character.charCodeAt(0)));
  };
  const request = async (path, token, options = {}) => {
    const response = await fetch(path, {
      ...options,
      headers: {"Content-Type":"application/json", Authorization:`Bearer ${token}`, ...(options.headers || {})}
    });
    if (!response.ok) throw new Error("Notification setup is temporarily unavailable.");
    return response.status === 204 ? null : response.json();
  };
  const currentSubscription = async () => {
    const registration = await navigator.serviceWorker.ready;
    return [registration, await registration.pushManager.getSubscription()];
  };
  const save = async (token, portal, subscription) => {
    const json = subscription.toJSON();
    await request("/api/push/subscriptions", token, {
      method:"PUT",
      body:JSON.stringify({endpoint:json.endpoint, keys:json.keys, portal, userAgent:navigator.userAgent})
    });
  };
  const subscribe = async (token, portal) => {
    const config = await request("/api/push/config", token);
    if (!config.available) return false;
    const [registration, existing] = await currentSubscription();
    const subscription = existing || await registration.pushManager.subscribe({
      userVisibleOnly:true,
      applicationServerKey:decodeKey(config.publicKey)
    });
    await save(token, portal, subscription);
    return true;
  };
  const removePrompt = () => document.querySelector("[data-push-prompt]")?.remove();
  const showPrompt = (token, portal) => {
    if (document.querySelector("[data-push-prompt]")) return;
    const deferredUntil = Number(localStorage.getItem("lakshya_push_prompt_after") || 0);
    if (deferredUntil > Date.now()) return;
    const panel = document.createElement("aside");
    panel.className = "push-permission-card";
    panel.dataset.pushPrompt = "";
    panel.setAttribute("aria-labelledby", "push-permission-title");
    panel.innerHTML = `<div><strong id="push-permission-title">Get announcement alerts</strong><p>Receive a private alert when Lakshya publishes an update.</p></div><div class="push-permission-actions"><button type="button" data-push-later>Not now</button><button type="button" data-push-enable>Enable</button></div>`;
    panel.querySelector("[data-push-later]").addEventListener("click", () => {
      localStorage.setItem("lakshya_push_prompt_after", String(Date.now() + 7 * 86400000));
      removePrompt();
    });
    panel.querySelector("[data-push-enable]").addEventListener("click", async event => {
      const button = event.currentTarget;
      button.disabled = true;
      button.textContent = "Enabling…";
      try {
        const permission = await Notification.requestPermission();
        if (permission === "granted") await subscribe(token, portal);
        removePrompt();
      } catch {
        button.disabled = false;
        button.textContent = "Try again";
      }
    });
    document.body.append(panel);
  };
  const markOpened = async token => {
    const url = new URL(location.href);
    const noticeId = url.searchParams.get("notice");
    if (!noticeId) return;
    try { await request(`/api/push/notices/${encodeURIComponent(noticeId)}/opened`, token, {method:"POST"}); } catch {}
    url.searchParams.delete("notice");
    history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
  };
  const sync = async ({token, portal}) => {
    if (!token || !supported()) return;
    await markOpened(token);
    if (Notification.permission === "granted") {
      try { await subscribe(token, portal); } catch {}
    } else if (Notification.permission === "default") {
      showPrompt(token, portal);
    }
  };
  const unsubscribe = async ({token}) => {
    removePrompt();
    if (!supported()) return;
    try {
      const [, subscription] = await currentSubscription();
      if (!subscription) return;
      if (token) await request("/api/push/subscriptions", token, {method:"DELETE", body:JSON.stringify({endpoint:subscription.endpoint})});
      await subscription.unsubscribe();
    } catch {}
  };
  window.LakshyaPush = {sync, unsubscribe};
})();
