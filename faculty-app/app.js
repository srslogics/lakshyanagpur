"use strict";

const icons = {
  arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',
  home:'<path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1v-9Z"/>',
  calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4m8-4v4M3 10h18"/>',
  book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
  exam:'<path d="M7 3h10a2 2 0 0 1 2 2v16H5V5a2 2 0 0 1 2-2Z"/><path d="M9 7h6M9 11h6m-6 4h3"/><path d="m14 16 1.5 1.5L19 14"/>',
  check:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="m8 14 2.5 2.5L16 11"/>',
  more:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  spark:'<path d="m12 3 1.4 4.1 4.1 1.4-4.1 1.4L12 14l-1.4-4.1-4.1-1.4 4.1-1.4L12 3Z"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  notice:'<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z"/>',
  logout:'<path d="m10 17 5-5-5-5m5 5H3m12-9h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"/>',
  eye:'<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  "eye-off":'<path d="m3 3 18 18M10.6 5.2A11.4 11.4 0 0 1 12 5c6.5 0 10 7 10 7a16 16 0 0 1-2.1 3.2M6.6 6.6C3.6 8.6 2 12 2 12s3.5 7 10 7a10.7 10.7 0 0 0 4.1-.8M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
  plus:'<path d="M12 5v14M5 12h14"/>',
  close:'<path d="m6 6 12 12M18 6 6 18"/>',
  users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  lock:'<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  link:'<path d="M10 13a5 5 0 0 0 7.1.1l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1"/><path d="M14 11a5 5 0 0 0-7.1-.1l-2 2A5 5 0 0 0 12 20l1.1-1.1"/>',
  user:'<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  "arrow-left":'<path d="m15 18-6-6 6-6M9 12h10"/>',
  "chevron-right":'<path d="m9 18 6-6-6-6"/>',
  external:'<path d="M14 4h6v6m0-6-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/>'
};

const state = {
  token: localStorage.getItem("lakshya_faculty_token"),
  identity: null,
  loginMode: "mobile",
  data: null,
  view: "dashboard",
  assignmentFilter: "active",
  examinationFilter: "action",
  scheduleDate: "all",
  activeExam: null,
  publishingAssignment: null,
  editingAssignment: null,
  editingExamination: null,
  lastFocus: null,
  online: navigator.onLine
};
const PORTAL_VIEWS = new Set(["dashboard", "assignments", "examinations", "schedule", "batches", "notices", "profile", "more"]);
const OVERFLOW_VIEWS = new Set(["batches", "notices", "profile", "more"]);

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.spark}</svg>`;
const esc = (value = "") => String(value ?? "").replace(/[&<>'"]/g, character => ({
  "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;"
}[character]));
const initials = name => String(name || "LF").split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join("").toUpperCase();
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const asDate = value => {
  if (value instanceof Date) return value;
  const text = String(value || "");
  return new Date(/[zZ]$|[+-]\d{2}:?\d{2}$/.test(text) ? text : `${text}Z`);
};
const dateParts = value => {
  const parts = new Intl.DateTimeFormat("en-IN", {
    timeZone:"Asia/Kolkata", year:"numeric", month:"2-digit", day:"2-digit"
  }).formatToParts(asDate(value));
  const get = type => parts.find(part => part.type === type)?.value || "";
  return {year:get("year"), month:get("month"), day:get("day")};
};
const dateKey = value => {
  const {year, month, day} = dateParts(value);
  return `${year}-${month}-${day}`;
};
const dateText = value => new Intl.DateTimeFormat("en-IN", {
  timeZone:"Asia/Kolkata", day:"numeric", month:"short"
}).format(asDate(value));
const dateLong = value => new Intl.DateTimeFormat("en-IN", {
  timeZone:"Asia/Kolkata", weekday:"short", day:"numeric", month:"short"
}).format(asDate(value));
const timeText = value => new Intl.DateTimeFormat("en-IN", {
  timeZone:"Asia/Kolkata", hour:"2-digit", minute:"2-digit"
}).format(asDate(value));
const todayKey = () => dateKey(new Date());
const localInputValue = (date = new Date(Date.now() + 7 * 86400000)) => {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone:"Asia/Kolkata", year:"numeric", month:"2-digit", day:"2-digit",
    hour:"2-digit", minute:"2-digit", hourCycle:"h23"
  }).formatToParts(asDate(date));
  const value = type => parts.find(part => part.type === type)?.value || "";
  return `${value("year")}-${value("month")}-${value("day")}T${value("hour")}:${value("minute")}`;
};
const indiaInputToISOString = value => new Date(`${String(value)}:00+05:30`).toISOString();
const safeExternalUrl = value => {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
};
const titleCase = value => String(value || "").replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase());

function injectIcons(root = document) {
  $$("[data-icon]", root).forEach(node => {
    node.innerHTML = icon(node.dataset.icon);
  });
}

function setConnectionState(online) {
  const changed = state.online !== online;
  state.online = online;
  document.documentElement.classList.toggle("is-offline", !online);
  let banner = $("#connection-banner");
  if (!banner) {
    banner = document.createElement("div");
    banner.id = "connection-banner";
    banner.className = "connection-banner";
    banner.setAttribute("role", "status");
    banner.setAttribute("aria-live", "polite");
    document.body.append(banner);
  }
  banner.textContent = online ? "Connection restored." : "You are offline. Saved sign-in remains available.";
  banner.classList.toggle("visible", !online || changed);
  if (online && changed) setTimeout(() => banner.classList.remove("visible"), 2200);
}

async function resilientFetch(path, options = {}) {
  const attempts = String(options.method || "GET").toUpperCase() === "GET" ? 2 : 1;
  let lastError;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(path, {cache:"no-store", ...options, signal:controller.signal});
      clearTimeout(timer);
      setConnectionState(true);
      if (response.status >= 500 && attempt + 1 < attempts) continue;
      return response;
    } catch (error) {
      clearTimeout(timer);
      lastError = error;
      setConnectionState(navigator.onLine);
      if (attempt + 1 < attempts) continue;
    }
  }
  const error = new Error(lastError?.name === "AbortError" ? "The server took too long to respond. Try again." : "Unable to reach the server. Check your connection and retry.");
  error.status = 0;
  error.transient = true;
  throw error;
}

async function api(path, options = {}) {
  const headers = {"Content-Type":"application/json", ...(options.headers || {})};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await resilientFetch(path, {...options, headers});
  let body = {};
  try { body = await response.json(); } catch {}
  if (response.status === 401) {
    clearSession();
    showLogin("Your session expired. Sign in again.");
  }
  if (!response.ok) {
    const detail = body?.detail;
    const error = new Error(
      typeof detail === "string"
        ? detail
        : detail?.message || body?.error?.message || (response.status >= 500 ? "The service is temporarily unavailable. Try again." : "Unable to complete this request.")
    );
    error.status = response.status;
    error.transient = response.status >= 500;
    throw error;
  }
  return body;
}

function clearSession() {
  state.token = null;
  state.identity = null;
  state.data = null;
  localStorage.removeItem("lakshya_faculty_token");
}

function showLogin(message = "") {
  $("#startup-screen").classList.add("hidden");
  $("#mobile-setup-screen").classList.add("hidden");
  $("#faculty-password-change-screen").classList.add("hidden");
  $("#faculty-shell").classList.add("hidden");
  $("#login-screen").classList.remove("hidden");
  $("#login-password").value = "";
  setLoginMode(state.loginMode);
  if (message) {
    $("#login-error").textContent = message;
    $("#login-error").classList.remove("hidden");
  } else {
    $("#login-error").classList.add("hidden");
  }
  requestAnimationFrame(() => $("#login-identity").focus());
}

function setLoginMode(mode) {
  state.loginMode = mode === "email" ? "email" : "mobile";
  const emailMode = state.loginMode === "email";
  const field = $("#login-identity");
  $("#login-identity-label").textContent = emailMode ? "Email address" : "Mobile number";
  field.type = emailMode ? "email" : "tel";
  field.inputMode = emailMode ? "email" : "tel";
  field.placeholder = emailMode ? "Faculty email address" : "10-digit mobile number";
  field.maxLength = emailMode ? 254 : 16;
  $("#login-mode-button").textContent = emailMode ? "Use mobile number" : "First sign-in with email";
  $("#login-error").classList.add("hidden");
}

function showMobileSetup(identity) {
  state.identity = identity;
  $("#startup-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#faculty-password-change-screen").classList.add("hidden");
  $("#faculty-shell").classList.add("hidden");
  $("#mobile-setup-screen").classList.remove("hidden");
  $("#mobile-setup-identity").textContent = identity.email || identity.fullName;
  $("#mobile-setup-error").classList.add("hidden");
  $("#faculty-mobile").value = "";
  requestAnimationFrame(() => $("#faculty-mobile").focus());
}

function showFacultyPasswordChange(identity) {
  state.identity = identity;
  $("#startup-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#mobile-setup-screen").classList.add("hidden");
  $("#faculty-shell").classList.add("hidden");
  $("#faculty-password-change-screen").classList.remove("hidden");
  $("#faculty-password-change-form").reset();
  $("#faculty-password-change-error").classList.add("hidden");
  requestAnimationFrame(() => $("[name=currentPassword]", $("#faculty-password-change-form")).focus());
}

function toast(message) {
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  $("#toast-region").append(node);
  setTimeout(() => node.remove(), 3200);
}

function showStartupError(error) {
  $("#login-screen").classList.add("hidden");
  $("#mobile-setup-screen").classList.add("hidden");
  $("#faculty-password-change-screen").classList.add("hidden");
  $("#faculty-shell").classList.add("hidden");
  const boot = $("#startup-screen");
  boot.classList.remove("hidden");
  let panel = $("#startup-error");
  if (!panel) {
    panel = document.createElement("div");
    panel.id = "startup-error";
    panel.className = "startup-error";
    panel.innerHTML = '<strong>Faculty portal is temporarily unavailable</strong><p></p><button type="button">Retry</button>';
    boot.append(panel);
    $("button", panel).addEventListener("click", () => location.reload());
  }
  $("p", panel).textContent = error.message;
}

function empty(name, title, copy = "") {
  return `<div class="empty"><div><span>${icon(name)}</span><strong>${esc(title)}</strong>${copy ? `<p>${esc(copy)}</p>` : ""}</div></div>`;
}

async function initialize() {
  injectIcons();
  bindEvents();
  setConnectionState(navigator.onLine);
  $("#assignment-due").value = localInputValue();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  if (!state.token) {
    showLogin();
    return;
  }
  try {
    const identity = await api("/api/auth/me");
    if (identity.role !== "faculty") {
      const error = new Error("This account does not have Faculty access.");
      error.status = 403;
      throw error;
    }
    state.identity = identity;
    if (!identity.mobile) {
      showMobileSetup(identity);
      return;
    }
    if (identity.mustChangePassword) {
      showFacultyPasswordChange(identity);
      return;
    }
    await loadPortal();
  } catch (error) {
    if (error.status === 403) {
      clearSession();
      showLogin(error.message);
    } else if (error.status !== 401) {
      showStartupError(error);
    }
  }
}

async function login(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const button = $("#login-button");
  const label = $("#login-button-label");
  button.disabled = true;
  label.textContent = "Signing in…";
  $("#login-error").classList.add("hidden");
  try {
    const data = new FormData(form);
    const identity = String(data.get("identity")).trim();
    const result = await api("/api/auth/login", {
      method:"POST",
      body:JSON.stringify({
        [state.loginMode]:identity,
        password:String(data.get("password"))
      })
    });
    if (result.user.role !== "faculty") throw new Error("This account does not have Faculty access.");
    state.token = result.access_token;
    state.identity = result.user;
    localStorage.setItem("lakshya_faculty_token", state.token);
    if (!result.user.mobile) {
      showMobileSetup(result.user);
      return;
    }
    if (result.user.mustChangePassword) {
      showFacultyPasswordChange(result.user);
      return;
    }
    await loadPortal();
  } catch (error) {
    if (state.token && error.status !== 401 && (error.transient || error.status === 0)) {
      showStartupError(error);
    } else {
      clearSession();
      showLogin(error.message.includes("permission") ? "This account does not have Faculty access." : error.message);
    }
  } finally {
    button.disabled = false;
    label.textContent = "Sign in";
  }
}

async function activateMobile(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const button = $("#mobile-setup-button");
  const label = $("#mobile-setup-button-label");
  button.disabled = true;
  label.textContent = "Saving…";
  $("#mobile-setup-error").classList.add("hidden");
  try {
    const data = new FormData(form);
    const newPassword = String(data.get("newPassword"));
    if (newPassword !== String(data.get("confirmPassword"))) {
      throw new Error("The personal passwords do not match.");
    }
    const result = await api("/api/faculty/activate-mobile", {
      method:"POST",
      body:JSON.stringify({
        mobile:String(data.get("mobile")).trim(),
        newPassword
      })
    });
    clearSession();
    setLoginMode("mobile");
    showLogin("Account activated. Sign in with your mobile and personal password.");
    $("#login-identity").value = result.mobile;
  } catch (error) {
    $("#mobile-setup-error").textContent = error.message;
    $("#mobile-setup-error").classList.remove("hidden");
  } finally {
    button.disabled = false;
    label.textContent = "Activate account";
  }
}

async function changeFacultyPassword(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  const currentPassword = String(data.get("currentPassword"));
  const newPassword = String(data.get("newPassword"));
  const error = $("#faculty-password-change-error");
  if (newPassword !== String(data.get("confirmPassword"))) {
    error.textContent = "The new passwords do not match.";
    error.classList.remove("hidden");
    return;
  }
  if (newPassword === currentPassword) {
    error.textContent = "Choose a personal password different from the temporary password.";
    error.classList.remove("hidden");
    return;
  }
  const button = $("#faculty-password-change-button");
  const idle = button.innerHTML;
  button.disabled = true;
  button.textContent = "Saving…";
  error.classList.add("hidden");
  try {
    const mobile = state.identity?.mobile || "";
    await api("/api/auth/change-password", {
      method:"POST",
      body:JSON.stringify({currentPassword, newPassword})
    });
    clearSession();
    setLoginMode("mobile");
    showLogin("Personal password saved. Sign in again.");
    $("#login-identity").value = mobile;
  } catch (requestError) {
    error.textContent = requestError.message;
    error.classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.innerHTML = idle;
    injectIcons(button);
  }
}

async function loadPortal() {
  const [portal, examinations] = await Promise.all([
    api("/api/faculty/bootstrap"),
    api("/api/examinations")
  ]);
  state.data = {...portal, examinations};
  $("#startup-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#mobile-setup-screen").classList.add("hidden");
  $("#faculty-password-change-screen").classList.add("hidden");
  $("#faculty-shell").classList.remove("hidden");
  renderAll();
  const hashView = location.hash.slice(1);
  showView(PORTAL_VIEWS.has(hashView) ? hashView : "dashboard", false);
}

async function refreshPortal(message = "") {
  const [portal, examinations] = await Promise.all([
    api("/api/faculty/bootstrap"),
    api("/api/examinations")
  ]);
  state.data = {...portal, examinations};
  renderAll();
  showView(state.view, false);
  if (message) toast(message);
}

async function logout() {
  const token = state.token;
  if (token) {
    try {
      await fetch("/api/auth/logout", {method:"POST", headers:{Authorization:`Bearer ${token}`}});
    } catch {}
  }
  clearSession();
  state.view = "dashboard";
  history.replaceState(null, "", location.pathname + location.search);
  showLogin();
  toast("Signed out securely.");
}

function showView(view, updateHash = true) {
  if (!PORTAL_VIEWS.has(view)) return;
  state.view = view;
  $$(".app-view").forEach(node => node.classList.toggle("active", node.id === view));
  $$(".sidebar [data-view]").forEach(node => {
    const active = node.dataset.view === view;
    node.classList.toggle("active", active);
    active ? node.setAttribute("aria-current", "page") : node.removeAttribute("aria-current");
  });
  const mobileView = OVERFLOW_VIEWS.has(view) ? "more" : view;
  $$(".bottom-nav [data-view]").forEach(node => {
    const active = node.dataset.view === mobileView;
    node.classList.toggle("active", active);
    active ? node.setAttribute("aria-current", "page") : node.removeAttribute("aria-current");
  });
  const titles = {dashboard:"Today", assignments:"Assignments", examinations:"Examinations", schedule:"Schedule", batches:"Batches", notices:"Notices", profile:"Profile", more:"More"};
  $("#header-title").textContent = titles[view];
  if (updateHash && location.hash !== `#${view}`) history.pushState(null, "", `#${view}`);
  $("#faculty-main").focus({preventScroll:true});
  window.scrollTo({top:0, behavior:reducedMotion() ? "auto" : "smooth"});
}

function renderAll() {
  const {profile, summary, teachingPairs} = state.data;
  const firstName = profile.fullName.split(/\s+/).filter(Boolean).find(part => !/^(dr|prof|mr|mrs|ms)\.?$/i.test(part)) || "Faculty";
  const greeting = new Date().getHours() < 12 ? "Good morning" : new Date().getHours() < 17 ? "Good afternoon" : "Good evening";
  $("#today-label").textContent = new Intl.DateTimeFormat("en-IN", {
    timeZone:"Asia/Kolkata", weekday:"long", day:"numeric", month:"long"
  }).format(new Date()).toUpperCase();
  $("#dashboard-heading").firstChild.textContent = `${greeting}, `;
  $("#faculty-first-name").textContent = firstName;
  $("#teaching-summary").textContent = teachingPairs.length
    ? `${teachingPairs.length} teaching ${teachingPairs.length === 1 ? "assignment" : "assignments"} across ${summary.activeBatches} ${summary.activeBatches === 1 ? "batch" : "batches"}.`
    : "Your assigned batches and subjects will appear here.";
  $("#header-avatar").textContent = initials(profile.fullName);
  $("#sidebar-avatar").textContent = initials(profile.fullName);
  $("#sidebar-name").textContent = profile.fullName;
  renderDashboard();
  renderAssignments();
  renderExaminations();
  renderSchedule();
  renderBatches();
  renderNotices();
  renderProfile();
  renderMore();
  injectIcons();
}

function metric(label, value, attention = false) {
  return `<article class="metric-card ${attention ? "attention" : ""}"><span>${esc(label)}</span><strong>${esc(value)}</strong></article>`;
}

function renderDashboard() {
  const {summary, sessions, assignments, notices} = state.data;
  $("#dashboard-metrics").innerHTML = [
    metric("Classes today", String(summary.todayClasses)),
    metric("Open assignments", String(summary.openAssignments)),
    metric("Active batches", String(summary.activeBatches))
  ].join("");

  const next = sessions.find(item => item.status === "scheduled" && asDate(item.endsAt).getTime() >= Date.now());
  $("#next-class").innerHTML = next ? classCard(next) : empty("calendar", "No upcoming class", "Your next scheduled class will appear here.");
  $("#dashboard-assignments").innerHTML = assignments.slice(0, 3).map(item => `
    <div class="compact-row">
      <span class="row-icon">${icon("book")}</span>
      <span><strong>${esc(item.title)}</strong><small>${esc(item.batch)} · ${esc(item.subject)}</small></span>
      <time>${dateText(item.dueAt)}</time>
    </div>
  `).join("") || empty("book", "No assignments yet", "Create work for an assigned batch and subject.");
  $("#latest-notice").innerHTML = notices[0] ? noticeCard(notices[0]) : empty("notice", "No institute notices");
}

function classCard(item) {
  return `
    <article class="class-card">
      <div class="class-time"><strong>${timeText(item.startsAt)}</strong><span>${dateLong(item.startsAt)}</span></div>
      <div>
        <h3>${esc(item.subject)}</h3>
        <p>${esc(item.batch)} · ${esc(item.room)}</p>
        <footer>
          <span class="tag">${esc(item.subjectCode)}</span>
          <span class="tag">${item.studentCount} students</span>
        </footer>
      </div>
    </article>
  `;
}

function assignmentState(item) {
  if (item.status === "draft") return "draft";
  return asDate(item.dueAt).getTime() < Date.now() ? "overdue" : "active";
}

function renderAssignments() {
  const all = state.data.assignments;
  const active = all.filter(item => assignmentState(item) === "active").length;
  const drafts = all.filter(item => assignmentState(item) === "draft").length;
  const overdue = all.filter(item => assignmentState(item) === "overdue").length;
  $("#assignment-metrics").innerHTML = [
    metric("Active", String(active)),
    metric("Drafts", String(drafts), drafts > 0),
    metric("Past due", String(overdue))
  ].join("");
  const rows = all.filter(item => state.assignmentFilter === "all" || assignmentState(item) === state.assignmentFilter);
  $("#assignment-list").innerHTML = rows.length ? rows.map(item => {
    const itemState = assignmentState(item);
    const resourceUrl = safeExternalUrl(item.externalUrl);
    const publishing = state.publishingAssignment === item.id;
    return `
    <article class="assignment-card">
      <header>
        <span class="subject-mark">${esc(item.subject.slice(0, 3).toUpperCase())}</span>
        <span class="status-pill ${esc(itemState)}">${esc(titleCase(itemState))}</span>
      </header>
      <h3>${esc(item.title)}</h3>
      <p>${esc(item.instructions || "No additional instructions.")}</p>
      <div class="assignment-progress" aria-label="Assignment progress">
        <span>${item.progress?.notStarted ?? item.recipientCount} not started</span>
        <span>${item.progress?.viewed || 0} viewed</span>
        <span>${item.progress?.submitted || 0} submitted</span>
        <span>${item.progress?.completed || 0} reviewed</span>
      </div>
      <footer>
        <span><strong>${esc(item.batch)} · ${esc(item.subject)}</strong>Due ${dateLong(item.dueAt)} · ${item.recipientCount} students</span>
        <div class="assignment-actions">
          ${resourceUrl ? `<a href="${esc(resourceUrl)}" target="_blank" rel="noopener">Material ${icon("external")}</a>` : ""}
          <button type="button" data-edit-assignment="${esc(item.id)}">Edit</button>
          ${item.status === "draft" ? `<button type="button" data-publish-assignment="${esc(item.id)}" ${publishing ? "disabled" : ""}>${publishing ? "Publishing…" : "Publish"}</button>` : ""}
        </div>
      </footer>
    </article>
  `;
  }).join("") : empty("book", state.assignmentFilter === "all" ? "No assignments yet" : `No ${state.assignmentFilter === "overdue" ? "past due" : state.assignmentFilter} assignments`);
}

async function publishAssignment(assignmentId) {
  if (state.publishingAssignment) return;
  state.publishingAssignment = assignmentId;
  renderAssignments();
  try {
    await api(`/api/academics/assignments/${encodeURIComponent(assignmentId)}/publish`, {method:"POST"});
    await refreshPortal("Assignment published.");
  } catch (error) {
    toast(error.message);
  } finally {
    state.publishingAssignment = null;
    renderAssignments();
    injectIcons($("#assignments"));
  }
}

function examinationState(item) {
  if (item.status === "published" || item.status === "cancelled") return item.status;
  if (item.status === "marks_entry" || asDate(item.scheduledAt).getTime() <= Date.now()) return "action";
  return "upcoming";
}

function renderExaminations() {
  const all = state.data.examinations || [];
  const action = all.filter(item => examinationState(item) === "action");
  const upcoming = all.filter(item => examinationState(item) === "upcoming");
  const published = all.filter(item => item.status === "published");
  $("#examination-metrics").innerHTML = [
    metric("Needs action", String(action.length), action.length > 0),
    metric("Upcoming", String(upcoming.length)),
    metric("Published", String(published.length))
  ].join("");
  $("#sidebar-examination-badge").textContent = action.length;
  $("#sidebar-examination-badge").classList.toggle("hidden", !action.length);
  const rows = all.filter(item => state.examinationFilter === "all"
    || (state.examinationFilter === "published" ? item.status === "published" : examinationState(item) === state.examinationFilter));
  $("#examination-list").innerHTML = rows.length ? rows.map(item => {
    const itemState = examinationState(item);
    const progress = item.participantCount ? Math.round(Number(item.marksEntered || 0) / Number(item.participantCount) * 100) : 0;
    const resultCopy = item.status === "published"
      ? `${item.averageMarks == null ? "—" : item.averageMarks} average · ${item.highestMarks == null ? "—" : item.highestMarks} highest`
      : `${item.marksEntered}/${item.participantCount} results entered`;
    return `<article class="faculty-exam-card">
      <div class="faculty-exam-date"><strong>${dateText(item.scheduledAt).split(" ")[0]}</strong><small>${dateText(item.scheduledAt).split(" ")[1]}</small></div>
      <div class="faculty-exam-copy">
        <span class="status-pill ${esc(itemState)}">${esc(itemState === "action" ? "Marks due" : titleCase(itemState))}</span>
        <h3>${esc(item.name)}</h3>
        <p>${esc(item.batch)} · ${esc(item.subject)} · ${timeText(item.scheduledAt)} · ${item.durationMinutes} min</p>
        <div class="faculty-exam-progress"><span><i style="width:${progress}%"></i></span><small>${esc(resultCopy)}</small></div>
      </div>
      <div class="faculty-exam-actions">
        ${item.status !== "published" && item.status !== "cancelled" && !item.marksEntered ? `<button class="session-action secondary" type="button" data-edit-examination="${esc(item.id)}">Edit</button>` : ""}
        <button class="session-action ${itemState === "action" ? "" : "secondary"}" type="button" data-open-examination-results="${esc(item.id)}">${item.status === "published" ? "View results" : item.marksEntered ? "Continue marks" : "Enter marks"}</button>
      </div>
    </article>`;
  }).join("") : empty("exam", state.examinationFilter === "action" ? "No marks pending" : "No examinations in this view");
}

function renderSchedule() {
  const rows = state.data.sessions.filter(item => item.status === "scheduled");
  const dates = [...new Set(rows.map(item => dateKey(item.startsAt)))];
  const upcoming = rows.filter(item => asDate(item.startsAt).getTime() >= Date.now());
  $("#schedule-metrics").innerHTML = [
    metric("Upcoming classes", String(upcoming.length)),
    metric("Scheduled days", String(new Set(upcoming.map(item => dateKey(item.startsAt))).size)),
    metric("Assigned batches", String(new Set(rows.map(item => item.batchId)).size))
  ].join("");
  if (state.scheduleDate !== "all" && !dates.includes(state.scheduleDate)) state.scheduleDate = "all";
  $("#schedule-dates").innerHTML = [`<button type="button" class="${state.scheduleDate === "all" ? "active" : ""}" data-schedule-date="all" aria-pressed="${state.scheduleDate === "all"}">All classes</button>`].concat(dates.map(key => `
    <button type="button" class="${key === state.scheduleDate ? "active" : ""}" data-schedule-date="${key}" aria-pressed="${key === state.scheduleDate}">
      ${dateLong(`${key}T06:30:00.000Z`)}
    </button>
  `)).join("");
  const visible = state.scheduleDate === "all" ? rows : rows.filter(item => dateKey(item.startsAt) === state.scheduleDate);
  $("#schedule-list").innerHTML = visible.length ? visible.map(item => `
    <article class="timeline-card">
      <div class="timeline-time">${timeText(item.startsAt)}<br>${timeText(item.endsAt)}</div>
      <div>
        <h3>${esc(item.subject)}</h3>
        <p>${esc(item.batch)} · ${esc(item.program)}</p>
        <footer><span class="tag">${esc(item.room)}</span><span class="tag">${item.studentCount} students</span></footer>
      </div>
      <span class="timeline-state state-${esc(item.status)}">${esc(titleCase(item.status))}</span>
    </article>
  `).join("") : empty("calendar", rows.length ? "No classes on this day" : "Schedule not published");
}

function noticeCard(item) {
  return `
    <article class="notice-card">
      <h3>${esc(item.title)}</h3>
      <p>${esc(item.body)}</p>
      <time>${dateLong(item.publishedAt)}${item.batch ? ` · ${esc(item.batch)}` : ""}</time>
    </article>
  `;
}

function renderBatches() {
  const pairs = state.data.teachingPairs;
  const studentsByBatch = new Map();
  pairs.forEach(item => studentsByBatch.set(item.batchId, Number(item.studentCount || 0)));
  const totalStudents = [...studentsByBatch.values()].reduce((sum, count) => sum + count, 0);
  $("#batch-metrics").innerHTML = [
    metric("Teaching assignments", String(pairs.length)),
    metric("Unique batches", String(new Set(pairs.map(item => item.batchId)).size)),
    metric("Assigned students", String(totalStudents))
  ].join("");
  $("#batch-list").innerHTML = pairs.length ? pairs.map(item => {
    const matchingSessions = state.data.sessions.filter(session => session.status === "scheduled" && session.batchId === item.batchId && session.subjectId === item.subjectId);
    const next = matchingSessions.find(session => asDate(session.startsAt).getTime() >= Date.now());
    return `
      <article class="faculty-batch-card">
        <header><span class="subject-mark">${esc(item.subjectCode)}</span><span>${item.studentCount} students</span></header>
        <h2>${esc(item.batch)}</h2>
        <p>${esc(item.subject)} · ${esc(item.program)}</p>
        <dl><div><dt>Classes</dt><dd>${matchingSessions.length}</dd></div><div><dt>Next class</dt><dd>${next ? `${dateLong(next.startsAt)} · ${timeText(next.startsAt)}` : "Not scheduled"}</dd></div></dl>
        <button type="button" data-go="schedule">View timetable</button>
      </article>`;
  }).join("") : empty("users", "No assigned batches", "Ask the owner to assign a batch and subject.");
}

function renderNotices() {
  const notices = state.data.notices;
  const batchNotices = notices.filter(item => item.batch).length;
  $("#notice-metrics").innerHTML = [
    metric("Published", String(notices.length)),
    metric("Batch notices", String(batchNotices)),
    metric("Latest", notices[0] ? dateText(notices[0].publishedAt) : "None")
  ].join("");
  $("#notice-list").innerHTML = notices.length ? notices.map(noticeCard).join("") : empty("notice", "No notices published", "Faculty and batch announcements will appear here.");
}

function renderProfile() {
  const {profile, teachingPairs, summary} = state.data;
  $("#profile-card").innerHTML = `
    <span class="profile-avatar">${initials(profile.fullName)}</span>
    <span><strong>${esc(profile.fullName)}</strong><span>${esc(profile.mobile ? `+91 ${profile.mobile}` : "Mobile not assigned")}</span><span>Faculty account</span></span>
  `;
  const details = [
    ["Full name", profile.fullName],
    ["Portal login", profile.mobile ? `+91 ${profile.mobile}` : "Mobile not assigned"],
    ["Role", "Faculty"],
    ["Teaching assignments", teachingPairs.length],
    ["Active batches", summary.activeBatches],
    ["Assigned subjects", new Set(teachingPairs.map(item => item.subjectId)).size]
  ];
  $("#profile-details").innerHTML = details.map(([label, value]) => `<div><dt>${esc(label)}</dt><dd>${esc(value)}</dd></div>`).join("");
}

function renderMore() {
  const {profile, teachingPairs, notices} = state.data;
  $("#more-batch-copy").textContent = teachingPairs.length ? `${teachingPairs.length} teaching ${teachingPairs.length === 1 ? "assignment" : "assignments"}` : "No teaching assignments";
  $("#more-notice-copy").textContent = notices.length ? `${notices.length} published ${notices.length === 1 ? "notice" : "notices"}` : "No published notices";
  $("#more-profile-copy").textContent = profile.mobile ? `+91 ${profile.mobile}` : "Mobile not assigned";
}

function openModal(id, trigger) {
  state.lastFocus = trigger || document.activeElement;
  const modal = $("#" + id);
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  requestAnimationFrame(() => $("input,select,button", modal)?.focus());
}

function closeModal(id) {
  const modal = $("#" + id);
  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  if (id === "assignment-modal") state.editingAssignment = null;
  if (id === "examination-modal") state.editingExamination = null;
  state.lastFocus?.focus?.();
  state.lastFocus = null;
}

function openAssignmentModal(trigger, item = null) {
  const pairs = state.data.teachingPairs;
  if (!pairs.length) {
    toast("Ask the owner to assign you a batch and subject.");
    return;
  }
  if (item && !pairs.some(pair => pair.batchId === item.batchId && pair.subjectId === item.subjectId)) {
    toast("This teaching assignment is no longer active.");
    return;
  }
  const form = $("#assignment-form");
  form.reset();
  state.editingAssignment = item?.id || null;
  $("#assignment-pair").innerHTML = pairs.map(item => `
    <option value="${esc(item.batchId)}|${esc(item.subjectId)}">${esc(item.batch)} · ${esc(item.subject)}</option>
  `).join("");
  $("#assignment-modal-title").textContent = item ? "Edit assignment" : "New assignment";
  $("#assignment-submit").textContent = item ? "Save changes" : "Create assignment";
  $("#assignment-error").classList.add("hidden");
  $("#assignment-due").value = item ? localInputValue(asDate(item.dueAt)) : localInputValue();
  if (item) {
    form.elements.pair.value = `${item.batchId}|${item.subjectId}`;
    form.elements.title.value = item.title;
    form.elements.instructions.value = item.instructions || "";
    form.elements.status.value = item.status;
    form.elements.externalUrl.value = item.externalUrl || "";
  }
  openModal("assignment-modal", trigger);
}

async function saveAssignment(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const button = $("#assignment-submit");
  const data = new FormData(form);
  const [batchId, subjectId] = String(data.get("pair")).split("|");
  const assignmentId = state.editingAssignment;
  button.disabled = true;
  button.textContent = assignmentId ? "Saving…" : "Creating…";
  $("#assignment-error").classList.add("hidden");
  try {
    await api(assignmentId ? `/api/academics/assignments/${encodeURIComponent(assignmentId)}` : "/api/academics/assignments", {
      method:assignmentId ? "PATCH" : "POST",
      body:JSON.stringify({
        batchId,
        subjectId,
        title:String(data.get("title")).trim(),
        instructions:String(data.get("instructions")).trim(),
        dueAt:indiaInputToISOString(data.get("dueAt")),
        externalUrl:String(data.get("externalUrl")).trim(),
        status:String(data.get("status"))
      })
    });
    form.reset();
    closeModal("assignment-modal");
    await refreshPortal(assignmentId ? "Assignment updated." : "Assignment created.");
  } catch (error) {
    $("#assignment-error").textContent = error.message;
    $("#assignment-error").classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.textContent = state.editingAssignment ? "Save changes" : "Create assignment";
  }
}

function openExaminationModal(trigger, item = null) {
  const pairs = state.data.teachingPairs;
  if (!pairs.length) {
    toast("Ask the owner to assign you a batch and subject.");
    return;
  }
  if (item && !pairs.some(pair => pair.batchId === item.batchId && pair.subjectId === item.subjectId)) {
    toast("This teaching assignment is no longer active.");
    return;
  }
  state.editingExamination = item?.id || null;
  $("#examination-pair").innerHTML = pairs.map(item => `
    <option value="${esc(item.batchId)}|${esc(item.subjectId)}">${esc(item.batch)} · ${esc(item.subject)}</option>
  `).join("");
  const form = $("#examination-form");
  form.reset();
  $("#examination-modal-title").textContent = item ? "Edit examination" : "New examination";
  $("#examination-submit").textContent = item ? "Save changes" : "Create examination";
  $("#examination-date").value = item ? localInputValue(asDate(item.scheduledAt)) : localInputValue(new Date(Date.now() + 2 * 86400000));
  if (item) {
    form.elements.pair.value = `${item.batchId}|${item.subjectId}`;
    form.elements.name.value = item.name;
    form.elements.durationMinutes.value = item.durationMinutes;
    form.elements.maxMarks.value = item.maxMarks;
    form.elements.passMarks.value = item.passMarks;
    form.elements.instructions.value = item.instructions || "";
    form.elements.status.value = item.status === "draft" ? "draft" : "scheduled";
  }
  $("#examination-error").classList.add("hidden");
  openModal("examination-modal", trigger);
}

async function saveExamination(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  const [batchId, subjectId] = String(data.get("pair")).split("|");
  const examinationId = state.editingExamination;
  const maxMarks = Number(data.get("maxMarks"));
  const passMarks = Number(data.get("passMarks"));
  if (passMarks > maxMarks) {
    $("#examination-error").textContent = "Pass marks cannot exceed maximum marks.";
    $("#examination-error").classList.remove("hidden");
    return;
  }
  const button = $("#examination-submit");
  button.disabled = true;
  button.textContent = examinationId ? "Saving…" : "Creating…";
  $("#examination-error").classList.add("hidden");
  try {
    await api(examinationId ? `/api/examinations/${encodeURIComponent(examinationId)}` : "/api/examinations", {
      method:examinationId ? "PATCH" : "POST",
      body:JSON.stringify({
        batchId,
        subjectId,
        facultyId:state.data.profile.id,
        name:String(data.get("name")).trim(),
        scheduledAt:indiaInputToISOString(data.get("scheduledAt")),
        durationMinutes:Number(data.get("durationMinutes")),
        maxMarks,
        passMarks,
        instructions:String(data.get("instructions") || "").trim(),
        status:String(data.get("status") || "scheduled")
      })
    });
    form.reset();
    closeModal("examination-modal");
    await refreshPortal(examinationId ? "Examination updated." : "Examination scheduled.");
  } catch (error) {
    $("#examination-error").textContent = error.message;
    $("#examination-error").classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.textContent = state.editingExamination ? "Save changes" : "Create examination";
  }
}

async function openExaminationResults(examId, trigger) {
  const item = state.data.examinations.find(exam => exam.id === examId);
  if (!item) return;
  state.activeExam = null;
  $("#examination-results-title").textContent = item.name;
  $("#examination-results-meta").textContent = `${item.batch} · ${item.subject} · ${dateLong(item.scheduledAt)} at ${timeText(item.scheduledAt)}`;
  $("#examination-result-summary").innerHTML = "";
  $("#examination-roster-list").innerHTML = empty("users", "Loading examination roster");
  $("#examination-results-error").classList.add("hidden");
  openModal("examination-results-modal", trigger);
  try {
    state.activeExam = await api(`/api/examinations/${encodeURIComponent(examId)}`);
    renderExaminationResults();
  } catch (error) {
    $("#examination-roster-list").innerHTML = empty("exam", "Unable to load examination", error.message);
  }
}

function renderExaminationResults() {
  const exam = state.activeExam;
  if (!exam) return;
  const readOnly = exam.status === "published";
  const graded = exam.students.filter(item => item.resultStatus === "graded");
  const passed = graded.filter(item => Number(item.marksObtained) >= Number(exam.passMarks)).length;
  const average = graded.length ? graded.reduce((sum, item) => sum + Number(item.marksObtained || 0), 0) / graded.length : null;
  $("#examination-results-kicker").textContent = readOnly ? "PUBLISHED RESULTS" : "MARKS ENTRY";
  $("#examination-result-summary").innerHTML = `
    <div><span>Students</span><strong>${exam.participantCount}</strong></div>
    <div><span>Maximum</span><strong>${exam.maxMarks}</strong></div>
    <div><span>Entered</span><strong>${exam.marksEntered}/${exam.participantCount}</strong></div>
    <div><span>${readOnly ? "Pass rate" : "Pass marks"}</span><strong>${readOnly && graded.length ? `${Math.round(passed / graded.length * 100)}%` : exam.passMarks}</strong></div>
    ${readOnly && average != null ? `<p>Average ${average.toFixed(1)} · Highest ${exam.highestMarks ?? "—"}</p>` : ""}`;
  $("#save-examination-results").classList.toggle("hidden", readOnly);
  $("#publish-examination-results").classList.toggle("hidden", readOnly);
  $("#examination-roster-list").innerHTML = exam.students.length ? exam.students.map(item => {
    if (readOnly) {
      const value = item.resultStatus === "graded" ? `${item.marksObtained} / ${exam.maxMarks}` : titleCase(item.resultStatus);
      return `<div class="exam-result-row"><span class="exam-student"><strong>${esc(item.fullName)}</strong><small>${esc(item.admissionNumber)}</small></span><strong>${esc(value)}</strong><span class="status-pill ${esc(item.resultStatus)}">${esc(titleCase(item.resultStatus))}</span><small>${esc(item.remarks || "")}</small></div>`;
    }
    return `<div class="exam-entry-row" data-exam-student="${esc(item.studentId)}">
      <span class="exam-student"><strong>${esc(item.fullName)}</strong><small>${esc(item.admissionNumber)}</small></span>
      <label><span>Result</span><select data-result-status><option value="pending"${item.resultStatus === "pending" ? " selected" : ""}>Pending</option><option value="graded"${item.resultStatus === "graded" ? " selected" : ""}>Graded</option><option value="absent"${item.resultStatus === "absent" ? " selected" : ""}>Absent</option><option value="withheld"${item.resultStatus === "withheld" ? " selected" : ""}>Withheld</option></select></label>
      <label><span>Marks</span><input data-result-marks type="number" min="0" max="${esc(exam.maxMarks)}" step="0.01" value="${esc(item.marksObtained ?? "")}" ${item.resultStatus === "graded" ? "" : "disabled"}></label>
      <label><span>Remarks</span><input data-result-remarks type="text" maxlength="500" value="${esc(item.remarks || "")}" placeholder="Optional"></label>
    </div>`;
  }).join("") : empty("users", "No active students in this batch");
}

function examinationResultsPayload() {
  const exam = state.activeExam;
  return $$("[data-exam-student]", $("#examination-results-form")).map(row => {
    const resultStatus = $("[data-result-status]", row).value;
    const marksField = $("[data-result-marks]", row);
    const marksObtained = resultStatus === "graded" && marksField.value !== "" ? Number(marksField.value) : null;
    if (resultStatus === "graded" && marksObtained === null) throw new Error("Enter marks for every graded student.");
    if (marksObtained !== null && (marksObtained < 0 || marksObtained > Number(exam.maxMarks))) throw new Error(`Marks must be between 0 and ${exam.maxMarks}.`);
    return {
      studentId:row.dataset.examStudent,
      resultStatus,
      marksObtained,
      remarks:String($("[data-result-remarks]", row).value || "").trim()
    };
  });
}

async function saveExaminationResults(publish = false) {
  if (!state.activeExam) return;
  const buttons = [$("#save-examination-results"), $("#publish-examination-results")];
  const idle = buttons.map(button => button.textContent);
  buttons.forEach(button => { button.disabled = true; });
  (publish ? $("#publish-examination-results") : $("#save-examination-results")).textContent = publish ? "Publishing…" : "Saving…";
  $("#examination-results-error").classList.add("hidden");
  try {
    const entries = examinationResultsPayload();
    await api(`/api/examinations/${encodeURIComponent(state.activeExam.id)}/marks`, {
      method:"PUT",
      body:JSON.stringify({entries})
    });
    if (publish) {
      await api(`/api/examinations/${encodeURIComponent(state.activeExam.id)}/publish`, {method:"POST"});
      closeModal("examination-results-modal");
      await refreshPortal("Results published to students.");
    } else {
      state.activeExam = await api(`/api/examinations/${encodeURIComponent(state.activeExam.id)}`);
      renderExaminationResults();
      toast("Marks draft saved.");
    }
  } catch (error) {
    $("#examination-results-error").textContent = error.message;
    $("#examination-results-error").classList.remove("hidden");
  } finally {
    buttons.forEach((button, index) => {
      button.disabled = false;
      button.textContent = idle[index];
    });
  }
}

function togglePassword() {
  const field = $("#login-password");
  const button = $("#password-toggle");
  const glyph = $("[data-icon]", button);
  const show = field.type === "password";
  field.type = show ? "text" : "password";
  button.setAttribute("aria-label", show ? "Hide password" : "Show password");
  glyph.dataset.icon = show ? "eye-off" : "eye";
  injectIcons(button);
}

function bindEvents() {
  $("#login-form").addEventListener("submit", login);
  $("#login-mode-button").addEventListener("click", () => {
    setLoginMode(state.loginMode === "mobile" ? "email" : "mobile");
    $("#login-identity").value = "";
    $("#login-identity").focus();
  });
  $("#mobile-setup-form").addEventListener("submit", activateMobile);
  $("#faculty-password-change-form").addEventListener("submit", changeFacultyPassword);
  $("#password-toggle").addEventListener("click", togglePassword);
  $("#signout-button").addEventListener("click", logout);
  $("#sidebar-signout").addEventListener("click", logout);
  $("#profile-button").addEventListener("click", () => showView("profile"));
  $("#assignment-form").addEventListener("submit", saveAssignment);
  $("#examination-form").addEventListener("submit", saveExamination);
  $("#examination-results-form").addEventListener("submit", event => {
    event.preventDefault();
    saveExaminationResults(true);
  });
  $("#save-examination-results").addEventListener("click", () => saveExaminationResults(false));
  window.addEventListener("online", () => setConnectionState(true));
  window.addEventListener("offline", () => setConnectionState(false));
  $("#examination-results-form").addEventListener("change", event => {
    if (!event.target.matches("[data-result-status]")) return;
    const row = event.target.closest("[data-exam-student]");
    const marks = $("[data-result-marks]", row);
    const graded = event.target.value === "graded";
    marks.disabled = !graded;
    if (!graded) marks.value = "";
  });
  document.addEventListener("click", event => {
    const view = event.target.closest("[data-view]")?.dataset.view || event.target.closest("[data-go]")?.dataset.go;
    if (view) showView(view);

    const assignmentTrigger = event.target.closest("[data-open-assignment]");
    if (assignmentTrigger) openAssignmentModal(assignmentTrigger);
    const assignmentEdit = event.target.closest("[data-edit-assignment]");
    if (assignmentEdit) {
      const item = state.data.assignments.find(row => row.id === assignmentEdit.dataset.editAssignment);
      if (item) openAssignmentModal(assignmentEdit, item);
    }

    const examinationTrigger = event.target.closest("[data-open-examination]");
    if (examinationTrigger) openExaminationModal(examinationTrigger);
    const examinationEdit = event.target.closest("[data-edit-examination]");
    if (examinationEdit) {
      const item = (state.data.examinations || []).find(row => row.id === examinationEdit.dataset.editExamination);
      if (item) openExaminationModal(examinationEdit, item);
    }

    const examinationResultsTrigger = event.target.closest("[data-open-examination-results]");
    if (examinationResultsTrigger) openExaminationResults(examinationResultsTrigger.dataset.openExaminationResults, examinationResultsTrigger);

    const publishTrigger = event.target.closest("[data-publish-assignment]");
    if (publishTrigger) publishAssignment(publishTrigger.dataset.publishAssignment);

    const closeTrigger = event.target.closest("[data-close-modal]");
    if (closeTrigger) closeModal(closeTrigger.dataset.closeModal);

    const assignmentFilter = event.target.closest("[data-assignment-filter]")?.dataset.assignmentFilter;
    if (assignmentFilter) {
      state.assignmentFilter = assignmentFilter;
      $$("[data-assignment-filter]").forEach(node => {
        const active = node.dataset.assignmentFilter === assignmentFilter;
        node.classList.toggle("active", active);
        node.setAttribute("aria-pressed", String(active));
      });
      renderAssignments();
    }

    const examinationFilter = event.target.closest("[data-examination-filter]")?.dataset.examinationFilter;
    if (examinationFilter) {
      state.examinationFilter = examinationFilter;
      $$("[data-examination-filter]").forEach(node => {
        const active = node.dataset.examinationFilter === examinationFilter;
        node.classList.toggle("active", active);
        node.setAttribute("aria-pressed", String(active));
      });
      renderExaminations();
    }

    const scheduleDate = event.target.closest("[data-schedule-date]")?.dataset.scheduleDate;
    if (scheduleDate) {
      state.scheduleDate = scheduleDate;
      renderSchedule();
    }

    const backdrop = event.target.classList.contains("modal-backdrop") ? event.target : null;
    if (backdrop) closeModal(backdrop.id);
  });
  document.addEventListener("keydown", event => {
    const open = $$(".modal-backdrop:not(.hidden)").at(-1);
    if (!open) return;
    if (event.key === "Escape") {
      event.preventDefault();
      closeModal(open.id);
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = $$('button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])', open)
      .filter(node => !node.closest(".hidden") && node.offsetParent !== null);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  window.addEventListener("popstate", () => {
    const view = location.hash.slice(1);
    if (state.data && PORTAL_VIEWS.has(view)) showView(view, false);
  });
}

initialize();
