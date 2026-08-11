"use strict";

const icons = {
  eye: '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/>',
  "eye-off": '<path d="m3 3 18 18M10.6 5.2A11.4 11.4 0 0 1 12 5c6.5 0 10 7 10 7a16 16 0 0 1-2.1 3.2M6.6 6.6C3.6 8.6 2 12 2 12s3.5 7 10 7a10.7 10.7 0 0 0 4.1-.8M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
  "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
  shield: '<path d="M12 3 5 6v5c0 4.5 2.8 8.1 7 10 4.2-1.9 7-5.5 7-10V6l-7-3Z"/><path d="m9 12 2 2 4-4"/>',
  building: '<path d="M4 21V5l8-3 8 3v16M8 9h2m4 0h2M8 13h2m4 0h2M9 21v-4h6v4M2 21h20"/>',
  "chevron-down": '<path d="m7 10 5 5 5-5"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  spark: '<path d="m12 3 1.4 4.1L17.5 8.5l-4.1 1.4L12 14l-1.4-4.1-4.1-1.4 4.1-1.4L12 3ZM19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8L19 14ZM5 14l.8 2.2L8 17l-2.2.8L5 20l-.8-2.2L2 17l2.2-.8L5 14Z"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  wallet: '<path d="M4 5h15a2 2 0 0 1 2 2v12H4a2 2 0 0 1-2-2V5.5A2.5 2.5 0 0 1 4.5 3H18"/><path d="M16 11h5v4h-5a2 2 0 0 1 0-4Z"/>',
  "calendar-check": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18m-12 5 2 2 4-4"/>',
  book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
  exam: '<path d="M8 3h8m-7 0v3h6V3"/><rect x="5" y="5" width="14" height="17" rx="2"/><path d="M9 11h6m-6 4h4m-4 4h6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  message: '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z"/><path d="M8 9h8M8 13h5"/>',
  inventory: '<path d="m4 7 8-4 8 4-8 4-8-4Z"/><path d="m4 7v10l8 4 8-4V7M12 11v10"/>',
  chart: '<path d="M4 20V10m6 10V4m6 16v-7m6 7H2"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/>',
  x: '<path d="m6 6 12 12M18 6 6 18"/>', more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>', search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  moon: '<path d="M20 15.5A8.5 8.5 0 0 1 8.5 4 8.5 8.5 0 1 0 20 15.5Z"/>', sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4"/>', plus: '<path d="M12 5v14M5 12h14"/>',
  refresh: '<path d="M20 6v5h-5M4 18v-5h5"/><path d="M6.1 9a7 7 0 0 1 11.7-2.6L20 11M4 13l2.2 4.6A7 7 0 0 0 18 15"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M5 21h14"/>', receipt: '<path d="M5 3v18l3-2 4 2 4-2 3 2V3l-3 2-4-2-4 2-3-2Z"/><path d="M9 9h6M9 13h6"/>',
  "arrow-left": '<path d="M19 12H5m6-6-6 6 6 6"/>', printer: '<path d="M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v7H6z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>', trend: '<path d="m3 17 6-6 4 4 8-9M15 6h6v6"/>',
  alert: '<path d="M10.3 4.5 2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.5a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/>',
  "chevron-right": '<path d="m9 18 6-6-6-6"/>', user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>', logout: '<path d="M10 17l5-5-5-5M15 12H3M15 3h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"/>'
};

const cachedUser = (() => {
  try { return JSON.parse(sessionStorage.getItem("lakshya_user") || "null"); }
  catch { return null; }
})();
const state = { token: sessionStorage.getItem("lakshya_token"), user: cachedUser, setupRequired: false, view: "dashboard", students: [], agreements: [], payments: [], installments: [], leads: [], stages: [], sessions: [], timetable: { batches: [], subjects: [], rooms: [], faculty: [], teachingAssignments: [] }, assignments: [], examinations: [], attendanceSessions: [], notices: [], conversations: { threads: [], subjects: [], canCreate: false, canAnnounce: true }, inventory: { items: [], summary: {} }, report: null, masters: { users: [], batches: [], subjects: [], rooms: [], studentAccess: [], parentAccess: [] }, audit: [] };
const loadedResources = new Set();
const resourceLoads = new Map();
const ROLE_VIEWS = {
  owner: Object.keys({dashboard:1,admissions:1,students:1,finance:1,attendance:1,academics:1,examinations:1,timetable:1,communication:1,inventory:1,reports:1,settings:1}),
  admissions_manager: ["dashboard","admissions","students","finance","communication"],
  counsellor: ["dashboard","admissions"],
  front_desk: ["dashboard","admissions","students","timetable","communication"],
  accounts: ["dashboard","students","finance","inventory","reports"],
  academic_coordinator: ["dashboard","students","attendance","academics","examinations","timetable","communication","reports"],
  faculty: ["dashboard","academics","examinations","timetable"],
  storekeeper: ["dashboard","inventory"]
};
const OPERATIONS_MODULES = ["admissions", "students", "finance", "attendance", "academics", "examinations", "timetable", "communication", "inventory", "reports"];
const PERMISSION_MODULE_LABELS = { admissions: "Admissions", students: "Students", finance: "Fees & finance", attendance: "Attendance", academics: "Academics", examinations: "Examinations", timetable: "Faculty & timetable", communication: "Communication", inventory: "Inventory", reports: "Reports" };
function canAccess(module, action = "read") {
  if (state.user?.role === "owner") return true;
  const permission = state.user?.permissions?.[module];
  if (permission) return Boolean(permission[action]);
  return action === "read" && (ROLE_VIEWS[state.user?.role] || []).includes(module);
}
const allowedViews = () => new Set([
  "dashboard",
  ...OPERATIONS_MODULES.filter(module => canAccess(module, "read")),
  ...(state.user?.role === "owner" ? ["settings"] : []),
]);
let financeStudentFilter = "";
let ledgerCurrentStudentId = "";
let ledgerReturnFocus = null;
let detailReturnFocus = null;
let detailRouteStudentId = "";
let settingsAccountSearch = "";
let settingsAccountFilter = "all";
let settingsSection = "accounts";
let timetableSelectedDate = "";
let timetableView = "schedule";
const STUDENT_BATCH_ORDER = ["Essential", "Tatva"];
const STUDENT_PROGRAM_ORDER = ["JEE", "NEET", "MHT-CET", "Boards"];
const RECONCILIATION_ACTION_STATES = new Set(["review", "needs_date", "needs_mode"]);
const VIEW_PATHS = {
  dashboard: "/operations",
  admissions: "/operations/admissions",
  students: "/operations/students",
  finance: "/operations/finance",
  attendance: "/operations/attendance",
  academics: "/operations/academics",
  examinations: "/operations/examinations",
  timetable: "/operations/timetable",
  communication: "/operations/communication",
  inventory: "/operations/inventory",
  reports: "/operations/reports",
  settings: "/operations/settings",
};
const studentHierarchyState = { batch: "Essential", program: "" };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const esc = (value = "") => String(value ?? "").replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
const initials = name => String(name || "Lakshya").split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join("").toUpperCase();
const normalize = value => String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const normalizedMobile = value => {
  let digits = String(value || "").replace(/\D/g, "");
  if (digits.length === 12 && digits.startsWith("91")) digits = digits.slice(2);
  else if (digits.length === 11 && digits.startsWith("0")) digits = digits.slice(1);
  return /^[6-9]\d{9}$/.test(digits) ? digits : "";
};
const mobileLabel = value => value ? `+91 ${String(value).slice(0, 5)} ${String(value).slice(5)}` : "Mobile not assigned";
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.info}</svg>`;
const money = value => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value || 0));
const shortMoney = value => Number(value || 0) >= 100000 ? `₹${(Number(value) / 100000).toFixed(2)}L` : money(value);
const formatDate = value => value ? new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(`${value}T00:00:00`)) : "—";
const asInstant = value => {
  if (value instanceof Date) return value;
  const text = String(value || "");
  return new Date(/[zZ]$|[+-]\d{2}:?\d{2}$/.test(text) ? text : `${text}Z`);
};
const indiaDateParts = (date = new Date()) => {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(asInstant(date));
  const value = type => parts.find(part => part.type === type)?.value || "";
  return { year: value("year"), month: value("month"), day: value("day"), hour: value("hour"), minute: value("minute") };
};
const formatDateTime = value => value ? new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
}).format(asInstant(value)) : "—";
const indiaDateKey = value => {
  const parts = indiaDateParts(value);
  return `${parts.year}-${parts.month}-${parts.day}`;
};
const classTime = value => value ? new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  hour: "2-digit",
  minute: "2-digit",
  hour12: true,
}).format(asInstant(value)) : "—";
const timetableDateLabel = value => new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  weekday: "short",
  day: "2-digit",
  month: "short",
}).format(asInstant(value));
const localInputValue = (date = new Date(Date.now() + 86400000)) => {
  const { year, month, day, hour, minute } = indiaDateParts(date);
  return `${year}-${month}-${day}T${hour}:${minute}`;
};
const dateInputValue = (date = new Date()) => {
  const { year, month, day } = indiaDateParts(date);
  return `${year}-${month}-${day}`;
};
const indiaInputToISOString = value => new Date(`${String(value)}:00+05:30`).toISOString();
const status = value => `<span class="status status-${normalize(value) || "neutral"}">${esc(String(value || "Unknown").replaceAll("_", " "))}</span>`;

function injectIcons(root = document) {
  $$('[data-icon]', root).forEach(node => { if (icons[node.dataset.icon]) node.innerHTML = icon(node.dataset.icon); });
}

function passwordControl(name, { label = "password", autocomplete = "new-password", minlength = 6, required = false } = {}) {
  return `<span class="password-control"><input name="${esc(name)}" type="password" minlength="${minlength}" autocomplete="${esc(autocomplete)}"${required ? " required" : ""}><button class="icon-button password-toggle" type="button" data-password-toggle data-password-label="${esc(label)}" aria-label="Show ${esc(label)}" aria-pressed="false" data-icon="eye"></button></span>`;
}

function togglePassword(button) {
  const field = $("input", button.closest(".password-control"));
  if (!field) return;
  const show = field.type === "password";
  field.type = show ? "text" : "password";
  button.setAttribute("aria-pressed", String(show));
  button.setAttribute("aria-label", `${show ? "Hide" : "Show"} ${button.dataset.passwordLabel || "password"}`);
  button.dataset.icon = show ? "eye-off" : "eye";
  injectIcons(button);
}

function resetPasswordVisibility(root = document) {
  $$("[data-password-toggle]", root).forEach(button => {
    const field = $("input", button.closest(".password-control"));
    if (field) field.type = "password";
    button.setAttribute("aria-pressed", "false");
    button.setAttribute("aria-label", `Show ${button.dataset.passwordLabel || "password"}`);
    button.dataset.icon = "eye";
    injectIcons(button);
  });
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const method = String(options.method || "GET").toUpperCase();
  const requestPath = method === "GET" && path.startsWith("/api/")
    ? `${path}${path.includes("?") ? "&" : "?"}_fresh=${Date.now()}`
    : path;
  const response = await fetch(requestPath, { ...options, headers, cache: method === "GET" ? "no-store" : undefined });
  let body = null;
  try { body = await response.json(); } catch { body = {}; }
  if (!response.ok) {
    const detail = body?.detail;
    const error = new Error(response.status === 401 && state.token
      ? "Your session expired. Please sign in again."
      : typeof detail === "string" ? detail : detail?.message || body?.error?.message || "Something went wrong. Please try again.");
    error.status = response.status;
    if (response.status === 401 && state.token) expireSession();
    throw error;
  }
  return body;
}

function toast(message, tone = "success") {
  const node = document.createElement("div");
  node.className = "toast";
  node.classList.toggle("toast-error", tone === "error");
  node.textContent = message;
  $("#toast-region").append(node);
  setTimeout(() => node.remove(), 3600);
}

function setAuthMode(setup, allowLegacyEmailLogin = false) {
  state.setupRequired = setup;
  state.allowLegacyEmailLogin = allowLegacyEmailLogin;
  setLegacyLoginMode(false);
  $$(".setup-only").forEach(node => node.classList.toggle("hidden", !setup));
  $("#legacy-login-toggle").classList.toggle("hidden", setup || !allowLegacyEmailLogin);
  $("#auth-title").textContent = setup ? "Create owner" : "Sign in";
  $("#auth-submit-label").textContent = setup ? "Create account" : "Sign in";
  $("#password-help").textContent = "Use at least 6 characters.";
  $("#auth-password").minLength = 6;
  $("#auth-password").autocomplete = setup ? "new-password" : "current-password";
}

function setLegacyLoginMode(enabled) {
  state.legacyEmailLogin = enabled;
  const field = $("#auth-mobile");
  $("#auth-identity-label").textContent = enabled ? "Existing email address" : "Mobile number";
  field.type = enabled ? "email" : "tel";
  field.inputMode = enabled ? "email" : "tel";
  field.placeholder = enabled ? "owner email address" : "10-digit mobile number";
  field.maxLength = enabled ? 255 : 16;
  field.value = "";
  $("#legacy-login-toggle").textContent = enabled ? "Use mobile number" : "Existing account without mobile?";
  $('[data-error-for="mobile"]').textContent = "";
}

async function initialize() {
  injectIcons();
  initializeTheme();
  bindEvents();
  refreshServiceWorker();
  try {
    if (state.token) {
      try {
        state.user = await api("/api/auth/me");
        sessionStorage.setItem("lakshya_user", JSON.stringify(state.user));
        await enterWorkspace();
      }
      catch (error) {
        if (error.status !== 401 && state.token) showBootError("Workspace unavailable", error.message);
      }
    } else {
      const setup = await api("/api/auth/bootstrap-status");
      setAuthMode(setup.setupRequired, setup.allowLegacyEmailLogin);
      showAuth();
    }
  } catch (error) {
    if (error.status !== 401) showBootError("Service unavailable", "The latest workspace data could not be loaded.");
  }
}

async function refreshServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  try {
    const registration = await navigator.serviceWorker.register("/sw.js");
    await registration.update();
  } catch {}
}

function showBootError(title, message) {
  $("#auth-screen").classList.add("hidden");
  $("#app-shell").classList.add("hidden");
  $("#boot-screen").classList.remove("hidden");
  $("#boot-screen").classList.add("has-error");
  $("#boot-title").textContent = title;
  $("#boot-message").textContent = message;
  $("#boot-retry").classList.remove("hidden");
}

function clearSession() {
  state.token = null;
  state.user = null;
  state.view = "dashboard";
  loadedResources.clear();
  resourceLoads.clear();
  Object.assign(state, { students: [], agreements: [], payments: [], installments: [], leads: [], stages: [], sessions: [], timetable: { batches: [], subjects: [], rooms: [], faculty: [], teachingAssignments: [] }, assignments: [], examinations: [], attendanceSessions: [], notices: [], conversations: { threads: [], subjects: [], canCreate: false, canAnnounce: true }, inventory: { items: [], summary: {} }, report: null, masters: { users: [], batches: [], subjects: [], rooms: [], studentAccess: [], parentAccess: [] }, audit: [] });
  sessionStorage.removeItem("lakshya_token");
  sessionStorage.removeItem("lakshya_user");
}

function resetAuthForm() {
  $("#auth-password").value = "";
  resetPasswordVisibility($("#auth-screen"));
  $$(".field-error").forEach(node => node.textContent = "");
  $("#auth-error").classList.add("hidden");
}

function showAuth(message = "") {
  closeAccountMenu();
  $("#boot-screen").classList.add("hidden");
  $("#auth-screen").classList.remove("hidden");
  $("#app-shell").classList.add("hidden");
  if (message) { $("#auth-error").textContent = message; $("#auth-error").classList.remove("hidden"); }
}

function expireSession() {
  clearSession();
  resetAuthForm();
  showAuth("Your session expired. Please sign in again.");
}

async function handleAuth(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const fullName = String(form.get("fullName") || "").trim();
  const identity = String(form.get("mobile") || "").trim();
  const legacyEmail = !state.setupRequired && state.legacyEmailLogin;
  const mobile = legacyEmail ? "" : normalizedMobile(identity);
  const password = String(form.get("password") || "");
  $$(".field-error").forEach(node => node.textContent = "");
  $("#auth-error").classList.add("hidden");
  let invalid = false;
  if (state.setupRequired && fullName.length < 2) { $('[data-error-for="fullName"]').textContent = "Enter the owner’s full name."; invalid = true; }
  if (legacyEmail && !/^\S+@\S+\.\S+$/.test(identity)) { $('[data-error-for="mobile"]').textContent = "Enter the existing owner email address."; invalid = true; }
  if (!legacyEmail && !mobile) { $('[data-error-for="mobile"]').textContent = "Enter a valid 10-digit Indian mobile number."; invalid = true; }
  if (password.length < 6) { $('[data-error-for="password"]').textContent = "Use at least 6 characters."; invalid = true; }
  if (invalid) return;
  const button = $("#auth-submit"); button.disabled = true; $("#auth-submit-label").textContent = state.setupRequired ? "Creating…" : "Signing in…";
  try {
    const payload = state.setupRequired
      ? { fullName, mobile, password }
      : legacyEmail ? { email: identity, password } : { mobile, password };
    const result = await api(state.setupRequired ? "/api/auth/bootstrap" : "/api/auth/login", { method: "POST", body: JSON.stringify(payload) });
    state.token = result.access_token; sessionStorage.setItem("lakshya_token", state.token);
    state.user = result.user;
    sessionStorage.setItem("lakshya_user", JSON.stringify(state.user));
    await enterWorkspace();
  } catch (error) {
    $("#auth-error").textContent = error.message; $("#auth-error").classList.remove("hidden");
    $("#auth-password").value = "";
    $("#auth-password").focus();
  } finally {
    button.disabled = false; $("#auth-submit-label").textContent = state.setupRequired ? "Create account" : "Sign in";
  }
}

async function enterWorkspace() {
  if (!ROLE_VIEWS[state.user?.role] && !OPERATIONS_MODULES.some(module => canAccess(module, "read"))) {
    const portal = state.user?.role === "parent" ? "Parent portal" : ["student","parent_student"].includes(state.user?.role) ? "Student portal" : state.user?.role === "attendance_operator" ? "Attendance Desk" : "assigned portal";
    clearSession();
    showAuth(`This account belongs to the ${portal}. Open that application to continue.`);
    return;
  }
  const name = state.user?.fullName || "Lakshya Director";
  const label = state.user?.role?.replaceAll("_", " ") || "Owner";
  $("#sidebar-user-name").textContent = name; $("#sidebar-user-role").textContent = label.replace(/\b\w/g, c => c.toUpperCase());
  $("#dashboard-date").textContent = new Intl.DateTimeFormat("en-IN", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
  $("#account-menu-name").textContent = name; $("#account-menu-role").textContent = label.replace(/\b\w/g, c => c.toUpperCase());
  [$("#user-avatar"), $("#topbar-avatar"), $("#account-menu-avatar")].forEach(node => node.textContent = initials(name));
  await loadInitialWorkspace();
  $("#boot-screen").classList.add("hidden");
  $("#auth-screen").classList.add("hidden");
  $("#app-shell").classList.remove("hidden");
  applyRoleUI();
  const route = currentOperationsRoute();
  const requestedView = allowedViews().has(route.view) ? route.view : "dashboard";
  showView(requestedView, false);
  replaceOperationsRoute(requestedView, route.kind === "view" || route.view !== requestedView ? null : route);
  if (route.kind === "student" && requestedView === "students") await openStudent(route.studentId, false);
  else if (route.kind === "ledger" && requestedView === "finance") openStudentLedger(route.studentId, null, false);
}

async function fetchAll(path, pageSize = 100) {
  const separator = path.includes("?") ? "&" : "?";
  const first = await api(`${path}${separator}page=1&page_size=${pageSize}`);
  const items = [...(first.items || [])];
  const pages = Math.ceil((first.total || items.length) / pageSize);
  for (let page = 2; page <= pages; page += 1) {
    const next = await api(`${path}${separator}page=${page}&page_size=${pageSize}`); items.push(...(next.items || []));
  }
  return items;
}

async function optional(load, fallback) {
  try { return await load(); }
  catch (error) {
    if (error.status === 403 || error.status === 404) return fallback;
    throw error;
  }
}

async function loadInitialWorkspace() {
  const workspace = await api("/api/workspace/bootstrap");
  Object.assign(state, {
    students: workspace.students || [],
    agreements: workspace.agreements || [],
    payments: workspace.payments || [],
    installments: workspace.installments || [],
    leads: workspace.leads || [],
    stages: workspace.admissionsMeta?.stageOrder || [],
  });
  renderCore();
}

async function loadResource(resource) {
  if (loadedResources.has(resource)) return;
  if (resourceLoads.has(resource)) return resourceLoads.get(resource);
  const request = (async () => {
    if (resource === "timetable") {
      state.timetable = await api("/api/timetable/bootstrap");
      state.sessions = state.timetable.sessions || [];
    } else if (resource === "references") state.timetable = { ...state.timetable, ...await api("/api/workspace/reference-data") };
    else if (resource === "assignments") state.assignments = await api("/api/academics/assignments");
    else if (resource === "examinations") state.examinations = await api("/api/examinations");
    else if (resource === "attendance") state.attendanceSessions = await api("/api/attendance/sessions");
    else if (resource === "notices") state.notices = await api("/api/communication/notices");
    else if (resource === "conversations") state.conversations = await api("/api/communication/inbox");
    else if (resource === "inventory") state.inventory = await api("/api/inventory/bootstrap");
    else if (resource === "reports") state.report = await api("/api/reports/overview");
    else if (resource === "masters") state.masters = await api("/api/settings/bootstrap");
    else if (resource === "audit") state.audit = await api("/api/settings/audit");
    loadedResources.add(resource);
    renderResource(resource);
  })().finally(() => resourceLoads.delete(resource));
  resourceLoads.set(resource, request);
  return request;
}

async function loadViewResources(view) {
  const requirements = {
    timetable: ["timetable"],
    academics: ["references", "assignments"],
    examinations: ["references", "examinations"],
    attendance: ["attendance"],
    communication: ["references", "notices", "conversations"],
    inventory: ["inventory"],
    reports: ["reports"],
    settings: ["timetable", "masters", "audit"],
  }[view] || [];
  if (!requirements.some(resource => !loadedResources.has(resource))) return;
  const viewNode = document.getElementById(view);
  viewNode?.setAttribute("aria-busy", "true");
  try {
    await Promise.all(requirements.map(loadResource));
  } finally {
    viewNode?.removeAttribute("aria-busy");
  }
}

function renderCore() {
  $("#nav-leads-count").textContent = state.leads.length;
  const reviewCount = state.payments.filter(item => item.status === "staged" && RECONCILIATION_ACTION_STATES.has(item.reconciliationStatus)).length;
  $("#payment-review-count").textContent = reviewCount ? `${reviewCount} review` : "";
  $("#payment-review-count").classList.toggle("hidden", !reviewCount);
  renderDashboard(); renderStudents(); renderFinance(); renderAdmissions(); renderCommandResults(); injectIcons(); applyRoleUI();
}

function renderResource(resource) {
  if (resource === "timetable") renderTimetable();
  else if (resource === "assignments") renderAcademics();
  else if (resource === "examinations") {
    $("#nav-examinations-count").textContent = state.examinations.length;
    renderExaminations();
  } else if (resource === "attendance") renderAttendance();
  else if (resource === "notices" || resource === "conversations") renderCommunication();
  else if (resource === "inventory") {
    $("#nav-inventory-count").textContent = state.inventory.items?.length || 0;
    renderInventory();
  } else if (resource === "reports") renderReports();
  else if (resource === "masters" || resource === "audit") renderSettings();
  injectIcons();
  applyRoleUI();
}

function renderAll() {
  renderCore();
  renderTimetable(); renderAcademics(); renderExaminations(); renderAttendance(); renderCommunication(); renderInventory(); renderReports(); renderSettings();
  $("#nav-examinations-count").textContent = state.examinations.length;
  $("#nav-inventory-count").textContent = state.inventory.items?.length || 0;
  injectIcons(); applyRoleUI();
}

function metricCard(label, value, iconName, featured = false) {
  return `<article class="metric-card ${featured ? "metric-card-featured" : ""}"><div class="metric-card-head"><span class="metric-label">${esc(label)}</span><span class="metric-icon">${icon(iconName)}</span></div><p class="metric-value">${esc(value)}</p></article>`;
}

function renderDashboard() {
  const activeStudents = state.students.filter(student => student.status === "active");
  const openAgreements = state.agreements.filter(item => !["inactive", "forfeited"].includes(item.studentStatus) && item.status !== "inactive");
  const agreed = openAgreements.reduce((sum, item) => sum + Number(item.agreedAmount || 0), 0);
  const registration = openAgreements.reduce((sum, item) => sum + Number(item.legacyRegistrationTotal || 0), 0);
  $("#dashboard-metrics").innerHTML = [
    metricCard("Active students", String(activeStudents.length), "users", true),
    metricCard("Agreed fees", shortMoney(agreed), "wallet"),
    metricCard("Workbook control", shortMoney(registration), "receipt"),
    metricCard("Enquiries", String(state.leads.length), "spark")
  ].join("");

  const programs = activeStudents.reduce((map, item) => map.set(item.program || "Unassigned", (map.get(item.program || "Unassigned") || 0) + 1), new Map());
  const sortedPrograms = [...programs.entries()].sort((a, b) => b[1] - a[1]);
  const max = Math.max(...sortedPrograms.map(([, count]) => count), 1);
  $("#program-chart").innerHTML = sortedPrograms.length ? sortedPrograms.map(([program, count]) => `<div class="program-row"><span title="${esc(program)}">${esc(program)}</span><div class="program-track"><div class="program-fill" style="width:${Math.round(count / max * 100)}%"></div></div><strong>${count}</strong></div>`).join("") : emptyState("users", "No enrollments");

  const quality = ["review", "blocked"].map(kind => ({ kind, count: activeStudents.filter(item => item.dataQualityStatus === kind).length })).filter(item => item.count);
  const paymentReview = state.payments.filter(item => item.status === "staged" && RECONCILIATION_ACTION_STATES.has(item.reconciliationStatus)).length;
  if (paymentReview) quality.push({ kind: "payment review", count: paymentReview });
  $("#attention-count").textContent = quality.reduce((sum, item) => sum + item.count, 0);
  $("#attention-list").innerHTML = quality.length ? quality.map(item => `<button class="attention-item" type="button" data-view-target="${item.kind === "payment review" ? "finance" : "students"}"><span>${icon("alert")}</span><strong>${esc(item.kind.replace(/\b\w/g, c => c.toUpperCase()))}</strong><em>${item.count}</em></button>`).join("") : `<div class="attention-item"><span>${icon("shield")}</span><strong>No review items</strong></div>`;

  const recent = [...activeStudents].sort((a, b) => String(b.enrollmentDate).localeCompare(String(a.enrollmentDate))).slice(0, 5);
  $("#recent-students").innerHTML = recent.length ? recent.map(student => `<button class="record-item" type="button" data-student-id="${esc(student.id)}"><span class="record-avatar">${initials(student.fullName)}</span><span><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)}</small></span><span class="record-program">${esc(student.program)}</span><span class="record-date">${formatDate(student.enrollmentDate)}</span>${status(student.dataQualityStatus)}</button>`).join("") : emptyState("users", "No admissions");

  const stagedRows = state.payments.filter(item => item.status === "staged");
  const stagedTotal = state.payments.reduce((sum, item) => sum + Number(item.receivedAmount ?? 0), 0);
  const readyPayments = stagedRows.filter(item => item.reconciliationStatus === "ready").length;
  const actionPayments = stagedRows.filter(needsPaymentReview).length;
  const excludedNotes = stagedRows.filter(item => item.reconciliationStatus === "do_not_import").length;
  const classifiedPayments = readyPayments + actionPayments;
  const readyPercent = classifiedPayments ? Math.round(readyPayments / classifiedPayments * 100) : 100;
  $("#finance-pulse-body").innerHTML = `<div class="finance-pulse-body"><div class="finance-total">${money(stagedTotal)}<small>${state.payments.length} ledger entries${excludedNotes ? ` · ${excludedNotes} excluded source notes` : ""}</small></div><div class="reconcile-bar"><div class="reconcile-track"><span style="width:${readyPercent}%"></span><span style="width:${100 - readyPercent}%"></span></div><div class="reconcile-labels"><span>${readyPayments} imported ready</span><span>${actionPayments} need client input</span></div></div><button class="button button-secondary" type="button" data-view-target="finance">Open receivables ${icon("arrow-right")}</button></div>`;
}

function compactMetrics(items) { return items.map(item => `<div class="compact-metric"><span>${esc(item.label)}</span><strong>${esc(item.value)}</strong></div>`).join(""); }
function studentPrimary(name, detail = "") { return `<div class="table-primary"><span class="record-avatar">${initials(name)}</span><span><strong>${esc(name)}</strong><small>${esc(detail)}</small></span></div>`; }
function emptyState(iconName, title, copy = "") { return `<div class="empty-state"><span class="empty-icon">${icon(iconName)}</span><div><h3>${esc(title)}</h3>${copy ? `<p>${esc(copy)}</p>` : ""}</div></div>`; }
function isOwner() { return state.user?.role === "owner"; }
function canManageFinance() { return canAccess("finance", "create") || canAccess("finance", "edit"); }
function canReadInventory() { return canAccess("inventory", "read"); }
function canManageInventory() { return canAccess("inventory", "create") || canAccess("inventory", "edit"); }
function canConvertAdmissions() { return canAccess("admissions", "edit"); }
function ownerEditButton(kind, id, label = "Edit") {
  const module = { student: "students", lead: "admissions", agreement: "finance", payment: "finance", session: "timetable", assignment: "academics", notice: "communication" }[kind];
  const allowed = module ? canAccess(module, "edit") : isOwner();
  return allowed ? `<button class="button button-secondary button-small owner-edit-button" type="button" data-owner-edit="${esc(kind)}" data-edit-id="${esc(id)}">${icon("edit")}${esc(label)}</button>` : "";
}

function studentBatchKey(batch) {
  const value = String(batch || "").trim().toLowerCase();
  return STUDENT_BATCH_ORDER.find(name => name.toLowerCase() === value) || "Records for review";
}

function studentProgramKey(program) {
  const value = String(program || "").trim().toLowerCase();
  if (value.includes("mht") || value.includes("cet")) return "MHT-CET";
  if (value.includes("neet")) return "NEET";
  if (value.includes("jee")) return "JEE";
  if (value.includes("board")) return "Boards";
  return "Unassigned";
}

function filteredStudents() {
  const search = $("#student-search").value.trim().toLowerCase();
  const quality = $("#student-quality-filter").value;
  return state.students.filter(item =>
    (!search || [item.fullName, item.mobile, item.admissionNumber, item.previousSchool, item.batch, item.program].some(value => String(value || "").toLowerCase().includes(search)))
    && (!quality || item.dataQualityStatus === quality)
    && (studentHierarchyState.batch === "Opted out" ? ["inactive", "forfeited"].includes(item.status) : studentBatchKey(item.batch) === studentHierarchyState.batch && !["inactive", "forfeited"].includes(item.status))
    && (!studentHierarchyState.program || studentProgramKey(item.program) === studentHierarchyState.program)
  );
}

function renderStudents() {
  $("#new-student").classList.toggle("hidden", !canAccess("students", "create"));
  renderStudentRows();
}

function renderStudentDirectoryRow(student) {
  const contact = student.mobile ? mobileLabel(student.mobile) : "Contact missing";
  const school = student.previousSchool || "School not recorded";
  return `<button class="student-directory-row" type="button" data-student-id="${esc(student.id)}" aria-label="Open ${esc(student.fullName)}">
    <span class="record-avatar">${initials(student.fullName)}</span>
    <span class="student-directory-identity"><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)}</small></span>
    <span class="student-directory-context"><strong>${esc(studentProgramKey(student.program))}</strong><small>${esc(school)}</small></span>
    <span class="student-directory-contact"><strong>${esc(contact)}</strong><small>${esc(student.batch || "Batch not assigned")}</small></span>
    <span class="student-directory-status">${["inactive", "forfeited"].includes(student.status) ? `<span class="status status-inactive">Opted out</span>` : status(student.dataQualityStatus)}</span>
    <span class="student-directory-open" aria-hidden="true">${icon("chevron-right")}</span>
  </button>`;
}

function renderStudentRows() {
  const search = $("#student-search").value.trim().toLowerCase();
  const quality = $("#student-quality-filter").value;
  const baseRows = state.students.filter(item =>
    (!search || [item.fullName, item.mobile, item.admissionNumber, item.previousSchool, item.batch, item.program].some(value => String(value || "").toLowerCase().includes(search)))
    && (!quality || item.dataQualityStatus === quality)
  );
  const batchNames = [...STUDENT_BATCH_ORDER, "Records for review", "Opted out"].filter(batch =>
    batch === "Opted out"
      ? baseRows.some(item => ["inactive", "forfeited"].includes(item.status))
      : batch !== "Records for review" || baseRows.some(item => studentBatchKey(item.batch) === batch && !["inactive", "forfeited"].includes(item.status))
  );
  if (!batchNames.includes(studentHierarchyState.batch)) {
    studentHierarchyState.batch = batchNames[0] || "Essential";
    studentHierarchyState.program = "";
  }
  const batchRows = baseRows.filter(item => studentHierarchyState.batch === "Opted out"
    ? ["inactive", "forfeited"].includes(item.status)
    : studentBatchKey(item.batch) === studentHierarchyState.batch && !["inactive", "forfeited"].includes(item.status));
  const programCounts = new Map(STUDENT_PROGRAM_ORDER.map(program => [program, batchRows.filter(item => studentProgramKey(item.program) === program).length]));
  if (studentHierarchyState.batch === "Records for review") {
    batchRows.forEach(item => {
      const program = studentProgramKey(item.program);
      if (!programCounts.has(program)) programCounts.set(program, batchRows.filter(row => studentProgramKey(row.program) === program).length);
    });
  }
  if (studentHierarchyState.program && !programCounts.get(studentHierarchyState.program)) studentHierarchyState.program = "";
  const rows = [...batchRows]
    .filter(item => !studentHierarchyState.program || studentProgramKey(item.program) === studentHierarchyState.program)
    .sort((a, b) => String(a.fullName || "").localeCompare(String(b.fullName || "")));
  const batchTabs = batchNames.map(batch => {
    const count = baseRows.filter(item => batch === "Opted out" ? ["inactive", "forfeited"].includes(item.status) : studentBatchKey(item.batch) === batch && !["inactive", "forfeited"].includes(item.status)).length;
    const label = batch === "Records for review" ? "Needs assignment" : batch;
    const active = studentHierarchyState.batch === batch;
    return `<button type="button" role="tab" aria-selected="${active}" class="student-batch-tab${active ? " active" : ""}${batch === "Records for review" ? " review" : ""}${batch === "Opted out" ? " inactive" : ""}" data-student-batch="${esc(batch)}"><span>${esc(label)}</span><strong>${count}</strong></button>`;
  }).join("");
  const programTabs = [["", "All", batchRows.length], ...[...programCounts.entries()].filter(([, count]) => count > 0).map(([program, count]) => [program, program, count])]
    .map(([value, label, count]) => `<button type="button" class="student-program-chip${studentHierarchyState.program === value ? " active" : ""}" data-student-program="${esc(value)}"><span>${esc(label)}</span><strong>${count}</strong></button>`).join("");
  const resultLabel = `${rows.length} ${rows.length === 1 ? "student" : "students"}`;
  $("#student-result-count").textContent = resultLabel;
  $("#student-hierarchy").innerHTML = `<div class="student-batch-tabs" role="tablist" aria-label="Student batches">${batchTabs}</div><div class="student-directory-bar"><div class="student-program-chips" aria-label="Filter by program">${programTabs}</div></div><div class="student-directory-list" role="list">${rows.length ? rows.map(renderStudentDirectoryRow).join("") : emptyState("search", "No students here", "Choose another batch or clear the filters.")}</div>`;
}

function studentPayments(studentId) {
  return state.payments.filter(item =>
    item.studentId === studentId
    && ["staged", "posted"].includes(item.status)
    && item.reconciliationStatus !== "do_not_import"
  );
}

const needsPaymentReview = item => item.status === "staged" && RECONCILIATION_ACTION_STATES.has(item.reconciliationStatus);

function studentAccount(agreement) {
  const payments = studentPayments(agreement.studentId);
  const ledgerEffect = payments.reduce((sum, item) => sum + Number(item.signedAmount ?? item.amount ?? 0), 0);
  const paid = payments.reduce((sum, item) => sum + Number(item.receivedAmount ?? item.signedAmount ?? item.amount ?? 0), 0);
  const agreed = Number(agreement.agreedAmount || 0);
  const workbookControl = Number(agreement.legacyRegistrationTotal || 0);
  const balance = agreed - ledgerEffect;
  const difference = paid - workbookControl;
  const reviewCount = state.payments.filter(item => item.studentId === agreement.studentId && needsPaymentReview(item)).length;
  const clientBalanceEntry = payments.find(item => ["balance_credit", "balance_debit"].includes(item.type));
  const accountClosed = ["inactive", "forfeited"].includes(agreement.studentStatus) || agreement.status === "inactive";
  return {
    ...agreement,
    payments,
    paid,
    ledgerEffect,
    agreed,
    workbookControl,
    balance,
    difference,
    reviewCount,
    clientBalanceEntry,
    accountClosed,
    balanceState: balance > 0 ? "due" : balance < 0 ? "credit" : "settled",
    needsReconciliation: reviewCount > 0 || (!clientBalanceEntry && difference !== 0)
  };
}

function accountBalance(value) {
  if (value < 0) return `${money(Math.abs(value))} Cr`;
  if (value > 0) return `${money(value)} Dr`;
  return money(0);
}

function reconciliationBadge(account) {
  if (account.accountClosed) return `<span class="status status-inactive">Opted out</span>`;
  if (account.clientBalanceEntry && !account.needsReconciliation) return `<span class="status status-ready">Verified</span>`;
  if (!account.needsReconciliation) return `<span class="status status-ready">Up to date</span>`;
  return `<span class="status status-review">Needs attention</span>`;
}

function renderFinance() {
  const accounts = state.agreements.map(studentAccount);
  const openAccounts = accounts.filter(item => !item.accountClosed);
  const paymentTotal = accounts.reduce((sum, item) => sum + item.paid, 0);
  const outstanding = openAccounts.reduce((sum, item) => sum + Math.max(item.balance, 0), 0);
  const dueAccounts = openAccounts.filter(item => item.balance > 0).length;
  const review = state.payments.filter(needsPaymentReview).length;
  const registerCount = state.payments.length + state.installments.length;
  $("#new-future-payment").classList.toggle("hidden", !canAccess("finance", "create"));
  $("#new-fee-agreement").classList.toggle("hidden", !canManageFinance());
  $("#new-payment").classList.toggle("hidden", !canManageFinance());
  $("#finance-metrics").innerHTML = compactMetrics([{ label: "Outstanding", value: shortMoney(outstanding) }, { label: "Collected", value: shortMoney(paymentTotal) }, { label: "Accounts due", value: String(dueAccounts) }]);
  $("#fee-agreement-count").textContent = openAccounts.length;
  $("#payment-total-count").textContent = registerCount;
  $("#payment-review-count").textContent = review ? `${review} review` : "";
  $("#payment-review-count").classList.toggle("hidden", !review);
  $("#finance-agreements-tab").setAttribute("aria-label", `Student balances, ${openAccounts.length} active accounts`);
  $("#finance-payments-tab").setAttribute("aria-label", `Payments, ${registerCount} entries${review ? `, ${review} need attention` : ""}`);
  renderAgreementRows(); renderPaymentRows();
  if (ledgerCurrentStudentId) renderStudentLedger(ledgerCurrentStudentId);
}

function renderAgreementRows() {
  const search = $("#agreement-search").value.trim().toLowerCase();
  const filter = $("#agreement-balance-filter").value;
  const rows = state.agreements.map(studentAccount).filter(item => {
    const matchesSearch = !search || [item.studentName, item.admissionNumber].some(value => String(value || "").toLowerCase().includes(search));
    const matchesFilter = !filter || (filter === "closed" ? item.accountClosed : filter === "reconcile" ? !item.accountClosed && item.needsReconciliation : !item.accountClosed && item.balanceState === filter);
    return matchesSearch && matchesFilter;
  });
  const visibleOutstanding = rows.reduce((sum, item) => sum + (item.accountClosed ? 0 : Math.max(item.balance, 0)), 0);
  $("#agreement-result-summary").textContent = `${rows.length} ${rows.length === 1 ? "account" : "accounts"} · ${money(visibleOutstanding)} outstanding`;
  const openLedgerButton = item => `<button class="button button-secondary button-small open-ledger-button" type="button" data-open-ledger="${esc(item.studentId)}" aria-label="Open ledger for ${esc(item.studentName)}">${icon("book")}Ledger</button>`;
  const editAccountButton = item => canAccess("finance", "edit") ? `<button class="icon-button receivable-edit-button" type="button" data-owner-edit="agreement" data-edit-id="${esc(item.id)}" aria-label="Edit fee agreement for ${esc(item.studentName)}" title="Edit fee agreement">${icon("edit")}</button>` : "";
  const balanceBadge = item => item.accountClosed ? `<span class="ledger-balance-state ledger-balance-settled">Closed</span>` : `<span class="ledger-balance-state ledger-balance-${item.balanceState}">${item.balanceState === "credit" ? "Credit" : item.balanceState === "settled" ? "Settled" : "Due"}</span>`;
  $("#agreements-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td class="receivable-student">${studentPrimary(item.studentName, item.admissionNumber)}</td><td class="receivable-fee-summary"><strong class="currency">${money(item.agreed)}</strong><small>${money(item.paid)} paid</small></td><td class="receivable-outstanding"><strong class="currency">${money(Math.abs(item.balance))}</strong>${balanceBadge(item)}</td><td class="receivable-reconciliation">${reconciliationBadge(item)}</td><td class="receivable-actions"><div class="cell-actions">${openLedgerButton(item)}${editAccountButton(item)}</div></td></tr>`).join("") : `<tr><td colspan="5">${emptyState("search", "No matching balances", "Clear a filter to see every student balance.")}</td></tr>`;
  $("#agreements-mobile-list").innerHTML = rows.length ? rows.map(item => `<article class="mobile-record-card receivable-mobile-card"><div class="mobile-record-card-head">${studentPrimary(item.studentName, item.admissionNumber)}${balanceBadge(item)}</div><div class="mobile-record-meta"><div><span>Agreed</span><strong>${money(item.agreed)}</strong></div><div><span>Paid</span><strong>${money(item.paid)}</strong></div><div><span>Balance</span><strong>${money(Math.abs(item.balance))}</strong></div><div><span>Status</span><strong>${item.needsReconciliation ? "Needs attention" : "Up to date"}</strong></div></div><div class="mobile-card-actions">${openLedgerButton(item)}${ownerEditButton("agreement", item.id)}</div></article>`).join("") : emptyState("search", "No matching balances", "Clear a filter to see every student balance.");
}

function renderPaymentRows() {
  const filter = $("#payment-status-filter").value;
  const search = $("#payment-search").value.trim().toLowerCase();
  const today = dateInputValue();
  const entryCategory = item => {
    if (item.type === "scheduled_payment") return "future";
    if (needsPaymentReview(item)) return "review";
    if (item.status === "staged" && item.reconciliationStatus === "do_not_import") return "adjustments";
    if (["refund", "reversal", "void", "balance_credit", "balance_debit"].includes(item.type)) return "adjustments";
    return "received";
  };
  const register = [...state.payments, ...state.installments].sort((a, b) =>
    String(a.date || "9999-12-31").localeCompare(String(b.date || "9999-12-31"))
    || String(a.studentName || "").localeCompare(String(b.studentName || ""))
  );
  const rows = register.filter(item => {
    const matchesStudent = !financeStudentFilter || item.studentId === financeStudentFilter;
    const matchesStatus = !filter || entryCategory(item) === filter;
    const matchesSearch = !search || [item.studentName, item.method, item.sourceNote, item.reference, item.receiptNumber, item.date, item.amount, item.type].some(value => String(value || "").toLowerCase().includes(search));
    return matchesStudent && matchesStatus && matchesSearch;
  });
  const student = financeStudentFilter
    ? register.find(item => item.studentId === financeStudentFilter) || state.agreements.find(item => item.studentId === financeStudentFilter)
    : null;
  $("#payment-student-filter").classList.toggle("hidden", !student);
  $("#payment-student-filter-name").textContent = student?.studentName || "";
  const paymentRows = rows.filter(item => item.type !== "scheduled_payment");
  const installmentRows = rows.filter(item => item.type === "scheduled_payment");
  const total = paymentRows.reduce((sum, item) => sum + Number(item.receivedAmount ?? item.signedAmount ?? item.amount ?? 0), 0);
  $("#payment-result-summary").textContent = `${rows.length} ${rows.length === 1 ? "entry" : "entries"} · ${money(total)} received${installmentRows.length ? ` · ${installmentRows.length} planned` : ""}`;
  const typeLabel = item => ({
    payment: "Payment received",
    reversal: "Reversal",
    refund: "Refund",
    void: "Void",
    balance_credit: "Balance adjustment",
    balance_debit: "Balance adjustment",
    scheduled_payment: "Planned payment",
  }[item.type] || String(item.type || "Entry").replaceAll("_", " "));
  const displayState = item => item.type === "scheduled_payment"
    ? item.status === "cancelled" ? "Cancelled" : item.date < today ? "Overdue" : "Planned"
    : needsPaymentReview(item) ? "Needs attention"
      : item.status === "staged" && item.reconciliationStatus === "do_not_import" ? "Excluded"
        : item.status === "staged" ? "Recorded"
      : ["refund", "reversal", "void", "balance_credit", "balance_debit"].includes(item.type) ? "Adjustment" : "Received";
  const amountLabel = item => {
    const amount = Number(item.signedAmount ?? item.amount ?? 0);
    return amount < 0 ? `−${money(Math.abs(amount))}` : money(amount);
  };
  const sourceLabel = item => item.receiptNumber || item.reference || item.sourceNote || (item.type === "scheduled_payment" ? "Client schedule" : "—");
  const action = item => item.type === "scheduled_payment"
    ? canAccess("finance", "edit") ? `<button class="button button-secondary button-small" type="button" data-installment-edit="${esc(item.id)}">${icon("edit")}Edit</button>` : ""
    : item.status === "staged"
      ? ownerEditButton("payment", item.id, "Review")
      : item.type === "payment" && canManageFinance()
        ? `<button class="button button-secondary button-small" type="button" data-payment-reverse="${esc(item.id)}">${icon("refresh")}Reverse</button>`
        : "";
  $("#payments-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td>${studentPrimary(item.studentName, item.admissionNumber || `Line ${item.line || "—"}`)}</td><td>${esc(typeLabel(item))}</td><td>${formatDate(item.date)}</td><td class="currency">${amountLabel(item)}</td><td>${esc(String(item.method || "Not captured").replaceAll("_", " "))}</td><td title="${esc([item.receiptNumber, item.reference, item.notes || item.sourceNote].filter(Boolean).join(" · "))}"><strong>${esc(sourceLabel(item).slice(0, 32))}</strong>${item.reference && item.receiptNumber ? `<br><small>${esc(item.reference.slice(0, 32))}</small>` : ""}</td><td><div class="cell-actions">${status(displayState(item))}${action(item)}</div></td></tr>`).join("") : `<tr><td colspan="7">${emptyState("search", "No matching payments", "Clear a filter to see every payment.")}</td></tr>`;
  $("#payments-mobile-list").innerHTML = rows.length ? rows.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div>${studentPrimary(item.studentName, formatDate(item.date))}</div>${status(displayState(item))}</div><div class="mobile-record-meta"><div><span>Type</span><strong>${esc(typeLabel(item))}</strong></div><div><span>Amount</span><strong>${amountLabel(item)}</strong></div><div><span>Mode</span><strong>${esc(String(item.method || "Not captured").replaceAll("_", " "))}</strong></div><div><span>Receipt</span><strong>${esc(sourceLabel(item).slice(0, 30))}</strong></div></div>${action(item)}</article>`).join("") : emptyState("search", "No matching payments", "Clear a filter to see every payment.");
}

function activateFinanceTab(name, focus = false) {
  const buttons = $$("[data-finance-tab]");
  buttons.forEach(button => {
    const active = button.dataset.financeTab === name;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
    if (active && focus) button.focus();
  });
  $$(".finance-tab").forEach(panel => {
    const active = panel.id === `finance-${name}-panel`;
    panel.classList.toggle("active", active);
    panel.hidden = !active;
  });
}

function showStudentPayments(studentId) {
  closeStudentLedger(false);
  financeStudentFilter = studentId;
  $("#payment-search").value = "";
  $("#payment-status-filter").value = "";
  activateFinanceTab("payments");
  renderPaymentRows();
  $("#finance-payments-panel").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderStudentLedger(studentId) {
  const agreement = state.agreements.find(item => item.studentId === studentId);
  if (!agreement) { closeStudentLedger(false); return; }
  const account = studentAccount(agreement);
  const student = state.students.find(item => item.id === studentId);
  const payments = [...account.payments].sort((a, b) => String(a.date || "9999-12-31").localeCompare(String(b.date || "9999-12-31")) || Number(a.line || 0) - Number(b.line || 0));
  let runningBalance = account.agreed;
  const transactions = [{
    date: student?.enrollmentDate || null,
    particulars: `${student?.program || "Course"} fee charged`,
    reference: agreement.admissionNumber,
    mode: "—",
    debit: account.agreed,
    credit: null,
    balance: runningBalance,
    note: "Fee agreement"
  }, ...payments.map(item => {
    const effect = Number(item.signedAmount ?? item.amount ?? 0);
    runningBalance -= effect;
    return {
      date: item.date,
      particulars: item.type === "payment" ? "Fee received" : item.type === "balance_credit" || item.type === "balance_debit" ? item.sourceNote || "Balance adjustment" : String(item.type || "Adjustment").replaceAll("_", " ").replace(/^./, value => value.toUpperCase()),
      reference: item.receiptNumber || (item.line ? `Import line ${item.line}` : item.reference || "—"),
      mode: item.method || "Not captured",
      debit: effect < 0 ? Math.abs(effect) : null,
      credit: effect > 0 ? effect : null,
      balance: runningBalance,
      note: item.notes || item.sourceNote || "",
      reconciliationStatus: item.reconciliationStatus
    };
  })];
  const knownDates = transactions.map(item => item.date).filter(Boolean).sort();
  const balanceLabel = account.accountClosed ? "Account balance" : account.balance < 0 ? "Credit balance" : account.balance === 0 ? "Balance settled" : "Outstanding";
  const accountStatus = account.balance < 0 ? "credit" : account.balance === 0 ? "settled" : "due";
  $("#ledger-student-name").textContent = account.studentName;
  $("#ledger-student-meta").textContent = [account.admissionNumber, student?.program, student?.batch].filter(Boolean).join(" · ");
  $("#ledger-period").textContent = knownDates.length ? `${formatDate(knownDates[0])} – ${formatDate(knownDates[knownDates.length - 1])}` : "Current statement";
  $("#ledger-owner-action").innerHTML = ownerEditButton("agreement", account.id, "Edit account");
  $("#ledger-summary").innerHTML = [
    { label: "Agreed fee", value: money(account.agreed), detail: "Account debit" },
    { label: "Paid", value: money(account.paid), detail: `${account.payments.length} ${account.payments.length === 1 ? "payment" : "payments"}` },
    { label: balanceLabel, value: accountBalance(account.balance), detail: accountStatus === "due" ? "Amount receivable" : accountStatus === "credit" ? "Student credit" : "No amount due", featured: true },
    { label: "Account status", value: account.accountClosed ? "Opted out" : accountStatus === "due" ? "Payment due" : accountStatus === "credit" ? "Credit" : "Settled", detail: account.accountClosed ? "Future liability closed" : account.needsReconciliation ? "Control needs review" : "Control matched" }
  ].map(item => `<article class="ledger-summary-card ${item.featured ? "ledger-summary-featured" : ""}"><span>${esc(item.label)}</span><strong>${esc(item.value)}</strong><small>${esc(item.detail)}</small></article>`).join("");
  $("#ledger-table-body").innerHTML = transactions.map(item => `<tr><td>${item.date ? formatDate(item.date) : `<span class="unknown-date">Date unknown</span>`}</td><td><strong>${esc(item.particulars)}</strong>${item.note ? `<small>${esc(item.note)}</small>` : ""}</td><td>${esc(item.reference)}</td><td class="payment-mode">${esc(item.mode)}</td><td class="currency ledger-number">${item.debit == null ? "—" : money(item.debit)}</td><td class="currency ledger-number">${item.credit == null ? "—" : money(item.credit)}</td><td class="currency ledger-number ledger-running-balance">${accountBalance(item.balance)}</td></tr>`).join("");
  $("#ledger-mobile-list").innerHTML = transactions.map(item => `<article class="mobile-record-card ledger-mobile-card"><div class="mobile-record-card-head"><div><h3>${esc(item.particulars)}</h3><p>${item.date ? formatDate(item.date) : "Date unknown"} · ${esc(item.reference)}</p></div><strong class="ledger-mobile-balance">${accountBalance(item.balance)}</strong></div>${item.note ? `<p class="ledger-mobile-note">${esc(item.note)}</p>` : ""}<div class="mobile-record-meta"><div><span>Debit</span><strong>${item.debit == null ? "—" : money(item.debit)}</strong></div><div><span>Credit</span><strong>${item.credit == null ? "—" : money(item.credit)}</strong></div><div><span>Mode</span><strong class="payment-mode">${esc(item.mode)}</strong></div><div><span>Balance</span><strong>${accountBalance(item.balance)}</strong></div></div></article>`).join("");
  const controlDifference = account.difference;
  $("#ledger-control-values").innerHTML = account.clientBalanceEntry
    ? `<div><span>Client-confirmed balance</span><strong>${accountBalance(account.balance)}</strong></div><div><span>Confirmed on</span><strong>${formatDate(account.clientBalanceEntry.date)}</strong></div><div><span>Recorded payments</span><strong>${money(account.paid)}</strong></div><div><span>Review items</span><strong>${account.reviewCount}</strong></div>`
    : `<div><span>Workbook control</span><strong>${money(account.workbookControl)}</strong></div><div><span>Posted payments</span><strong>${money(account.paid)}</strong></div><div><span>Difference</span><strong class="${controlDifference ? "control-difference" : ""}">${controlDifference ? `${money(Math.abs(controlDifference))} ${controlDifference < 0 ? "below" : "above"}` : money(0)}</strong></div><div><span>Review items</span><strong>${account.reviewCount}</strong></div>`;
  injectIcons($("#student-ledger-view"));
}

function openStudentLedger(studentId, trigger = null, updateRoute = true) {
  ledgerCurrentStudentId = studentId;
  ledgerReturnFocus = trigger;
  if (updateRoute) writeOperationsRoute("finance", { kind: "ledger", studentId });
  renderStudentLedger(studentId);
  $("#finance-workspace").classList.add("hidden");
  $("#student-ledger-view").classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "auto" });
  setTimeout(() => $("#ledger-back").focus(), 10);
}

function closeStudentLedger(restoreFocus = true, updateRoute = true) {
  if (!ledgerCurrentStudentId && $("#student-ledger-view").classList.contains("hidden")) return;
  const hadLedgerRoute = Boolean(ledgerCurrentStudentId);
  ledgerCurrentStudentId = "";
  $("#student-ledger-view").classList.add("hidden");
  $("#finance-workspace").classList.remove("hidden");
  if (restoreFocus && ledgerReturnFocus?.isConnected) ledgerReturnFocus.focus();
  ledgerReturnFocus = null;
  if (hadLedgerRoute && updateRoute) writeOperationsRoute("finance");
}

function renderAdmissions() {
  const stageFilter = $("#lead-stage-filter"), current = stageFilter.value;
  stageFilter.innerHTML = `<option value="">All stages</option>${state.stages.map(stage => `<option>${esc(stage)}</option>`).join("")}`; stageFilter.value = current;
  $("#admissions-metrics").innerHTML = compactMetrics([
    { label: "Open enquiries", value: String(state.leads.filter(item => !["Converted", "Lost", "Not Interested"].includes(item.stage)).length) },
    { label: "Follow-ups", value: String(state.leads.filter(item => item.nextFollowUpAt).length) }, { label: "Confirmed", value: String(state.leads.filter(item => item.stage === "Admission Confirmed").length) }, { label: "Converted", value: String(state.leads.filter(item => item.stage === "Converted").length) }
  ]);
  renderLeadRows();
}

function renderLeadRows() {
  const search = $("#lead-search").value.trim().toLowerCase(), stage = $("#lead-stage-filter").value;
  const rows = state.leads.filter(item => (!search || [item.student, item.mobile, item.program].some(value => String(value || "").toLowerCase().includes(search))) && (!stage || item.stage === stage));
  const actions = item => `<div class="cell-actions"><button class="button button-secondary button-small" type="button" data-lead-follow-up="${esc(item.id)}">${icon("message")}Follow-up</button>${item.stage === "Admission Confirmed" && canConvertAdmissions() ? `<button class="button button-primary button-small" type="button" data-lead-convert="${esc(item.id)}">${icon("arrow-right")}Convert</button>` : ""}${ownerEditButton("lead", item.id)}</div>`;
  $("#leads-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td>${studentPrimary(item.student, item.mobile)}</td><td>${esc(item.program || "—")}</td><td>${esc(item.counsellor || "Unassigned")}</td><td>${status(item.stage)}</td><td>${esc(item.nextAction || "—")}</td><td>${actions(item)}</td></tr>`).join("") : `<tr><td colspan="6">${emptyState("spark", state.leads.length ? "No matching enquiries" : "No enquiries", state.leads.length ? "Clear a filter." : "Create an enquiry to begin.")}</td></tr>`;
  $("#leads-mobile-list").innerHTML = rows.map(item => `<article class="mobile-record-card"><div>${studentPrimary(item.student, item.mobile)}${status(item.stage)}</div><div class="mobile-record-meta"><div><span>Program</span><strong>${esc(item.program || "—")}</strong></div><div><span>Next action</span><strong>${esc(item.nextAction || "—")}</strong></div></div>${actions(item)}</article>`).join("");
}

function renderTimetable() {
  const teachingAssignments = state.timetable.teachingAssignments || [];
  const activeAssignments = teachingAssignments.filter(item => item.isActive);
  $("#teaching-assignment-count").textContent = String(activeAssignments.length);
  $("#timetable-faculty-tab").setAttribute("aria-label", `Faculty setup, ${activeAssignments.length} active assignments`);
  const scheduledRows = [...state.sessions].filter(item => item.status === "scheduled").sort((a, b) => asInstant(a.startsAt) - asInstant(b.startsAt));
  const sessionDates = [...new Map(scheduledRows.map(item => [indiaDateKey(item.startsAt), item.startsAt])).entries()];
  const todayKey = indiaDateKey(new Date());
  const futureDates = sessionDates.filter(([key]) => key >= todayKey);
  const availableDates = (futureDates.length ? futureDates : sessionDates.slice(-6)).slice(0, 6);
  if (!availableDates.some(([key]) => key === timetableSelectedDate)) timetableSelectedDate = availableDates[0]?.[0] || "";
  $("#timetable-date-tabs").innerHTML = availableDates.length ? availableDates.map(([key, value]) => {
    const selected = key === timetableSelectedDate;
    const label = timetableDateLabel(value).split(", ");
    return `<button class="timetable-date-tab${selected ? " active" : ""}" type="button" role="tab" aria-selected="${selected}" data-timetable-date="${esc(key)}"><span>${esc(label[0])}</span><strong>${esc(label[1] || label[0])}</strong></button>`;
  }).join("") : "";
  const selectedRows = scheduledRows.filter(item => indiaDateKey(item.startsAt) === timetableSelectedDate);
  const selectedDateValue = availableDates.find(([key]) => key === timetableSelectedDate)?.[1];
  $("#weekly-timetable-range").textContent = selectedDateValue ? timetableDateLabel(selectedDateValue) : "No schedule";
  const orderedBatches = ["Tatva", "Essential", ...new Set(selectedRows.map(item => item.batch).filter(name => !["Tatva", "Essential"].includes(name)))];
  $("#operations-timetable-grid").innerHTML = selectedRows.length ? orderedBatches.filter(batch => selectedRows.some(item => item.batch === batch)).map(batch => {
    const batchRows = selectedRows.filter(item => item.batch === batch);
    return `<section class="timetable-batch-lane" aria-label="${esc(batch)} timetable"><header><span class="timetable-batch-mark">${esc(batch.slice(0, 1))}</span><span><strong>${esc(batch)}</strong><small>${batchRows.length} ${batchRows.length === 1 ? "class" : "classes"}</small></span></header><div class="timetable-slot-list">${batchRows.map(item => `<article class="timetable-slot"><time>${esc(classTime(item.startsAt))}<small>${esc(classTime(item.endsAt))}</small></time><span><strong>${esc(item.subject)}</strong><small>${esc(item.faculty)} · ${esc(item.room)}</small></span>${ownerEditButton("session", item.id, "Edit")}</article>`).join("")}</div></section>`;
  }).join("") : emptyState("clock", "No classes scheduled", "Choose another date or schedule a class.");
  $("#teaching-assignments-table-body").innerHTML = teachingAssignments.length ? teachingAssignments.map(item => `<tr><td>${studentPrimary(item.faculty, item.sessionCount ? `${item.sessionCount} scheduled ${item.sessionCount === 1 ? "class" : "classes"}` : "No classes scheduled")}</td><td>${esc(item.batch)}<br><small>${esc(item.program)}</small></td><td><strong>${esc(item.subject)}</strong><br><small>${esc(item.subjectCode)}</small></td><td>${item.sessionCount}</td><td>${status(item.isActive ? "active" : "inactive")}</td><td>${teachingAssignmentEditButton(item)}</td></tr>`).join("") : `<tr><td colspan="6">${emptyState("users", "No teaching assignments", "Assign a faculty member to a batch and subject.")}</td></tr>`;
  $("#teaching-assignments-mobile-list").innerHTML = teachingAssignments.length ? teachingAssignments.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.faculty)}</h3><p>${esc(item.subject)} · ${esc(item.subjectCode)}</p></div>${status(item.isActive ? "active" : "inactive")}</div><div class="mobile-record-meta"><div><span>Batch</span><strong>${esc(item.batch)}</strong></div><div><span>Classes</span><strong>${item.sessionCount}</strong></div></div>${teachingAssignmentEditButton(item)}</article>`).join("") : emptyState("users", "No teaching assignments", "Assign a faculty member to a batch and subject.");
  activateTimetableView(timetableView);
}

function activateTimetableView(name, focus = false) {
  timetableView = name === "faculty" ? "faculty" : "schedule";
  $$('[data-timetable-view]').forEach(button => {
    const active = button.dataset.timetableView === timetableView;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
    if (active && focus) button.focus();
  });
  $$(".timetable-workspace-panel").forEach(panel => {
    const active = panel.id === `timetable-${timetableView}-panel`;
    panel.classList.toggle("active", active);
    panel.hidden = !active;
  });
  $("#new-session").classList.toggle("hidden", timetableView !== "schedule" || !canAccess("timetable", "create"));
  $("#new-teaching-assignment").classList.toggle("hidden", timetableView !== "faculty" || !canAccess("timetable", "create"));
}

function teachingAssignmentEditButton(item) {
  return canAccess("timetable", "edit") ? `<button class="button button-secondary button-small owner-edit-button" type="button" data-teaching-assignment-edit="${esc(item.id)}">${icon("edit")}Edit</button>` : "";
}

function renderAcademics() {
  const now = Date.now();
  $("#academics-metrics").innerHTML = compactMetrics([{ label: "Assignments", value: String(state.assignments.length) }, { label: "Published", value: String(state.assignments.filter(item => item.status === "published").length) }, { label: "Due", value: String(state.assignments.filter(item => asInstant(item.dueAt).getTime() >= now).length) }, { label: "Recipients", value: String(state.assignments.reduce((sum, item) => sum + Number(item.recipientCount || 0), 0)) }]);
  $("#assignments-table-body").innerHTML = state.assignments.length ? state.assignments.map(item => `<tr><td><strong>${esc(item.title)}</strong><br><small><a href="${esc(item.externalUrl)}" target="_blank" rel="noopener">Open material</a></small></td><td>${esc(item.batch)}<br><small>${esc(item.program || "")}</small></td><td>${esc(item.subject)}</td><td>${formatDateTime(item.dueAt)}</td><td>${item.recipientCount}</td><td><div class="cell-actions">${status(item.status)}${ownerEditButton("assignment", item.id)}</div></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("book", "No assignments")}</td></tr>`;
  $("#assignments-mobile-list").innerHTML = state.assignments.length ? state.assignments.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.title)}</h3><p>${esc(item.subject)} · ${esc(item.batch)}${item.program ? ` · ${esc(item.program)}` : ""}</p></div>${status(item.status)}</div><div class="mobile-record-meta"><div><span>Due</span><strong>${formatDateTime(item.dueAt)}</strong></div><div><span>Students</span><strong>${item.recipientCount}</strong></div></div><div class="mobile-card-actions"><a class="button button-secondary" href="${esc(item.externalUrl)}" target="_blank" rel="noopener">Open material</a>${ownerEditButton("assignment", item.id)}</div></article>`).join("") : emptyState("book", "No assignments");
}

function filteredExaminations() {
  const search = $("#examination-search").value.trim().toLowerCase();
  const filter = $("#examination-status-filter").value;
  return state.examinations.filter(item => {
    const matchesSearch = !search || [item.name, item.batch, item.subject, item.faculty].some(value => String(value || "").toLowerCase().includes(search));
    return matchesSearch && (!filter || item.status === filter);
  });
}

function examinationAction(item) {
  if (item.status === "cancelled") return "";
  if (item.status !== "published" && !canAccess("examinations", "edit")) return `<button class="button button-secondary button-small" type="button" data-examination-open="${esc(item.id)}">${icon("exam")}View</button>`;
  const label = item.status === "published" ? "View results" : item.marksEntered ? "Continue marks" : "Enter marks";
  return `<button class="button button-primary button-small" type="button" data-examination-open="${esc(item.id)}">${icon(item.status === "published" ? "chart" : "exam")}${label}</button>`;
}

function renderExaminations() {
  const exams = filteredExaminations();
  const now = Date.now();
  $("#examination-metrics").innerHTML = compactMetrics([
    { label: "Examinations", value: String(state.examinations.length) },
    { label: "Upcoming", value: String(state.examinations.filter(item => item.status === "scheduled" && asInstant(item.scheduledAt).getTime() >= now).length) },
    { label: "Marks in progress", value: String(state.examinations.filter(item => item.status === "marks_entry").length) },
    { label: "Published", value: String(state.examinations.filter(item => item.status === "published").length) }
  ]);
  $("#examination-result-summary").textContent = `${exams.length} ${exams.length === 1 ? "examination" : "examinations"}`;
  $("#examination-table-body").innerHTML = exams.length ? exams.map(item => {
    const progress = item.participantCount ? Math.round(Number(item.marksEntered || 0) / Number(item.participantCount) * 100) : 0;
    const resultSummary = item.status === "published"
      ? `${item.averageMarks == null ? "—" : item.averageMarks} avg · ${item.highestMarks == null ? "—" : item.highestMarks} high`
      : `${item.marksEntered}/${item.participantCount} entered`;
    return `<tr><td><strong>${esc(item.name)}</strong><br><small>${esc(item.subject)} · ${esc(item.faculty)}</small></td><td>${esc(item.batch)}<br><small>${esc(item.program)}</small></td><td><strong>${formatDateTime(item.scheduledAt)}</strong><br><small>${item.durationMinutes} minutes</small></td><td class="numeric-heading"><strong>${esc(item.maxMarks)}</strong><br><small>Pass ${esc(item.passMarks)}</small></td><td><div class="exam-progress-copy"><strong>${esc(resultSummary)}</strong><span class="exam-progress" aria-label="${progress}% of marks entered"><i style="width:${progress}%"></i></span></div></td><td>${status(item.status)}</td><td><div class="cell-actions examination-actions">${examinationAction(item)}${canAccess("examinations", "edit") && item.status !== "published" ? `<button class="icon-button exam-edit-button" type="button" data-examination-edit="${esc(item.id)}" aria-label="Edit ${esc(item.name)}" title="Edit examination">${icon("edit")}</button>` : ""}</div></td></tr>`;
  }).join("") : `<tr><td colspan="7">${emptyState("exam", state.examinations.length ? "No matching examinations" : "No examinations scheduled", state.examinations.length ? "Clear a filter to see every examination." : "Create an examination for a batch and subject.")}</td></tr>`;
  $("#examination-mobile-list").innerHTML = exams.length ? exams.map(item => `<article class="mobile-record-card examination-mobile-card"><div class="mobile-record-card-head"><div><h3>${esc(item.name)}</h3><p>${esc(item.subject)} · ${esc(item.batch)}</p></div>${status(item.status)}</div><div class="mobile-record-meta"><div><span>Schedule</span><strong>${formatDateTime(item.scheduledAt)}</strong></div><div><span>Maximum</span><strong>${esc(item.maxMarks)} marks</strong></div><div><span>Faculty</span><strong>${esc(item.faculty)}</strong></div><div><span>Results</span><strong>${item.marksEntered}/${item.participantCount} entered</strong></div></div><div class="mobile-card-actions">${examinationAction(item)}${canAccess("examinations", "edit") && item.status !== "published" ? `<button class="button button-secondary button-small" type="button" data-examination-edit="${esc(item.id)}">${icon("edit")}Edit</button>` : ""}</div></article>`).join("") : emptyState("exam", state.examinations.length ? "No matching examinations" : "No examinations scheduled");
}

function renderAttendance() {
  const submitted = state.attendanceSessions.filter(item => item.registerStatus === "submitted").length;
  $("#attendance-metrics").innerHTML = compactMetrics([{ label: "Classes", value: String(state.attendanceSessions.length) }, { label: "Submitted", value: String(submitted) }, { label: "Draft", value: String(state.attendanceSessions.filter(item => item.registerStatus === "draft").length) }, { label: "Pending", value: String(state.attendanceSessions.length - submitted) }]);
  $("#attendance-table-body").innerHTML = state.attendanceSessions.length ? state.attendanceSessions.map(item => `<tr><td><strong>${esc(item.subject)}</strong><br><small>${esc(item.batch)} · ${esc(item.program || "")} · ${formatDateTime(item.startsAt)}</small></td><td>${esc(item.faculty)}</td><td>${esc(item.room)}</td><td>${item.markedCount}/${item.studentCount}</td><td>${status(item.registerStatus)}</td><td><button class="button button-secondary button-small" type="button" data-attendance-id="${esc(item.id)}">Open</button></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("calendar-check", "No attendance registers")}</td></tr>`;
  $("#attendance-mobile-list").innerHTML = state.attendanceSessions.length ? state.attendanceSessions.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.subject)}</h3><p>${esc(item.batch)} · ${esc(item.program || "")} · ${formatDateTime(item.startsAt)}</p></div>${status(item.registerStatus)}</div><div class="mobile-record-meta"><div><span>Faculty</span><strong>${esc(item.faculty)}</strong></div><div><span>Marked</span><strong>${item.markedCount}/${item.studentCount}</strong></div></div><button class="button button-secondary" type="button" data-attendance-id="${esc(item.id)}">Open register</button></article>`).join("") : emptyState("calendar-check", "No attendance registers");
}

function renderCommunication() {
  const threads = state.conversations?.threads || [];
  const openThreads = threads.filter(item => item.status === "open");
  const parentThreads = threads.filter(item => item.originRole === "parent");
  const subjectThreads = threads.filter(item => item.subjectId);
  $("#communication-metrics").innerHTML = compactMetrics([{ label: "Open conversations", value: String(openThreads.length) }, { label: "From parents", value: String(parentThreads.length) }, { label: "Subject conversations", value: String(subjectThreads.length) }, { label: "Published announcements", value: String(state.notices.filter(item => item.status === "published").length) }]);
  $("#communication-thread-count").textContent = `${openThreads.length} open`;
  $("#communication-thread-list").innerHTML = threads.length ? threads.map(item => `<button class="communication-thread" type="button" data-conversation-id="${esc(item.id)}">
    <span class="thread-avatar">${esc(initials(item.studentName))}</span>
    <span class="thread-copy"><span><strong>${esc(item.studentName)}</strong><em>${esc(item.subject)}</em></span><b>${esc(item.topic)}</b><small>${esc(item.lastSender)} · ${esc(item.lastMessage || "Conversation started")}</small></span>
    <span class="thread-meta">${status(item.status)}<time>${formatDateTime(item.lastMessageAt)}</time></span>
  </button>`).join("") : emptyState("message", "No conversations", "Student and parent messages will appear here.");
  $("#notice-list").innerHTML = state.notices.length ? state.notices.map(item => `<article class="surface notice-card"><div class="notice-card-head"><span class="icon-tile">${icon("message")}</span><div class="cell-actions">${status(item.deliveryStatus || item.status)}${ownerEditButton("notice", item.id)}</div></div><h3>${esc(item.title)}</h3><p>${esc(item.body)}</p><footer><span>${esc(item.batch ? `${item.batch} · ${item.program}` : item.audience)}</span><span>${esc(item.channel.replaceAll("_", " "))}</span><time>${formatDateTime(item.publishedAt || item.createdAt)}</time></footer></article>`).join("") : emptyState("message", "No notices");
}

async function refreshConversations() {
  state.conversations = await api("/api/communication/inbox");
  renderCommunication();
}

function conversationMarkup(detail) {
  const messages = detail.messages.map(item => `<article class="conversation-message ${item.senderId === state.user?.id ? "is-mine" : ""}"><header><strong>${esc(item.senderName)}</strong><span>${esc(item.senderRole.replaceAll("_", " "))}</span><time>${formatDateTime(item.createdAt)}</time></header><p>${esc(item.body)}</p></article>`).join("");
  return `<div class="conversation-context"><span>${icon(detail.subjectId ? "book" : "building")}</span><div><strong>${esc(detail.studentName)}</strong><small>${esc(detail.admissionNumber)} · ${esc(detail.subject)}</small></div>${status(detail.status)}</div>
    <div class="conversation-messages">${messages}</div>
    ${detail.canReply ? `<form class="auth-form conversation-reply" id="conversation-reply-form" data-thread-id="${esc(detail.id)}"><label class="field"><span>Reply</span><textarea name="body" rows="4" maxlength="3000" placeholder="Write a clear reply…" required></textarea></label>${formError("conversation-reply-error")}<button class="button button-primary button-large" type="submit">${icon("message")}Send reply</button></form>` : `<div class="inline-notice">${icon("shield")}<span>This conversation is closed.</span></div>`}
    ${detail.canClose ? `<button class="button button-secondary button-large conversation-status-button" type="button" data-thread-status="${detail.status === "open" ? "closed" : "open"}" data-thread-id="${esc(detail.id)}">${detail.status === "open" ? "Close conversation" : "Reopen conversation"}</button>` : ""}`;
}

async function openConversation(threadId) {
  openDrawer("Conversation", '<div class="skeleton-line"></div>');
  try {
    const detail = await api(`/api/communication/threads/${encodeURIComponent(threadId)}`);
    $("#drawer-title").textContent = detail.topic;
    $("#detail-drawer-body").innerHTML = conversationMarkup(detail);
    injectIcons($("#detail-drawer-body"));
    $("#conversation-reply-form")?.addEventListener("submit", async event => {
      event.preventDefault();
      const form = event.currentTarget, button = $('button[type="submit"]', form), body = String(new FormData(form).get("body") || "").trim();
      if (!body) return;
      button.disabled = true;
      try {
        await api(`/api/communication/threads/${encodeURIComponent(threadId)}/messages`, { method: "POST", body: JSON.stringify({ body }) });
        await refreshConversations();
        await openConversation(threadId);
      } catch (error) { showFormError("#conversation-reply-error", error); button.disabled = false; }
    });
    $("[data-thread-status]")?.addEventListener("click", async event => {
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await api(`/api/communication/threads/${encodeURIComponent(threadId)}/status`, { method: "PATCH", body: JSON.stringify({ status: button.dataset.threadStatus }) });
        await refreshConversations();
        await openConversation(threadId);
      } catch (error) { toast(error.message, "error"); button.disabled = false; }
    });
  } catch (error) {
    $("#detail-drawer-body").innerHTML = emptyState("alert", "Could not open conversation", error.message);
  }
}

function inventoryCategory(value) {
  return ({ book: "Book", bag: "Bag", apparel: "Apparel", other: "Other" })[value] || value;
}

function renderInventory() {
  const inventory = state.inventory || { items: [], summary: {} };
  const summary = inventory.summary || {};
  const search = $("#inventory-search").value.trim().toLowerCase();
  const category = $("#inventory-category-filter").value;
  const rows = (inventory.items || []).filter(item =>
    (!search || [item.name, item.sku, item.category].some(value => String(value || "").toLowerCase().includes(search)))
    && (!category || item.category === category)
  );
  $("#new-inventory-item").classList.toggle("hidden", !canManageInventory());
  $("#inventory-metrics").innerHTML = compactMetrics([
    { label: "Stock items", value: String(summary.activeItems || 0) },
    { label: "Units issued", value: String(summary.issuedToStudents || 0) },
    { label: "Students supplied", value: String(summary.studentsWithItems || 0) },
    { label: "Low stock", value: String(summary.lowStock || 0) },
  ]);
  $("#inventory-result-summary").textContent = `${rows.length} of ${(inventory.items || []).length} items`;
  const actions = item => canManageInventory() ? `<div class="cell-actions"><button class="button button-primary button-small" type="button" data-inventory-movement="${esc(item.id)}">${icon("inventory")}Movement</button><button class="button button-secondary button-small" type="button" data-inventory-edit="${esc(item.id)}">${icon("edit")}Edit</button></div>` : "";
  const stockState = item => !item.isActive ? "inactive" : item.quantityOnHand == null ? "quantity pending" : Number(item.quantityOnHand) <= Number(item.reorderLevel || 0) ? "low stock" : "active";
  const quantity = item => item.quantityOnHand == null ? `<strong>Quantity pending</strong><small>Record opening stock</small>` : `<strong>${esc(item.quantityOnHand)} ${esc(item.unit)}</strong><small>Reorder at ${esc(item.reorderLevel || 0)}</small>`;
  $("#inventory-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td>${studentPrimary(item.name, item.vendorReference || item.sourceNote || "ERP entry")}</td><td><strong>${esc(item.sku)}</strong></td><td>${esc(inventoryCategory(item.category))}</td><td>${esc(item.unit)}</td><td><span class="inventory-quantity">${quantity(item)}</span></td><td>${status(stockState(item))}</td><td>${actions(item)}</td></tr>`).join("") : `<tr><td colspan="7">${emptyState("inventory", "No matching inventory items", "Clear a filter or add a new item.")}</td></tr>`;
  $("#inventory-mobile-list").innerHTML = rows.length ? rows.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.name)}</h3><p>${esc(item.sku)} · ${esc(inventoryCategory(item.category))}</p></div>${status(stockState(item))}</div><div class="mobile-record-meta"><div><span>Available</span><strong>${item.quantityOnHand == null ? "Quantity pending" : `${esc(item.quantityOnHand)} ${esc(item.unit)}`}</strong></div><div><span>Reorder level</span><strong>${esc(item.reorderLevel || 0)} ${esc(item.unit)}</strong></div></div>${actions(item)}</article>`).join("") : emptyState("inventory", "No matching inventory items");
  const movements = inventory.recentMovements || [];
  $("#inventory-movement-list").innerHTML = movements.length ? movements.map(item => `<div class="audit-row"><span class="icon-tile">${icon("inventory")}</span><span><strong>${esc(item.itemName)} · ${esc(item.movementType.replaceAll("_", " "))}</strong><small>${esc(item.createdBy)} · ${formatDate(item.occurredOn)}${item.targetReference ? ` · ${esc(item.targetReference)}` : ""} · ${esc(item.reason)}</small></span><em>${item.quantityDelta > 0 ? "+" : ""}${esc(item.quantityDelta)} · ${esc(item.balanceAfter)} left</em></div>`).join("") : emptyState("inventory", "No stock movements", "Record opening stock or an inward, issue, return or adjustment.");
}

function renderReports() {
  const report = state.report;
  if (!report) { $("#report-metrics").innerHTML = metricCard("Access", "Owner only", "shield", true); $("#report-leads").innerHTML = emptyState("shield", "Reports are restricted"); $("#report-attendance").innerHTML = ""; $("#report-audit").innerHTML = ""; return; }
  const metrics = report.metrics || {};
  $("#report-metrics").innerHTML = [metricCard("Students", String(metrics.students || 0), "users", true), metricCard("Attendance", metrics.attendanceRate == null ? "—" : `${metrics.attendanceRate}%`, "calendar-check"), metricCard("Payments", shortMoney(metrics.recordedPayments), "wallet"), metricCard("Upcoming classes", String(metrics.scheduledClasses || 0), "clock")].join("");
  renderBars("#report-leads", report.leadFunnel || [], "stage"); renderBars("#report-attendance", report.attendance || [], "status");
  $("#report-audit").innerHTML = auditRows(report.recentAudit || []);
}

async function downloadReport(reportName, button) {
  button.disabled = true;
  try {
    const response = await fetch(`/api/reports/export/${encodeURIComponent(reportName)}`, {
      headers: { Authorization: `Bearer ${state.token}` },
      cache: "no-store",
    });
    if (!response.ok) {
      let message = "The report could not be generated.";
      try {
        const body = await response.json();
        message = typeof body.detail === "string" ? body.detail : body.detail?.message || message;
      } catch {}
      throw new Error(message);
    }
    const blob = await response.blob();
    const disposition = response.headers.get("content-disposition") || "";
    const filename = disposition.match(/filename="([^"]+)"/)?.[1] || `lakshya-${reportName}.csv`;
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast(`${reportName.replaceAll("_", " ")} report downloaded.`);
  } catch (error) {
    toast(error.message, "error");
  } finally {
    button.disabled = false;
  }
}

function renderBars(selector, rows, labelKey) {
  const max = Math.max(...rows.map(item => item.count), 1);
  $(selector).innerHTML = rows.length ? rows.map(item => `<div class="program-row"><span>${esc(item[labelKey])}</span><div class="program-track"><div class="program-fill" style="width:${Math.round(item.count / max * 100)}%"></div></div><strong>${item.count}</strong></div>`).join("") : emptyState("chart", "No data");
}

function auditRows(rows) { return rows.length ? rows.map(item => `<div class="audit-row"><span class="icon-tile">${icon("shield")}</span><span><strong>${esc(item.action.replaceAll(".", " "))}</strong><small>${esc(item.actor || "System")} · ${formatDateTime(item.createdAt)}</small></span><em>${esc(item.entityType || "record")}</em></div>`).join("") : emptyState("shield", "No activity"); }

function settingsAccountGroup(role = "") {
  if (["student", "parent_student"].includes(role)) return "student";
  if (role === "parent") return "parent";
  if (role === "faculty") return "faculty";
  if (role === "attendance_operator") return "attendance";
  return "staff";
}

function settingsAccountLabel(role = "") {
  const labels = {
    student: "Student portal",
    parent_student: "Student portal",
    parent: "Parent portal",
    faculty: "Faculty portal",
    attendance_operator: "Attendance desk",
    owner: "Owner",
    academic_coordinator: "Academic coordinator",
    admissions_manager: "Admissions manager",
    counsellor: "Counsellor",
    front_desk: "Front desk",
    accounts: "Accounts",
    storekeeper: "Storekeeper",
  };
  return labels[role] || String(role || "Staff").replaceAll("_", " ");
}

function canConfigureOperationsAccess(item) {
  return item && !["owner", "student", "parent", "parent_student"].includes(item.role);
}

function settingsPermissionsButton(item) {
  if (!canConfigureOperationsAccess(item)) return "";
  return `<button class="button button-secondary button-small" type="button" data-user-permissions="${esc(item.id)}">${icon("shield")}Access</button>`;
}

function renderSettingsAccounts() {
  const masters = state.masters;
  const studentLinks = new Map((masters.studentAccess || []).map(item => [item.userId, item]));
  const parentLinks = new Map((masters.parentAccess || []).map(item => [item.userId, item]));
  const query = settingsAccountSearch.trim().toLowerCase();
  const rows = (masters.users || []).filter(item => {
    const group = settingsAccountGroup(item.role);
    const student = studentLinks.get(item.id);
    const parent = parentLinks.get(item.id);
    const searchable = [item.fullName, item.mobile, item.email, item.role, student?.admissionNumber, parent?.admissionNumber, parent?.studentName].filter(Boolean).join(" ").toLowerCase();
    return (settingsAccountFilter === "all" || group === settingsAccountFilter) && (!query || searchable.includes(query));
  });
  $("#settings-account-count").textContent = `${rows.length} of ${(masters.users || []).length} accounts`;
  $("#settings-users").innerHTML = rows.length ? rows.map(item => {
    const student = studentLinks.get(item.id);
    const parent = parentLinks.get(item.id);
    const context = student?.admissionNumber || (parent ? `${parent.studentName} · ${parent.admissionNumber}` : item.email || "Institute account");
    const accessCopy = canConfigureOperationsAccess(item)
      ? `${Object.values(item.permissions || {}).filter(permission => permission.read).length} modules`
      : settingsAccountGroup(item.role) === "staff" ? "Operations" : "Portal access";
    return `<div class="settings-account-row"><span class="settings-account-identity"><i>${esc(initials(item.fullName))}</i><span><strong>${esc(item.fullName)}</strong><small>${esc(context)}</small></span></span><span class="settings-account-access"><strong>${esc(settingsAccountLabel(item.role))}</strong><small>${esc(accessCopy)}</small></span><span class="settings-account-login"><strong>${esc(mobileLabel(item.mobile))}</strong><small>${item.mobile ? "Mobile login" : "Setup required"}</small></span><span class="settings-account-status">${status(item.isActive ? "active" : "inactive")}</span><span class="settings-account-edit">${settingsPermissionsButton(item)}${ownerEditButton("user", item.id)}</span></div>`;
  }).join("") : emptyState("search", "No matching accounts", "Try another name, mobile number or access type.");
}

function openUserPermissions(userId) {
  const user = (state.masters.users || []).find(item => item.id === userId);
  if (!canConfigureOperationsAccess(user)) {
    toast(user?.role === "owner" ? "Owner access is always unrestricted." : "Portal accounts do not use Operations permissions.", "error");
    return;
  }
  const modules = state.masters.permissionModules?.length
    ? state.masters.permissionModules
    : OPERATIONS_MODULES.map(key => ({ key, label: PERMISSION_MODULE_LABELS[key] }));
  const rows = modules.map(module => {
    const permission = user.permissions?.[module.key] || { read: false, create: false, edit: false };
    return `<div class="permission-row" role="group" aria-label="${esc(module.label)} permissions" data-permission-module="${esc(module.key)}"><strong>${esc(module.label)}</strong><label><input type="checkbox" data-permission-action="read"${checked(permission.read)}><span>View</span></label><label><input type="checkbox" data-permission-action="create"${checked(permission.create)}><span>Add</span></label><label><input type="checkbox" data-permission-action="edit"${checked(permission.edit)}><span>Edit</span></label></div>`;
  }).join("");
  openDrawer("Module access", `<form class="permission-form" id="user-permissions-form" data-user-id="${esc(user.id)}"><div class="permission-person"><span>${esc(initials(user.fullName))}</span><div><strong>${esc(user.fullName)}</strong><small>${esc(settingsAccountLabel(user.role))} · ${user.hasCustomPermissions ? "Custom access" : "Role defaults"}</small></div></div><div class="permission-presets" aria-label="Permission presets"><button class="button button-secondary button-small" type="button" data-permission-preset="read">View only</button><button class="button button-secondary button-small" type="button" data-permission-preset="full">Full access</button><button class="button button-quiet button-small" type="button" data-permission-preset="none">Clear</button></div><div class="permission-matrix-head" aria-hidden="true"><span>Module</span><span>View</span><span>Add</span><span>Edit</span></div><div class="permission-matrix">${rows}</div><p class="permission-help">Add and Edit always require View access. Changes apply to this person only and are enforced by the server.</p>${formError("user-permissions-error")}<button class="button button-primary button-large" type="submit">${icon("shield")}Save access</button></form>`);
  const form = $("#user-permissions-form");
  form.addEventListener("change", event => {
    const row = event.target.closest("[data-permission-module]");
    if (!row) return;
    const read = $('[data-permission-action="read"]', row);
    const create = $('[data-permission-action="create"]', row);
    const edit = $('[data-permission-action="edit"]', row);
    if (event.target === read && !read.checked) { create.checked = false; edit.checked = false; }
    if ((event.target === create || event.target === edit) && event.target.checked) read.checked = true;
  });
  form.addEventListener("click", event => {
    const preset = event.target.closest("[data-permission-preset]")?.dataset.permissionPreset;
    if (!preset) return;
    $$('[data-permission-module]', form).forEach(row => {
      $('[data-permission-action="read"]', row).checked = preset !== "none";
      $('[data-permission-action="create"]', row).checked = preset === "full";
      $('[data-permission-action="edit"]', row).checked = preset === "full";
    });
  });
  form.addEventListener("submit", submitUserPermissions);
}

async function submitUserPermissions(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  button.disabled = true;
  const permissions = Object.fromEntries($$('[data-permission-module]', form).map(row => [row.dataset.permissionModule, {
    read: $('[data-permission-action="read"]', row).checked,
    create: $('[data-permission-action="create"]', row).checked,
    edit: $('[data-permission-action="edit"]', row).checked,
  }]));
  try {
    const result = await api(`/api/settings/users/${encodeURIComponent(form.dataset.userId)}/permissions`, { method: "PUT", body: JSON.stringify({ permissions }) });
    const user = state.masters.users.find(item => item.id === form.dataset.userId);
    if (user) { user.permissions = result.permissions; user.hasCustomPermissions = true; }
    closeDetail();
    renderSettingsAccounts();
    toast("Module access updated.");
  } catch (error) {
    showFormError("#user-permissions-error", error);
    button.disabled = false;
  }
}

function showSettingsSection(section = "accounts") {
  settingsSection = ["accounts", "academics", "audit"].includes(section) ? section : "accounts";
  $$('[data-settings-section]').forEach(button => {
    const active = button.dataset.settingsSection === settingsSection;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
  });
  $$('[data-settings-panel]').forEach(panel => { panel.hidden = panel.dataset.settingsPanel !== settingsSection; });
}

function renderSettings() {
  const masters = state.masters;
  const facultyAccess = (masters.users || []).filter(item => item.role === "faculty");
  const attendanceAccess = (masters.users || []).filter(item => item.role === "attendance_operator");
  const staffAccess = (masters.users || []).filter(item => settingsAccountGroup(item.role) === "staff");
  $("#settings-metrics").innerHTML = compactMetrics([{ label: "All accounts", value: String(masters.users?.length || 0) }, { label: "Students", value: String(masters.studentAccess?.length || 0) }, { label: "Parents", value: String(masters.parentAccess?.length || 0) }, { label: "Staff", value: String(staffAccess.length + facultyAccess.length + attendanceAccess.length) }]);
  $("#settings-account-search").value = settingsAccountSearch;
  $("#settings-account-filter").value = settingsAccountFilter;
  renderSettingsAccounts();
  const academicImport = masters.academicImports?.[0];
  $("#academic-import-status").textContent = academicImport ? "Loaded" : "Not loaded";
  $("#academic-import-message").textContent = academicImport
    ? "Import completed. Source rows remain auditable."
    : "Owner-only import. Select the reviewed academic JSON file.";
  $("#academic-import-message").classList.remove("error");
  $("#settings-academic-import").innerHTML = academicImport
    ? masterRows([academicImport], item => [`${item.activeStudents} students · ${item.attendanceEntries} attendance marks`, `${item.subjectSelections} subject selections · ${item.sourceRecords} source rows`, item.unresolvedItems ? "review" : "ready"])
    : `<div class="master-empty">No academic workbook imported</div>`;
  $("#settings-batches").innerHTML = masterRows(masters.batches || [], item => [item.name, item.program, item.isActive ? "active" : "inactive"], "batch");
  $("#settings-subjects").innerHTML = masterRows(masters.subjects || [], item => [item.name, `${item.code} · ${item.program}`, item.isActive ? "active" : "inactive"], "subject");
  $("#settings-rooms").innerHTML = masterRows(masters.rooms || [], item => [item.name, `${item.capacity} seats`, item.isActive ? "active" : "inactive"], "room");
  $("#settings-audit").innerHTML = auditRows(state.audit);
  showSettingsSection(settingsSection);
}

function openSettingsAccountPicker() {
  openDrawer("Add account", `<div class="settings-access-picker"><p>Choose where this person will sign in.</p><button type="button" data-settings-account-type="student"><span>${icon("users")}</span><span><strong>Student</strong><small>Link an enrolled student to the Student portal.</small></span>${icon("chevron-right")}</button><button type="button" data-settings-account-type="parent"><span>${icon("shield")}</span><span><strong>Parent</strong><small>Link a parent or contact to one student.</small></span>${icon("chevron-right")}</button><button type="button" data-settings-account-type="faculty"><span>${icon("book")}</span><span><strong>Faculty</strong><small>Create access for a teacher or professor.</small></span>${icon("chevron-right")}</button><button type="button" data-settings-account-type="attendance"><span>${icon("calendar-check")}</span><span><strong>Attendance desk</strong><small>Create access for the attendance operator.</small></span>${icon("chevron-right")}</button><button type="button" data-settings-account-type="staff"><span>${icon("building")}</span><span><strong>Other staff</strong><small>Admissions, accounts, front desk or administration.</small></span>${icon("chevron-right")}</button></div>`);
}

async function importAcademicData(event) {
  const input = event.currentTarget;
  const file = input.files?.[0];
  if (!file) return;
  input.disabled = true;
  $("#academic-import-status").textContent = "Importing…";
  $("#academic-import-message").textContent = "Validating and saving the workbook data…";
  $("#academic-import-message").classList.remove("error");
  try {
    const payload = JSON.parse(await file.text());
    const result = await api("/api/settings/imports/academic", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    const [masters, students] = await Promise.all([
      api("/api/settings/bootstrap"),
      fetchAll("/api/students"),
    ]);
    state.masters = masters;
    state.students = students;
    renderAll();
    toast(`${result.active_students} academic records imported.`);
  } catch (error) {
    const message = error instanceof SyntaxError ? "Select the reviewed academic JSON file." : error.message;
    $("#academic-import-status").textContent = "Failed";
    $("#academic-import-message").textContent = message;
    $("#academic-import-message").classList.add("error");
    toast(message, "error");
  } finally {
    input.value = "";
    input.disabled = false;
  }
}

function masterRows(rows, map, editKind = "", idKey = "id") { return rows.length ? rows.map(item => { const [title, detail, stateValue] = map(item); return `<div class="master-row"><span><strong>${esc(title)}</strong><small>${esc(detail)}</small></span><div class="cell-actions">${status(stateValue)}${editKind && item[idKey] ? ownerEditButton(editKind, item[idKey]) : ""}</div></div>`; }).join("") : `<div class="master-empty">No records</div>`; }

async function openStudent(studentId, updateRoute = true) {
  if (state.view !== "students") showView("students", false);
  detailRouteStudentId = studentId;
  if (updateRoute) writeOperationsRoute("students", { kind: "student", studentId });
  const drawer = $("#detail-drawer"), body = $("#detail-drawer-body");
  if (!drawer.classList.contains("open")) detailReturnFocus = document.activeElement;
  drawer.classList.add("open"); $("#detail-overlay").classList.add("open"); drawer.setAttribute("aria-hidden", "false");
  syncBodyScrollLock();
  body.innerHTML = '<div class="skeleton-line"></div>';
  setTimeout(() => $("#detail-close").focus(), 10);
  try {
    const [student, inventory] = await Promise.all([
      api(`/api/students/${encodeURIComponent(studentId)}`),
      canReadInventory()
        ? api(`/api/inventory/students/${encodeURIComponent(studentId)}`)
        : Promise.resolve(null),
    ]); $("#drawer-title").textContent = student.fullName;
    const issues = student.migration?.issues || [];
    const academic = student.academicProfile;
    body.innerHTML = `<div class="profile-hero"><span class="record-avatar">${initials(student.fullName)}</span><h3>${esc(student.fullName)}</h3><p>${esc(student.admissionNumber)} · ${esc(student.enrollment?.program || "Program not assigned")}</p></div>
      ${canAccess("students", "edit") ? `<div class="owner-record-actions">${student.status === "active" ? `<button class="button button-danger button-small" type="button" data-student-lifecycle="inactive" data-lifecycle-student-id="${esc(student.id)}" data-lifecycle-student-name="${esc(student.fullName)}">Mark opted out</button>` : ["inactive", "forfeited"].includes(student.status) ? `<button class="button button-primary button-small" type="button" data-student-lifecycle="active" data-lifecycle-student-id="${esc(student.id)}" data-lifecycle-student-name="${esc(student.fullName)}">Reactivate</button>` : ""}${ownerEditButton("student", student.id, "Edit student")}</div>` : ""}
      <section class="detail-section"><h4>Student &amp; enrollment</h4><div class="detail-grid">${detailField("Primary mobile", student.mobile)}${detailField("Secondary mobile", student.secondaryMobile)}${detailField("Previous school", student.previousSchool)}${detailField("Enrollment date", formatDate(student.enrollment?.enrollmentDate))}${detailField("Batch", student.enrollment?.batch)}${detailField("Status", student.status)}</div></section>
      <section class="detail-section"><h4>Academic profile</h4><div class="detail-grid">${detailField("Source student ID", academic?.sourceStudentCode)}${detailField("Mentor", academic?.mentorName)}${detailField("Workbook stream", academic?.sourceStream)}${detailField("Workbook school", academic?.sourceSchoolName)}${detailField("Selected subjects", academic?.subjects?.join(", "))}${detailField("Workbook contact", [academic?.sourcePrimaryMobile, academic?.sourceSecondaryMobile].filter(Boolean).join(", "))}</div></section>
      ${studentInventoryMarkup(student, inventory)}
      <section class="detail-section"><h4>Fee agreement</h4><div class="detail-grid">${detailField("Agreed amount", money(student.feeAgreement?.agreedAmount))}${detailField("Registration", money(student.feeAgreement?.legacyRegistrationTotal))}${detailField("Agreement status", student.feeAgreement?.status)}${detailField("Currency", student.feeAgreement?.currency || "INR")}</div></section>
      <section class="detail-section"><h4>Migration trace</h4><div class="detail-grid">${detailField("Source row", student.migration?.sourceRow)}${detailField("Import readiness", student.migration?.readiness)}</div>${issues.length ? `<div class="issue-list">${issues.map(issue => `<div>${icon("alert")}<span>${esc(typeof issue === "string" ? issue : issue.message || JSON.stringify(issue))}</span></div>`).join("")}</div>` : ""}</section>`;
  } catch (error) { body.innerHTML = emptyState("alert", "Could not open this record", error.message); }
}
function detailField(label, value) { return `<div class="detail-field"><span>${esc(label)}</span><strong>${esc(value || "—")}</strong></div>`; }

function openStudentLifecycleForm(studentId, studentName, targetStatus) {
  if (!canAccess("students", "edit")) { toast("Edit access to Students is required.", "error"); return; }
  const optingOut = targetStatus === "inactive";
  openDrawer(optingOut ? `Mark opted out · ${studentName}` : `Reactivate · ${studentName}`, `<form class="auth-form" id="student-lifecycle-form" data-student-id="${esc(studentId)}" data-target-status="${esc(targetStatus)}">
    <div class="inline-notice${optingOut ? " inline-notice-danger" : ""}">${icon(optingOut ? "alert" : "shield")}<span>${optingOut ? "This closes the unpaid fee balance, cancels future payment plans and disables student and parent portal access. Existing receipts remain in the ledger." : "This restores the previously closed fee liability and portal access. Cancelled payment plans stay cancelled and can be rescheduled if needed."}</span></div>
    <label class="field"><span>Reason</span><textarea name="reason" rows="4" minlength="3" maxlength="500" placeholder="${optingOut ? "Example: Student discontinued the course" : "Example: Student rejoined the course"}" required></textarea><small>This note is stored in the audit trail and fee adjustment.</small></label>
    ${formError("student-lifecycle-error")}
    <button class="button ${optingOut ? "button-danger" : "button-primary"} button-large" type="submit">${optingOut ? "Confirm opt-out" : "Reactivate student"}</button>
  </form>`);
  $("#student-lifecycle-form").addEventListener("submit", submitStudentLifecycle);
}

async function refreshStudentAndFinanceState() {
  const [students, agreements, payments, installments] = await Promise.all([
    fetchAll("/api/students"),
    fetchAll("/api/finance/agreements"),
    fetchAll("/api/finance/transactions"),
    fetchAll("/api/finance/installments"),
  ]);
  state.students = students;
  state.agreements = agreements;
  state.payments = payments;
  state.installments = installments;
}

async function submitStudentLifecycle(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('button[type="submit"]', form);
  button.disabled = true;
  try {
    const result = await api(`/api/students/${encodeURIComponent(form.dataset.studentId)}/status`, {
      method: "PATCH",
      body: JSON.stringify({
        status: form.dataset.targetStatus,
        reason: String(new FormData(form).get("reason") || "").trim(),
      }),
    });
    await refreshStudentAndFinanceState();
    closeDetail();
    renderAll();
    const adjustment = Number(result.lifecycle?.adjustmentAmount || 0);
    toast(result.status === "active" ? `Student reactivated${adjustment ? ` · ${money(adjustment)} receivable restored` : ""}.` : `Student opted out${adjustment ? ` · ${money(adjustment)} future liability closed` : ""}.`);
  } catch (error) {
    showFormError("#student-lifecycle-error", error);
    button.disabled = false;
  }
}

function studentInventoryMarkup(student, inventory) {
  if (!inventory) return "";
  const holdings = inventory.holdings || [];
  const history = inventory.history || [];
  const summary = inventory.summary || {};
  const holdingRows = holdings.length
    ? holdings.map(item => `<article class="student-stock-item">
        <span class="student-stock-icon">${icon("inventory")}</span>
        <span class="student-stock-copy"><strong>${esc(item.itemName)}</strong><small>${esc(item.sku)} · ${esc(inventoryCategory(item.category))} · issued ${formatDate(item.lastIssuedOn)}</small></span>
        <span class="student-stock-quantity"><strong>${esc(item.quantityIssued)}</strong><small>${esc(item.unit)}</small></span>
        ${canManageInventory() ? `<button class="button button-secondary button-small" type="button" data-student-inventory-return="${esc(item.itemId)}" data-inventory-student-id="${esc(student.id)}">Return</button>` : ""}
      </article>`).join("")
    : `<div class="student-stock-empty">${icon("inventory")}<span><strong>No items currently issued</strong><small>Books, bags and apparel issued to this student will appear here.</small></span></div>`;
  const historyRows = history.slice(0, 12).map(item => {
    const issued = item.movementType === "issue";
    return `<div class="student-stock-history-row"><span class="student-stock-history-mark ${issued ? "is-issue" : "is-return"}">${issued ? "−" : "+"}</span><span><strong>${issued ? "Issued" : "Returned"} · ${esc(item.itemName)}</strong><small>${formatDate(item.occurredOn)} · ${esc(item.createdBy)}${item.reference ? ` · ${esc(item.reference)}` : ""}</small></span><em>${esc(Math.abs(item.quantityDelta))} ${esc((inventory.availableItems || []).find(row => row.id === item.itemId)?.unit || "piece")}</em></div>`;
  }).join("");
  return `<section class="detail-section student-stock-section">
    <div class="detail-section-heading"><div><h4>Inventory issued</h4><p>Student issues automatically update available stock.</p></div>${canManageInventory() ? `<button class="button button-primary button-small" type="button" data-student-inventory-issue="${esc(student.id)}">${icon("plus")}Issue item</button>` : ""}</div>
    <div class="student-stock-summary"><span><strong>${esc(summary.itemTypes || 0)}</strong><small>Item types</small></span><span><strong>${esc(summary.issuedUnits || 0)}</strong><small>Units with student</small></span><span><strong>${esc(summary.transactions || 0)}</strong><small>Transactions</small></span></div>
    <div class="student-stock-list">${holdingRows}</div>
    ${historyRows ? `<details class="student-stock-history"><summary>Transaction history <span>${esc(history.length)}</span></summary><div>${historyRows}</div></details>` : ""}
  </section>`;
}

async function refreshStudentInventory(studentId) {
  state.inventory = await api("/api/inventory/bootstrap");
  loadedResources.add("inventory");
  $("#nav-inventory-count").textContent = state.inventory.items?.length || 0;
  renderInventory();
  injectIcons($("#inventory"));
  await openStudent(studentId, false);
}

async function openStudentInventoryIssue(studentId) {
  if (!canManageInventory()) { toast("Inventory access is required.", "error"); return; }
  try {
    const inventory = await api(`/api/inventory/students/${encodeURIComponent(studentId)}`);
    const issuable = (inventory.availableItems || []).filter(item => item.isActive && Number(item.quantityOnHand || 0) > 0);
    if (!issuable.length) {
      openDrawer("Issue inventory", `<div class="student-stock-unavailable">${icon("inventory")}<h3>No stock is ready to issue</h3><p>Record opening quantities or receive stock in the Inventory module first.</p><button class="button button-primary button-large" type="button" data-view-target="inventory">Open inventory</button></div>`);
      return;
    }
    openDrawer(`Issue inventory · ${inventory.studentName}`, `<form class="auth-form" id="student-inventory-issue-form">
      <div class="inline-notice">${icon("inventory")}<span>This creates an auditable student issue and reduces available inventory immediately.</span></div>
      <label class="field"><span>Item</span><select name="itemId" required><option value="">Select an item</option>${issuable.map(item => `<option value="${esc(item.id)}" data-balance="${esc(item.quantityOnHand)}">${esc(item.name)} · ${esc(item.quantityOnHand)} ${esc(item.unit)} available</option>`).join("")}</select></label>
      <div class="form-pair"><label class="field"><span>Quantity</span><input name="quantity" type="number" min="1" step="1" value="1" inputmode="numeric" required></label><label class="field"><span>Issue date</span><input name="occurredOn" type="date" value="${dateInputValue()}" required></label></div>
      <label class="field"><span>Reference <small>(optional)</small></span><input name="reference" maxlength="255" placeholder="Receipt or kit reference"></label>
      <label class="field"><span>Notes</span><textarea name="reason" rows="3" minlength="3" maxlength="2000" required>Issued to student</textarea></label>
      ${formError("student-inventory-issue-error")}
      <button class="button button-primary button-large" type="submit">${icon("inventory")}Issue and update stock</button>
    </form>`);
    const form = $("#student-inventory-issue-form");
    const syncMaximum = () => {
      const selectedOption = form.elements.itemId.selectedOptions[0];
      form.elements.quantity.max = selectedOption?.dataset.balance || "";
    };
    form.elements.itemId.addEventListener("change", syncMaximum);
    syncMaximum();
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const data = new FormData(form), button = $('button[type="submit"]', form);
      button.disabled = true;
      try {
        await api(`/api/inventory/items/${encodeURIComponent(data.get("itemId"))}/movements`, {
          method: "POST",
          body: JSON.stringify({
            movementType: "issue",
            quantity: Number(data.get("quantity")),
            occurredOn: data.get("occurredOn"),
            targetType: "student",
            studentId,
            reference: String(data.get("reference") || "").trim() || null,
            reason: String(data.get("reason") || "").trim(),
          }),
        });
        await refreshStudentInventory(studentId);
        toast("Item issued and stock updated.");
      } catch (error) {
        showFormError("#student-inventory-issue-error", error);
        button.disabled = false;
      }
    });
  } catch (error) { toast(error.message, "error"); }
}

async function openStudentInventoryReturn(studentId, itemId) {
  if (!canManageInventory()) { toast("Inventory access is required.", "error"); return; }
  try {
    const inventory = await api(`/api/inventory/students/${encodeURIComponent(studentId)}`);
    const holding = (inventory.holdings || []).find(item => item.itemId === itemId);
    if (!holding) { toast("This item is no longer issued to the student.", "error"); await openStudent(studentId, false); return; }
    openDrawer(`Return inventory · ${holding.itemName}`, `<form class="auth-form" id="student-inventory-return-form">
      <div class="inline-notice">${icon("inventory")}<span><strong>${esc(holding.quantityIssued)} ${esc(holding.unit)}</strong> currently ${holding.quantityIssued === 1 ? "is" : "are"} with ${esc(inventory.studentName)}. The return will restore available stock.</span></div>
      <div class="form-pair"><label class="field"><span>Return quantity</span><input name="quantity" type="number" min="1" max="${esc(holding.quantityIssued)}" step="1" value="1" inputmode="numeric" required></label><label class="field"><span>Return date</span><input name="occurredOn" type="date" value="${dateInputValue()}" required></label></div>
      <label class="field"><span>Reference <small>(optional)</small></span><input name="reference" maxlength="255" placeholder="Return receipt or correction reference"></label>
      <label class="field"><span>Reason</span><textarea name="reason" rows="3" minlength="3" maxlength="2000" required>Returned by student</textarea></label>
      ${formError("student-inventory-return-error")}
      <button class="button button-primary button-large" type="submit">${icon("refresh")}Return and restore stock</button>
    </form>`);
    const form = $("#student-inventory-return-form");
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const data = new FormData(form), button = $('button[type="submit"]', form);
      button.disabled = true;
      try {
        await api(`/api/inventory/items/${encodeURIComponent(itemId)}/movements`, {
          method: "POST",
          body: JSON.stringify({
            movementType: "return",
            quantity: Number(data.get("quantity")),
            occurredOn: data.get("occurredOn"),
            targetType: "student",
            studentId,
            reference: String(data.get("reference") || "").trim() || null,
            reason: String(data.get("reason") || "").trim(),
          }),
        });
        await refreshStudentInventory(studentId);
        toast("Return recorded and stock restored.");
      } catch (error) {
        showFormError("#student-inventory-return-error", error);
        button.disabled = false;
      }
    });
  } catch (error) { toast(error.message, "error"); }
}

function closeDetail(restoreFocus = true, updateRoute = true) {
  const drawer = $("#detail-drawer");
  const wasOpen = drawer.classList.contains("open");
  const closedStudentRoute = detailRouteStudentId;
  detailRouteStudentId = "";
  drawer.classList.remove("open", "detail-drawer-wide");
  $("#detail-overlay").classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
  syncBodyScrollLock();
  if (wasOpen && restoreFocus && detailReturnFocus?.isConnected) detailReturnFocus.focus();
  detailReturnFocus = null;
  if (closedStudentRoute && updateRoute) writeOperationsRoute("students");
}

function openStudentCreateForm() {
  if (!canAccess("students", "create")) { toast("Add access to Students is required.", "error"); return; }
  openDrawer("Add student", `<form class="auth-form" id="student-create-form">
    <label class="field"><span>Student name</span><input name="fullName" autocomplete="name" required></label>
    <div class="form-pair"><label class="field"><span>Primary mobile <small>(optional)</small></span><input name="mobile" type="tel" inputmode="tel" autocomplete="tel" placeholder="10-digit mobile number" maxlength="16"></label><label class="field"><span>Secondary mobile <small>(optional)</small></span><input name="secondaryMobile" type="tel" inputmode="tel" placeholder="10-digit mobile number" maxlength="16"></label></div>
    <div class="form-pair"><label class="field"><span>Email <small>(optional)</small></span><input name="email" type="email" autocomplete="email"></label><label class="field"><span>Previous school <small>(optional)</small></span><input name="previousSchool"></label></div>
    <div class="form-pair"><label class="field"><span>Program</span><select name="program" required><option value="">Select program</option>${STUDENT_PROGRAM_ORDER.map(program => `<option value="${esc(program)}">${esc(program)}</option>`).join("")}</select></label><label class="field"><span>Batch</span><select name="batch" required><option value="">Select batch</option>${STUDENT_BATCH_ORDER.map(batch => `<option value="${esc(batch)}">${esc(batch)}</option>`).join("")}</select></label></div>
    <fieldset class="choice-fieldset"><legend>Subjects</legend><div class="choice-grid">${["Physics", "Chemistry", "Mathematics", "Biology"].map(subject => `<label class="check-field"><input name="subjects" type="checkbox" value="${subject}"><span>${subject}</span></label>`).join("")}</div><small>Select every subject this student will attend.</small></fieldset>
    <label class="field"><span>Agreed course fee</span><input name="agreedAmount" type="number" min="0" step="1" inputmode="numeric" required></label>
    <div class="form-pair"><label class="field"><span>Enrollment date</span><input name="enrollmentDate" type="date" value="${dateInputValue()}" required></label><label class="field"><span>Student status</span><select name="status"><option value="active">Active</option><option value="draft">Draft</option></select></label></div>
    <div class="immutable-record-note">${icon("shield")}<span>Admission number generated automatically.<small>Enrollment, attendance profile and fee agreement are created together. Portal access remains a separate owner action.</small></span></div>
    ${formError("student-create-error")}
    <button class="button button-primary button-large" type="submit">${icon("plus")}Add student</button>
  </form>`);
  $("#student-create-form").addEventListener("submit", createStudent);
}

async function createStudent(event) {
  event.preventDefault();
  const form = event.currentTarget, formData = new FormData(form), data = Object.fromEntries(formData.entries());
  const button = $('button[type="submit"]', form); button.disabled = true;
  const payload = {
    ...data,
    fullName: String(data.fullName || "").trim(),
    mobile: String(data.mobile || "").trim() || null,
    secondaryMobile: String(data.secondaryMobile || "").trim() || null,
    email: String(data.email || "").trim() || null,
    previousSchool: String(data.previousSchool || "").trim() || null,
    subjects: formData.getAll("subjects"),
    agreedAmount: Number(data.agreedAmount),
  };
  if (!payload.subjects.length) {
    showFormError("#student-create-error", new Error("Select at least one subject."));
    button.disabled = false;
    return;
  }
  try {
    const student = await api("/api/students", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.students = await fetchAll("/api/students");
    state.agreements = await fetchAll("/api/finance/agreements");
    state.report = await optional(() => api("/api/reports/overview"), state.report);
    studentHierarchyState.batch = studentBatchKey(student.batch);
    studentHierarchyState.program = studentProgramKey(student.program);
    closeDetail();
    renderAll();
    toast(`Student added · ${student.admissionNumber}`);
  } catch (error) {
    showFormError("#student-create-error", error);
    button.disabled = false;
  }
}

function openLeadForm() {
  openDrawer("New enquiry", `<form class="auth-form" id="lead-create-form"><label class="field"><span>Student name</span><input name="student" required></label><label class="field"><span>Mobile number</span><input name="mobile" inputmode="numeric" required></label><label class="field"><span>Program</span><select name="program" required><option value="">Select program</option>${STUDENT_PROGRAM_ORDER.map(program => `<option value="${esc(program)}">${esc(program)}</option>`).join("")}</select></label><label class="field"><span>Parent / guardian</span><input name="parent" required></label><label class="field"><span>Counsellor</span><input name="counsellor" value="${esc(state.user?.fullName || "Admissions desk")}" required></label><label class="field"><span>Source</span><select name="source" required><option value="walk-in">Walk-in</option><option value="phone">Phone</option><option value="whatsapp">WhatsApp</option><option value="website">Website</option><option value="referral">Referral</option><option value="campaign">Campaign</option><option value="seminar">Seminar</option><option value="social media">Social media</option></select></label><label class="field"><span>Next action</span><input name="nextAction" placeholder="Call, campus visit, counselling…" required></label><div class="auth-error hidden" id="lead-form-error" role="alert"></div><button class="button button-primary button-large" type="submit">${icon("plus")}Create enquiry</button></form>`);
  $("#lead-create-form").addEventListener("submit", createLead);
}

async function createLead(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget); const button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = Object.fromEntries([...form.entries()].map(([key, value]) => [key, String(value).trim()]));
  try { const lead = await api("/api/admissions/leads", { method: "POST", body: JSON.stringify(payload) }); state.leads.unshift(lead); closeDetail(); renderAdmissions(); $("#nav-leads-count").textContent = state.leads.length; toast("Enquiry created."); }
  catch (error) { $("#lead-form-error").textContent = error.message; $("#lead-form-error").classList.remove("hidden"); button.disabled = false; }
}

function openLeadFollowUpForm(lead) {
  openDrawer(`Follow-up · ${lead.student}`, `<form class="auth-form" id="lead-follow-up-form" data-lead-id="${esc(lead.id)}">
    <label class="field"><span>Activity</span><select name="kind"><option value="call">Call</option><option value="follow_up">Follow-up</option><option value="counselling">Counselling</option><option value="note">Note</option></select></label>
    <label class="field"><span>Outcome / note</span><textarea name="note" rows="4" minlength="2" required></textarea></label>
    <label class="field"><span>Next action <small>(optional)</small></span><input name="nextAction" value="${esc(lead.nextAction || "")}" maxlength="255"></label>
    <label class="field"><span>Next follow-up <small>(optional)</small></span><input name="nextFollowUpAt" type="datetime-local" value="${lead.nextFollowUpAt ? localInputValue(lead.nextFollowUpAt) : ""}"></label>
    ${formError("lead-follow-up-error")}
    <button class="button button-primary button-large" type="submit">${icon("message")}Save follow-up</button>
  </form>`);
  $("#lead-follow-up-form").addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget, data = new FormData(form), button = $('button[type="submit"]', form);
    button.disabled = true;
    try {
      await api(`/api/admissions/leads/${encodeURIComponent(form.dataset.leadId)}/activity`, {
        method: "POST",
        body: JSON.stringify({
          kind: data.get("kind"),
          note: String(data.get("note") || "").trim(),
          nextAction: String(data.get("nextAction") || "").trim() || null,
          nextFollowUpAt: data.get("nextFollowUpAt") ? indiaInputToISOString(data.get("nextFollowUpAt")) : null,
        }),
      });
      state.leads = await fetchAll("/api/admissions/leads");
      closeDetail();
      renderAdmissions();
      toast("Follow-up saved.");
    } catch (error) {
      showFormError("#lead-follow-up-error", error);
      button.disabled = false;
    }
  });
}

function openLeadConversionForm(lead) {
  if (!canConvertAdmissions()) { toast("Admissions manager access is required.", "error"); return; }
  openDrawer(`Convert admission · ${lead.student}`, `<form class="auth-form" id="lead-conversion-form" data-lead-id="${esc(lead.id)}">
    <div class="inline-notice">${icon("shield")}<span>This creates the active student, enrollment, attendance profile and fee agreement in one transaction.</span></div>
    <div class="form-pair"><label class="field"><span>Batch</span><select name="batch" required><option value="">Select batch</option>${STUDENT_BATCH_ORDER.map(batch => `<option value="${batch}">${batch}</option>`).join("")}</select></label><label class="field"><span>Enrollment date</span><input name="enrollmentDate" type="date" value="${dateInputValue()}" required></label></div>
    <fieldset class="choice-fieldset"><legend>Subjects</legend><div class="choice-grid">${["Physics", "Chemistry", "Mathematics", "Biology"].map(subject => `<label class="check-field"><input name="subjects" type="checkbox" value="${subject}"><span>${subject}</span></label>`).join("")}</div></fieldset>
    <label class="field"><span>Agreed course fee</span><input name="agreedAmount" type="number" min="0" step="1" inputmode="numeric" required></label>
    <label class="field"><span>Guardian relationship</span><select name="guardianRelationship"><option value="guardian">Guardian</option><option value="father">Father</option><option value="mother">Mother</option></select></label>
    <label class="check-field"><input name="concessionRequested" type="checkbox"><span>Fee concession requested</span></label>
    ${formError("lead-conversion-error")}
    <button class="button button-primary button-large" type="submit">${icon("arrow-right")}Create student record</button>
  </form>`);
  $("#lead-conversion-form").addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget, data = new FormData(form), button = $('button[type="submit"]', form);
    const subjects = data.getAll("subjects");
    if (!subjects.length) { showFormError("#lead-conversion-error", new Error("Select at least one subject.")); return; }
    button.disabled = true;
    try {
      const result = await api(`/api/admissions/leads/${encodeURIComponent(form.dataset.leadId)}/convert`, {
        method: "POST",
        body: JSON.stringify({
          batch: data.get("batch"),
          enrollmentDate: data.get("enrollmentDate"),
          subjects,
          agreedAmount: Number(data.get("agreedAmount")),
          guardianRelationship: data.get("guardianRelationship"),
          concessionRequested: data.get("concessionRequested") === "on",
        }),
      });
      [state.leads, state.students, state.agreements] = await Promise.all([
        fetchAll("/api/admissions/leads"),
        fetchAll("/api/students"),
        fetchAll("/api/finance/agreements"),
      ]);
      closeDetail();
      renderAll();
      toast(`Admission converted · ${state.students.find(row => row.id === result.studentId)?.admissionNumber || "student created"}`);
    } catch (error) {
      showFormError("#lead-conversion-error", error);
      button.disabled = false;
    }
  });
}

function openDrawer(title, html, wide = false) {
  const drawer = $("#detail-drawer");
  if (!drawer.classList.contains("open")) detailReturnFocus = document.activeElement;
  drawer.classList.toggle("detail-drawer-wide", wide);
  drawer.classList.add("open");
  $("#detail-overlay").classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  $("#drawer-title").textContent = title;
  $("#detail-drawer-body").innerHTML = html;
  injectIcons($("#detail-drawer-body"));
  syncBodyScrollLock();
  setTimeout(() => {
    const firstControl = $('#detail-drawer-body input:not([disabled]), #detail-drawer-body select:not([disabled]), #detail-drawer-body textarea:not([disabled]), #detail-drawer-body button:not([disabled])');
    (firstControl || $("#detail-close")).focus();
  }, 10);
}

function trapDrawerFocus(event) {
  if (event.key !== "Tab" || !$("#detail-drawer").classList.contains("open")) return;
  const focusable = $$('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])', $("#detail-drawer"))
    .filter(node => node.offsetParent !== null);
  if (!focusable.length) return;
  const first = focusable[0], last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}

const options = (rows, label) => rows.map(item => `<option value="${esc(item.id)}">${esc(label(item))}</option>`).join("");
const formError = id => `<div class="auth-error hidden" id="${id}" role="alert"></div>`;
function showFormError(id, error) { const node = $(id); node.textContent = error.message; node.classList.remove("hidden"); }

const studentPickerId = item => item.studentId || item.id;
const studentPickerMobile = item => item.studentMobile || item.mobile || state.students.find(student => student.id === studentPickerId(item))?.mobile || "";
const studentPickerLabel = item => [item.studentName || item.fullName, item.admissionNumber, studentPickerMobile(item) ? mobileLabel(studentPickerMobile(item)) : ""].filter(Boolean).join(" · ");
let studentPickerSequence = 0;

function studentPickerMarkup({ label = "Student", selectedItem = null, scope = "all", placeholder = "Search by name, admission ID or mobile" } = {}) {
  const sequence = ++studentPickerSequence;
  const inputId = `student-picker-input-${sequence}`;
  const resultsId = `student-picker-results-${sequence}`;
  const selectedId = selectedItem ? studentPickerId(selectedItem) : "";
  const selectedLabel = selectedItem ? studentPickerLabel(selectedItem) : "";
  return `<div class="field student-picker" data-student-picker data-picker-scope="${esc(scope)}"><label for="${inputId}">${esc(label)}</label><span class="student-picker-control"><input id="${inputId}" type="search" data-student-picker-input value="${esc(selectedLabel)}" placeholder="${esc(placeholder)}" autocomplete="off" role="combobox" aria-autocomplete="list" aria-controls="${resultsId}" aria-expanded="false" required><input type="hidden" name="studentId" data-student-picker-id value="${esc(selectedId)}"><span class="student-picker-results" id="${resultsId}" data-student-picker-results role="listbox" hidden></span></span><small>Type a name, admission ID or mobile number and select one verified record.</small></div>`;
}

function bindStudentPicker(form) {
  const picker = $("[data-student-picker]", form);
  const input = $("[data-student-picker-input]", form);
  const hidden = $("[data-student-picker-id]", form);
  const results = $("[data-student-picker-results]", form);
  if (!picker || !input || !hidden || !results) return;
  const scope = picker.dataset.pickerScope || "all";
  let available = [];
  let activeIndex = -1;
  let timer = null;
  let requestSequence = 0;
  let chosenLabel = input.value.trim();

  const closeResults = () => {
    results.hidden = true;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
    activeIndex = -1;
  };
  const setActive = index => {
    const buttons = $$("[data-student-picker-option]", results);
    if (!buttons.length) return;
    activeIndex = Math.max(0, Math.min(index, buttons.length - 1));
    buttons.forEach((button, position) => button.classList.toggle("active", position === activeIndex));
    input.setAttribute("aria-activedescendant", buttons[activeIndex].id);
    buttons[activeIndex].scrollIntoView({ block: "nearest" });
  };
  const choose = item => {
    hidden.value = studentPickerId(item);
    input.value = studentPickerLabel(item);
    chosenLabel = input.value.trim();
    input.setCustomValidity("");
    closeResults();
  };
  const renderResults = rows => {
    available = rows;
    results.innerHTML = rows.length
      ? rows.map((item, index) => `<button class="student-picker-option" id="student-picker-option-${normalize(studentPickerId(item))}-${index}" type="button" role="option" data-student-picker-option="${esc(studentPickerId(item))}"><strong>${esc(item.fullName || item.studentName)}</strong><small>${esc([item.admissionNumber, studentPickerMobile(item) ? mobileLabel(studentPickerMobile(item)) : "Mobile not assigned"].filter(Boolean).join(" · "))}</small></button>`).join("")
      : `<span class="student-picker-empty">No eligible students found.</span>`;
    results.hidden = false;
    input.setAttribute("aria-expanded", "true");
    activeIndex = -1;
  };
  const load = async () => {
    const sequence = ++requestSequence;
    results.innerHTML = `<span class="student-picker-empty">Searching…</span>`;
    results.hidden = false;
    input.setAttribute("aria-expanded", "true");
    try {
      const response = await api(`/api/students/picker?scope=${encodeURIComponent(scope)}&limit=20&search=${encodeURIComponent(input.value.trim())}`);
      if (sequence !== requestSequence) return;
      renderResults(response.items || []);
    } catch (error) {
      if (sequence !== requestSequence) return;
      results.innerHTML = `<span class="student-picker-empty">${esc(error.message || "Search unavailable")}</span>`;
    }
  };
  const resolve = () => {
    const query = input.value.trim().toLowerCase();
    if (hidden.value && query === chosenLabel.toLowerCase()) {
      input.setCustomValidity("");
      return hidden.value;
    }
    const mobile = normalizedMobile(input.value);
    const matches = available.filter(item => {
      const candidateMobile = normalizedMobile(studentPickerMobile(item));
      return studentPickerLabel(item).toLowerCase() === query
        || String(item.admissionNumber || "").toLowerCase() === query
        || String(item.studentName || item.fullName || "").toLowerCase() === query
        || (mobile && candidateMobile === mobile);
    });
    hidden.value = matches.length === 1 ? studentPickerId(matches[0]) : "";
    input.setCustomValidity(hidden.value ? "" : "Choose one student from the verified search results.");
    return hidden.value;
  };
  input.addEventListener("focus", load);
  input.addEventListener("input", () => {
    hidden.value = "";
    chosenLabel = "";
    input.setCustomValidity("");
    clearTimeout(timer);
    timer = setTimeout(load, 180);
  });
  input.addEventListener("keydown", event => {
    const buttons = $$("[data-student-picker-option]", results);
    if (event.key === "ArrowDown" && buttons.length) { event.preventDefault(); setActive(activeIndex + 1); }
    else if (event.key === "ArrowUp" && buttons.length) { event.preventDefault(); setActive(activeIndex <= 0 ? buttons.length - 1 : activeIndex - 1); }
    else if (event.key === "Enter" && activeIndex >= 0 && available[activeIndex]) { event.preventDefault(); choose(available[activeIndex]); }
    else if (event.key === "Escape") closeResults();
  });
  results.addEventListener("mousedown", event => event.preventDefault());
  results.addEventListener("click", event => {
    const button = event.target.closest("[data-student-picker-option]");
    if (!button) return;
    const item = available.find(row => studentPickerId(row) === button.dataset.studentPickerOption);
    if (item) choose(item);
  });
  input.addEventListener("blur", () => {
    setTimeout(() => { resolve(); closeResults(); }, 120);
  });
  form.resolveStudentPicker = resolve;
}

function requireStudentPicker(form) {
  if (!form.resolveStudentPicker || form.resolveStudentPicker()) return true;
  const input = $("[data-student-picker-input]", form);
  input?.reportValidity();
  return false;
}

function openSessionForm() {
  const start = new Date(Date.now() + 86400000), end = new Date(start.getTime() + 5400000);
  openDrawer("Schedule class", `<form class="auth-form" id="session-form"><label class="field"><span>Batch</span><select name="batchId" required><option value="">Select batch</option>${options(state.timetable.batches || [], item => `${item.name} · ${item.program}`)}</select></label><label class="field"><span>Subject</span><select name="subjectId" required><option value="">Select subject</option>${options(state.timetable.subjects || [], item => `${item.name} · ${item.code}`)}</select></label><label class="field"><span>Faculty</span><select name="facultyId" required><option value="">Select faculty</option>${options(state.timetable.faculty || [], item => item.fullName)}</select></label><label class="field"><span>Room</span><select name="roomId" required><option value="">Select room</option>${options(state.timetable.rooms || [], item => `${item.name} · ${item.capacity} seats`)}</select></label><div class="form-pair"><label class="field"><span>Starts</span><input name="startsAt" type="datetime-local" value="${localInputValue(start)}" required></label><label class="field"><span>Ends</span><input name="endsAt" type="datetime-local" value="${localInputValue(end)}" required></label></div><label class="field"><span>Notes</span><textarea name="notes" rows="3"></textarea></label><label class="check-field"><input name="allowOverride" type="checkbox"><span>Authorised conflict override</span></label><label class="field"><span>Override reason</span><textarea name="overrideReason" rows="2"></textarea></label>${formError("session-form-error")}<button class="button button-primary button-large" type="submit">${icon("calendar-check")}Schedule class</button></form>`);
  $("#session-form").addEventListener("submit", submitSession);
}

async function submitSession(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget), button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = { batchId: form.get("batchId"), subjectId: form.get("subjectId"), facultyId: form.get("facultyId"), roomId: form.get("roomId"), startsAt: indiaInputToISOString(form.get("startsAt")), endsAt: indiaInputToISOString(form.get("endsAt")), notes: String(form.get("notes") || "").trim(), allowOverride: form.get("allowOverride") === "on", overrideReason: String(form.get("overrideReason") || "").trim() || null };
  try { await api("/api/timetable/sessions", { method: "POST", body: JSON.stringify(payload) }); state.timetable = await api("/api/timetable/bootstrap"); state.sessions = state.timetable.sessions; state.attendanceSessions = await api("/api/attendance/sessions"); closeDetail(); renderTimetable(); renderAttendance(); toast("Class scheduled."); }
  catch (error) { showFormError("#session-form-error", error); button.disabled = false; }
}

function openTeachingAssignmentForm(item = null) {
  openDrawer(item ? "Edit teaching assignment" : "Assign faculty", `<form class="auth-form" id="teaching-assignment-form" data-assignment-id="${esc(item?.id || "")}">
    <label class="field"><span>Faculty</span><select name="facultyId" required><option value="">Select faculty</option>${(state.timetable.faculty || []).map(row => `<option value="${esc(row.id)}"${selected(row.id, item?.facultyId)}>${esc(row.fullName)}</option>`).join("")}</select></label>
    <label class="field"><span>Batch</span><select name="batchId" required><option value="">Select batch</option>${(state.timetable.batches || []).map(row => `<option value="${esc(row.id)}"${selected(row.id, item?.batchId)}>${esc(row.name)} · ${esc(row.program)}</option>`).join("")}</select></label>
    <label class="field"><span>Subject</span><select name="subjectId" required><option value="">Select subject</option>${(state.timetable.subjects || []).map(row => `<option value="${esc(row.id)}"${selected(row.id, item?.subjectId)}>${esc(row.name)} · ${esc(row.code)}</option>`).join("")}</select></label>
    ${item ? `<label class="check-field"><input name="isActive" type="checkbox"${checked(item.isActive)}><span>Teaching assignment active</span></label>` : ""}
    ${formError("teaching-assignment-form-error")}
    <button class="button button-primary button-large" type="submit">${icon(item ? "edit" : "plus")}${item ? "Save changes" : "Assign faculty"}</button>
  </form>`);
  $("#teaching-assignment-form").addEventListener("submit", submitTeachingAssignment);
}

async function submitTeachingAssignment(event) {
  event.preventDefault();
  const form = event.currentTarget, data = new FormData(form), assignmentId = form.dataset.assignmentId;
  const button = $("button[type=submit]", form); button.disabled = true;
  const payload = {
    facultyId: data.get("facultyId"),
    batchId: data.get("batchId"),
    subjectId: data.get("subjectId"),
    ...(assignmentId ? { isActive: form.elements.isActive.checked } : {}),
  };
  try {
    await api(assignmentId ? `/api/timetable/teaching-assignments/${encodeURIComponent(assignmentId)}` : "/api/timetable/teaching-assignments", {
      method: assignmentId ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    state.timetable = await api("/api/timetable/bootstrap");
    state.sessions = state.timetable.sessions || [];
    closeDetail();
    renderTimetable();
    toast(assignmentId ? "Teaching assignment updated." : "Faculty assigned.");
  } catch (error) {
    showFormError("#teaching-assignment-form-error", error);
    button.disabled = false;
  }
}

function openInventoryItemForm(item = null) {
  if (!canManageInventory()) { toast("Inventory access is required.", "error"); return; }
  openDrawer(item ? "Edit inventory item" : "New inventory item", `<form class="auth-form" id="inventory-item-form" data-item-id="${esc(item?.id || "")}">
    <label class="field"><span>Item name</span><input name="name" value="${esc(item?.name || "")}" required></label>
    <div class="form-pair"><label class="field"><span>SKU</span><input name="sku" value="${esc(item?.sku || "")}" placeholder="ITEM-CODE" ${item ? "readonly" : "required"}></label><label class="field"><span>Category</span><select name="category" required><option value="book"${selected("book", item?.category)}>Book</option><option value="bag"${selected("bag", item?.category)}>Bag</option><option value="apparel"${selected("apparel", item?.category)}>Apparel</option><option value="other"${selected("other", item?.category)}>Other</option></select></label></div>
    <div class="form-pair"><label class="field"><span>Unit</span><input name="unit" value="${esc(item?.unit || "piece")}" required></label><label class="field"><span>${item?.quantityOnHand == null ? "Opening quantity" : "Current balance"}</span><input name="quantityOnHand" type="number" min="0" value="${item?.quantityOnHand ?? ""}" placeholder="Not supplied"${item?.quantityOnHand != null ? " readonly" : ""}></label></div>
    <div class="form-pair"><label class="field"><span>Reorder level</span><input name="reorderLevel" type="number" min="0" value="${item?.reorderLevel ?? 0}" required></label><label class="field"><span>Vendor reference <small>(optional)</small></span><input name="vendorReference" value="${esc(item?.vendorReference || "")}"></label></div>
    ${item?.quantityOnHand != null ? `<div class="inline-notice">${icon("shield")}<span>Stock balance is controlled by the movement register and cannot be edited directly.</span></div>` : ""}
    <label class="field"><span>Notes</span><textarea name="notes" rows="4">${esc(item?.notes || "")}</textarea></label>
    ${item ? `<label class="check-field"><input name="isActive" type="checkbox"${checked(item.isActive)}><span>Inventory item active</span></label>` : ""}
    ${formError("inventory-item-error")}
    <button class="button button-primary button-large" type="submit">${icon(item ? "edit" : "plus")}${item ? "Save item" : "Add item"}</button>
  </form>`);
  $("#inventory-item-form").addEventListener("submit", submitInventoryItem);
}

async function submitInventoryItem(event) {
  event.preventDefault();
  const form = event.currentTarget, itemId = form.dataset.itemId, data = new FormData(form);
  const button = $('button[type="submit"]', form); button.disabled = true;
  const quantity = String(data.get("quantityOnHand") || "").trim();
  const payload = {
    ...(itemId ? {} : { sku: String(data.get("sku") || "").trim() }),
    name: String(data.get("name") || "").trim(),
    category: data.get("category"),
    unit: String(data.get("unit") || "").trim(),
    quantityOnHand: quantity === "" ? null : Number(quantity),
    reorderLevel: Number(data.get("reorderLevel") || 0),
    vendorReference: String(data.get("vendorReference") || "").trim() || null,
    notes: String(data.get("notes") || "").trim(),
    ...(itemId ? { isActive: form.elements.isActive.checked } : {}),
  };
  try {
    await api(itemId ? `/api/inventory/items/${encodeURIComponent(itemId)}` : "/api/inventory/items", {
      method: itemId ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    state.inventory = await api("/api/inventory/bootstrap");
    closeDetail();
    renderInventory();
    $("#nav-inventory-count").textContent = state.inventory.items.length;
    injectIcons($("#inventory"));
    toast(itemId ? "Inventory item updated." : "Inventory item added.");
  } catch (error) {
    showFormError("#inventory-item-error", error);
    button.disabled = false;
  }
}

function openInventoryMovementForm(item) {
  if (!canManageInventory()) { toast("Inventory access is required.", "error"); return; }
  const studentOptions = state.inventory.studentTargets || state.students.filter(student => student.status === "active");
  openDrawer(`Record movement · ${item.name}`, `<form class="auth-form" id="inventory-movement-form" data-item-id="${esc(item.id)}">
    <div class="inline-notice">${icon("inventory")}<span>Available: <strong>${item.quantityOnHand ?? 0} ${esc(item.unit)}</strong>. Every movement is permanent and auditable.</span></div>
    <div class="form-pair"><label class="field"><span>Movement</span><select name="movementType"><option value="inward">Purchase / inward</option><option value="issue">Issue</option><option value="return">Return</option><option value="write_off">Write-off</option><option value="adjustment">Adjustment (+ or −)</option></select></label><label class="field"><span>Quantity</span><input name="quantity" type="number" step="1" value="1" required></label></div>
    <label class="field"><span>Movement date</span><input name="occurredOn" type="date" value="${dateInputValue()}" required></label>
    <div class="form-pair"><label class="field"><span>Target / source</span><select name="targetType"><option value="">Not applicable</option><option value="student">Student</option><option value="batch">Batch</option><option value="faculty">Faculty</option><option value="department">Department</option><option value="vendor">Vendor</option><option value="other">Other</option></select></label><label class="field"><span>Reference</span><input name="reference" placeholder="Invoice or issue reference"></label></div>
    <label class="field hidden" id="inventory-movement-student-field"><span>Student</span><select name="studentId"><option value="">Select student</option>${options(studentOptions, student => `${student.fullName} · ${student.admissionNumber}`)}</select></label>
    <label class="field" id="inventory-movement-target-field"><span>Target / source name <small>(optional)</small></span><input name="targetReference" placeholder="Batch, vendor or department"></label>
    <label class="field"><span>Reason</span><textarea name="reason" rows="3" minlength="3" required></textarea></label>
    ${formError("inventory-movement-error")}
    <button class="button button-primary button-large" type="submit">${icon("inventory")}Record movement</button>
  </form>`);
  const form = $("#inventory-movement-form");
  form.elements.targetType.addEventListener("change", () => {
    const studentTarget = form.elements.targetType.value === "student";
    $("#inventory-movement-student-field").classList.toggle("hidden", !studentTarget);
    $("#inventory-movement-target-field").classList.toggle("hidden", studentTarget);
    form.elements.studentId.required = studentTarget;
  });
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(form), button = $('button[type="submit"]', form);
    button.disabled = true;
    const payload = {
      movementType: data.get("movementType"),
      quantity: Number(data.get("quantity")),
      occurredOn: data.get("occurredOn"),
      targetType: data.get("targetType") || null,
      targetReference: String(data.get("targetReference") || "").trim() || null,
      studentId: data.get("studentId") || null,
      reference: String(data.get("reference") || "").trim() || null,
      reason: String(data.get("reason") || "").trim(),
    };
    try {
      await api(`/api/inventory/items/${encodeURIComponent(form.dataset.itemId)}/movements`, { method: "POST", body: JSON.stringify(payload) });
      state.inventory = await api("/api/inventory/bootstrap");
      closeDetail();
      renderInventory();
      injectIcons($("#inventory"));
      toast("Stock movement recorded.");
    } catch (error) {
      showFormError("#inventory-movement-error", error);
      button.disabled = false;
    }
  });
}

function openFuturePaymentForm(item = null) {
  const action = item ? "edit" : "create";
  if (!canAccess("finance", action)) { toast(`${item ? "Edit" : "Add"} access to Fees & finance is required.`, "error"); return; }
  if (!item && !state.agreements.length) {
    toast("Create a fee agreement before scheduling a payment.", "error");
    return;
  }
  const preferredStudent = financeStudentFilter && state.agreements.some(row => row.studentId === financeStudentFilter)
    ? financeStudentFilter
    : "";
  const preferredAccount = state.agreements.find(row => row.studentId === preferredStudent) || null;
  const studentField = item
    ? `<div class="immutable-record-note">${icon("user")}<span>${esc(item.studentName)}<small>${esc(item.admissionNumber || "Student fee account")}</small></span></div>`
    : studentPickerMarkup({ label: "Student account", selectedItem: preferredAccount, scope: "with_agreement" });
  const dueDate = item?.date || dateInputValue(new Date(Date.now() + 30 * 86400000));
  openDrawer(item ? "Edit future payment" : "Schedule future payment", `<form class="auth-form" id="future-payment-form" data-installment-id="${esc(item?.id || "")}">
    ${studentField}
    <div class="form-pair"><label class="field"><span>Expected date</span><input name="dueDate" type="date"${item ? "" : ` min="${dateInputValue()}"`} value="${esc(dueDate)}" required></label><label class="field"><span>Amount</span><input name="amount" type="number" min="1" step="1" value="${item?.amount ?? ""}" inputmode="numeric" required></label></div>
    <label class="field"><span>Expected payment mode</span><select name="expectedMethod"><option value="not_decided"${selected("not_decided", item?.method)}>Not decided</option><option value="cash"${selected("cash", item?.method)}>Cash</option><option value="upi"${selected("upi", item?.method)}>UPI</option><option value="bank_transfer"${selected("bank_transfer", item?.method)}>Bank transfer</option><option value="cheque"${selected("cheque", item?.method)}>Cheque</option><option value="card"${selected("card", item?.method)}>Card</option><option value="other"${selected("other", item?.method)}>Other</option></select></label>
    <label class="field"><span>Note <small>(optional)</small></span><textarea name="notes" rows="4" placeholder="Installment reference or commitment details">${esc(item?.sourceNote || "")}</textarea></label>
    ${item ? `<label class="field"><span>Status</span><select name="status"><option value="scheduled"${selected("scheduled", item.status)}>Scheduled</option><option value="cancelled"${selected("cancelled", item.status)}>Cancelled</option></select></label>` : ""}
    <div class="immutable-record-note">${icon("info")}<span>This is a payment schedule only.<small>It will not reduce the student's outstanding balance until an actual payment is recorded.</small></span></div>
    ${formError("future-payment-error")}
    <button class="button button-primary button-large" type="submit">${icon(item ? "edit" : "calendar-check")}${item ? "Save future payment" : "Schedule payment"}</button>
  </form>`);
  const futurePaymentForm = $("#future-payment-form");
  if (!item) bindStudentPicker(futurePaymentForm);
  futurePaymentForm.addEventListener("submit", submitFuturePayment);
}

function paymentMethodOptions(current = "") {
  return [
    ["cash", "Cash"],
    ["upi", "UPI"],
    ["bank_transfer", "Bank transfer"],
    ["cheque", "Cheque"],
    ["card", "Card"],
    ["other", "Other"],
  ].map(([value, label]) => `<option value="${value}"${selected(value, current)}>${label}</option>`).join("");
}

function openPaymentForm() {
  if (!canManageFinance()) { toast("Finance access is required.", "error"); return; }
  if (!state.agreements.length) { toast("Create a fee agreement before recording a payment.", "error"); return; }
  const preferredStudent = financeStudentFilter && state.agreements.some(row => row.studentId === financeStudentFilter)
    ? financeStudentFilter
    : "";
  const preferredAccount = state.agreements.find(row => row.studentId === preferredStudent) || null;
  openDrawer("Record payment", `<form class="auth-form" id="payment-create-form">
    <div class="inline-notice">${icon("receipt")}<span>A numbered receipt is created immediately.<small>Posted entries cannot be edited or deleted; corrections use a reversal.</small></span></div>
    ${studentPickerMarkup({ label: "Student account", selectedItem: preferredAccount, scope: "with_agreement" })}
    <div class="form-pair"><label class="field"><span>Payment date</span><input name="transactionDate" type="date" max="${dateInputValue()}" value="${dateInputValue()}" required></label><label class="field"><span>Amount received</span><input name="amount" type="number" min="1" step="1" inputmode="numeric" required></label></div>
    <label class="field"><span>Payment mode</span><select name="method" required><option value="">Select payment mode</option>${paymentMethodOptions()}</select></label>
    <label class="field"><span>Bank / UPI / cheque reference <small>(optional for cash)</small></span><input name="reference" maxlength="255"></label>
    <label class="field"><span>Internal note <small>(optional)</small></span><textarea name="notes" rows="3" maxlength="2000"></textarea></label>
    ${formError("payment-create-error")}
    <button class="button button-primary button-large" type="submit">${icon("receipt")}Post payment &amp; issue receipt</button>
  </form>`);
  const paymentForm = $("#payment-create-form");
  bindStudentPicker(paymentForm);
  paymentForm.addEventListener("submit", submitPayment);
}

async function submitPayment(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!requireStudentPicker(form)) return;
  const data = new FormData(form);
  const button = $('button[type="submit"]', form); button.disabled = true;
  const payload = {
    studentId: data.get("studentId"),
    transactionDate: data.get("transactionDate"),
    amount: Number(data.get("amount")),
    method: data.get("method"),
    reference: String(data.get("reference") || "").trim() || null,
    notes: String(data.get("notes") || "").trim(),
  };
  try {
    const payment = await api("/api/finance/payments", { method: "POST", body: JSON.stringify(payload) });
    state.payments = await fetchAll("/api/finance/transactions");
    closeDetail();
    renderAll();
    activateFinanceTab("payments");
    toast(`Payment posted · ${payment.receiptNumber}`);
  } catch (error) {
    showFormError("#payment-create-error", error);
    button.disabled = false;
  }
}

function openPaymentReversalForm(item) {
  if (!item || item.status !== "posted" || item.type !== "payment") return;
  openDrawer("Reverse payment", `<form class="auth-form" id="payment-reversal-form" data-payment-id="${esc(item.id)}">
    <div class="immutable-record-note">${icon("receipt")}<span>${esc(item.receiptNumber)} · ${money(item.amount)}<small>${esc(item.studentName)} · ${formatDate(item.date)}</small></span></div>
    <label class="field"><span>Correction type</span><select name="kind"><option value="reversal">Reversal</option><option value="refund">Refund</option><option value="void">Void</option></select></label>
    <div class="form-pair"><label class="field"><span>Date</span><input name="transactionDate" type="date" min="${esc(item.date)}" max="${dateInputValue()}" value="${dateInputValue()}" required></label><label class="field"><span>Amount</span><input name="amount" type="number" min="1" max="${item.amount}" value="${item.amount}" required></label></div>
    <label class="field"><span>Reason</span><textarea name="reason" rows="4" minlength="3" required></textarea></label>
    <label class="field"><span>Reference <small>(optional)</small></span><input name="reference" maxlength="255"></label>
    <div class="inline-notice inline-notice-danger">${icon("alert")}<span>This creates a permanent offsetting entry.<small>The original receipt remains in the audit trail.</small></span></div>
    ${formError("payment-reversal-error")}
    <button class="button button-danger button-large" type="submit">${icon("refresh")}Post correction</button>
  </form>`);
  $("#payment-reversal-form").addEventListener("submit", submitPaymentReversal);
}

async function submitPaymentReversal(event) {
  event.preventDefault();
  const form = event.currentTarget, data = new FormData(form);
  const button = $('button[type="submit"]', form); button.disabled = true;
  try {
    const kind = data.get("kind");
    await api(`/api/finance/payments/${encodeURIComponent(form.dataset.paymentId)}/reverse`, {
      method: "POST",
      body: JSON.stringify({
        transactionDate: data.get("transactionDate"),
        kind,
        amount: Number(data.get("amount")),
        reason: String(data.get("reason") || "").trim(),
        reference: String(data.get("reference") || "").trim() || null,
      }),
    });
    state.payments = await fetchAll("/api/finance/transactions");
    closeDetail();
    renderAll();
    activateFinanceTab("payments");
    toast(`${String(kind).replace(/^./, value => value.toUpperCase())} posted.`);
  } catch (error) {
    showFormError("#payment-reversal-error", error);
    button.disabled = false;
  }
}

function openFeeAgreementForm() {
  if (!canManageFinance()) { toast("Finance access is required.", "error"); return; }
  const existingIds = new Set(state.agreements.map(row => row.studentId));
  const students = state.students.filter(row => ["active", "draft"].includes(row.status) && !existingIds.has(row.id));
  if (!students.length) { toast("Every student already has a fee agreement."); return; }
  openDrawer("Create fee agreement", `<form class="auth-form" id="fee-agreement-create-form">
    ${studentPickerMarkup({ scope: "without_agreement" })}
    <label class="field"><span>Agreed course fee</span><input name="agreedAmount" type="number" min="0" step="1" inputmode="numeric" required></label>
    <div class="form-pair"><label class="field"><span>Currency</span><input name="currency" value="INR" readonly aria-readonly="true"></label><label class="field"><span>Status</span><select name="status"><option value="active">Active</option><option value="draft">Draft</option></select></label></div>
    ${formError("fee-agreement-create-error")}
    <button class="button button-primary button-large" type="submit">${icon("wallet")}Create fee agreement</button>
  </form>`);
  const feeAgreementForm = $("#fee-agreement-create-form");
  bindStudentPicker(feeAgreementForm);
  feeAgreementForm.addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!requireStudentPicker(form)) return;
    const data = new FormData(form), button = $('button[type="submit"]', form);
    button.disabled = true;
    try {
      await api("/api/finance/agreements", { method: "POST", body: JSON.stringify({
        studentId: data.get("studentId"),
        agreedAmount: Number(data.get("agreedAmount")),
        currency: data.get("currency"),
        status: data.get("status"),
      }) });
      state.agreements = await fetchAll("/api/finance/agreements");
      closeDetail();
      renderAll();
      toast("Fee agreement created.");
    } catch (error) {
      showFormError("#fee-agreement-create-error", error);
      button.disabled = false;
    }
  });
}

async function submitFuturePayment(event) {
  event.preventDefault();
  const form = event.currentTarget, installmentId = form.dataset.installmentId;
  if (!installmentId && !requireStudentPicker(form)) return;
  const data = new FormData(form);
  const button = $('button[type="submit"]', form); button.disabled = true;
  const payload = {
    ...(installmentId ? {} : { studentId: data.get("studentId") }),
    dueDate: data.get("dueDate"),
    amount: Number(data.get("amount")),
    expectedMethod: data.get("expectedMethod"),
    notes: String(data.get("notes") || "").trim(),
    ...(installmentId ? { status: data.get("status") } : {}),
  };
  try {
    await api(installmentId ? `/api/finance/installments/${encodeURIComponent(installmentId)}` : "/api/finance/installments", {
      method: installmentId ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    state.installments = await fetchAll("/api/finance/installments");
    closeDetail();
    renderAll();
    activateFinanceTab("payments");
    toast(installmentId ? "Future payment updated." : "Future payment scheduled.");
  } catch (error) {
    showFormError("#future-payment-error", error);
    button.disabled = false;
  }
}

function openAssignmentForm() {
  openDrawer("New assignment", `<form class="auth-form" id="assignment-form"><label class="field"><span>Title</span><input name="title" required></label><label class="field"><span>Batch</span><select name="batchId" required><option value="">Select batch</option>${options(state.timetable.batches || [], item => `${item.name} · ${item.program}`)}</select></label><label class="field"><span>Subject</span><select name="subjectId" required><option value="">Select subject</option>${options(state.timetable.subjects || [], item => `${item.name} · ${item.code}`)}</select></label><label class="field"><span>Due</span><input name="dueAt" type="datetime-local" value="${localInputValue(new Date(Date.now() + 604800000))}" required></label><label class="field"><span>Material link</span><input name="externalUrl" type="url" placeholder="https://" required></label><label class="field"><span>Instructions</span><textarea name="instructions" rows="4"></textarea></label><label class="field"><span>Status</span><select name="status"><option value="published">Published</option><option value="draft">Draft</option></select></label>${formError("assignment-form-error")}<button class="button button-primary button-large" type="submit">${icon("book")}Publish assignment</button></form>`);
  $("#assignment-form").addEventListener("submit", submitAssignment);
}

async function submitAssignment(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget), button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = { title: String(form.get("title")).trim(), batchId: form.get("batchId"), subjectId: form.get("subjectId"), dueAt: indiaInputToISOString(form.get("dueAt")), externalUrl: String(form.get("externalUrl")).trim(), instructions: String(form.get("instructions") || "").trim(), status: form.get("status") };
  try { const row = await api("/api/academics/assignments", { method: "POST", body: JSON.stringify(payload) }); state.assignments.unshift(row); closeDetail(); renderAcademics(); toast(`Assignment published to ${row.recipientCount} students.`); }
  catch (error) { showFormError("#assignment-form-error", error); button.disabled = false; }
}

function examinationFormMarkup(item = null) {
  const scheduledAt = item?.scheduledAt || new Date(Date.now() + 172800000);
  const currentStatus = item?.status || "scheduled";
  return `<form class="auth-form" id="examination-form" data-examination-id="${esc(item?.id || "")}">
    <label class="field"><span>Examination name</span><input name="name" value="${esc(item?.name || "")}" placeholder="Unit Test 01" required></label>
    <div class="form-pair"><label class="field"><span>Batch</span><select name="batchId" required><option value="">Select batch</option>${(state.timetable.batches || []).map(row => `<option value="${esc(row.id)}"${selected(row.id, item?.batchId)}>${esc(row.name)} · ${esc(row.program)}</option>`).join("")}</select></label><label class="field"><span>Subject</span><select name="subjectId" required><option value="">Select subject</option>${(state.timetable.subjects || []).map(row => `<option value="${esc(row.id)}"${selected(row.id, item?.subjectId)}>${esc(row.name)} · ${esc(row.code)}</option>`).join("")}</select></label></div>
    <label class="field"><span>Faculty</span><select name="facultyId" required><option value="">Select faculty</option>${(state.timetable.faculty || []).map(row => `<option value="${esc(row.id)}"${selected(row.id, item?.facultyId)}>${esc(row.fullName)}</option>`).join("")}</select></label>
    <div class="form-pair"><label class="field"><span>Date &amp; time</span><input name="scheduledAt" type="datetime-local" value="${localInputValue(scheduledAt)}" required></label><label class="field"><span>Duration</span><input name="durationMinutes" type="number" min="15" max="480" step="5" value="${esc(item?.durationMinutes || 60)}" required></label></div>
    <div class="form-pair"><label class="field"><span>Maximum marks</span><input name="maxMarks" type="number" min="0.01" max="10000" step="0.01" value="${esc(item?.maxMarks || 100)}" required></label><label class="field"><span>Pass marks</span><input name="passMarks" type="number" min="0" max="10000" step="0.01" value="${esc(item?.passMarks ?? 40)}" required></label></div>
    <label class="field"><span>Instructions</span><textarea name="instructions" rows="4" placeholder="Reporting time, permitted materials, or other instructions">${esc(item?.instructions || "")}</textarea></label>
    <label class="field"><span>Status</span><select name="status"><option value="scheduled"${selected("scheduled", currentStatus)}>Scheduled</option><option value="draft"${selected("draft", currentStatus)}>Draft</option>${item?.status === "marks_entry" ? `<option value="marks_entry" selected>Marks entry</option>` : ""}${item ? `<option value="cancelled"${selected("cancelled", currentStatus)}>Cancelled</option>` : ""}</select></label>
    ${formError("examination-form-error")}
    <button class="button button-primary button-large" type="submit">${icon("exam")}${item ? "Save examination" : "Create examination"}</button>
  </form>`;
}

function openExaminationForm(item = null) {
  openDrawer(item ? "Edit examination" : "New examination", examinationFormMarkup(item));
  $("#examination-form").addEventListener("submit", submitExamination);
}

async function submitExamination(event) {
  event.preventDefault();
  const formNode = event.currentTarget;
  const form = new FormData(formNode);
  const button = $('button[type="submit"]', formNode);
  const examId = formNode.dataset.examinationId;
  const payload = {
    name: String(form.get("name") || "").trim(),
    batchId: form.get("batchId"),
    subjectId: form.get("subjectId"),
    facultyId: form.get("facultyId"),
    scheduledAt: indiaInputToISOString(form.get("scheduledAt")),
    durationMinutes: Number(form.get("durationMinutes")),
    maxMarks: Number(form.get("maxMarks")),
    passMarks: Number(form.get("passMarks")),
    instructions: String(form.get("instructions") || "").trim(),
    status: form.get("status")
  };
  if (payload.passMarks > payload.maxMarks) {
    showFormError("#examination-form-error", new Error("Pass marks cannot exceed maximum marks."));
    return;
  }
  button.disabled = true;
  try {
    await api(`/api/examinations${examId ? `/${encodeURIComponent(examId)}` : ""}`, { method: examId ? "PATCH" : "POST", body: JSON.stringify(payload) });
    state.examinations = await api("/api/examinations");
    closeDetail(); renderExaminations(); $("#nav-examinations-count").textContent = state.examinations.length; toast(examId ? "Examination updated." : "Examination created.");
  } catch (error) { showFormError("#examination-form-error", error); button.disabled = false; }
}

function examinationResultSummary(detail) {
  const graded = detail.students.filter(item => item.resultStatus === "graded");
  const passed = graded.filter(item => Number(item.marksObtained) >= Number(detail.passMarks)).length;
  const average = graded.length ? graded.reduce((sum, item) => sum + Number(item.marksObtained || 0), 0) / graded.length : null;
  return `<div class="exam-detail-summary"><div><span>Batch</span><strong>${esc(detail.batch)}</strong></div><div><span>Maximum</span><strong>${esc(detail.maxMarks)}</strong></div><div><span>Entered</span><strong>${detail.marksEntered}/${detail.participantCount}</strong></div><div><span>${detail.status === "published" ? "Pass rate" : "Scheduled"}</span><strong>${detail.status === "published" && graded.length ? `${Math.round(passed / graded.length * 100)}%` : formatDateTime(detail.scheduledAt)}</strong></div></div>${detail.status === "published" && average != null ? `<p class="exam-published-note">${icon("shield")} Published results · Average ${average.toFixed(1)} · Highest ${detail.highestMarks ?? "—"}</p>` : ""}`;
}

function renderExaminationRoster(detail) {
  $("#drawer-title").textContent = detail.name;
  const readOnly = detail.status === "published" || !canAccess("examinations", "edit");
  const rows = detail.students.map(item => {
    if (readOnly) {
      const resultValue = item.resultStatus === "graded" ? `${item.marksObtained} / ${detail.maxMarks}` : item.resultStatus.replaceAll("_", " ");
      return `<div class="exam-result-row"><div>${studentPrimary(item.fullName, item.admissionNumber)}</div><strong>${esc(resultValue)}</strong><span>${status(item.resultStatus)}</span><small>${esc(item.remarks || "")}</small></div>`;
    }
    return `<div class="exam-mark-row" data-exam-student="${esc(item.studentId)}"><span class="exam-mark-student"><strong>${esc(item.fullName)}</strong><small>${esc(item.admissionNumber)}</small></span><label><span>Result</span><select data-exam-result-status><option value="pending"${selected("pending", item.resultStatus)}>Pending</option><option value="graded"${selected("graded", item.resultStatus)}>Graded</option><option value="absent"${selected("absent", item.resultStatus)}>Absent</option><option value="withheld"${selected("withheld", item.resultStatus)}>Withheld</option></select></label><label><span>Marks</span><input data-exam-marks type="number" min="0" max="${esc(detail.maxMarks)}" step="0.01" value="${esc(item.marksObtained ?? "")}" ${item.resultStatus === "graded" ? "" : "disabled"}></label><label><span>Remarks</span><input data-exam-remarks maxlength="500" value="${esc(item.remarks || "")}" placeholder="Optional"></label></div>`;
  }).join("");
  $("#detail-drawer-body").innerHTML = `${examinationResultSummary(detail)}${readOnly ? `<div class="exam-results-list">${rows}</div>` : `<form id="examination-marks-form" data-examination-id="${esc(detail.id)}" data-max-marks="${esc(detail.maxMarks)}"><div class="exam-roster-head"><span>${detail.students.length} students</span><strong>Complete every result before publishing</strong></div><div class="exam-marks-list">${rows}</div>${formError("examination-marks-error")}<div class="drawer-actions exam-drawer-actions"><button class="button button-secondary" id="save-examination-marks" type="button">Save draft</button><button class="button button-primary" type="submit">${icon("shield")}Publish results</button></div></form>`}`;
  if (readOnly) return;
  $$("[data-exam-result-status]", $("#examination-marks-form")).forEach(select => select.addEventListener("change", event => {
    const row = event.currentTarget.closest("[data-exam-student]");
    const marks = $("[data-exam-marks]", row);
    const graded = event.currentTarget.value === "graded";
    marks.disabled = !graded;
    if (!graded) marks.value = "";
  }));
  $("#save-examination-marks").addEventListener("click", () => saveExaminationMarks(false));
  $("#examination-marks-form").addEventListener("submit", event => { event.preventDefault(); saveExaminationMarks(true); });
}

async function openExamination(examId) {
  openDrawer("Examination", '<div class="skeleton-line"></div>', true);
  try {
    const detail = await api(`/api/examinations/${encodeURIComponent(examId)}`);
    renderExaminationRoster(detail);
  } catch (error) { $("#detail-drawer-body").innerHTML = emptyState("alert", "Could not open examination", error.message); }
}

function examinationMarksPayload(form) {
  const maxMarks = Number(form.dataset.maxMarks);
  return $$("[data-exam-student]", form).map(row => {
    const resultStatus = $("[data-exam-result-status]", row).value;
    const marksField = $("[data-exam-marks]", row);
    const marksObtained = resultStatus === "graded" && marksField.value !== "" ? Number(marksField.value) : null;
    if (resultStatus === "graded" && marksObtained == null) throw new Error("Enter marks for every graded student.");
    if (marksObtained != null && marksObtained > maxMarks) throw new Error(`Marks cannot exceed ${maxMarks}.`);
    return { studentId: row.dataset.examStudent, resultStatus, marksObtained, remarks: String($("[data-exam-remarks]", row).value || "").trim() };
  });
}

async function saveExaminationMarks(publish) {
  const form = $("#examination-marks-form");
  const buttons = $$("button", form);
  buttons.forEach(button => { button.disabled = true; });
  $("#examination-marks-error").classList.add("hidden");
  try {
    const entries = examinationMarksPayload(form);
    await api(`/api/examinations/${encodeURIComponent(form.dataset.examinationId)}/marks`, { method: "PUT", body: JSON.stringify({ entries }) });
    if (publish) await api(`/api/examinations/${encodeURIComponent(form.dataset.examinationId)}/publish`, { method: "POST" });
    state.examinations = await api("/api/examinations");
    renderExaminations();
    if (publish) { closeDetail(); toast("Results published to students."); }
    else {
      const detail = await api(`/api/examinations/${encodeURIComponent(form.dataset.examinationId)}`);
      renderExaminationRoster(detail); toast("Marks draft saved.");
    }
  } catch (error) {
    showFormError("#examination-marks-error", error);
    buttons.forEach(button => { button.disabled = false; });
  }
}

function openNoticeForm() {
  openDrawer("New notice", `<form class="auth-form" id="notice-form"><label class="field"><span>Title</span><input name="title" required></label><label class="field"><span>Message</span><textarea name="body" rows="5" required></textarea></label><label class="field"><span>Audience</span><select name="audience"><option value="all">Everyone</option><option value="parents">Parents</option><option value="students">Students</option><option value="faculty">Faculty</option><option value="batch">Batch</option></select></label><label class="field"><span>Batch</span><select name="batchId"><option value="">Not selected</option>${options(state.timetable.batches || [], item => `${item.name} · ${item.program}`)}</select></label><label class="field"><span>Channel</span><select name="channel"><option value="in_app">In app</option><option value="email" disabled>Email · provider not connected</option><option value="sms" disabled>SMS · provider not connected</option><option value="whatsapp" disabled>WhatsApp · provider not connected</option></select></label><div class="inline-notice">${icon("info")}<span>Email, SMS and WhatsApp become available after a delivery provider is connected. In-app notices work now.</span></div><label class="field"><span>Status</span><select name="status"><option value="published">Publish now</option><option value="draft">Save draft</option></select></label>${formError("notice-form-error")}<button class="button button-primary button-large" type="submit">${icon("message")}Save notice</button></form>`);
  $("#notice-form").addEventListener("submit", submitNotice);
}

async function submitNotice(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget), button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = Object.fromEntries(["title", "body", "audience", "channel", "status"].map(key => [key, String(form.get(key)).trim()])); payload.batchId = String(form.get("batchId") || "") || null;
  try { const row = await api("/api/communication/notices", { method: "POST", body: JSON.stringify(payload) }); state.notices.unshift(row); closeDetail(); renderCommunication(); toast("Notice published."); }
  catch (error) { showFormError("#notice-form-error", error); button.disabled = false; }
}

async function openAttendance(sessionId) {
  openDrawer("Attendance", '<div class="skeleton-line"></div>');
  try {
    const roster = await api(`/api/attendance/sessions/${encodeURIComponent(sessionId)}`), locked = roster.session.registerStatus === "submitted";
    const editable = canAccess("attendance", "edit");
    $("#drawer-title").textContent = `${roster.session.subject} · ${roster.session.batch} · ${roster.session.program || ""}`;
    $("#detail-drawer-body").innerHTML = `<form class="attendance-form" id="attendance-form" data-session-id="${esc(sessionId)}" data-locked="${locked}"><div class="attendance-form-head">${status(roster.session.registerStatus)}<span>${roster.entries.length} students</span></div>${!editable ? `<div class="inline-notice">${icon("shield")}<span>This register is read-only for your account.</span></div>` : ""}${roster.entries.map(entry => `<label class="attendance-student"><span><strong>${esc(entry.fullName)}</strong><small>${esc(entry.admissionNumber)}</small></span><select name="${esc(entry.studentId)}" data-original="${esc(entry.status)}"${editable ? "" : " disabled"}><option value="present" ${entry.status === "present" ? "selected" : ""}>Present</option><option value="late" ${entry.status === "late" ? "selected" : ""}>Late</option><option value="absent" ${entry.status === "absent" ? "selected" : ""}>Absent</option><option value="excused" ${entry.status === "excused" ? "selected" : ""}>Excused</option></select></label>`).join("")}${editable && locked ? `<label class="field"><span>Correction reason</span><textarea name="correctionReason" rows="3" required></textarea></label>` : ""}${editable ? `${formError("attendance-form-error")}<div class="drawer-actions">${locked ? `<button class="button button-primary" type="submit">Apply corrections</button>` : `<button class="button button-secondary" type="button" id="save-attendance">Save draft</button><button class="button button-primary" type="submit">Submit &amp; lock</button>`}</div>` : ""}</form>`;
    if (editable) {
      $("#attendance-form").addEventListener("submit", submitAttendance);
      $("#save-attendance")?.addEventListener("click", () => saveAttendance(false));
    }
  } catch (error) { $("#detail-drawer-body").innerHTML = emptyState("alert", "Could not open register", error.message); }
}

function attendanceEntries(form) { return $$('select[data-original]', form).map(select => ({ studentId: select.name, status: select.value, reason: "" })); }
async function saveAttendance(submit) {
  const form = $("#attendance-form"), button = $(submit ? 'button[type="submit"]' : "#save-attendance", form); button.disabled = true;
  try { await api(`/api/attendance/sessions/${encodeURIComponent(form.dataset.sessionId)}${submit ? "/submit" : ""}`, { method: submit ? "POST" : "PUT", body: JSON.stringify({ entries: attendanceEntries(form) }) }); state.attendanceSessions = await api("/api/attendance/sessions"); closeDetail(); renderAttendance(); toast(submit ? "Attendance submitted and locked." : "Attendance draft saved."); }
  catch (error) { showFormError("#attendance-form-error", error); button.disabled = false; }
}
async function submitAttendance(event) {
  event.preventDefault(); const form = event.currentTarget;
  if (form.dataset.locked !== "true") { await saveAttendance(true); return; }
  const changed = $$('select[data-original]', form).filter(select => select.value !== select.dataset.original), reason = String(new FormData(form).get("correctionReason") || "").trim(), button = $('button[type="submit"]', form); button.disabled = true;
  if (!changed.length) { showFormError("#attendance-form-error", new Error("Change at least one attendance status.")); button.disabled = false; return; }
  try { await Promise.all(changed.map(select => api(`/api/attendance/sessions/${encodeURIComponent(form.dataset.sessionId)}/corrections/${encodeURIComponent(select.name)}`, { method: "POST", body: JSON.stringify({ status: select.value, reason }) }))); state.attendanceSessions = await api("/api/attendance/sessions"); closeDetail(); renderAttendance(); toast("Attendance correction recorded."); }
  catch (error) { showFormError("#attendance-form-error", error); button.disabled = false; }
}

function openUserForm(presetRole = "") {
  const accessConfig = {
    faculty: {
      title: "Faculty access",
      description: "Creates a mobile login for the Faculty portal.",
      button: "Create faculty access",
      success: "Faculty access created.",
    },
    attendance_operator: {
      title: "Attendance access",
      description: "Creates a mobile login for the Attendance Desk.",
      button: "Create attendance access",
      success: "Attendance access created.",
    },
  }[presetRole];
  const roleField = accessConfig
    ? `<input name="role" type="hidden" value="${esc(presetRole)}"><div class="inline-notice">${icon("shield")}<span>${esc(accessConfig.description)}</span></div>`
    : `<label class="field"><span>Role</span><select name="role"><option value="academic_coordinator">Academic coordinator</option><option value="admissions_manager">Admissions manager</option><option value="counsellor">Counsellor</option><option value="front_desk">Front desk</option><option value="accounts">Accounts</option><option value="storekeeper">Storekeeper</option></select></label>`;
  const title = accessConfig?.title || "New user";
  const buttonLabel = accessConfig?.button || "Create user";
  const successMessage = accessConfig?.success || "User created.";
  openDrawer(title, `<form class="auth-form" id="user-form">${roleField}<label class="field"><span>Full name</span><input name="fullName" autocomplete="name" required></label><label class="field"><span>Mobile number</span><input name="mobile" type="tel" inputmode="tel" autocomplete="tel" placeholder="10-digit mobile number" maxlength="16" required></label><label class="field"><span>Email <small>(optional)</small></span><input name="email" type="email" autocomplete="email"></label><label class="field"><span>Temporary password</span>${passwordControl("password", { label: "temporary password", required: true })}</label>${formError("user-form-error")}<button class="button button-primary button-large" type="submit">${icon("user")}${esc(buttonLabel)}</button></form>`);
  $("#user-form").addEventListener("submit", async event => { event.preventDefault(); const form = new FormData(event.currentTarget), button = $('button[type="submit"]', event.currentTarget); button.disabled = true; try { await api("/api/settings/users", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) }); state.masters = await api("/api/settings/bootstrap"); closeDetail(); renderSettings(); toast(successMessage); } catch (error) { showFormError("#user-form-error", error); button.disabled = false; } });
}

function openStudentAccessForm() {
  const linked = new Set((state.masters.studentAccess || []).map(item => item.studentId));
  const available = state.students.filter(item => !linked.has(item.id));
  openDrawer("Student portal access", `<form class="auth-form" id="student-access-form"><div class="inline-notice">${icon("shield")}<span>${state.masters.studentAccess?.length || 0} of 100 accounts active</span></div><label class="field"><span>Student</span><select name="studentId" required><option value="">Select student</option>${options(available, item => `${item.fullName} · ${item.admissionNumber}`)}</select></label><label class="field"><span>Login mobile</span><input name="mobile" type="tel" inputmode="tel" autocomplete="tel" placeholder="10-digit mobile number" maxlength="16" required></label><label class="field"><span>Temporary password</span>${passwordControl("password", { label: "temporary password", required: true })}</label>${formError("student-access-error")}<button class="button button-primary button-large" type="submit">${icon("user")}Create student access</button></form>`);
  $("#student-access-form").addEventListener("submit", async event => { event.preventDefault(); const form=new FormData(event.currentTarget),button=$("button[type=submit]",event.currentTarget);button.disabled=true;try{await api("/api/settings/student-access",{method:"POST",body:JSON.stringify(Object.fromEntries(form.entries()))});state.masters=await api("/api/settings/bootstrap");closeDetail();renderSettings();toast("Student portal access created.");}catch(error){showFormError("#student-access-error",error);button.disabled=false;} });
}

function openParentAccessForm() {
  openDrawer("Parent portal access", `<form class="auth-form" id="parent-access-form"><div class="inline-notice">${icon("shield")}<span>Create a separate parent login linked to one student record. A mobile number can belong to only one login.</span></div><label class="field"><span>Student</span><select name="studentId" required><option value="">Select student</option>${options(state.students, item => `${item.fullName} · ${item.admissionNumber}`)}</select></label><label class="field"><span>Contact name</span><input name="fullName" autocomplete="name" required></label><label class="field"><span>Contact type</span><select name="contactType"><option value="primary_contact">Primary contact</option><option value="secondary_contact">Secondary contact</option></select></label><label class="field"><span>Login mobile</span><input name="mobile" type="tel" inputmode="tel" autocomplete="tel" placeholder="10-digit mobile number" maxlength="16" required></label><label class="field"><span>Temporary password</span>${passwordControl("password", { label: "temporary password", required: true })}</label>${formError("parent-access-error")}<button class="button button-primary button-large" type="submit">${icon("user")}Create parent access</button></form>`);
  $("#parent-access-form").addEventListener("submit", async event => { event.preventDefault(); const form = new FormData(event.currentTarget), button = $("button[type=submit]", event.currentTarget); button.disabled = true; try { await api("/api/settings/parent-access", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) }); state.masters = await api("/api/settings/bootstrap"); closeDetail(); renderSettings(); toast("Parent portal access created."); } catch (error) { showFormError("#parent-access-error", error); button.disabled = false; } });
}

function openMasterForm() {
  openDrawer("Academic setup", `<div class="setup-forms"><form class="auth-form master-form" data-kind="batches"><h3>Batch</h3><label class="field"><span>Name</span><input name="name" required></label><label class="field"><span>Program</span><input name="program" required></label><button class="button button-secondary" type="submit">Add batch</button></form><form class="auth-form master-form" data-kind="subjects"><h3>Subject</h3><label class="field"><span>Name</span><input name="name" required></label><div class="form-pair"><label class="field"><span>Code</span><input name="code" required></label><label class="field"><span>Program</span><input name="program" required></label></div><button class="button button-secondary" type="submit">Add subject</button></form><form class="auth-form master-form" data-kind="rooms"><h3>Room</h3><label class="field"><span>Name</span><input name="name" required></label><label class="field"><span>Capacity</span><input name="capacity" type="number" min="1" value="40" required></label><button class="button button-secondary" type="submit">Add room</button></form>${formError("master-form-error")}</div>`);
  $$(".master-form").forEach(form => form.addEventListener("submit", submitMaster));
}
async function submitMaster(event) {
  event.preventDefault(); const form = event.currentTarget, kind = form.dataset.kind, data = Object.fromEntries(new FormData(form).entries()), button = $('button[type="submit"]', form); if (data.capacity) data.capacity = Number(data.capacity); button.disabled = true;
  try { await api(`/api/settings/${kind}`, { method: "POST", body: JSON.stringify(data) }); state.masters = await api("/api/settings/bootstrap"); state.timetable = await api("/api/timetable/bootstrap"); state.sessions = state.timetable.sessions; form.reset(); renderSettings(); toast(`${kind.slice(0, -1).replace(/^./, c => c.toUpperCase())} added.`); button.disabled = false; }
  catch (error) { showFormError("#master-form-error", error); button.disabled = false; }
}

const selected = (value, current) => String(value ?? "") === String(current ?? "") ? " selected" : "";
const checked = value => value ? " checked" : "";
const ownerStatusOptions = (values, current) => values.map(value => `<option value="${esc(value)}"${selected(value, current)}>${esc(value.replaceAll("_", " "))}</option>`).join("");

async function openOwnerEdit(kind, id) {
  const module = { student: "students", lead: "admissions", agreement: "finance", payment: "finance", session: "timetable", assignment: "academics", notice: "communication" }[kind];
  if (module ? !canAccess(module, "edit") : !isOwner()) { toast(module ? `Edit access to ${PERMISSION_MODULE_LABELS[module]} is required.` : "Owner access is required.", "error"); return; }
  let item;
  if (kind === "student") item = await api(`/api/students/${encodeURIComponent(id)}`);
  else if (kind === "lead") item = state.leads.find(row => row.id === id);
  else if (kind === "agreement") item = state.agreements.find(row => row.id === id);
  else if (kind === "payment") item = state.payments.find(row => row.id === id);
  else if (kind === "session") item = state.sessions.find(row => row.id === id);
  else if (kind === "assignment") item = state.assignments.find(row => row.id === id);
  else if (kind === "notice") item = state.notices.find(row => row.id === id);
  else if (kind === "user" || kind === "access-user") item = state.masters.users.find(row => row.id === id);
  else item = state.masters[{ batch: "batches", subject: "subjects", room: "rooms" }[kind]]?.find(row => row.id === id);
  if (!item) { toast("This record is no longer available.", "error"); return; }

  let title = "Edit record", fields = "";
  if (kind === "student") {
    title = "Edit student";
    fields = `<div class="form-pair"><label class="field"><span>Admission number</span><input name="admissionNumber" value="${esc(item.admissionNumber)}" required></label><label class="field"><span>Student name</span><input name="fullName" value="${esc(item.fullName)}" required></label></div>
      <div class="form-pair"><label class="field"><span>Primary mobile</span><input name="mobile" value="${esc(item.mobile || "")}" inputmode="numeric"></label><label class="field"><span>Secondary mobile</span><input name="secondaryMobile" value="${esc(item.secondaryMobile || "")}" inputmode="numeric"></label></div>
      <label class="field"><span>Email</span><input name="email" type="email" value="${esc(item.email || "")}"></label>
      <label class="field"><span>Previous school</span><input name="previousSchool" value="${esc(item.previousSchool || "")}"></label>
      <div class="form-pair"><label class="field"><span>Student status</span><select name="status"><option value="active"${selected("active", item.status)}>Active</option><option value="draft"${selected("draft", item.status)}>Draft</option><option value="inactive"${selected("inactive", item.status)}>Opted out / inactive</option><option value="forfeited"${selected("forfeited", item.status)}>Forfeited</option></select><small>Changing an active student to opted out closes future fee liability and portal access.</small></label><label class="field"><span>Data quality</span><select name="dataQualityStatus">${ownerStatusOptions(["ready","review","blocked"], item.dataQualityStatus)}</select></label></div>
      <div class="form-pair"><label class="field"><span>Program</span><select name="program"><option value="">Not assigned</option>${STUDENT_PROGRAM_ORDER.map(program => `<option value="${esc(program)}"${selected(program, item.enrollment?.program)}>${esc(program)}</option>`).join("")}</select></label><label class="field"><span>Batch</span><select name="batch"><option value="">Not assigned</option>${STUDENT_BATCH_ORDER.map(batch => `<option value="${esc(batch)}"${selected(batch, item.enrollment?.batch)}>${esc(batch)}</option>`).join("")}</select></label></div>
      <label class="field"><span>Enrollment date</span><input name="enrollmentDate" type="date" value="${esc(item.enrollment?.enrollmentDate || "")}"></label>
      <fieldset class="choice-fieldset"><legend>Subjects</legend><div class="choice-grid">${["Physics", "Chemistry", "Mathematics", "Biology"].map(subject => `<label class="check-field"><input name="subjects" type="checkbox" value="${subject}"${checked(item.academicProfile?.subjects?.includes(subject))}><span>${subject}</span></label>`).join("")}</div></fieldset>`;
  } else if (kind === "lead") {
    title = "Edit enquiry";
    fields = `<div class="form-pair"><label class="field"><span>Student name</span><input name="student" value="${esc(item.student)}" required></label><label class="field"><span>Mobile</span><input name="mobile" value="${esc(item.mobile)}" required></label></div>
      <div class="form-pair"><label class="field"><span>Email</span><input name="email" type="email" value="${esc(item.email || "")}"></label><label class="field"><span>Program</span><select name="program" required>${STUDENT_PROGRAM_ORDER.map(program => `<option value="${esc(program)}"${selected(program, item.program)}>${esc(program)}</option>`).join("")}</select></label></div>
      <div class="form-pair"><label class="field"><span>Parent / guardian</span><input name="parent" value="${esc(item.parent)}" required></label><label class="field"><span>Parent mobile</span><input name="parentMobile" value="${esc(item.parentMobile || "")}"></label></div>
      <div class="form-pair"><label class="field"><span>Source</span><select name="source">${ownerStatusOptions(["walk-in","website","phone","whatsapp","referral","campaign","seminar","social media"], item.source)}</select></label><label class="field"><span>Counsellor</span><input name="counsellor" value="${esc(item.counsellor)}" required></label></div>
      <div class="form-pair"><label class="field"><span>Stage</span><select name="stage">${state.stages.map(value => `<option${selected(value,item.stage)}>${esc(value)}</option>`).join("")}</select></label><label class="field"><span>Priority</span><select name="priority">${ownerStatusOptions(["low","medium","high","urgent"], item.priority)}</select></label></div>
      <label class="field"><span>Next action</span><input name="nextAction" value="${esc(item.nextAction)}" required></label>
      <label class="field"><span>Next follow-up</span><input name="nextFollowUpAt" type="datetime-local" value="${item.nextFollowUpAt ? localInputValue(item.nextFollowUpAt) : ""}"></label>
      <label class="field"><span>Summary</span><textarea name="summary">${esc(item.summary || "")}</textarea></label>`;
  } else if (kind === "agreement") {
    title = `Edit fee agreement · ${item.studentName}`;
    fields = `<div class="form-pair"><label class="field"><span>Agreed fee</span><input name="agreedAmount" type="number" min="0" value="${item.agreedAmount}" required></label><label class="field"><span>Registration total</span><input name="legacyRegistrationTotal" type="number" min="0" value="${item.legacyRegistrationTotal}" required></label></div><div class="form-pair"><label class="field"><span>Currency</span><input name="currency" value="INR" readonly aria-readonly="true"></label><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["active","draft","inactive","completed"], item.status)}</select></label></div>`;
  } else if (kind === "payment") {
    title = `Review staged payment · ${item.studentName}`;
    fields = `<div class="immutable-record-note">${icon("shield")}<span>${money(item.amount)} · ${esc(item.sourceNote || "Imported workbook row")}<small>The source row and amount remain immutable. Confirm the normalized date and payment mode before including it in trusted totals.</small></span></div>
      <div class="form-pair"><label class="field"><span>Confirmed payment date</span><input name="transactionDate" type="date" value="${esc(item.date || "")}" max="${dateInputValue()}"></label><label class="field"><span>Confirmed payment mode</span><select name="method"><option value="">Select mode</option>${paymentMethodOptions(item.method)}</select></label></div>
      <label class="field"><span>Bank / UPI / cheque reference <small>(optional for cash)</small></span><input name="reference" value="${esc(item.reference || "")}" maxlength="255"></label>
      <label class="field"><span>Reconciliation note <small>(optional)</small></span><textarea name="notes" rows="3" maxlength="2000">${esc(item.notes || "")}</textarea></label>
      <label class="field"><span>Review classification</span><select name="reconciliationStatus">${ownerStatusOptions(["ready","needs_date","needs_mode","review","do_not_import"], item.reconciliationStatus)}</select><small>Only Ready rows contribute to recorded-payment totals. Excluded notes remain auditable without affecting balances.</small></label>`;
  } else if (kind === "session") {
    title = "Edit class";
    fields = `<label class="field"><span>Batch</span><select name="batchId">${state.timetable.batches.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.batchId)}>${esc(row.name)} · ${esc(row.program)}</option>`).join("")}</select></label><label class="field"><span>Subject</span><select name="subjectId">${state.timetable.subjects.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.subjectId)}>${esc(row.name)}</option>`).join("")}</select></label><div class="form-pair"><label class="field"><span>Faculty</span><select name="facultyId">${state.timetable.faculty.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.facultyId)}>${esc(row.fullName)}</option>`).join("")}</select></label><label class="field"><span>Room</span><select name="roomId">${state.timetable.rooms.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.roomId)}>${esc(row.name)}</option>`).join("")}</select></label></div><div class="form-pair"><label class="field"><span>Starts</span><input name="startsAt" type="datetime-local" value="${localInputValue(item.startsAt)}" required></label><label class="field"><span>Ends</span><input name="endsAt" type="datetime-local" value="${localInputValue(item.endsAt)}" required></label></div><div class="form-pair"><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["scheduled","completed","cancelled"], item.status)}</select></label><label class="check-field"><input name="allowOverride" type="checkbox"><span>Allow schedule override</span></label></div><label class="field"><span>Notes</span><textarea name="notes">${esc(item.notes || "")}</textarea></label><label class="field"><span>Override reason</span><textarea name="overrideReason">${esc(item.overrideReason || "")}</textarea></label>`;
  } else if (kind === "assignment") {
    title = "Edit assignment";
    fields = `<label class="field"><span>Title</span><input name="title" value="${esc(item.title)}" required></label><div class="form-pair"><label class="field"><span>Batch</span><select name="batchId">${state.timetable.batches.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.batchId)}>${esc(row.name)} · ${esc(row.program)}</option>`).join("")}</select></label><label class="field"><span>Subject</span><select name="subjectId">${state.timetable.subjects.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.subjectId)}>${esc(row.name)}</option>`).join("")}</select></label></div><label class="field"><span>Due</span><input name="dueAt" type="datetime-local" value="${localInputValue(item.dueAt)}" required></label><label class="field"><span>Material link</span><input name="externalUrl" type="url" value="${esc(item.externalUrl)}" required></label><label class="field"><span>Instructions</span><textarea name="instructions">${esc(item.instructions || "")}</textarea></label><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["draft","published"], item.status)}</select></label>`;
  } else if (kind === "notice") {
    title = "Edit notice";
    fields = `<label class="field"><span>Title</span><input name="title" value="${esc(item.title)}" required></label><label class="field"><span>Message</span><textarea name="body" required>${esc(item.body)}</textarea></label><div class="form-pair"><label class="field"><span>Audience</span><select name="audience">${ownerStatusOptions(["all","parents","students","faculty","batch"], item.audience)}</select></label><label class="field"><span>Channel</span><select name="channel">${ownerStatusOptions(["in_app","email","sms","whatsapp"], item.channel)}</select></label></div><label class="field"><span>Batch</span><select name="batchId"><option value="">Not selected</option>${state.timetable.batches.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.batchId)}>${esc(row.name)} · ${esc(row.program)}</option>`).join("")}</select></label><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["draft","published"], item.status)}</select></label>`;
  } else if (kind === "user" || kind === "access-user") {
    title = "Edit user access";
    fields = `<label class="field"><span>Full name</span><input name="fullName" value="${esc(item.fullName)}" autocomplete="name" required></label><label class="field"><span>Mobile number</span><input name="mobile" type="tel" inputmode="tel" autocomplete="tel" value="${esc(item.mobile || "")}" placeholder="10-digit mobile number" maxlength="16" required></label><label class="field"><span>Email <small>(optional contact only)</small></span><input name="email" type="email" autocomplete="email" value="${esc(item.email || "")}"></label><div class="form-pair"><label class="field"><span>Role</span><select name="role">${ownerStatusOptions(["owner","admissions_manager","counsellor","front_desk","accounts","academic_coordinator","faculty","attendance_operator","storekeeper","student","parent","parent_student"], item.role)}</select></label><label class="check-field"><input name="isActive" type="checkbox"${checked(item.isActive)}><span>Account active</span></label></div><label class="field"><span>New password</span>${passwordControl("password", { label: "new password" })}<small>Leave blank to keep the existing password.</small></label>`;
  } else if (kind === "batch") {
    title = "Edit batch"; fields = `<label class="field"><span>Name</span><input name="name" value="${esc(item.name)}" required></label><label class="field"><span>Program</span><input name="program" value="${esc(item.program)}" required></label><label class="check-field"><input name="isActive" type="checkbox"${checked(item.isActive)}><span>Batch active</span></label>`;
  } else if (kind === "subject") {
    title = "Edit subject"; fields = `<label class="field"><span>Name</span><input name="name" value="${esc(item.name)}" required></label><div class="form-pair"><label class="field"><span>Code</span><input name="code" value="${esc(item.code)}" required></label><label class="field"><span>Program</span><input name="program" value="${esc(item.program)}" required></label></div><label class="check-field"><input name="isActive" type="checkbox"${checked(item.isActive)}><span>Subject active</span></label>`;
  } else if (kind === "room") {
    title = "Edit room"; fields = `<div class="form-pair"><label class="field"><span>Name</span><input name="name" value="${esc(item.name)}" required></label><label class="field"><span>Capacity</span><input name="capacity" type="number" min="1" max="500" value="${item.capacity}" required></label></div><label class="check-field"><input name="isActive" type="checkbox"${checked(item.isActive)}><span>Room active</span></label>`;
  }
  openDrawer(title, `<form class="auth-form owner-edit-form" id="owner-edit-form" data-kind="${esc(kind)}" data-record-id="${esc(id)}">${fields}${formError("owner-edit-error")}<button class="button button-primary button-large" type="submit">${icon("edit")}Save changes</button></form>`);
  $("#owner-edit-form").addEventListener("submit", submitOwnerEdit);
}

async function submitOwnerEdit(event) {
  event.preventDefault();
  const form = event.currentTarget, kind = form.dataset.kind, id = form.dataset.recordId, data = Object.fromEntries(new FormData(form).entries());
  const button = $('button[type="submit"]', form); button.disabled = true;
  let endpoint = "", payload = { ...data };
  if (kind === "student") { endpoint = `/api/students/${id}`; payload.email ||= null; payload.mobile ||= null; payload.secondaryMobile ||= null; payload.previousSchool ||= null; payload.program ||= null; payload.batch ||= null; payload.enrollmentDate ||= null; payload.subjects = new FormData(form).getAll("subjects"); }
  else if (kind === "lead") { endpoint = `/api/admissions/leads/${id}`; payload.email ||= null; payload.parentMobile ||= null; payload.nextFollowUpAt = payload.nextFollowUpAt ? indiaInputToISOString(payload.nextFollowUpAt) : null; }
  else if (kind === "agreement") { endpoint = `/api/finance/agreements/${id}`; payload.agreedAmount = Number(payload.agreedAmount); payload.legacyRegistrationTotal = Number(payload.legacyRegistrationTotal); }
  else if (kind === "payment") { endpoint = `/api/finance/staged-payments/${id}/review`; payload.transactionDate ||= null; payload.method ||= null; payload.reference ||= null; }
  else if (kind === "session") { endpoint = `/api/timetable/sessions/${id}`; payload.startsAt = indiaInputToISOString(payload.startsAt); payload.endsAt = indiaInputToISOString(payload.endsAt); payload.allowOverride = form.elements.allowOverride.checked; }
  else if (kind === "assignment") { endpoint = `/api/academics/assignments/${id}`; payload.dueAt = indiaInputToISOString(payload.dueAt); }
  else if (kind === "notice") { endpoint = `/api/communication/notices/${id}`; payload.batchId ||= null; }
  else if (kind === "user" || kind === "access-user") { endpoint = `/api/settings/users/${id}`; payload.isActive = form.elements.isActive.checked; payload.password ||= null; }
  else { endpoint = `/api/settings/${{ batch: "batches", subject: "subjects", room: "rooms" }[kind]}/${id}`; payload.isActive = form.elements.isActive.checked; if (kind === "room") payload.capacity = Number(payload.capacity); }
  try {
    await api(endpoint, { method: "PATCH", body: JSON.stringify(payload) });
    if (kind === "student") await refreshStudentAndFinanceState();
    else if (kind === "lead") state.leads = await fetchAll("/api/admissions/leads");
    else if (kind === "agreement") state.agreements = await fetchAll("/api/finance/agreements");
    else if (kind === "payment") state.payments = await fetchAll("/api/finance/transactions");
    else if (kind === "session") { state.timetable = await api("/api/timetable/bootstrap"); state.sessions = state.timetable.sessions; state.attendanceSessions = await api("/api/attendance/sessions"); }
    else if (kind === "assignment") state.assignments = await api("/api/academics/assignments");
    else if (kind === "notice") state.notices = await api("/api/communication/notices");
    else { state.masters = await api("/api/settings/bootstrap"); state.timetable = await api("/api/timetable/bootstrap"); state.sessions = state.timetable.sessions; }
    closeDetail(); renderAll(); toast("Changes saved.");
  } catch (error) { showFormError("#owner-edit-error", error); button.disabled = false; }
}

const viewTitles = { dashboard: "Overview", admissions: "Enquiries", students: "Students", finance: "Finance", attendance: "Attendance", academics: "Academics", examinations: "Examinations", timetable: "Faculty & timetable", communication: "Communication", inventory: "Inventory", reports: "Reports", settings: "Settings & audit" };

function currentOperationsRoute() {
  const path = location.pathname.replace(/\/+$/, "") || "/";
  const studentMatch = path.match(/^\/operations\/students\/([^/]+)$/);
  if (studentMatch) return { kind: "student", view: "students", studentId: decodeURIComponent(studentMatch[1]) };
  const ledgerMatch = path.match(/^\/operations\/finance\/ledger\/([^/]+)$/);
  if (ledgerMatch) return { kind: "ledger", view: "finance", studentId: decodeURIComponent(ledgerMatch[1]) };
  const entry = Object.entries(VIEW_PATHS).find(([, routePath]) => routePath === path);
  if (entry) return { kind: "view", view: entry[0] };
  const legacyView = location.hash.slice(1);
  return { kind: "view", view: viewTitles[legacyView] ? legacyView : "dashboard" };
}

function operationsPath(view, detail = null) {
  if (detail?.kind === "student" && detail.studentId) return `/operations/students/${encodeURIComponent(detail.studentId)}`;
  if (detail?.kind === "ledger" && detail.studentId) return `/operations/finance/ledger/${encodeURIComponent(detail.studentId)}`;
  return VIEW_PATHS[view] || VIEW_PATHS.dashboard;
}

function writeOperationsRoute(view, detail = null, replace = false) {
  const path = operationsPath(view, detail);
  if (`${location.pathname}${location.search}${location.hash}` === path) return;
  history[replace ? "replaceState" : "pushState"]({ view, detail }, "", path);
}

function replaceOperationsRoute(view, detail = null) {
  writeOperationsRoute(view, detail, true);
}

async function applyCurrentOperationsRoute() {
  if (!state.token) return;
  const route = currentOperationsRoute();
  const view = allowedViews().has(route.view) ? route.view : "dashboard";
  showView(view, false);
  if (route.kind === "student" && view === "students") await openStudent(route.studentId, false);
  else if (route.kind === "ledger" && view === "finance") openStudentLedger(route.studentId, null, false);
  else {
    if (detailRouteStudentId) closeDetail(false, false);
    if (ledgerCurrentStudentId) closeStudentLedger(false, false);
  }
}

function showView(view, updateRoute = true) {
  if (!$("#" + view) || !allowedViews().has(view)) return; state.view = view;
  if (detailRouteStudentId && (view !== "students" || updateRoute)) closeDetail(false, false);
  if (view === "finance") closeStudentLedger(false, false);
  $$(".app-view").forEach(node => node.classList.toggle("active", node.id === view));
  $$(".nav-item").forEach(node => { const active = node.dataset.view === view; node.classList.toggle("active", active); active ? node.setAttribute("aria-current", "page") : node.removeAttribute("aria-current"); });
  $("#page-title").textContent = viewTitles[view];
  if (updateRoute) writeOperationsRoute(view);
  closeSidebar(); closeCommand(); $("#main-content").focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  loadViewResources(view).catch(error => {
    if (state.token && error.status !== 401) toast(error.message || "This module could not be loaded.", "error");
  });
}

function renderCommandResults(query = "") {
  const needle = query.trim().toLowerCase();
  const views = Object.entries(viewTitles).filter(([key, title]) => allowedViews().has(key) && (!needle || title.toLowerCase().includes(needle))).slice(0, 7);
  const students = state.students.filter(item => !needle || [item.fullName, item.admissionNumber, item.mobile].some(value => String(value || "").toLowerCase().includes(needle))).slice(0, needle ? 7 : 3);
  $("#command-results").innerHTML = `<p>${needle ? "Results" : "Navigate"}</p>${views.map(([key, title]) => `<button class="command-item" type="button" data-command-view="${key}"><span>${icon(key === "dashboard" ? "grid" : key === "finance" ? "wallet" : key === "students" ? "users" : key === "examinations" ? "exam" : "arrow-right")}</span><strong>${esc(title)}</strong><span>${icon("chevron-right")}</span></button>`).join("")}${students.length ? `<p>Students</p>${students.map(student => `<button class="command-item" type="button" data-command-student="${esc(student.id)}"><span>${icon("user")}</span><span><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)} · ${esc(student.program)}</small></span><span>${icon("chevron-right")}</span></button>`).join("")}` : needle ? emptyState("search", "No results") : ""}`;
}
function syncBodyScrollLock() {
  const overlayOpen = $("#detail-drawer").classList.contains("open") || !$("#command-overlay").classList.contains("hidden") || $("#sidebar").classList.contains("open");
  document.body.classList.toggle("no-scroll", overlayOpen);
}
let commandTrigger = null;
function openCommand() { commandTrigger = document.activeElement; $("#command-overlay").classList.remove("hidden"); $("#command-overlay").setAttribute("aria-hidden", "false"); $("#global-search").value = ""; renderCommandResults(); syncBodyScrollLock(); setTimeout(() => $("#global-search").focus(), 10); }
function closeCommand(restoreFocus = false) { const wasOpen = !$("#command-overlay").classList.contains("hidden"); $("#command-overlay").classList.add("hidden"); $("#command-overlay").setAttribute("aria-hidden", "true"); syncBodyScrollLock(); if (restoreFocus && wasOpen) commandTrigger?.focus?.(); commandTrigger = null; }
const mobileNavigation = matchMedia("(max-width: 960px)");
let sidebarTrigger = null;
function syncSidebarAccessibility() {
  const mobile = mobileNavigation.matches;
  const open = $("#sidebar").classList.contains("open");
  $("#sidebar").inert = mobile && !open;
  $("#sidebar").setAttribute("aria-hidden", String(mobile && !open));
  $("#main-content").inert = mobile && open;
}
function openSidebar() { sidebarTrigger = document.activeElement; $("#sidebar").classList.add("open"); $("#drawer-scrim").classList.add("open"); $("#menu-button").setAttribute("aria-expanded", "true"); syncSidebarAccessibility(); syncBodyScrollLock(); $("#sidebar-close").focus(); }
function closeSidebar(restoreFocus = false) { const wasOpen = $("#sidebar").classList.contains("open"); $("#sidebar").classList.remove("open"); $("#drawer-scrim").classList.remove("open"); $("#menu-button").setAttribute("aria-expanded", "false"); syncSidebarAccessibility(); syncBodyScrollLock(); if (restoreFocus && wasOpen) (sidebarTrigger || $("#menu-button")).focus(); sidebarTrigger = null; }

function applyRoleUI() {
  const role = state.user?.role || "";
  const visibleViews = allowedViews();
  document.body.dataset.role = role;
  $$(".nav-item").forEach(node => {
    const visible = visibleViews.has(node.dataset.view);
    node.hidden = !visible;
    node.disabled = !visible;
  });
  const actionPermissions = {
    "#quick-new-lead": ["admissions", "create"],
    "#quick-new-student": ["students", "create"],
    "#quick-new-payment": ["finance", "create"],
    "#quick-new-session": ["timetable", "create"],
    "#quick-new-notice": ["communication", "create"],
    "#new-lead-button": ["admissions", "create"],
    "#new-student": ["students", "create"],
    "#new-payment": ["finance", "create"],
    "#new-fee-agreement": ["finance", "create"],
    "#new-future-payment": ["finance", "create"],
    "#new-session": ["timetable", "create"],
    "#new-teaching-assignment": ["timetable", "create"],
    "#new-assignment": ["academics", "create"],
    "#new-examination": ["examinations", "create"],
    "#new-notice": ["communication", "create"],
    "#new-inventory-item": ["inventory", "create"]
  };
  Object.entries(actionPermissions).forEach(([selector, [module, action]]) => {
    const node = $(selector);
    if (node) node.hidden = !canAccess(module, action);
  });
  ["#settings-add-account", "#new-master"].forEach(selector => {
    const node = $(selector);
    if (node) node.hidden = !isOwner();
  });
  const quickActionPanel = $("#dashboard-quick-actions");
  if (quickActionPanel) quickActionPanel.hidden = !$$('[data-dashboard-action]', quickActionPanel).some(node => !node.hidden);
  $$("[data-owner-edit]").forEach(node => {
    const kind = node.dataset.ownerEdit;
    const module = { student: "students", lead: "admissions", agreement: "finance", payment: "finance", session: "timetable", assignment: "academics", notice: "communication" }[kind];
    node.hidden = module ? !canAccess(module, "edit") : !isOwner();
  });
  $$("[data-inventory-edit], [data-inventory-movement]").forEach(node => { node.hidden = !canAccess("inventory", "edit"); });
  $$("[data-teaching-assignment-edit]").forEach(node => { node.hidden = !canAccess("timetable", "edit"); });
  $$("[data-examination-edit]").forEach(node => { node.hidden = !canAccess("examinations", "edit"); });
}

function handleCommandKeyboard(event) {
  if ($("#command-overlay").classList.contains("hidden")) return;
  const items = $$(".command-item", $("#command-results"));
  if (["ArrowDown", "ArrowUp"].includes(event.key)) {
    event.preventDefault();
    if (!items.length) return;
    const current = items.indexOf(document.activeElement);
    const next = current < 0 ? (event.key === "ArrowDown" ? 0 : items.length - 1) : (current + (event.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
    items[next].focus();
    return;
  }
  if (event.key === "Enter" && document.activeElement === $("#global-search") && items.length) {
    event.preventDefault();
    items[0].click();
    return;
  }
  if (event.key !== "Tab") return;
  const focusable = [$("#global-search"), ...items];
  const first = focusable[0], last = focusable.at(-1);
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

let accountMenuTrigger = null;
function closeAccountMenu(restoreFocus = false) {
  $("#account-menu").classList.add("hidden");
  [$("#user-menu-button"), $("#topbar-profile-button")].forEach(button => button.setAttribute("aria-expanded", "false"));
  if (restoreFocus && accountMenuTrigger) accountMenuTrigger.focus();
  accountMenuTrigger = null;
}
function toggleAccountMenu(trigger) {
  const menu = $("#account-menu");
  const reopening = menu.classList.contains("hidden") || accountMenuTrigger !== trigger;
  closeAccountMenu();
  if (!reopening) return;
  accountMenuTrigger = trigger;
  menu.classList.toggle("from-sidebar", trigger.id === "user-menu-button");
  menu.classList.remove("hidden");
  trigger.setAttribute("aria-expanded", "true");
  $("#logout-button").focus();
}

function initializeTheme() {
  const saved = localStorage.getItem("lakshya_theme") || "light"; document.documentElement.dataset.theme = saved; updateThemeIcon();
}
function updateThemeIcon() { const dark = document.documentElement.dataset.theme === "dark"; $("#theme-toggle").dataset.icon = dark ? "sun" : "moon"; $("#theme-toggle").setAttribute("aria-label", dark ? "Use light appearance" : "Use dark appearance"); injectIcons($("#theme-toggle")); }
function toggleTheme() { const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = next; localStorage.setItem("lakshya_theme", next); updateThemeIcon(); }
async function logout(notify = true) {
  const token = state.token;
  closeAccountMenu();
  if (token) {
    try { await fetch("/api/auth/logout", { method: "POST", headers: { Authorization: `Bearer ${token}` } }); }
    catch { /* Local sign-out must still complete when the network is unavailable. */ }
  }
  clearSession();
  resetAuthForm();
  showAuth();
  if (notify) toast("Signed out.");
}

function exportStudents() {
  const rows = filteredStudents(), fields = [["Admission number", "Student", "Mobile", "Previous school", "Program", "Batch", "Enrollment date", "Data quality"], ...rows.map(item => [item.admissionNumber, item.fullName, item.mobile, item.previousSchool, item.program, item.batch, item.enrollmentDate, item.dataQualityStatus])];
  const csv = fields.map(row => row.map(value => `"${String(value || "").replaceAll('"', '""')}"`).join(",")).join("\n");
  const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" })); link.download = `lakshya-students-${new Date().toISOString().slice(0, 10)}.csv`; link.click(); URL.revokeObjectURL(link.href); toast(`${rows.length} student records exported.`);
}

function bindEvents() {
  $("#boot-retry").addEventListener("click", () => window.location.reload());
  $("#auth-form").addEventListener("submit", handleAuth);
  $("#legacy-login-toggle").addEventListener("click", () => {
    setLegacyLoginMode(!state.legacyEmailLogin);
    $("#auth-mobile").focus();
  });
  document.addEventListener("click", event => {
    const passwordToggle = event.target.closest("[data-password-toggle]");
    if (passwordToggle) {
      togglePassword(passwordToggle);
      return;
    }
    const view = event.target.closest("[data-view], [data-view-target]")?.dataset; if (view) showView(view.view || view.viewTarget);
    const dashboardAction = event.target.closest("[data-dashboard-action]")?.dataset.dashboardAction;
    if (dashboardAction === "lead") openLeadForm();
    else if (dashboardAction === "student") openStudentCreateForm();
    else if (dashboardAction === "payment") openPaymentForm();
    else if (dashboardAction === "session") openSessionForm();
    else if (dashboardAction === "notice") openNoticeForm();
    const settingsTab = event.target.closest("[data-settings-section]");
    if (settingsTab) showSettingsSection(settingsTab.dataset.settingsSection);
    const settingsAccountType = event.target.closest("[data-settings-account-type]")?.dataset.settingsAccountType;
    if (settingsAccountType === "student") openStudentAccessForm();
    else if (settingsAccountType === "parent") openParentAccessForm();
    else if (settingsAccountType === "faculty") openUserForm("faculty");
    else if (settingsAccountType === "attendance") openUserForm("attendance_operator");
    else if (settingsAccountType === "staff") openUserForm();
    const batchButton = event.target.closest("[data-student-batch]");
    if (batchButton) {
      studentHierarchyState.batch = batchButton.dataset.studentBatch;
      studentHierarchyState.program = "";
      renderStudentRows();
    }
    const programButton = event.target.closest("[data-student-program]");
    if (programButton) {
      studentHierarchyState.program = programButton.dataset.studentProgram;
      renderStudentRows();
    }
    const ownerEdit = event.target.closest("[data-owner-edit]");
    if (ownerEdit) openOwnerEdit(ownerEdit.dataset.ownerEdit, ownerEdit.dataset.editId);
    const userPermissions = event.target.closest("[data-user-permissions]");
    if (userPermissions) openUserPermissions(userPermissions.dataset.userPermissions);
    const viewPayments = event.target.closest("[data-view-payments]")?.dataset.viewPayments;
    if (viewPayments) showStudentPayments(viewPayments);
    const ledgerButton = event.target.closest("[data-open-ledger]");
    if (ledgerButton) openStudentLedger(ledgerButton.dataset.openLedger, ledgerButton);
    const examinationButton = event.target.closest("[data-examination-open]");
    if (examinationButton) openExamination(examinationButton.dataset.examinationOpen);
    const conversationButton = event.target.closest("[data-conversation-id]");
    if (conversationButton) openConversation(conversationButton.dataset.conversationId);
    const examinationEdit = event.target.closest("[data-examination-edit]");
    if (examinationEdit) {
      const item = state.examinations.find(row => row.id === examinationEdit.dataset.examinationEdit);
      if (item) openExaminationForm(item);
    }
    const teachingAssignmentEdit = event.target.closest("[data-teaching-assignment-edit]");
    if (teachingAssignmentEdit) {
      const item = (state.timetable.teachingAssignments || []).find(row => row.id === teachingAssignmentEdit.dataset.teachingAssignmentEdit);
      if (item) openTeachingAssignmentForm(item);
    }
    const studentInventoryIssue = event.target.closest("[data-student-inventory-issue]");
    if (studentInventoryIssue) openStudentInventoryIssue(studentInventoryIssue.dataset.studentInventoryIssue);
    const studentInventoryReturn = event.target.closest("[data-student-inventory-return]");
    if (studentInventoryReturn) openStudentInventoryReturn(studentInventoryReturn.dataset.inventoryStudentId, studentInventoryReturn.dataset.studentInventoryReturn);
    const studentLifecycle = event.target.closest("[data-student-lifecycle]");
    if (studentLifecycle) openStudentLifecycleForm(studentLifecycle.dataset.lifecycleStudentId, studentLifecycle.dataset.lifecycleStudentName, studentLifecycle.dataset.studentLifecycle);
    const inventoryEdit = event.target.closest("[data-inventory-edit]");
    if (inventoryEdit) {
      const item = (state.inventory.items || []).find(row => row.id === inventoryEdit.dataset.inventoryEdit);
      if (item) openInventoryItemForm(item);
    }
    const inventoryMovement = event.target.closest("[data-inventory-movement]");
    if (inventoryMovement) {
      const item = (state.inventory.items || []).find(row => row.id === inventoryMovement.dataset.inventoryMovement);
      if (item) openInventoryMovementForm(item);
    }
    const installmentEdit = event.target.closest("[data-installment-edit]");
    if (installmentEdit) {
      const item = state.installments.find(row => row.id === installmentEdit.dataset.installmentEdit);
      if (item) openFuturePaymentForm(item);
    }
    const paymentReverse = event.target.closest("[data-payment-reverse]");
    if (paymentReverse) {
      const item = state.payments.find(row => row.id === paymentReverse.dataset.paymentReverse);
      if (item) openPaymentReversalForm(item);
    }
    const leadFollowUp = event.target.closest("[data-lead-follow-up]");
    if (leadFollowUp) {
      const item = state.leads.find(row => row.id === leadFollowUp.dataset.leadFollowUp);
      if (item) openLeadFollowUpForm(item);
    }
    const leadConvert = event.target.closest("[data-lead-convert]");
    if (leadConvert) {
      const item = state.leads.find(row => row.id === leadConvert.dataset.leadConvert);
      if (item) openLeadConversionForm(item);
    }
    const student = event.target.closest("[data-student-id]")?.dataset.studentId; if (student) openStudent(student);
    const commandView = event.target.closest("[data-command-view]")?.dataset.commandView; if (commandView) showView(commandView);
    const commandStudent = event.target.closest("[data-command-student]")?.dataset.commandStudent; if (commandStudent) { closeCommand(); openStudent(commandStudent); }
    const attendance = event.target.closest("[data-attendance-id]")?.dataset.attendanceId; if (attendance) openAttendance(attendance);
    const timetableDate = event.target.closest("[data-timetable-date]")?.dataset.timetableDate;
    if (timetableDate) { timetableSelectedDate = timetableDate; renderTimetable(); }
    if (!event.target.closest("#account-menu, #user-menu-button, #topbar-profile-button")) closeAccountMenu();
  });
  $("#menu-button").addEventListener("click", openSidebar); $("#sidebar-close").addEventListener("click", closeSidebar); $("#drawer-scrim").addEventListener("click", closeSidebar);
  $("#detail-close").addEventListener("click", closeDetail); $("#detail-overlay").addEventListener("click", closeDetail);
  $("#search-trigger").addEventListener("click", openCommand); $("#command-overlay").addEventListener("click", event => { if (event.target === event.currentTarget) closeCommand(); });
  $("#global-search").addEventListener("input", event => renderCommandResults(event.target.value));
  $("#global-search").addEventListener("keydown", handleCommandKeyboard);
  $("#command-results").addEventListener("keydown", handleCommandKeyboard);
  $("#theme-toggle").addEventListener("click", toggleTheme);
  [$("#user-menu-button"), $("#topbar-profile-button")].forEach(button => button.addEventListener("click", event => toggleAccountMenu(event.currentTarget)));
  $("#logout-button").addEventListener("click", () => logout());
  $("#student-search").addEventListener("input", renderStudentRows); $("#student-quality-filter").addEventListener("change", renderStudentRows);
  $("#agreement-search").addEventListener("input", renderAgreementRows); $("#agreement-balance-filter").addEventListener("change", renderAgreementRows); $("#payment-search").addEventListener("input", renderPaymentRows); $("#payment-status-filter").addEventListener("change", renderPaymentRows);
  $("#clear-payment-student-filter").addEventListener("click", () => { financeStudentFilter = ""; renderPaymentRows(); });
  $("#ledger-back").addEventListener("click", () => closeStudentLedger());
  $("#ledger-payment-register").addEventListener("click", () => { const studentId = ledgerCurrentStudentId; if (studentId) showStudentPayments(studentId); });
  $("#print-student-ledger").addEventListener("click", () => window.print());
  $("#lead-search").addEventListener("input", renderLeadRows); $("#lead-stage-filter").addEventListener("change", renderLeadRows); $("#refresh-leads").addEventListener("click", async () => { try { state.leads = await fetchAll("/api/admissions/leads"); renderAdmissions(); toast("Enquiries refreshed."); } catch (error) { toast(error.message, "error"); } });
  $("#new-lead-button").addEventListener("click", openLeadForm); $("#new-student").addEventListener("click", openStudentCreateForm); $("#export-students").addEventListener("click", exportStudents);
  $("#new-session").addEventListener("click", openSessionForm); $("#new-teaching-assignment").addEventListener("click", () => openTeachingAssignmentForm()); $("#new-assignment").addEventListener("click", openAssignmentForm); $("#new-notice").addEventListener("click", openNoticeForm); $("#settings-add-account").addEventListener("click", openSettingsAccountPicker); $("#new-master").addEventListener("click", openMasterForm);
  $("#new-inventory-item").addEventListener("click", () => openInventoryItemForm());
  $("#new-future-payment").addEventListener("click", () => openFuturePaymentForm());
  $("#new-payment").addEventListener("click", openPaymentForm);
  $("#new-fee-agreement").addEventListener("click", openFeeAgreementForm);
  $("#inventory-search").addEventListener("input", renderInventory);
  $("#inventory-category-filter").addEventListener("change", renderInventory);
  $("#new-examination").addEventListener("click", () => openExaminationForm());
  $("#examination-search").addEventListener("input", renderExaminations);
  $("#examination-status-filter").addEventListener("change", renderExaminations);
  $("#academic-import-file").addEventListener("change", importAcademicData);
  $("#settings-account-search").addEventListener("input", event => { settingsAccountSearch = event.target.value; renderSettingsAccounts(); });
  $("#settings-account-filter").addEventListener("change", event => { settingsAccountFilter = event.target.value; renderSettingsAccounts(); });
  $(".settings-tabs").addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    const tabs = $$("[data-settings-section]");
    const current = Math.max(0, tabs.indexOf(document.activeElement));
    const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    event.preventDefault();
    showSettingsSection(tabs[next].dataset.settingsSection);
    tabs[next].focus();
  });
  $("#refresh-attendance").addEventListener("click", async () => { try { state.attendanceSessions = await api("/api/attendance/sessions"); renderAttendance(); toast("Attendance refreshed."); } catch (error) { toast(error.message, "error"); } });
  $("#refresh-reports").addEventListener("click", async () => { try { state.report = await api("/api/reports/overview"); renderReports(); toast("Reports refreshed."); } catch (error) { toast(error.message, "error"); } });
  $$("[data-report-export]").forEach(button => button.addEventListener("click", () => downloadReport(button.dataset.reportExport, button)));
  $$("[data-finance-tab]").forEach(button => button.addEventListener("click", () => activateFinanceTab(button.dataset.financeTab)));
  $("#finance-view-tabs").addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    const buttons = $$("[data-finance-tab]");
    const current = buttons.indexOf(document.activeElement);
    if (current < 0) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
    activateFinanceTab(buttons[next].dataset.financeTab, true);
  });
  $$("[data-timetable-view]").forEach(button => button.addEventListener("click", () => activateTimetableView(button.dataset.timetableView)));
  $("#timetable-view-tabs").addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    const buttons = $$("[data-timetable-view]");
    const current = buttons.indexOf(document.activeElement);
    if (current < 0) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
    activateTimetableView(buttons[next].dataset.timetableView, true);
  });
  document.addEventListener("keydown", event => {
    trapDrawerFocus(event);
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); openCommand(); }
    if (event.key === "Escape") { closeStudentLedger(); closeCommand(true); closeDetail(); closeSidebar(true); closeAccountMenu(true); }
    if (event.key === "Tab" && mobileNavigation.matches && $("#sidebar").classList.contains("open")) {
      const focusable = $$('button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])', $("#sidebar")).filter(node => node.offsetParent !== null);
      const first = focusable[0], last = focusable.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  window.addEventListener("popstate", () => {
    applyCurrentOperationsRoute().catch(error => {
      if (state.token && error.status !== 401) toast(error.message || "This record could not be opened.", "error");
    });
  });
  mobileNavigation.addEventListener?.("change", syncSidebarAccessibility);
  syncSidebarAccessibility();
}

initialize();
