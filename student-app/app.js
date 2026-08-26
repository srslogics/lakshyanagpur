"use strict";

const icons = {
  arrow: '<path d="M5 12h14m-6-6 6 6-6 6"/>',
  "arrow-left": '<path d="m15 18-6-6 6-6M9 12h10"/>',
  home: '<path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1v-9Z"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4m8-4v4M3 10h18"/>',
  book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
  exam: '<path d="M7 3h10a2 2 0 0 1 2 2v16H5V5a2 2 0 0 1 2-2Z"/><path d="M9 7h6M9 11h6m-6 4h3"/><path d="m14 16 1.5 1.5L19 14"/>',
  check: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="m8 14 2.5 2.5L16 11"/>',
  more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  spark: '<path d="m12 3 1.4 4.1 4.1 1.4-4.1 1.4L12 14l-1.4-4.1-4.1-1.4 4.1-1.4L12 3Z"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  notice: '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  logout: '<path d="m10 17 5-5-5-5m5 5H3m12-9h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  "chevron-right": '<path d="m9 18 6-6-6-6"/>',
  external: '<path d="M14 4h6v6m0-6-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/>',
  eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  "eye-off": '<path d="m3 3 18 18M10.6 5.2A11.4 11.4 0 0 1 12 5c6.5 0 10 7 10 7a16 16 0 0 1-2.1 3.2M6.6 6.6C3.6 8.6 2 12 2 12s3.5 7 10 7a10.7 10.7 0 0 0 4.1-.8M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
};

const views = new Set(["home", "schedule", "assignments", "examinations", "attendance", "messages", "notices", "profile", "more"]);
const overflowViews = new Set(["examinations", "messages", "notices", "profile", "more"]);
const CONSENT_VERSION = "student-parent-v1-2026-08-15";
const CONSENT_STORAGE_PREFIX = "lakshya_student_consent_";
const UPCOMING_CLASS_LIMIT = 7;
const RECENT_ATTENDANCE_LIMIT = 7;
const PORTAL_LIST_LIMIT = 8;
const titles = {
  home: "Home",
  schedule: "Schedule",
  assignments: "Assignments",
  examinations: "Examinations",
  attendance: "Attendance",
  messages: "Messages",
  notices: "Notices",
  profile: "Profile",
  more: "More",
};

const hashView = () => (views.has(location.hash.slice(1)) ? location.hash.slice(1) : "home");
const state = {
  token: localStorage.getItem("lakshya_student_token"),
  identity: (() => { try { return JSON.parse(localStorage.getItem("lakshya_student_user") || "null"); } catch { return null; } })(),
  data: null,
  communication: null,
  view: hashView(),
  assignmentFilter: "open",
  examinationFilter: "upcoming",
  scheduleDate: "all",
  savingAssignment: null,
  online: navigator.onLine,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const consentStorageKey = (mobile = "") => `${CONSENT_STORAGE_PREFIX}${String(mobile).replace(/\D/g, "").slice(-10)}`;

function consentRemembered(mobile = "") {
  const key = consentStorageKey(mobile);
  if (key === CONSENT_STORAGE_PREFIX) return false;
  try { return localStorage.getItem(key) === CONSENT_VERSION; } catch { return false; }
}

function syncConsentVisibility() {
  const section = $("#login-consent");
  const checkbox = $("#login-consent-checkbox");
  if (!section || !checkbox) return;
  const remembered = consentRemembered($("#login-mobile")?.value);
  section.classList.toggle("hidden", remembered);
  checkbox.required = !remembered;
  if (remembered) checkbox.checked = false;
}

function rememberConsent(mobile) {
  const key = consentStorageKey(mobile);
  if (key === CONSENT_STORAGE_PREFIX) return;
  try { localStorage.setItem(key, CONSENT_VERSION); } catch {}
}

function forgetConsent(mobile) {
  const key = consentStorageKey(mobile);
  if (key === CONSENT_STORAGE_PREFIX) return;
  try { localStorage.removeItem(key); } catch {}
}
const icon = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.spark}</svg>`;
const esc = (value = "") => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  "'": "&#39;",
  '"': "&quot;",
})[character]);
const initials = (name) => String(name || "LS")
  .split(/\s+/)
  .filter(Boolean)
  .slice(0, 2)
  .map((part) => part[0])
  .join("")
  .toUpperCase();
const asInstant = (value) => {
  if (value instanceof Date) return value;
  const text = String(value || "");
  return new Date(/[zZ]$|[+-]\d{2}:?\d{2}$/.test(text) || /^\d{4}-\d{2}-\d{2}$/.test(text) ? text : `${text}Z`);
};
const validDate = (value) => value && !Number.isNaN(asInstant(value).getTime());
const indiaDateParts = (value) => {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit",
  }).formatToParts(asInstant(value));
  const get = type => parts.find(part => part.type === type)?.value || "";
  return { year: get("year"), month: get("month"), day: get("day") };
};
const dateKey = (value) => {
  if (!validDate(value)) return "";
  const { year, month, day } = indiaDateParts(value);
  return `${year}-${month}-${day}`;
};
const dateText = (value, fallback = "Date pending") => validDate(value)
  ? new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", day: "numeric", month: "short", year: "numeric" }).format(asInstant(value))
  : fallback;
const dateLong = (value, fallback = "Date pending") => validDate(value)
  ? new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", weekday: "short", day: "numeric", month: "short" }).format(asInstant(value))
  : fallback;
const timeText = (value) => validDate(value)
  ? new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit" }).format(asInstant(value))
  : "Time pending";
const titleCase = (value) => String(value || "Not recorded").replace(/[_-]+/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
const displayValue = (value) => (value === null || value === undefined || String(value).trim() === "" ? "Not recorded" : String(value));
const safeExternalUrl = (value) => {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
};

function injectIcons(root = document) {
  $$("[data-icon]", root).forEach((node) => {
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
  const method = String(options.method || "GET").toUpperCase();
  const attempts = method === "GET" ? 2 : 1;
  let lastError;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(path, { cache: "no-store", ...options, signal: controller.signal });
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
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await resilientFetch(path, { ...options, headers });
  let body = {};
  try {
    body = await response.json();
  } catch {
    body = {};
  }
  if (response.status === 401) {
    clearSession();
    showLogin("Your session expired. Sign in again.");
  }
  if (!response.ok) {
    const detail = body?.detail;
    const error = new Error(typeof detail === "string" ? detail : detail?.message || body?.error?.message || (response.status >= 500 ? "The service is temporarily unavailable. Try again." : "Unable to complete this request."));
    error.status = response.status;
    error.transient = response.status >= 500;
    throw error;
  }
  return body;
}

async function downloadAssignmentPdf(assignmentId, fallbackName, button) {
  button.disabled = true;
  const idle = button.textContent;
  button.textContent = "Downloading…";
  try {
    const response = await resilientFetch(
      `/api/portal/assignments/${encodeURIComponent(assignmentId)}/material`,
      {headers:{Authorization:`Bearer ${state.token}`}}
    );
    if (!response.ok) {
      let body = {};
      try { body = await response.json(); } catch {}
      throw new Error(body?.detail || "This PDF is no longer available.");
    }
    const disposition = response.headers.get("content-disposition") || "";
    const encoded = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
    const filename = encoded ? decodeURIComponent(encoded) : fallbackName;
    const objectUrl = URL.createObjectURL(await response.blob());
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = filename || "assignment.pdf";
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
    const assignment = state.data.assignments.find(item => item.id === assignmentId);
    if (assignment && assignment.status === "published") assignment.status = "viewed";
    toast("PDF saved to your device.");
  } catch (error) {
    toast(error.message);
  } finally {
    button.disabled = false;
    button.textContent = idle;
  }
}

function clearSession() {
  state.token = null;
  state.identity = null;
  state.data = null;
  state.communication = null;
  localStorage.removeItem("lakshya_student_token");
  localStorage.removeItem("lakshya_student_user");
}

function showLogin(message = "") {
  $("#boot-screen").classList.add("hidden");
  $("#password-change-screen").classList.add("hidden");
  $("#student-shell").classList.add("hidden");
  $("#login-screen").classList.remove("hidden");
  $("#login-password").value = "";
  $("[name=consentAccepted]", $("#login-form")).checked = false;
  syncConsentVisibility();
  resetPasswordVisibility($("#login-screen"));
  $("#login-error").textContent = message;
  $("#login-error").classList.toggle("hidden", !message);
  requestAnimationFrame(() => $("#login-mobile").focus());
}

function loginErrorMessage(error) {
  if (error.status === 401) {
    return "Mobile number or password is incorrect. Re-enter your password and try again.";
  }
  return error.message;
}

function clearLoginError() {
  $("#login-error").textContent = "";
  $("#login-error").classList.add("hidden");
}

function showPasswordChange(identity) {
  state.identity = identity;
  $("#boot-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#student-shell").classList.add("hidden");
  $("#password-change-screen").classList.remove("hidden");
  $("#password-change-form").reset();
  resetPasswordVisibility($("#password-change-screen"));
  $("#password-change-error").classList.add("hidden");
  requestAnimationFrame(() => $("[name=currentPassword]", $("#password-change-form")).focus());
}

function toast(message) {
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  $("#toast-region").append(node);
  setTimeout(() => node.remove(), 2800);
}

function showStartupError(error) {
  $("#login-screen").classList.add("hidden");
  $("#password-change-screen").classList.add("hidden");
  $("#student-shell").classList.add("hidden");
  const boot = $("#boot-screen");
  boot.classList.remove("hidden");
  let panel = $("#startup-error");
  if (!panel) {
    panel = document.createElement("div");
    panel.id = "startup-error";
    panel.className = "startup-error";
    panel.innerHTML = '<strong>Student portal is temporarily unavailable</strong><p></p><button type="button">Retry</button>';
    boot.append(panel);
    $("button", panel).addEventListener("click", () => location.reload());
  }
  $("p", panel).textContent = error.message;
}

async function initialize() {
  injectIcons();
  bindEvents();
  setConnectionState(navigator.onLine);
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  if (!state.token) {
    showLogin();
    return;
  }
  try {
    const identity = state.identity || await api("/api/auth/me");
    if (!["student", "parent_student"].includes(identity.role)) {
      const error = new Error("This login is not assigned to the Student portal.");
      error.status = 403;
      throw error;
    }
    state.identity = identity;
    localStorage.setItem("lakshya_student_user", JSON.stringify(identity));
    if (identity.mustChangePassword) {
      showPasswordChange(identity);
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
  const button = $("#login-button");
  const idle = button.innerHTML;
  button.disabled = true;
  button.textContent = "Signing in…";
  $("#login-error").classList.add("hidden");
  try {
    const form = new FormData(event.currentTarget);
    const result = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        mobile: String(form.get("mobile")).trim(),
        password: String(form.get("password")),
        consentAccepted: form.get("consentAccepted") === "on",
        consentVersion: CONSENT_VERSION,
        portal: "student",
      }),
    });
    state.token = result.access_token;
    const account = result.user;
    if (!["student", "parent_student"].includes(account.role)) {
      throw new Error("This login is not assigned to the Student portal.");
    }
    rememberConsent(form.get("mobile"));
    state.identity = account;
    localStorage.setItem("lakshya_student_token", state.token);
    localStorage.setItem("lakshya_student_user", JSON.stringify(account));
    if (account.mustChangePassword) {
      showPasswordChange(account);
      return;
    }
    await loadPortal();
  } catch (error) {
    if (error.status === 400 && /Consent and Terms/i.test(error.message)) {
      forgetConsent($("#login-mobile").value);
    }
    if (state.token && error.status !== 401 && (error.transient || error.status === 0)) {
      showStartupError(error);
    } else {
      clearSession();
      showLogin(loginErrorMessage(error));
    }
  } finally {
    button.disabled = false;
    button.innerHTML = idle;
    injectIcons(button);
  }
}

async function changePassword(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  const currentPassword = String(data.get("currentPassword"));
  const newPassword = String(data.get("newPassword"));
  const confirmPassword = String(data.get("confirmPassword"));
  const error = $("#password-change-error");
  if (newPassword !== confirmPassword) {
    error.textContent = "The new passwords do not match.";
    error.classList.remove("hidden");
    return;
  }
  if (newPassword === currentPassword) {
    error.textContent = "Choose a personal password different from the temporary password.";
    error.classList.remove("hidden");
    return;
  }
  const button = $("#password-change-button");
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
    showLogin("Personal password saved. Sign in again.");
    $("#login-mobile").value = mobile;
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
  state.data = await api("/api/portal/bootstrap");
  renderAll();
  $("#boot-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#password-change-screen").classList.add("hidden");
  $("#student-shell").classList.remove("hidden");
  showView(hashView(), false);
  window.LakshyaPush?.sync({token:state.token, portal:"student"});
}

async function logout() {
  const token = state.token;
  if (token) {
    await window.LakshyaPush?.unsubscribe({token});
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      // Local credentials still need to be cleared if the server cannot be reached.
    }
  }
  clearSession();
  history.replaceState(null, "", location.pathname + location.search);
  showLogin();
  toast("Signed out securely.");
}

function showView(view, updateHash = true) {
  if (!views.has(view)) view = "home";
  state.view = view;
  $$(".portal-view").forEach((node) => node.classList.toggle("active", node.id === view));
  $$(".sidebar-nav [data-view]").forEach((node) => {
    const active = node.dataset.view === view;
    node.classList.toggle("active", active);
    active ? node.setAttribute("aria-current", "page") : node.removeAttribute("aria-current");
  });
  const mobileView = overflowViews.has(view) ? "more" : view;
  $$(".bottom-nav [data-view]").forEach((node) => {
    const active = node.dataset.view === mobileView;
    node.classList.toggle("active", active);
    active ? node.setAttribute("aria-current", "page") : node.removeAttribute("aria-current");
  });
  $("#header-title").textContent = titles[view];
  if (updateHash && location.hash !== `#${view}`) history.pushState(null, "", `#${view}`);
  $("#student-main").focus({ preventScroll: true });
  window.scrollTo({
    top: 0,
    behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
  });
  if (view === "messages") loadCommunication();
}

function empty(name, title, copy = "") {
  return `<div class="empty"><div><span>${icon(name)}</span><strong>${esc(title)}</strong>${copy ? `<p>${esc(copy)}</p>` : ""}</div></div>`;
}

function summaryCard(label, value, featured = false, view = "") {
  const attributes = view ? ` role="button" tabindex="0" data-go="${view}" aria-label="Open ${esc(label)}"` : "";
  return `<article class="summary-card ${featured ? "featured" : ""} ${view ? "interactive" : ""}"${attributes}><span>${esc(label)}</span><strong>${esc(value)}</strong></article>`;
}

function moduleMetric(label, value, attention = false) {
  return `<article class="module-metric ${attention ? "attention" : ""}"><span>${esc(label)}</span><strong>${esc(value)}</strong></article>`;
}

function assignmentState(item) {
  if (item.status === "completed") return "completed";
  return validDate(item.dueAt) && asInstant(item.dueAt).getTime() < Date.now() ? "overdue" : "open";
}

function classCard(item) {
  return `<article class="class-card">
    <div class="class-time">${timeText(item.startsAt)}</div>
    <div>
      <strong>${esc(item.subject)}</strong>
      <small>${dateLong(item.startsAt)}</small>
      <div class="class-meta">
        <span class="tag">${esc(item.faculty)}</span>
        <span class="tag">${esc(item.room)}</span>
      </div>
    </div>
  </article>`;
}

function renderAll() {
  const { profile } = state.data;
  const meta = [profile.admissionNumber, profile.program].filter(Boolean).join(" · ");
  $("#today-label").textContent = new Intl.DateTimeFormat("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date()).toUpperCase();
  $("#student-first-name").textContent = profile.fullName.split(/\s+/)[0];
  $("#student-program").textContent = [profile.program, profile.batch].filter(Boolean).join(" · ") || "Academic details pending";
  $("#header-avatar").textContent = initials(profile.fullName);
  $("#sidebar-avatar").textContent = initials(profile.fullName);
  $("#sidebar-name").textContent = profile.fullName;
  $("#sidebar-meta").textContent = meta || "Student account";
  renderHome();
  renderSchedule();
  renderAssignments();
  renderExaminations();
  renderAttendance();
  renderNotices();
  renderProfile();
  renderMore();
  injectIcons();
}

function renderHome() {
  const { summary, schedule, assignments, examinations, notices } = state.data;
  const openAssignments = assignments.filter((item) => assignmentState(item) !== "completed");
  $("#summary-strip").innerHTML = [
    summaryCard("Upcoming classes", String(summary.upcomingClasses), false, "schedule"),
    summaryCard("Open assignments", String(openAssignments.length), openAssignments.length > 0, "assignments"),
    summaryCard("Upcoming exams", String(summary.upcomingExams ?? examinations.filter((item) => item.status === "scheduled").length), false, "examinations"),
  ].join("");
  const next = schedule.find((item) => validDate(item.startsAt) && asInstant(item.startsAt) >= new Date());
  $("#next-class").innerHTML = next
    ? classCard(next)
    : empty("calendar", "Timetable not published", "Your next class will appear when the institute publishes the timetable.");
  $("#home-assignments").innerHTML = openAssignments.slice(0, 3).map((item) => {
    const itemState = assignmentState(item);
    return `<button class="compact-row compact-button" type="button" data-go="assignments">
      <span class="compact-icon">${icon("book")}</span>
      <span><strong>${esc(item.title)}</strong><small>${esc(item.subject)}</small></span>
      <time class="${itemState === "overdue" ? "overdue-text" : ""}">${itemState === "overdue" ? "Overdue" : dateText(item.dueAt)}</time>
    </button>`;
  }).join("") || empty("book", "No open assignments", "Published work will appear here after it is assigned.");
  const now = Date.now();
  const examRows = [...(examinations || [])];
  const upcomingExams = examRows
    .filter((item) => item.status === "scheduled" && validDate(item.scheduledAt) && asInstant(item.scheduledAt).getTime() >= now)
    .sort((a, b) => asInstant(a.scheduledAt) - asInstant(b.scheduledAt));
  const publishedResults = examRows
    .filter((item) => item.status === "published")
    .sort((a, b) => asInstant(b.publishedAt || b.scheduledAt) - asInstant(a.publishedAt || a.scheduledAt));
  const awaitingResult = examRows
    .filter((item) => item.status === "marks_entry" || (item.status === "scheduled" && validDate(item.scheduledAt) && asInstant(item.scheduledAt).getTime() < now))
    .sort((a, b) => asInstant(b.scheduledAt) - asInstant(a.scheduledAt))[0];
  const dashboardExams = [];
  const nextExam = upcomingExams[0];
  if (nextExam) {
    dashboardExams.push(`<button class="home-exam-card next" type="button" data-go="examinations">
      <span class="home-exam-icon">${icon("exam")}</span>
      <span class="home-exam-content">
        <span class="home-exam-head"><span class="home-exam-kicker">Next examination</span><span class="exam-state neutral">Scheduled</span></span>
        <strong>${esc(nextExam.name)}</strong>
        <small>${esc(nextExam.subject)} · ${esc(nextExam.faculty)}</small>
        <span class="home-exam-details"><span><em>Date</em><b>${dateText(nextExam.scheduledAt)}</b></span><span><em>Time</em><b>${timeText(nextExam.scheduledAt)}</b></span><span><em>Duration</em><b>${esc(nextExam.durationMinutes)} min</b></span></span>
      </span>
    </button>`);
  }
  const latestResult = publishedResults[0];
  if (latestResult) {
    const graded = latestResult.resultStatus === "graded" && latestResult.marksObtained !== null;
    const resultLabel = graded ? `${latestResult.marksObtained} / ${latestResult.maxMarks}` : titleCase(latestResult.resultStatus);
    dashboardExams.push(`<button class="home-exam-card result" type="button" data-go="examinations">
      <span class="home-exam-icon">${icon("check")}</span>
      <span class="home-exam-content">
        <span class="home-exam-head"><span class="home-exam-kicker">Latest result</span><span class="exam-state ${graded ? (latestResult.qualified ? "qualified" : "review") : "neutral"}">${esc(resultLabel)}</span></span>
        <strong>${esc(latestResult.name)}</strong>
        <small>${esc(latestResult.subject)} · ${dateText(latestResult.scheduledAt)}</small>
        <span class="home-result-summary"><b>${graded ? `${esc(latestResult.percentage)}%` : "Published"}</b><em>${graded ? (latestResult.qualified ? "Qualified" : "Below pass mark") : "Open examinations for details"}</em></span>
      </span>
    </button>`);
  } else if (awaitingResult) {
    dashboardExams.push(`<button class="home-exam-card pending" type="button" data-go="examinations">
      <span class="home-exam-icon">${icon("clock")}</span>
      <span class="home-exam-content">
        <span class="home-exam-head"><span class="home-exam-kicker">Result pending</span><span class="exam-state neutral">Evaluation underway</span></span>
        <strong>${esc(awaitingResult.name)}</strong>
        <small>${esc(awaitingResult.subject)} · ${dateText(awaitingResult.scheduledAt)}</small>
        <span class="home-result-summary"><b>${esc(awaitingResult.maxMarks)} marks</b><em>The result will appear here after publication.</em></span>
      </span>
    </button>`);
  }
  $("#home-examinations").innerHTML = dashboardExams.join("") || empty("exam", "No examinations published", "Upcoming examinations and released results will appear here.");
  const notice = notices[0];
  $("#latest-notice").innerHTML = notice
    ? `<article class="notice-preview"><strong>${esc(notice.title)}</strong><span>${esc(notice.body)}</span><time>${dateLong(notice.publishedAt)}</time></article>`
    : empty("notice", "No institute notices", "Published announcements will appear here.");
}

function renderSchedule() {
  const rows = [...state.data.schedule].sort((a, b) => asInstant(a.startsAt) - asInstant(b.startsAt));
  const upcoming = rows
    .filter((item) => validDate(item.startsAt) && asInstant(item.startsAt) >= new Date())
    .slice(0, UPCOMING_CLASS_LIMIT);
  const dateKeys = [...new Set(upcoming.map((item) => dateKey(item.startsAt)).filter(Boolean))];
  const subjects = new Set((state.data.profile.subjects || []).filter(Boolean));
  $("#schedule-metrics").innerHTML = [
    moduleMetric("Upcoming classes", String(upcoming.length)),
    moduleMetric("Scheduled days", String(dateKeys.length)),
    moduleMetric("Subjects", String(subjects.size)),
  ].join("");
  if (state.scheduleDate !== "all" && !dateKeys.includes(state.scheduleDate)) state.scheduleDate = "all";
  $("#schedule-dates").innerHTML = [
    `<button type="button" class="${state.scheduleDate === "all" ? "active" : ""}" data-schedule-date="all" aria-pressed="${state.scheduleDate === "all"}">All upcoming</button>`,
    ...dateKeys.map((key) => `<button type="button" class="${key === state.scheduleDate ? "active" : ""}" data-schedule-date="${key}" aria-pressed="${key === state.scheduleDate}">${dateLong(`${key}T12:00:00`)}</button>`),
  ].join("");
  const visible = state.scheduleDate === "all" ? upcoming : upcoming.filter((item) => dateKey(item.startsAt) === state.scheduleDate);
  $("#schedule-list-heading").textContent = state.scheduleDate === "all" ? "Upcoming timetable" : dateLong(`${state.scheduleDate}T12:00:00`);
  $("#schedule-list").innerHTML = visible.length
    ? visible.map((item) => `<article class="timeline-card">
      <div class="timeline-time">${timeText(item.startsAt)}<br>${timeText(item.endsAt)}</div>
      <div>
        <h3>${esc(item.subject)}</h3>
        <p>${esc(item.faculty)}</p>
        <footer><span class="tag">${esc(item.room)}</span><span class="tag">${esc(item.subjectCode)}</span></footer>
      </div>
    </article>`).join("")
    : empty("calendar", rows.length ? "No upcoming classes" : "Schedule not published", rows.length ? "There are no classes remaining in the published timetable." : "Your classes will appear when the academic team publishes them.");
}

function renderAssignments() {
  const all = state.data.assignments;
  const counts = {
    open: all.filter((item) => assignmentState(item) === "open").length,
    overdue: all.filter((item) => assignmentState(item) === "overdue").length,
    completed: all.filter((item) => assignmentState(item) === "completed").length,
  };
  const pending = counts.open + counts.overdue;
  $("#assignment-metrics").innerHTML = [
    moduleMetric("Open", String(counts.open)),
    moduleMetric("Overdue", String(counts.overdue), counts.overdue > 0),
    moduleMetric("Completed", String(counts.completed)),
  ].join("");
  ["#assignment-badge", "#sidebar-assignment-badge"].forEach((selector) => {
    $(selector).textContent = pending;
    $(selector).classList.toggle("hidden", !pending);
  });
  const rows = (state.assignmentFilter === "all"
    ? all
    : all.filter((item) => assignmentState(item) === state.assignmentFilter)).slice(0, PORTAL_LIST_LIMIT);
  $("#assignment-list").innerHTML = rows.length
    ? rows.map((item) => {
      const itemState = assignmentState(item);
      const saving = state.savingAssignment === item.id;
      const nextStatus = itemState === "completed" ? "published" : "completed";
      const resourceUrl = safeExternalUrl(item.externalUrl);
      return `<article class="assignment-card assignment-${itemState}">
        <header>
          <span class="subject-mark">${esc((item.subject || "SUB").slice(0, 3).toUpperCase())}</span>
          <span class="assignment-status status-${itemState}">${titleCase(itemState)}</span>
        </header>
        <h3>${esc(item.title)}</h3>
        <p>${esc(item.instructions || "Instructions have not been added.")}</p>
        <div class="assignment-meta">
          <span>${esc(item.subject)}</span>
          <span>Due ${dateText(item.dueAt)}</span>
          ${item.material?.available ? `<span>PDF available until ${dateText(item.material.expiresAt)}, ${timeText(item.material.expiresAt)}</span>` : ""}
        </div>
        <footer>
          <div class="assignment-resources">
            ${item.material?.available ? `<button class="assignment-download" type="button" data-download-assignment="${esc(item.id)}" data-material-name="${esc(item.material.filename)}">Save PDF</button>` : ""}
            ${resourceUrl ? `<a href="${esc(resourceUrl)}" target="_blank" rel="noopener">Open link ${icon("external")}</a>` : ""}
            ${!item.material?.available && !resourceUrl ? "<span>No attached material</span>" : ""}
          </div>
          <button class="assignment-action ${itemState === "completed" ? "secondary" : ""}" type="button" data-assignment-id="${esc(item.id)}" data-assignment-status="${nextStatus}" ${saving ? "disabled" : ""}>${saving ? "Saving…" : itemState === "completed" ? "Reopen" : "Mark complete"}</button>
        </footer>
      </article>`;
    }).join("")
    : empty("book", `No ${state.assignmentFilter === "all" ? "" : `${state.assignmentFilter} `}assignments`.trim(), state.assignmentFilter === "open" ? "You have no published work currently due." : "Assignments matching this filter will appear here.");
}

async function updateAssignmentStatus(assignmentId, status) {
  if (state.savingAssignment) return;
  state.savingAssignment = assignmentId;
  renderAssignments();
  try {
    const result = await api(`/api/portal/assignments/${encodeURIComponent(assignmentId)}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    const item = state.data.assignments.find((assignment) => assignment.id === assignmentId);
    if (item) item.status = result.status;
    state.data.summary.openAssignments = state.data.assignments.filter((assignment) => assignmentState(assignment) !== "completed").length;
    toast(status === "completed" ? "Assignment marked complete." : "Assignment reopened.");
    renderHome();
  } catch (error) {
    toast(error.message);
  } finally {
    state.savingAssignment = null;
    renderAssignments();
    injectIcons();
  }
}

function renderExaminations() {
  const all = [...(state.data.examinations || [])].sort((a, b) => asInstant(b.scheduledAt) - asInstant(a.scheduledAt));
  const now = Date.now();
  const upcoming = all.filter((item) => item.status === "scheduled" && asInstant(item.scheduledAt).getTime() >= now);
  const awaiting = all.filter((item) => item.status === "marks_entry" || (item.status === "scheduled" && asInstant(item.scheduledAt).getTime() < now));
  const results = all.filter((item) => item.status === "published");
  $("#examination-metrics").innerHTML = [
    moduleMetric("Upcoming", String(upcoming.length)),
    moduleMetric("Awaiting results", String(awaiting.length)),
    moduleMetric("Published", String(results.length)),
  ].join("");
  $("#sidebar-examination-badge").textContent = upcoming.length;
  $("#sidebar-examination-badge").classList.toggle("hidden", !upcoming.length);
  let rows = all;
  if (state.examinationFilter === "upcoming") rows = [...upcoming, ...awaiting];
  if (state.examinationFilter === "results") rows = results;
  rows = rows.slice(0, PORTAL_LIST_LIMIT);
  $("#examination-list").innerHTML = rows.length
    ? rows.map((item) => {
      const published = item.status === "published";
      const graded = published && item.resultStatus === "graded";
      const resultLabel = graded
        ? `${item.marksObtained} / ${item.maxMarks}`
        : published
          ? titleCase(item.resultStatus)
          : item.status === "marks_entry" || asInstant(item.scheduledAt).getTime() < now
            ? "Evaluation underway"
            : "Scheduled";
      const resultClass = graded ? (item.qualified ? "qualified" : "review") : item.resultStatus === "absent" ? "review" : "neutral";
      return `<article class="examination-card ${published ? "has-result" : ""}">
        <header><span class="subject-mark">${esc((item.subjectCode || item.subject || "EX").slice(0, 3).toUpperCase())}</span><span class="exam-state ${resultClass}">${esc(resultLabel)}</span></header>
        <h3>${esc(item.name)}</h3>
        <p>${esc(item.instructions || "No additional instructions.")}</p>
        <div class="exam-detail-grid">
          <div><span>Date</span><strong>${dateText(item.scheduledAt)}</strong></div>
          <div><span>Time</span><strong>${timeText(item.scheduledAt)}</strong></div>
          <div><span>Duration</span><strong>${esc(item.durationMinutes)} min</strong></div>
          <div><span>Faculty</span><strong>${esc(item.faculty)}</strong></div>
        </div>
        ${graded ? `<footer><span>${esc(item.subject)}</span><strong>${esc(item.percentage)}% · ${item.qualified ? "Qualified" : "Below pass mark"}</strong></footer>` : published && item.remarks ? `<footer><span>Remark</span><strong>${esc(item.remarks)}</strong></footer>` : ""}
      </article>`;
    }).join("")
    : empty("exam", state.examinationFilter === "results" ? "No published results" : "No examinations scheduled", state.examinationFilter === "results" ? "Released results will appear here." : "Your examination schedule will appear here after it is published.");
}

function renderAttendance() {
  const rows = state.data.attendance;
  const recentRows = [...rows]
    .sort((a, b) => asInstant(b.startsAt).getTime() - asInstant(a.startsAt).getTime())
    .slice(0, RECENT_ATTENDANCE_LIMIT);
  const confirmed = state.data.attendanceSummary;
  const presentStatuses = new Set(["present", "late", "excused"]);
  const present = confirmed?.presentDays ?? rows.filter((item) => presentStatuses.has(item.status)).length;
  const late = rows.filter((item) => item.status === "late").length;
  const absent = confirmed?.absentDays ?? rows.filter((item) => item.status === "absent").length;
  const unclassified = rows.filter((item) => item.status === "unclassified").length;
  const classified = rows.length - unclassified;
  const rate = confirmed?.attendanceRate ?? (classified ? Math.round((present / classified) * 1000) / 10 : null);
  $("#attendance-hero").innerHTML = `
    <div class="attendance-ring" style="--attendance:${rate ?? 0}%"><div><strong>${rate == null ? "—" : `${rate}%`}</strong><small>Overall</small></div></div>
    <div class="attendance-copy"><strong>${confirmed ? "Institute-confirmed attendance" : rows.length ? "Recorded attendance" : "No attendance submitted"}</strong><p>${confirmed ? `${present} present of ${confirmed.workingDays} applicable working days · ${dateText(confirmed.periodStart)} to ${dateText(confirmed.periodEnd)}.` : classified ? `${present} of ${classified} classified records count as attended.` : "This module will update after attendance is recorded."}</p></div>`;
  $("#attendance-metrics").innerHTML = confirmed ? [
    moduleMetric("Present", String(present)),
    moduleMetric("Absent", String(absent), absent > 0),
    moduleMetric("Working days", String(confirmed.workingDays)),
    moduleMetric("Mentor", confirmed.mentor || "—"),
  ].join("") : [
    moduleMetric("Attended", String(present)),
    moduleMetric("Late", String(late)),
    moduleMetric("Absent", String(absent), absent > 0),
    moduleMetric("Unclassified", String(unclassified), unclassified > 0),
  ].join("");
  const grouped = rows.reduce((groups, item) => {
    const subject = item.subject || "Other";
    groups[subject] ||= [];
    groups[subject].push(item);
    return groups;
  }, {});
  $("#attendance-breakdown").innerHTML = confirmed
    ? empty("check", "Confirmed period summary", "The client report contains a consolidated total; subject-level attendance was not supplied.")
    : Object.entries(grouped).length
    ? Object.entries(grouped).map(([subject, items]) => {
      const attended = items.filter((item) => presentStatuses.has(item.status)).length;
      const subjectRate = Math.round((attended / items.length) * 100);
      return `<article class="subject-attendance-card">
        <div><strong>${esc(subject)}</strong><span>${attended} of ${items.length} classes</span></div>
        <em>${subjectRate}%</em>
        <div class="subject-progress" aria-label="${esc(subject)} attendance ${subjectRate}%"><span style="width:${subjectRate}%"></span></div>
      </article>`;
    }).join("")
    : empty("check", "No subject records", "Subject attendance will appear after faculty submissions.");
  $("#attendance-list").innerHTML = recentRows.length
    ? recentRows.map((item) => `<article class="attendance-row">
      <time>${esc(item.dateLabel || dateText(item.startsAt))}</time>
      <span><strong>${esc(item.subject)}</strong><small>${item.startsAt ? timeText(item.startsAt) : `Source mark ${esc(item.rawStatus || "—")}`}${item.reason ? ` · ${esc(item.reason)}` : ""}</small></span>
      <em class="status status-${esc(item.status)}">${esc(item.status === "unclassified" && item.rawStatus ? item.rawStatus : titleCase(item.status))}</em>
    </article>`).join("")
    : empty("check", "Attendance not recorded yet", "Records will appear after faculty submits attendance.");
}

function renderNotices() {
  const allNotices = state.data.notices;
  const notices = allNotices.slice(0, 6);
  const batchNotices = allNotices.filter((item) => item.batch).length;
  $("#notice-metrics").innerHTML = [
    moduleMetric("Published", String(allNotices.length)),
    moduleMetric("For your batch", String(batchNotices)),
    moduleMetric("Latest", notices[0] ? dateText(notices[0].publishedAt) : "None"),
  ].join("");
  $("#notice-list").innerHTML = notices.length
    ? notices.map((item) => `<article class="notice-card">
      <div class="notice-card-top"><span>${esc([item.batch, item.subject].filter(Boolean).join(" · ") || "All students")}</span><time>${dateLong(item.publishedAt)}</time></div>
      <h3>${esc(item.title)}</h3>
      <p>${esc(item.body)}</p>
      <footer>${esc(titleCase(item.channel))}</footer>
    </article>`).join("")
    : empty("notice", "No published notices", "Institute announcements for students and your batch will appear here.");
}

function renderProfile() {
  const { profile, account } = state.data;
  $("#profile-card").innerHTML = `
    <span class="profile-avatar">${initials(profile.fullName)}</span>
    <span><strong>${esc(profile.fullName)}</strong><span>${esc(displayValue(profile.admissionNumber))}</span><span>${esc([profile.program, profile.batch].filter(Boolean).join(" · ") || "Academic details pending")}</span></span>`;
  const details = [
    ["Admission number", profile.admissionNumber],
    ["Program", profile.program],
    ["Batch", profile.batch],
    ["Subjects", (profile.subjects || []).join(", ")],
    ["Primary contact", profile.mobile],
    ["Secondary contact", profile.secondaryMobile],
    ["Student email", profile.email],
    ["Portal login", account?.mobile ? `+91 ${account.mobile}` : "Mobile not assigned"],
  ];
  $("#profile-details").innerHTML = details.map(([label, value]) => `<div><dt>${esc(label)}</dt><dd>${esc(displayValue(value))}</dd></div>`).join("");
}

function messageError(selector, error) {
  const node = $(selector);
  node.textContent = error.message;
  node.classList.remove("hidden");
}

async function loadCommunication(force = false) {
  if (state.communication && !force) return renderCommunication();
  $("#conversation-list").innerHTML = empty("clock", "Loading conversations");
  try {
    state.communication = await api("/api/communication/inbox");
    renderCommunication();
  } catch (error) {
    $("#conversation-list").innerHTML = empty("notice", "Messages unavailable", error.message);
  }
}

function renderCommunication() {
  const inbox = state.communication || { threads: [], subjects: [] };
  const openCount = inbox.threads.filter(item => item.status === "open").length;
  $("#conversation-count").textContent = `${openCount} open`;
  $("#more-message-copy").textContent = inbox.threads.length ? `${inbox.threads.length} conversation${inbox.threads.length === 1 ? "" : "s"}` : "Contact Operations or faculty";
  $("#conversation-subject").innerHTML = `<option value="">Institute office</option>${inbox.subjects.map(item => `<option value="${esc(item.id)}">${esc(item.name)}${item.faculty?.length ? ` · ${esc(item.faculty.join(", "))}` : ""}</option>`).join("")}`;
  $("#conversation-list").innerHTML = inbox.threads.length ? inbox.threads.map(item => `<button class="message-thread" type="button" data-message-thread="${esc(item.id)}"><span class="message-thread-icon">${icon(item.subjectId ? "book" : "notice")}</span><span><strong>${esc(item.topic)}</strong><small>${esc(item.subject)} · ${esc(item.lastSender)}</small><p>${esc(item.lastMessage)}</p></span><time>${dateText(item.lastMessageAt)}</time></button>`).join("") : empty("notice", "No conversations", "Start a conversation with the institute office or your subject faculty.");
  injectIcons($("#messages"));
}

async function openMessageThread(threadId) {
  const panel = $("#conversation-detail");
  panel.classList.remove("hidden");
  panel.innerHTML = empty("clock", "Loading conversation");
  try {
    const detail = await api(`/api/communication/threads/${encodeURIComponent(threadId)}`);
    panel.innerHTML = `<div class="message-detail-head"><div><p class="eyebrow">${esc(detail.subject)}</p><h2>${esc(detail.topic)}</h2><small>${esc(detail.status)}</small></div><button class="message-detail-close" type="button" aria-label="Close conversation">×</button></div><div class="message-log">${detail.messages.map(item => `<article class="message-bubble ${item.senderId === state.identity?.id ? "mine" : ""}"><header><strong>${esc(item.senderName)}</strong><time>${dateText(item.createdAt)} · ${timeText(item.createdAt)}</time></header><p>${esc(item.body)}</p></article>`).join("")}</div>${detail.canReply ? `<form class="message-reply-form" id="message-reply-form" data-thread-id="${esc(threadId)}"><label><span>Reply</span><textarea name="body" rows="3" maxlength="3000" required></textarea></label><div class="form-error hidden" id="message-reply-error" role="alert"></div><button class="primary-button" type="submit">Send reply</button></form>` : `<p class="message-closed">This conversation is closed. Start a new conversation if you need further help.</p>`}`;
    $(".message-detail-close", panel).addEventListener("click", () => panel.classList.add("hidden"));
    $("#message-reply-form")?.addEventListener("submit", replyToMessageThread);
    panel.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  } catch (error) { panel.innerHTML = empty("notice", "Conversation unavailable", error.message); }
}

async function createConversation(event) {
  event.preventDefault();
  const form = event.currentTarget, data = new FormData(form), button = $('button[type="submit"]', form);
  button.disabled = true;
  $("#conversation-create-error").classList.add("hidden");
  try {
    const detail = await api("/api/communication/threads", { method: "POST", body: JSON.stringify({ subjectId: String(data.get("subjectId") || "") || null, topic: String(data.get("topic") || "").trim(), body: String(data.get("body") || "").trim() }) });
    form.reset(); form.classList.add("hidden");
    await loadCommunication(true); await openMessageThread(detail.id); toast("Message sent.");
  } catch (error) { messageError("#conversation-create-error", error); }
  finally { button.disabled = false; }
}

async function replyToMessageThread(event) {
  event.preventDefault();
  const form = event.currentTarget, data = new FormData(form), button = $('button[type="submit"]', form), threadId = form.dataset.threadId;
  button.disabled = true; $("#message-reply-error").classList.add("hidden");
  try {
    await api(`/api/communication/threads/${encodeURIComponent(threadId)}/messages`, { method: "POST", body: JSON.stringify({ body: String(data.get("body") || "").trim() }) });
    await loadCommunication(true); await openMessageThread(threadId);
  } catch (error) { messageError("#message-reply-error", error); button.disabled = false; }
}

function renderMore() {
  const { profile, examinations, notices } = state.data;
  const upcomingExams = (examinations || []).filter((item) => item.status === "scheduled" && asInstant(item.scheduledAt).getTime() >= Date.now()).length;
  $("#more-examination-copy").textContent = upcomingExams ? `${upcomingExams} upcoming examination${upcomingExams === 1 ? "" : "s"}` : `${(examinations || []).filter((item) => item.status === "published").length} published results`;
  $("#more-notice-copy").textContent = notices.length ? `${notices.length} published notice${notices.length === 1 ? "" : "s"}` : "No published notices";
  $("#more-profile-copy").textContent = [profile.admissionNumber, profile.batch].filter(Boolean).join(" · ") || "Student and login details";
}

function togglePassword(button) {
  const field = $("input", button.closest(".password-field"));
  if (!field) return;
  const show = field.type === "password";
  field.type = show ? "text" : "password";
  button.setAttribute("aria-pressed", String(show));
  button.setAttribute("aria-label", `${show ? "Hide" : "Show"} ${button.dataset.passwordLabel || "password"}`);
  const glyph = $("[data-icon]", button);
  if (glyph) glyph.dataset.icon = show ? "eye-off" : "eye";
  injectIcons(button);
}

function resetPasswordVisibility(root = document) {
  $$("[data-password-toggle]", root).forEach(button => {
    const field = $("input", button.closest(".password-field"));
    if (field) field.type = "password";
    button.setAttribute("aria-pressed", "false");
    button.setAttribute("aria-label", `Show ${button.dataset.passwordLabel || "password"}`);
    const glyph = $("[data-icon]", button);
    if (glyph) glyph.dataset.icon = "eye";
    injectIcons(button);
  });
}

function bindEvents() {
  $("#login-form").addEventListener("submit", login);
  $$("input", $("#login-form")).forEach(field => field.addEventListener("input", clearLoginError));
  $("#login-mobile").addEventListener("input", syncConsentVisibility);
  $("#password-change-form").addEventListener("submit", changePassword);
  $("#signout-button").addEventListener("click", logout);
  $("#sidebar-signout").addEventListener("click", logout);
  $("#profile-button").addEventListener("click", () => showView("profile"));
  $("#new-conversation").addEventListener("click", () => $("#conversation-create-form").classList.toggle("hidden"));
  $("#cancel-conversation").addEventListener("click", () => $("#conversation-create-form").classList.add("hidden"));
  $("#conversation-create-form").addEventListener("submit", createConversation);
  window.addEventListener("popstate", () => state.data && showView(hashView(), false));
  window.addEventListener("online", () => setConnectionState(true));
  window.addEventListener("offline", () => setConnectionState(false));
  document.addEventListener("keydown", (event) => {
    if ((event.key === "Enter" || event.key === " ") && event.target.matches("[role='button'][data-go]")) {
      event.preventDefault();
      showView(event.target.dataset.go);
    }
  });
  document.addEventListener("click", (event) => {
    const passwordToggle = event.target.closest("[data-password-toggle]");
    if (passwordToggle) {
      togglePassword(passwordToggle);
      return;
    }
    const navigation = event.target.closest("[data-view],[data-go]");
    const view = navigation?.dataset.view || navigation?.dataset.go;
    if (view) {
      event.preventDefault();
      showView(view);
    }
    const messageThread = event.target.closest("[data-message-thread]");
    if (messageThread) openMessageThread(messageThread.dataset.messageThread);
    const scheduleButton = event.target.closest("[data-schedule-date]");
    if (scheduleButton) {
      state.scheduleDate = scheduleButton.dataset.scheduleDate;
      renderSchedule();
    }
    const filterButton = event.target.closest("[data-assignment-filter]");
    if (filterButton) {
      state.assignmentFilter = filterButton.dataset.assignmentFilter;
      $$("[data-assignment-filter]").forEach((node) => {
        const active = node.dataset.assignmentFilter === state.assignmentFilter;
        node.classList.toggle("active", active);
        node.setAttribute("aria-pressed", String(active));
      });
      renderAssignments();
      injectIcons($("#assignments"));
    }
    const examinationFilter = event.target.closest("[data-examination-filter]");
    if (examinationFilter) {
      state.examinationFilter = examinationFilter.dataset.examinationFilter;
      $$("[data-examination-filter]").forEach((node) => {
        const active = node.dataset.examinationFilter === state.examinationFilter;
        node.classList.toggle("active", active);
        node.setAttribute("aria-pressed", String(active));
      });
      renderExaminations();
      injectIcons($("#examinations"));
    }
    const assignmentButton = event.target.closest("[data-assignment-id][data-assignment-status]");
    if (assignmentButton) {
      updateAssignmentStatus(assignmentButton.dataset.assignmentId, assignmentButton.dataset.assignmentStatus);
    }
    const downloadButton = event.target.closest("[data-download-assignment]");
    if (downloadButton) {
      downloadAssignmentPdf(
        downloadButton.dataset.downloadAssignment,
        downloadButton.dataset.materialName || "assignment.pdf",
        downloadButton
      );
    }
  });
}

initialize();
