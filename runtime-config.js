"use strict";

(() => {
  // The static-site build replaces this token with the shared API service URL.
  // When FastAPI serves the portals locally, the empty fallback keeps requests
  // on the current origin.
  const configuredBase = "__LAKSHYA_API_BASE__";
  const apiBase = /^https?:\/\//i.test(configuredBase)
    ? configuredBase.replace(/\/$/, "")
    : "";

  const apiUrl = path => {
    if (!apiBase || /^https?:\/\//i.test(path)) return path;
    return `${apiBase}${String(path).startsWith("/") ? "" : "/"}${path}`;
  };

  let warmPromise;
  const warmApi = () => {
    if (!warmPromise) {
      warmPromise = fetch(apiUrl("/health"), {cache: "no-store", mode: "cors"})
        .catch(() => null);
    }
    return warmPromise;
  };

  window.LakshyaRuntime = Object.freeze({apiBase, apiUrl, warmApi});
  warmApi();
})();
