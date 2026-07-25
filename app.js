"use strict";

const icons = {
  eye: '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/>',
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
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  message: '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z"/><path d="M8 9h8M8 13h5"/>',
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
const state = { token: sessionStorage.getItem("lakshya_token"), user: cachedUser, setupRequired: false, view: "dashboard", students: [], agreements: [], payments: [], leads: [], stages: [], sessions: [], timetable: { batches: [], subjects: [], rooms: [], faculty: [] }, assignments: [], attendanceSessions: [], notices: [], report: null, masters: { users: [], batches: [], subjects: [], rooms: [], studentAccess: [], parentAccess: [] }, audit: [] };
let financeStudentFilter = "";
let ledgerCurrentStudentId = "";
let ledgerReturnFocus = null;
const STUDENT_BATCH_ORDER = ["Essential", "Tatva"];
const STUDENT_PROGRAM_ORDER = ["JEE", "NEET", "MHT-CET", "Boards"];
const studentHierarchyState = { open: new Set(["batch:Essential", "batch:Tatva"]) };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const esc = (value = "") => String(value ?? "").replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
const initials = name => String(name || "Lakshya").split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join("").toUpperCase();
const normalize = value => String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.info}</svg>`;
const money = value => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value || 0));
const shortMoney = value => Number(value || 0) >= 100000 ? `₹${(Number(value) / 100000).toFixed(2)}L` : money(value);
const formatDate = value => value ? new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(`${value}T00:00:00`)) : "—";
const formatDateTime = value => value ? new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(value)) : "—";
const localInputValue = (date = new Date(Date.now() + 86400000)) => new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
const status = value => `<span class="status status-${normalize(value) || "neutral"}">${esc(String(value || "Unknown").replaceAll("_", " "))}</span>`;

function injectIcons(root = document) {
  $$('[data-icon]', root).forEach(node => { if (icons[node.dataset.icon]) node.innerHTML = icon(node.dataset.icon); });
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

function setAuthMode(setup) {
  state.setupRequired = setup;
  $$(".setup-only").forEach(node => node.classList.toggle("hidden", !setup));
  $("#auth-title").textContent = setup ? "Create owner" : "Sign in";
  $("#auth-submit-label").textContent = setup ? "Create account" : "Sign in";
  $("#password-help").textContent = setup ? "Use at least 10 characters." : "Use at least 8 characters.";
  $("#auth-password").autocomplete = setup ? "new-password" : "current-password";
}

async function initialize() {
  injectIcons();
  initializeTheme();
  bindEvents();
  refreshServiceWorker();
  try {
    if (state.token) {
      try {
        if (!state.user) {
          state.user = await api("/api/auth/me");
          sessionStorage.setItem("lakshya_user", JSON.stringify(state.user));
        }
        await enterWorkspace();
      }
      catch (error) {
        if (error.status !== 401 && state.token) showBootError("Workspace unavailable", error.message);
      }
    } else {
      const setup = await api("/api/auth/bootstrap-status");
      setAuthMode(setup.setupRequired);
      showAuth();
    }
  } catch (error) {
    if (error.status !== 401) showBootError("Service unavailable", "The latest workspace data could not be loaded.");
  }
}

async function refreshServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  try {
    const registration = await navigator.serviceWorker.register("./sw.js");
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
  Object.assign(state, { students: [], agreements: [], payments: [], leads: [], stages: [], sessions: [], timetable: { batches: [], subjects: [], rooms: [], faculty: [] }, assignments: [], attendanceSessions: [], notices: [], report: null, masters: { users: [], batches: [], subjects: [], rooms: [], studentAccess: [], parentAccess: [] }, audit: [] });
  sessionStorage.removeItem("lakshya_token");
  sessionStorage.removeItem("lakshya_user");
}

function resetAuthForm() {
  $("#auth-password").value = "";
  $("#auth-password").type = "password";
  $(".password-toggle").setAttribute("aria-label", "Show password");
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
  const email = String(form.get("email") || "").trim();
  const password = String(form.get("password") || "");
  $$(".field-error").forEach(node => node.textContent = "");
  $("#auth-error").classList.add("hidden");
  let invalid = false;
  if (state.setupRequired && fullName.length < 2) { $('[data-error-for="fullName"]').textContent = "Enter the owner’s full name."; invalid = true; }
  if (!/^\S+@\S+\.\S+$/.test(email)) { $('[data-error-for="email"]').textContent = "Enter a valid email address."; invalid = true; }
  if (password.length < (state.setupRequired ? 10 : 8)) { $('[data-error-for="password"]').textContent = `Use at least ${state.setupRequired ? 10 : 8} characters.`; invalid = true; }
  if (invalid) return;
  const button = $("#auth-submit"); button.disabled = true; $("#auth-submit-label").textContent = state.setupRequired ? "Creating…" : "Signing in…";
  try {
    const payload = state.setupRequired ? { fullName, email, password } : { email, password };
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
  showView("dashboard");
  loadSecondaryWorkspace().catch(error => {
    if (state.token && error.status !== 401) toast("Some secondary modules are still loading.", "error");
  });
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
  const [students, agreements, payments, leads, admissionMeta] = await Promise.all([
    optional(() => fetchAll("/api/students"), []),
    optional(() => fetchAll("/api/finance/agreements"), []),
    optional(() => fetchAll("/api/finance/staged-payments"), []),
    optional(() => fetchAll("/api/admissions/leads"), []),
    optional(() => api("/api/admissions/bootstrap"), { stageOrder: [] }),
  ]);
  Object.assign(state, { students, agreements, payments, leads, stages: admissionMeta.stageOrder || [] });
  renderAll();
}

async function loadSecondaryWorkspace() {
  const [timetable, assignments, attendanceSessions, notices, report, masters, auditRows] = await Promise.all([
    optional(() => api("/api/timetable/bootstrap"), { sessions: [], batches: [], subjects: [], rooms: [], faculty: [] }), optional(() => api("/api/academics/assignments"), []), optional(() => api("/api/attendance/sessions"), []), optional(() => api("/api/communication/notices"), []), optional(() => api("/api/reports/overview"), null), optional(() => api("/api/settings/bootstrap"), { users: [], batches: [], subjects: [], rooms: [], studentAccess: [], parentAccess: [] }), optional(() => api("/api/settings/audit"), [])
  ]);
  Object.assign(state, { sessions: timetable.sessions || [], timetable, assignments, attendanceSessions, notices, report, masters, audit: auditRows });
  renderAll();
}

function renderAll() {
  $("#nav-students-count").textContent = state.students.length;
  $("#nav-leads-count").textContent = state.leads.length;
  const reviewCount = state.payments.filter(item => item.reconciliationStatus !== "ready").length;
  $("#nav-finance-count").textContent = state.payments.length;
  $("#payment-review-count").textContent = reviewCount ? `${reviewCount} review` : "";
  $("#payment-review-count").classList.toggle("hidden", !reviewCount);
  renderDashboard(); renderStudents(); renderFinance(); renderAdmissions(); renderTimetable(); renderAcademics(); renderAttendance(); renderCommunication(); renderReports(); renderSettings(); renderCommandResults(); injectIcons();
}

function metricCard(label, value, iconName, featured = false) {
  return `<article class="metric-card ${featured ? "metric-card-featured" : ""}"><div class="metric-card-head"><span class="metric-label">${esc(label)}</span><span class="metric-icon">${icon(iconName)}</span></div><p class="metric-value">${esc(value)}</p></article>`;
}

function renderDashboard() {
  const activeStudents = state.students.filter(student => student.status === "active");
  const agreed = state.agreements.reduce((sum, item) => sum + Number(item.agreedAmount || 0), 0);
  const registration = state.agreements.reduce((sum, item) => sum + Number(item.legacyRegistrationTotal || 0), 0);
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
  const paymentReview = state.payments.filter(item => item.reconciliationStatus !== "ready").length;
  if (paymentReview) quality.push({ kind: "payment review", count: paymentReview });
  $("#attention-count").textContent = quality.reduce((sum, item) => sum + item.count, 0);
  $("#attention-list").innerHTML = quality.length ? quality.map(item => `<button class="attention-item" type="button" data-view-target="${item.kind === "payment review" ? "finance" : "students"}"><span>${icon("alert")}</span><strong>${esc(item.kind.replace(/\b\w/g, c => c.toUpperCase()))}</strong><em>${item.count}</em></button>`).join("") : `<div class="attention-item"><span>${icon("shield")}</span><strong>No review items</strong></div>`;

  const recent = [...activeStudents].sort((a, b) => String(b.enrollmentDate).localeCompare(String(a.enrollmentDate))).slice(0, 5);
  $("#recent-students").innerHTML = recent.length ? recent.map(student => `<button class="record-item" type="button" data-student-id="${esc(student.id)}"><span class="record-avatar">${initials(student.fullName)}</span><span><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)}</small></span><span class="record-program">${esc(student.program)}</span><span class="record-date">${formatDate(student.enrollmentDate)}</span>${status(student.dataQualityStatus)}</button>`).join("") : emptyState("users", "No admissions");

  const stagedTotal = state.payments.filter(item => item.type === "payment").reduce((sum, item) => sum + Number(item.amount || 0), 0);
  const readyPayments = state.payments.filter(item => item.reconciliationStatus === "ready").length;
  const readyPercent = state.payments.length ? Math.round(readyPayments / state.payments.length * 100) : 0;
  $("#finance-pulse-body").innerHTML = `<div class="finance-pulse-body"><div class="finance-total">${money(stagedTotal)}<small>${state.payments.length} payment entries</small></div><div class="reconcile-bar"><div class="reconcile-track"><span style="width:${readyPercent}%"></span><span style="width:${100 - readyPercent}%"></span></div><div class="reconcile-labels"><span>${readyPayments} ready</span><span>${state.payments.length - readyPayments} review</span></div></div><button class="button button-secondary" type="button" data-view-target="finance">Open receivables ${icon("arrow-right")}</button></div>`;
}

function compactMetrics(items) { return items.map(item => `<div class="compact-metric"><span>${esc(item.label)}</span><strong>${esc(item.value)}</strong></div>`).join(""); }
function studentPrimary(name, detail = "") { return `<div class="table-primary"><span class="record-avatar">${initials(name)}</span><span><strong>${esc(name)}</strong><small>${esc(detail)}</small></span></div>`; }
function emptyState(iconName, title, copy = "") { return `<div class="empty-state"><span class="empty-icon">${icon(iconName)}</span><div><h3>${esc(title)}</h3>${copy ? `<p>${esc(copy)}</p>` : ""}</div></div>`; }
function isOwner() { return state.user?.role === "owner"; }
function ownerEditButton(kind, id, label = "Edit") {
  return isOwner() ? `<button class="button button-secondary button-small owner-edit-button" type="button" data-owner-edit="${esc(kind)}" data-edit-id="${esc(id)}">${icon("edit")}${esc(label)}</button>` : "";
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
  const search = $("#student-search").value.trim().toLowerCase(), program = $("#student-program-filter").value, quality = $("#student-quality-filter").value;
  return state.students.filter(item => (!search || [item.fullName, item.mobile, item.admissionNumber, item.previousSchool, item.batch, item.program].some(value => String(value || "").toLowerCase().includes(search))) && (!program || studentProgramKey(item.program) === program) && (!quality || item.dataQualityStatus === quality));
}

function renderStudents() {
  const programFilter = $("#student-program-filter"); const current = programFilter.value;
  programFilter.innerHTML = `<option value="">All programs</option>${STUDENT_PROGRAM_ORDER.map(program => `<option value="${program}">${program}</option>`).join("")}`; programFilter.value = current;
  const essential = state.students.filter(item => studentBatchKey(item.batch) === "Essential").length;
  const tatva = state.students.filter(item => studentBatchKey(item.batch) === "Tatva").length;
  const review = state.students.length - essential - tatva;
  $("#student-metrics").innerHTML = compactMetrics([
    { label: "Essential", value: String(essential) }, { label: "Tatva", value: String(tatva) },
    { label: "Programs", value: String(STUDENT_PROGRAM_ORDER.length) }, { label: "Records for review", value: String(review) }
  ]);
  renderStudentRows();
}

function studentTreeDomId(value) {
  return `student-tree-${String(value).toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
}

function renderStudentLeaf(student) {
  const contact = student.mobile || "Contact not captured";
  const school = student.previousSchool || "School not captured";
  return `<button class="student-tree-student" type="button" data-student-id="${esc(student.id)}" aria-label="Open ${esc(student.fullName)}">
    <span class="record-avatar">${initials(student.fullName)}</span>
    <span class="student-tree-student-copy"><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)} · ${esc(contact)}</small><small>${esc(school)}</small></span>
    ${status(student.dataQualityStatus)}
    <span class="student-tree-open" aria-hidden="true">${icon("chevron-right")}</span>
  </button>`;
}

function renderStudentProgram(batchName, programName, rows, forceOpen = false) {
  const key = `program:${batchName}:${programName}`, contentId = studentTreeDomId(key);
  const expanded = forceOpen || studentHierarchyState.open.has(key);
  const sorted = [...rows].sort((a, b) => String(a.fullName || "").localeCompare(String(b.fullName || "")));
  return `<section class="student-program-group">
    <button class="student-program-trigger" type="button" data-student-tree-toggle="${esc(key)}" aria-expanded="${expanded}" aria-controls="${contentId}">
      <span class="student-program-marker" aria-hidden="true"></span>
      <span class="student-tree-label"><strong>${esc(programName)}</strong><small>${sorted.length ? `${sorted.length} ${sorted.length === 1 ? "student" : "students"}` : "No students assigned"}</small></span>
      <span class="student-tree-count">${sorted.length}</span>
      <span class="student-tree-chevron" aria-hidden="true">${icon("chevron-down")}</span>
    </button>
    <div class="student-program-content" id="${contentId}" ${expanded ? "" : "hidden"}>
      ${sorted.length ? `<div class="student-leaf-grid">${sorted.map(renderStudentLeaf).join("")}</div>` : `<p class="student-tree-empty">No students in this program.</p>`}
    </div>
  </section>`;
}

function renderStudentBatch(batchName, rows, { review = false, searchActive = false, selectedProgram = "" } = {}) {
  const key = `batch:${batchName}`, contentId = studentTreeDomId(key);
  const expanded = searchActive || studentHierarchyState.open.has(key);
  const availablePrograms = review
    ? [...new Set(rows.map(item => studentProgramKey(item.program)))].sort((a, b) => {
      const aIndex = STUDENT_PROGRAM_ORDER.indexOf(a), bIndex = STUDENT_PROGRAM_ORDER.indexOf(b);
      return (aIndex < 0 ? 99 : aIndex) - (bIndex < 0 ? 99 : bIndex) || a.localeCompare(b);
    })
    : STUDENT_PROGRAM_ORDER;
  const programs = selectedProgram ? availablePrograms.filter(program => program === selectedProgram) : availablePrograms;
  const subtitle = review ? "Batch assignment required" : `${programs.filter(program => rows.some(item => studentProgramKey(item.program) === program)).length} active programs`;
  return `<section class="student-batch-group${review ? " student-batch-review" : ""}">
    <button class="student-batch-trigger" type="button" data-student-tree-toggle="${esc(key)}" aria-expanded="${expanded}" aria-controls="${contentId}">
      <span class="student-batch-icon" aria-hidden="true">${review ? icon("alert") : esc(batchName.charAt(0))}</span>
      <span class="student-tree-label"><strong>${esc(batchName)}</strong><small>${esc(subtitle)}</small></span>
      <span class="student-tree-count">${rows.length}</span>
      <span class="student-tree-chevron" aria-hidden="true">${icon("chevron-down")}</span>
    </button>
    <div class="student-batch-content" id="${contentId}" ${expanded ? "" : "hidden"}>
      ${programs.length ? programs.map(program => renderStudentProgram(batchName, program, rows.filter(item => studentProgramKey(item.program) === program), searchActive)).join("") : `<p class="student-tree-empty">No matching students in this group.</p>`}
    </div>
  </section>`;
}

function renderStudentRows() {
  const rows = filteredStudents(), searchActive = Boolean($("#student-search").value.trim()), selectedProgram = $("#student-program-filter").value;
  const assignedCount = rows.filter(item => STUDENT_BATCH_ORDER.includes(studentBatchKey(item.batch))).length;
  $("#student-result-count").textContent = rows.length === state.students.length
    ? `${rows.length} students · ${assignedCount} assigned to Essential or Tatva`
    : `${rows.length} of ${state.students.length} students`;
  if (!rows.length) {
    $("#student-hierarchy").innerHTML = emptyState("search", "No matching students", "Try clearing one of the directory filters.");
    return;
  }
  const groups = STUDENT_BATCH_ORDER.map(batch => renderStudentBatch(
    batch,
    rows.filter(item => studentBatchKey(item.batch) === batch),
    { searchActive, selectedProgram }
  ));
  const reviewRows = rows.filter(item => studentBatchKey(item.batch) === "Records for review");
  if (reviewRows.length) groups.push(renderStudentBatch("Records for review", reviewRows, { review: true, searchActive, selectedProgram }));
  $("#student-hierarchy").innerHTML = groups.join("");
}

function studentPayments(studentId) {
  return state.payments.filter(item => item.studentId === studentId && item.type === "payment" && item.reconciliationStatus !== "do_not_import");
}

function studentAccount(agreement) {
  const payments = studentPayments(agreement.studentId);
  const paid = payments.reduce((sum, item) => sum + Number(item.amount || 0), 0);
  const agreed = Number(agreement.agreedAmount || 0);
  const workbookControl = Number(agreement.legacyRegistrationTotal || 0);
  const balance = agreed - paid;
  const difference = paid - workbookControl;
  const reviewCount = state.payments.filter(item => item.studentId === agreement.studentId && item.reconciliationStatus !== "ready").length;
  return {
    ...agreement,
    payments,
    paid,
    agreed,
    workbookControl,
    balance,
    difference,
    reviewCount,
    balanceState: balance > 0 ? "due" : balance < 0 ? "credit" : "settled",
    needsReconciliation: difference !== 0 || reviewCount > 0
  };
}

function accountBalance(value) {
  if (value < 0) return `${money(Math.abs(value))} Cr`;
  if (value > 0) return `${money(value)} Dr`;
  return money(0);
}

function reconciliationBadge(account) {
  if (!account.needsReconciliation) return `<span class="status status-ready">Matched</span>`;
  const difference = account.difference
    ? `${money(Math.abs(account.difference))} ${account.difference < 0 ? "below" : "above"}`
    : `${account.reviewCount} review`;
  return `<span class="status status-review">${esc(difference)}</span>`;
}

function renderFinance() {
  const accounts = state.agreements.map(studentAccount);
  const agreed = accounts.reduce((sum, item) => sum + item.agreed, 0);
  const paymentTotal = accounts.reduce((sum, item) => sum + item.paid, 0);
  const outstanding = accounts.reduce((sum, item) => sum + Math.max(item.balance, 0), 0);
  const reconcileCount = accounts.filter(item => item.needsReconciliation).length;
  const review = state.payments.filter(item => item.reconciliationStatus !== "ready").length;
  $("#finance-metrics").innerHTML = compactMetrics([{ label: "Agreed fees", value: shortMoney(agreed) }, { label: "Recorded payments", value: shortMoney(paymentTotal) }, { label: "Outstanding", value: shortMoney(outstanding) }, { label: "Reconcile", value: String(reconcileCount) }]);
  $("#fee-agreement-count").textContent = accounts.length;
  $("#payment-total-count").textContent = state.payments.length;
  $("#payment-review-count").textContent = review ? `${review} review` : "";
  $("#payment-review-count").classList.toggle("hidden", !review);
  $("#finance-agreements-tab").setAttribute("aria-label", `Receivables, ${accounts.length} student accounts`);
  $("#finance-payments-tab").setAttribute("aria-label", `Payment register, ${state.payments.length} entries${review ? `, ${review} need review` : ""}`);
  renderAgreementRows(); renderPaymentRows();
  if (ledgerCurrentStudentId) renderStudentLedger(ledgerCurrentStudentId);
}

function renderAgreementRows() {
  const search = $("#agreement-search").value.trim().toLowerCase();
  const filter = $("#agreement-balance-filter").value;
  const rows = state.agreements.map(studentAccount).filter(item => {
    const matchesSearch = !search || [item.studentName, item.admissionNumber].some(value => String(value || "").toLowerCase().includes(search));
    const matchesFilter = !filter || (filter === "reconcile" ? item.needsReconciliation : item.balanceState === filter);
    return matchesSearch && matchesFilter;
  });
  const visibleOutstanding = rows.reduce((sum, item) => sum + Math.max(item.balance, 0), 0);
  $("#agreement-result-summary").textContent = `${rows.length} ${rows.length === 1 ? "account" : "accounts"} · ${money(visibleOutstanding)} outstanding`;
  const openLedgerButton = (item, compact = false) => `<button class="button button-primary button-small open-ledger-button" type="button" data-open-ledger="${esc(item.studentId)}" aria-label="Open ledger for ${esc(item.studentName)}">${icon("book")}${compact ? "Ledger" : "Open ledger"}</button>`;
  const editAccountButton = item => isOwner() ? `<button class="icon-button receivable-edit-button" type="button" data-owner-edit="agreement" data-edit-id="${esc(item.id)}" aria-label="Edit fee agreement for ${esc(item.studentName)}" title="Edit fee agreement">${icon("edit")}</button>` : "";
  const balanceBadge = item => `<span class="ledger-balance-state ledger-balance-${item.balanceState}">${item.balanceState === "credit" ? "Credit" : item.balanceState === "settled" ? "Settled" : "Due"}</span>`;
  $("#agreements-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td class="receivable-student">${studentPrimary(item.studentName)}</td><td class="receivable-admission">${esc(item.admissionNumber)}</td><td class="currency receivable-number">${money(item.agreed)}</td><td class="currency receivable-number">${money(item.paid)}</td><td class="receivable-outstanding"><strong class="currency">${accountBalance(item.balance)}</strong>${balanceBadge(item)}</td><td class="receivable-reconciliation">${reconciliationBadge(item)}</td><td class="receivable-actions"><div class="cell-actions">${openLedgerButton(item, true)}${editAccountButton(item)}</div></td></tr>`).join("") : `<tr><td colspan="7">${emptyState("search", "No matching accounts", "Clear a filter to see the complete receivables list.")}</td></tr>`;
  $("#agreements-mobile-list").innerHTML = rows.length ? rows.map(item => `<article class="mobile-record-card receivable-mobile-card"><div class="mobile-record-card-head">${studentPrimary(item.studentName, item.admissionNumber)}${balanceBadge(item)}</div><div class="mobile-record-meta"><div><span>Agreed fee</span><strong>${money(item.agreed)}</strong></div><div><span>Paid</span><strong>${money(item.paid)}</strong></div><div><span>Outstanding</span><strong>${accountBalance(item.balance)}</strong></div><div><span>Reconciliation</span><strong>${item.needsReconciliation ? "Review" : "Matched"}</strong></div></div><div class="mobile-card-actions">${openLedgerButton(item)}${ownerEditButton("agreement", item.id)}</div></article>`).join("") : emptyState("search", "No matching accounts", "Clear a filter to see the complete receivables list.");
}

function renderPaymentRows() {
  const filter = $("#payment-status-filter").value;
  const search = $("#payment-search").value.trim().toLowerCase();
  const rows = state.payments.filter(item => {
    const matchesStudent = !financeStudentFilter || item.studentId === financeStudentFilter;
    const matchesStatus = !filter || item.reconciliationStatus === filter;
    const matchesSearch = !search || [item.studentName, item.method, item.sourceNote, item.date, item.amount, item.type].some(value => String(value || "").toLowerCase().includes(search));
    return matchesStudent && matchesStatus && matchesSearch;
  });
  const student = financeStudentFilter
    ? state.payments.find(item => item.studentId === financeStudentFilter) || state.agreements.find(item => item.studentId === financeStudentFilter)
    : null;
  $("#payment-student-filter").classList.toggle("hidden", !student);
  $("#payment-student-filter-name").textContent = student?.studentName || "";
  const paymentRows = rows.filter(item => item.type === "payment");
  const total = paymentRows.reduce((sum, item) => sum + Number(item.amount || 0), 0);
  $("#payment-result-summary").textContent = `${rows.length} ${rows.length === 1 ? "entry" : "entries"} · ${paymentRows.length} ${paymentRows.length === 1 ? "payment" : "payments"} · ${money(total)}`;
  const typeLabel = item => item.type === "payment" ? "Payment" : "Incentive";
  $("#payments-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td>${studentPrimary(item.studentName, `Line ${item.line || "—"}`)}</td><td>${esc(typeLabel(item))}</td><td>${formatDate(item.date)}</td><td class="currency">${item.type === "payment" ? money(item.amount) : "—"}</td><td>${esc(item.method || "Not captured")}</td><td title="${esc(item.sourceNote || "")}">${esc((item.sourceNote || "—").slice(0, 42))}</td><td><div class="cell-actions">${status(item.reconciliationStatus)}${ownerEditButton("payment", item.id, "Review")}</div></td></tr>`).join("") : `<tr><td colspan="7">${emptyState("search", "No matching payment entries", "Clear a filter to see the complete ledger.")}</td></tr>`;
  $("#payments-mobile-list").innerHTML = rows.length ? rows.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div>${studentPrimary(item.studentName, formatDate(item.date))}</div>${status(item.reconciliationStatus)}</div><div class="mobile-record-meta"><div><span>Type</span><strong>${esc(typeLabel(item))}</strong></div><div><span>Amount</span><strong>${item.type === "payment" ? money(item.amount) : "—"}</strong></div><div><span>Mode</span><strong>${esc(item.method || "Not captured")}</strong></div><div><span>Source</span><strong>${esc((item.sourceNote || "—").slice(0, 30))}</strong></div></div>${ownerEditButton("payment", item.id, "Review")}</article>`).join("") : emptyState("search", "No matching payment entries", "Clear a filter to see the complete ledger.");
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
    runningBalance -= Number(item.amount || 0);
    return {
      date: item.date,
      particulars: "Fee received",
      reference: `Import line ${item.line || "—"}`,
      mode: item.method || "Not captured",
      debit: null,
      credit: Number(item.amount || 0),
      balance: runningBalance,
      note: item.sourceNote || "",
      reconciliationStatus: item.reconciliationStatus
    };
  })];
  const knownDates = transactions.map(item => item.date).filter(Boolean).sort();
  const balanceLabel = account.balance < 0 ? "Credit balance" : account.balance === 0 ? "Balance settled" : "Outstanding";
  const accountStatus = account.balance < 0 ? "credit" : account.balance === 0 ? "settled" : "due";
  $("#ledger-student-name").textContent = account.studentName;
  $("#ledger-student-meta").textContent = [account.admissionNumber, student?.program, student?.batch].filter(Boolean).join(" · ");
  $("#ledger-period").textContent = knownDates.length ? `${formatDate(knownDates[0])} – ${formatDate(knownDates[knownDates.length - 1])}` : "Current statement";
  $("#ledger-owner-action").innerHTML = ownerEditButton("agreement", account.id, "Edit account");
  $("#ledger-summary").innerHTML = [
    { label: "Agreed fee", value: money(account.agreed), detail: "Account debit" },
    { label: "Paid", value: money(account.paid), detail: `${account.payments.length} ${account.payments.length === 1 ? "payment" : "payments"}` },
    { label: balanceLabel, value: accountBalance(account.balance), detail: accountStatus === "due" ? "Amount receivable" : accountStatus === "credit" ? "Student credit" : "No amount due", featured: true },
    { label: "Account status", value: accountStatus === "due" ? "Payment due" : accountStatus === "credit" ? "Credit" : "Settled", detail: account.needsReconciliation ? "Control needs review" : "Control matched" }
  ].map(item => `<article class="ledger-summary-card ${item.featured ? "ledger-summary-featured" : ""}"><span>${esc(item.label)}</span><strong>${esc(item.value)}</strong><small>${esc(item.detail)}</small></article>`).join("");
  $("#ledger-table-body").innerHTML = transactions.map(item => `<tr><td>${item.date ? formatDate(item.date) : `<span class="unknown-date">Date unknown</span>`}</td><td><strong>${esc(item.particulars)}</strong>${item.note ? `<small>${esc(item.note)}</small>` : ""}</td><td>${esc(item.reference)}</td><td class="payment-mode">${esc(item.mode)}</td><td class="currency ledger-number">${item.debit == null ? "—" : money(item.debit)}</td><td class="currency ledger-number">${item.credit == null ? "—" : money(item.credit)}</td><td class="currency ledger-number ledger-running-balance">${accountBalance(item.balance)}</td></tr>`).join("");
  $("#ledger-mobile-list").innerHTML = transactions.map(item => `<article class="mobile-record-card ledger-mobile-card"><div class="mobile-record-card-head"><div><h3>${esc(item.particulars)}</h3><p>${item.date ? formatDate(item.date) : "Date unknown"} · ${esc(item.reference)}</p></div><strong class="ledger-mobile-balance">${accountBalance(item.balance)}</strong></div>${item.note ? `<p class="ledger-mobile-note">${esc(item.note)}</p>` : ""}<div class="mobile-record-meta"><div><span>Debit</span><strong>${item.debit == null ? "—" : money(item.debit)}</strong></div><div><span>Credit</span><strong>${item.credit == null ? "—" : money(item.credit)}</strong></div><div><span>Mode</span><strong class="payment-mode">${esc(item.mode)}</strong></div><div><span>Balance</span><strong>${accountBalance(item.balance)}</strong></div></div></article>`).join("");
  const controlDifference = account.difference;
  $("#ledger-control-values").innerHTML = `<div><span>Workbook control</span><strong>${money(account.workbookControl)}</strong></div><div><span>Posted payments</span><strong>${money(account.paid)}</strong></div><div><span>Difference</span><strong class="${controlDifference ? "control-difference" : ""}">${controlDifference ? `${money(Math.abs(controlDifference))} ${controlDifference < 0 ? "below" : "above"}` : money(0)}</strong></div><div><span>Review items</span><strong>${account.reviewCount}</strong></div>`;
  injectIcons($("#student-ledger-view"));
}

function openStudentLedger(studentId, trigger = null) {
  ledgerCurrentStudentId = studentId;
  ledgerReturnFocus = trigger;
  renderStudentLedger(studentId);
  $("#finance-workspace").classList.add("hidden");
  $("#student-ledger-view").classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "auto" });
  setTimeout(() => $("#ledger-back").focus(), 10);
}

function closeStudentLedger(restoreFocus = true) {
  if (!ledgerCurrentStudentId && $("#student-ledger-view").classList.contains("hidden")) return;
  ledgerCurrentStudentId = "";
  $("#student-ledger-view").classList.add("hidden");
  $("#finance-workspace").classList.remove("hidden");
  if (restoreFocus && ledgerReturnFocus?.isConnected) ledgerReturnFocus.focus();
  ledgerReturnFocus = null;
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
  $("#leads-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td>${studentPrimary(item.student, item.mobile)}</td><td>${esc(item.program || "—")}</td><td>${esc(item.counsellor || "Unassigned")}</td><td>${status(item.stage)}</td><td>${esc(item.nextAction || "—")}</td><td>${ownerEditButton("lead", item.id)}</td></tr>`).join("") : `<tr><td colspan="6">${emptyState("spark", state.leads.length ? "No matching enquiries" : "No enquiries", state.leads.length ? "Clear a filter." : "Create an enquiry to begin.")}</td></tr>`;
  $("#leads-mobile-list").innerHTML = rows.map(item => `<article class="mobile-record-card"><div>${studentPrimary(item.student, item.mobile)}${status(item.stage)}</div><div class="mobile-record-meta"><div><span>Program</span><strong>${esc(item.program || "—")}</strong></div><div><span>Next action</span><strong>${esc(item.nextAction || "—")}</strong></div></div>${ownerEditButton("lead", item.id)}</article>`).join("");
}

function renderTimetable() {
  const now = Date.now(), today = new Date().toDateString();
  $("#timetable-metrics").innerHTML = compactMetrics([{ label: "Classes", value: String(state.sessions.length) }, { label: "Today", value: String(state.sessions.filter(item => new Date(item.startsAt).toDateString() === today).length) }, { label: "Upcoming", value: String(state.sessions.filter(item => new Date(item.startsAt).getTime() >= now).length) }, { label: "Faculty", value: String(state.timetable.faculty?.length || 0) }]);
  const rows = [...state.sessions].sort((a, b) => new Date(a.startsAt) - new Date(b.startsAt));
  $("#sessions-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td><strong>${formatDateTime(item.startsAt)}</strong><br><small>${formatDateTime(item.endsAt).split(", ").pop()}</small></td><td>${esc(item.batch)}<br><small>${esc(item.program)}</small></td><td>${esc(item.subject)}</td><td>${esc(item.faculty)}</td><td>${esc(item.room)}</td><td><div class="cell-actions">${status(item.status)}${ownerEditButton("session", item.id)}</div></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("clock", "No classes scheduled")}</td></tr>`;
  $("#sessions-mobile-list").innerHTML = rows.length ? rows.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.subject)}</h3><p>${formatDateTime(item.startsAt)}</p></div>${status(item.status)}</div><div class="mobile-record-meta"><div><span>Batch</span><strong>${esc(item.batch)}</strong></div><div><span>Faculty</span><strong>${esc(item.faculty)}</strong></div><div><span>Room</span><strong>${esc(item.room)}</strong></div><div><span>Ends</span><strong>${formatDateTime(item.endsAt)}</strong></div></div>${ownerEditButton("session", item.id)}</article>`).join("") : emptyState("clock", "No classes scheduled");
}

function renderAcademics() {
  const now = Date.now();
  $("#academics-metrics").innerHTML = compactMetrics([{ label: "Assignments", value: String(state.assignments.length) }, { label: "Published", value: String(state.assignments.filter(item => item.status === "published").length) }, { label: "Due", value: String(state.assignments.filter(item => new Date(item.dueAt).getTime() >= now).length) }, { label: "Recipients", value: String(state.assignments.reduce((sum, item) => sum + Number(item.recipientCount || 0), 0)) }]);
  $("#assignments-table-body").innerHTML = state.assignments.length ? state.assignments.map(item => `<tr><td><strong>${esc(item.title)}</strong><br><small><a href="${esc(item.externalUrl)}" target="_blank" rel="noopener">Open material</a></small></td><td>${esc(item.batch)}</td><td>${esc(item.subject)}</td><td>${formatDateTime(item.dueAt)}</td><td>${item.recipientCount}</td><td><div class="cell-actions">${status(item.status)}${ownerEditButton("assignment", item.id)}</div></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("book", "No assignments")}</td></tr>`;
  $("#assignments-mobile-list").innerHTML = state.assignments.length ? state.assignments.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.title)}</h3><p>${esc(item.subject)} · ${esc(item.batch)}</p></div>${status(item.status)}</div><div class="mobile-record-meta"><div><span>Due</span><strong>${formatDateTime(item.dueAt)}</strong></div><div><span>Students</span><strong>${item.recipientCount}</strong></div></div><div class="mobile-card-actions"><a class="button button-secondary" href="${esc(item.externalUrl)}" target="_blank" rel="noopener">Open material</a>${ownerEditButton("assignment", item.id)}</div></article>`).join("") : emptyState("book", "No assignments");
}

function renderAttendance() {
  const submitted = state.attendanceSessions.filter(item => item.registerStatus === "submitted").length;
  $("#attendance-metrics").innerHTML = compactMetrics([{ label: "Classes", value: String(state.attendanceSessions.length) }, { label: "Submitted", value: String(submitted) }, { label: "Draft", value: String(state.attendanceSessions.filter(item => item.registerStatus === "draft").length) }, { label: "Pending", value: String(state.attendanceSessions.length - submitted) }]);
  $("#attendance-table-body").innerHTML = state.attendanceSessions.length ? state.attendanceSessions.map(item => `<tr><td><strong>${esc(item.subject)}</strong><br><small>${esc(item.batch)} · ${formatDateTime(item.startsAt)}</small></td><td>${esc(item.faculty)}</td><td>${esc(item.room)}</td><td>${item.markedCount}/${item.studentCount}</td><td>${status(item.registerStatus)}</td><td><button class="button button-secondary button-small" type="button" data-attendance-id="${esc(item.id)}">Open</button></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("calendar-check", "No attendance registers")}</td></tr>`;
  $("#attendance-mobile-list").innerHTML = state.attendanceSessions.length ? state.attendanceSessions.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.subject)}</h3><p>${esc(item.batch)} · ${formatDateTime(item.startsAt)}</p></div>${status(item.registerStatus)}</div><div class="mobile-record-meta"><div><span>Faculty</span><strong>${esc(item.faculty)}</strong></div><div><span>Marked</span><strong>${item.markedCount}/${item.studentCount}</strong></div></div><button class="button button-secondary" type="button" data-attendance-id="${esc(item.id)}">Open register</button></article>`).join("") : emptyState("calendar-check", "No attendance registers");
}

function renderCommunication() {
  $("#communication-metrics").innerHTML = compactMetrics([{ label: "Notices", value: String(state.notices.length) }, { label: "Published", value: String(state.notices.filter(item => item.status === "published").length) }, { label: "Batch", value: String(state.notices.filter(item => item.audience === "batch").length) }, { label: "Channels", value: String(new Set(state.notices.map(item => item.channel)).size) }]);
  $("#notice-list").innerHTML = state.notices.length ? state.notices.map(item => `<article class="surface notice-card"><div class="notice-card-head"><span class="icon-tile">${icon("message")}</span><div class="cell-actions">${status(item.status)}${ownerEditButton("notice", item.id)}</div></div><h3>${esc(item.title)}</h3><p>${esc(item.body)}</p><footer><span>${esc(item.batch || item.audience)}</span><span>${esc(item.channel.replaceAll("_", " "))}</span><time>${formatDateTime(item.publishedAt || item.createdAt)}</time></footer></article>`).join("") : emptyState("message", "No notices");
}

function renderReports() {
  const report = state.report;
  if (!report) { $("#report-metrics").innerHTML = metricCard("Access", "Owner only", "shield", true); $("#report-leads").innerHTML = emptyState("shield", "Reports are restricted"); $("#report-attendance").innerHTML = ""; $("#report-audit").innerHTML = ""; return; }
  const metrics = report.metrics || {};
  $("#report-metrics").innerHTML = [metricCard("Students", String(metrics.students || 0), "users", true), metricCard("Attendance", metrics.attendanceRate == null ? "—" : `${metrics.attendanceRate}%`, "calendar-check"), metricCard("Payments", shortMoney(metrics.recordedPayments), "wallet"), metricCard("Upcoming classes", String(metrics.scheduledClasses || 0), "clock")].join("");
  renderBars("#report-leads", report.leadFunnel || [], "stage"); renderBars("#report-attendance", report.attendance || [], "status");
  $("#report-audit").innerHTML = auditRows(report.recentAudit || []);
}

function renderBars(selector, rows, labelKey) {
  const max = Math.max(...rows.map(item => item.count), 1);
  $(selector).innerHTML = rows.length ? rows.map(item => `<div class="program-row"><span>${esc(item[labelKey])}</span><div class="program-track"><div class="program-fill" style="width:${Math.round(item.count / max * 100)}%"></div></div><strong>${item.count}</strong></div>`).join("") : emptyState("chart", "No data");
}

function auditRows(rows) { return rows.length ? rows.map(item => `<div class="audit-row"><span class="icon-tile">${icon("shield")}</span><span><strong>${esc(item.action.replaceAll(".", " "))}</strong><small>${esc(item.actor || "System")} · ${formatDateTime(item.createdAt)}</small></span><em>${esc(item.entityType || "record")}</em></div>`).join("") : emptyState("shield", "No activity"); }

function renderSettings() {
  const masters = state.masters;
  $("#settings-metrics").innerHTML = compactMetrics([{ label: "Users", value: String(masters.users?.length || 0) }, { label: "Batches", value: String(masters.batches?.length || 0) }, { label: "Subjects", value: String(masters.subjects?.length || 0) }, { label: "Rooms", value: String(masters.rooms?.length || 0) }]);
  $("#settings-users").innerHTML = masterRows(masters.users || [], item => [item.fullName, item.role.replaceAll("_", " "), item.isActive ? "active" : "inactive"], "user");
  $("#student-access-count").textContent = `${masters.studentAccess?.length || 0} / 100`;
  $("#settings-student-access").innerHTML = masterRows(masters.studentAccess || [], item => [item.fullName, `${item.admissionNumber} · ${item.email}`, item.isActive ? "active" : "inactive"], "access-user", "userId");
  $("#parent-access-count").textContent = `${masters.parentAccess?.length || 0}`;
  $("#settings-parent-access").innerHTML = masterRows(masters.parentAccess || [], item => [`${item.fullName} → ${item.studentName}`, `${item.admissionNumber} · ${item.email}`, item.contactType === "secondary_contact" ? "secondary" : "primary"], "access-user", "userId");
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

async function openStudent(studentId) {
  const drawer = $("#detail-drawer"), body = $("#detail-drawer-body");
  drawer.classList.add("open"); $("#detail-overlay").classList.add("open"); drawer.setAttribute("aria-hidden", "false");
  syncBodyScrollLock();
  body.innerHTML = '<div class="skeleton-line"></div>';
  try {
    const student = await api(`/api/students/${encodeURIComponent(studentId)}`); $("#drawer-title").textContent = student.fullName;
    const issues = student.migration?.issues || [];
    const academic = student.academicProfile;
    body.innerHTML = `<div class="profile-hero"><span class="record-avatar">${initials(student.fullName)}</span><h3>${esc(student.fullName)}</h3><p>${esc(student.admissionNumber)} · ${esc(student.enrollment?.program || "Program not assigned")}</p></div>
      ${isOwner() ? `<div class="owner-record-actions">${ownerEditButton("student", student.id, "Edit student")}</div>` : ""}
      <section class="detail-section"><h4>Student &amp; enrollment</h4><div class="detail-grid">${detailField("Primary mobile", student.mobile)}${detailField("Secondary mobile", student.secondaryMobile)}${detailField("Previous school", student.previousSchool)}${detailField("Enrollment date", formatDate(student.enrollment?.enrollmentDate))}${detailField("Batch", student.enrollment?.batch)}${detailField("Status", student.status)}</div></section>
      <section class="detail-section"><h4>Academic profile</h4><div class="detail-grid">${detailField("Source student ID", academic?.sourceStudentCode)}${detailField("Mentor", academic?.mentorName)}${detailField("Workbook stream", academic?.sourceStream)}${detailField("Workbook school", academic?.sourceSchoolName)}${detailField("Selected subjects", academic?.subjects?.join(", "))}${detailField("Workbook contact", [academic?.sourcePrimaryMobile, academic?.sourceSecondaryMobile].filter(Boolean).join(", "))}</div></section>
      <section class="detail-section"><h4>Fee agreement</h4><div class="detail-grid">${detailField("Agreed amount", money(student.feeAgreement?.agreedAmount))}${detailField("Registration", money(student.feeAgreement?.legacyRegistrationTotal))}${detailField("Agreement status", student.feeAgreement?.status)}${detailField("Currency", student.feeAgreement?.currency || "INR")}</div></section>
      <section class="detail-section"><h4>Migration trace</h4><div class="detail-grid">${detailField("Source row", student.migration?.sourceRow)}${detailField("Import readiness", student.migration?.readiness)}</div>${issues.length ? `<div class="issue-list">${issues.map(issue => `<div>${icon("alert")}<span>${esc(typeof issue === "string" ? issue : issue.message || JSON.stringify(issue))}</span></div>`).join("")}</div>` : ""}</section>`;
  } catch (error) { body.innerHTML = emptyState("alert", "Could not open this record", error.message); }
}
function detailField(label, value) { return `<div class="detail-field"><span>${esc(label)}</span><strong>${esc(value || "—")}</strong></div>`; }
function closeDetail() { $("#detail-drawer").classList.remove("open"); $("#detail-overlay").classList.remove("open"); $("#detail-drawer").setAttribute("aria-hidden", "true"); syncBodyScrollLock(); }

function openLeadForm() {
  const drawer = $("#detail-drawer"); drawer.classList.add("open"); $("#detail-overlay").classList.add("open"); drawer.setAttribute("aria-hidden", "false"); $("#drawer-title").textContent = "New enquiry";
  syncBodyScrollLock();
  $("#detail-drawer-body").innerHTML = `<form class="auth-form" id="lead-create-form"><label class="field"><span>Student name</span><input name="student" required></label><label class="field"><span>Mobile number</span><input name="mobile" inputmode="numeric" required></label><label class="field"><span>Program</span><input name="program" required></label><label class="field"><span>Parent / guardian</span><input name="parent" required></label><label class="field"><span>Counsellor</span><input name="counsellor" value="${esc(state.user?.fullName || "Admissions desk")}" required></label><label class="field"><span>Source</span><select name="source" required><option value="walk-in">Walk-in</option><option value="phone">Phone</option><option value="whatsapp">WhatsApp</option><option value="website">Website</option><option value="referral">Referral</option><option value="campaign">Campaign</option><option value="seminar">Seminar</option><option value="social media">Social media</option></select></label><label class="field"><span>Next action</span><input name="nextAction" placeholder="Call, campus visit, counselling…" required></label><div class="auth-error hidden" id="lead-form-error" role="alert"></div><button class="button button-primary button-large" type="submit">${icon("plus")}Create enquiry</button></form>`;
  $("#lead-create-form").addEventListener("submit", createLead);
}

async function createLead(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget); const button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = Object.fromEntries([...form.entries()].map(([key, value]) => [key, String(value).trim()]));
  try { const lead = await api("/api/admissions/leads", { method: "POST", body: JSON.stringify(payload) }); state.leads.unshift(lead); closeDetail(); renderAdmissions(); $("#nav-leads-count").textContent = state.leads.length; toast("Enquiry created."); }
  catch (error) { $("#lead-form-error").textContent = error.message; $("#lead-form-error").classList.remove("hidden"); button.disabled = false; }
}

function openDrawer(title, html) {
  const drawer = $("#detail-drawer"); drawer.classList.add("open"); $("#detail-overlay").classList.add("open"); drawer.setAttribute("aria-hidden", "false"); $("#drawer-title").textContent = title; $("#detail-drawer-body").innerHTML = html; syncBodyScrollLock();
}

const options = (rows, label) => rows.map(item => `<option value="${esc(item.id)}">${esc(label(item))}</option>`).join("");
const formError = id => `<div class="auth-error hidden" id="${id}" role="alert"></div>`;
function showFormError(id, error) { const node = $(id); node.textContent = error.message; node.classList.remove("hidden"); }

function openSessionForm() {
  const start = new Date(Date.now() + 86400000), end = new Date(start.getTime() + 5400000);
  openDrawer("Schedule class", `<form class="auth-form" id="session-form"><label class="field"><span>Batch</span><select name="batchId" required><option value="">Select batch</option>${options(state.timetable.batches || [], item => `${item.name} · ${item.program}`)}</select></label><label class="field"><span>Subject</span><select name="subjectId" required><option value="">Select subject</option>${options(state.timetable.subjects || [], item => `${item.name} · ${item.code}`)}</select></label><label class="field"><span>Faculty</span><select name="facultyId" required><option value="">Select faculty</option>${options(state.timetable.faculty || [], item => item.fullName)}</select></label><label class="field"><span>Room</span><select name="roomId" required><option value="">Select room</option>${options(state.timetable.rooms || [], item => `${item.name} · ${item.capacity} seats`)}</select></label><div class="form-pair"><label class="field"><span>Starts</span><input name="startsAt" type="datetime-local" value="${localInputValue(start)}" required></label><label class="field"><span>Ends</span><input name="endsAt" type="datetime-local" value="${localInputValue(end)}" required></label></div><label class="field"><span>Notes</span><textarea name="notes" rows="3"></textarea></label><label class="check-field"><input name="allowOverride" type="checkbox"><span>Authorised conflict override</span></label><label class="field"><span>Override reason</span><textarea name="overrideReason" rows="2"></textarea></label>${formError("session-form-error")}<button class="button button-primary button-large" type="submit">${icon("calendar-check")}Schedule class</button></form>`);
  $("#session-form").addEventListener("submit", submitSession);
}

async function submitSession(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget), button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = { batchId: form.get("batchId"), subjectId: form.get("subjectId"), facultyId: form.get("facultyId"), roomId: form.get("roomId"), startsAt: new Date(form.get("startsAt")).toISOString(), endsAt: new Date(form.get("endsAt")).toISOString(), notes: String(form.get("notes") || "").trim(), allowOverride: form.get("allowOverride") === "on", overrideReason: String(form.get("overrideReason") || "").trim() || null };
  try { await api("/api/timetable/sessions", { method: "POST", body: JSON.stringify(payload) }); state.timetable = await api("/api/timetable/bootstrap"); state.sessions = state.timetable.sessions; state.attendanceSessions = await api("/api/attendance/sessions"); closeDetail(); renderTimetable(); renderAttendance(); toast("Class scheduled."); }
  catch (error) { showFormError("#session-form-error", error); button.disabled = false; }
}

function openAssignmentForm() {
  openDrawer("New assignment", `<form class="auth-form" id="assignment-form"><label class="field"><span>Title</span><input name="title" required></label><label class="field"><span>Batch</span><select name="batchId" required><option value="">Select batch</option>${options(state.timetable.batches || [], item => `${item.name} · ${item.program}`)}</select></label><label class="field"><span>Subject</span><select name="subjectId" required><option value="">Select subject</option>${options(state.timetable.subjects || [], item => `${item.name} · ${item.code}`)}</select></label><label class="field"><span>Due</span><input name="dueAt" type="datetime-local" value="${localInputValue(new Date(Date.now() + 604800000))}" required></label><label class="field"><span>Material link</span><input name="externalUrl" type="url" placeholder="https://" required></label><label class="field"><span>Instructions</span><textarea name="instructions" rows="4"></textarea></label><label class="field"><span>Status</span><select name="status"><option value="published">Published</option><option value="draft">Draft</option></select></label>${formError("assignment-form-error")}<button class="button button-primary button-large" type="submit">${icon("book")}Publish assignment</button></form>`);
  $("#assignment-form").addEventListener("submit", submitAssignment);
}

async function submitAssignment(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget), button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = { title: String(form.get("title")).trim(), batchId: form.get("batchId"), subjectId: form.get("subjectId"), dueAt: new Date(form.get("dueAt")).toISOString(), externalUrl: String(form.get("externalUrl")).trim(), instructions: String(form.get("instructions") || "").trim(), status: form.get("status") };
  try { const row = await api("/api/academics/assignments", { method: "POST", body: JSON.stringify(payload) }); state.assignments.unshift(row); closeDetail(); renderAcademics(); toast(`Assignment published to ${row.recipientCount} students.`); }
  catch (error) { showFormError("#assignment-form-error", error); button.disabled = false; }
}

function openNoticeForm() {
  openDrawer("New notice", `<form class="auth-form" id="notice-form"><label class="field"><span>Title</span><input name="title" required></label><label class="field"><span>Message</span><textarea name="body" rows="5" required></textarea></label><label class="field"><span>Audience</span><select name="audience"><option value="all">Everyone</option><option value="parents">Parents</option><option value="students">Students</option><option value="faculty">Faculty</option><option value="batch">Batch</option></select></label><label class="field"><span>Batch</span><select name="batchId"><option value="">Not selected</option>${options(state.timetable.batches || [], item => item.name)}</select></label><label class="field"><span>Channel</span><select name="channel"><option value="in_app">In app</option><option value="email">Email</option><option value="sms">SMS</option><option value="whatsapp">WhatsApp</option></select></label><label class="field"><span>Status</span><select name="status"><option value="published">Published</option><option value="draft">Draft</option></select></label>${formError("notice-form-error")}<button class="button button-primary button-large" type="submit">${icon("message")}Publish notice</button></form>`);
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
    $("#drawer-title").textContent = `${roster.session.subject} · ${roster.session.batch}`;
    $("#detail-drawer-body").innerHTML = `<form class="attendance-form" id="attendance-form" data-session-id="${esc(sessionId)}" data-locked="${locked}"><div class="attendance-form-head">${status(roster.session.registerStatus)}<span>${roster.entries.length} students</span></div>${roster.entries.map(entry => `<label class="attendance-student"><span><strong>${esc(entry.fullName)}</strong><small>${esc(entry.admissionNumber)}</small></span><select name="${esc(entry.studentId)}" data-original="${esc(entry.status)}"><option value="present" ${entry.status === "present" ? "selected" : ""}>Present</option><option value="late" ${entry.status === "late" ? "selected" : ""}>Late</option><option value="absent" ${entry.status === "absent" ? "selected" : ""}>Absent</option><option value="excused" ${entry.status === "excused" ? "selected" : ""}>Excused</option></select></label>`).join("")}${locked ? `<label class="field"><span>Correction reason</span><textarea name="correctionReason" rows="3" required></textarea></label>` : ""}${formError("attendance-form-error")}<div class="drawer-actions">${locked ? `<button class="button button-primary" type="submit">Apply corrections</button>` : `<button class="button button-secondary" type="button" id="save-attendance">Save draft</button><button class="button button-primary" type="submit">Submit &amp; lock</button>`}</div></form>`;
    $("#attendance-form").addEventListener("submit", submitAttendance); $("#save-attendance")?.addEventListener("click", () => saveAttendance(false));
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

function openUserForm() {
  openDrawer("New user", `<form class="auth-form" id="user-form"><label class="field"><span>Full name</span><input name="fullName" required></label><label class="field"><span>Email</span><input name="email" type="email" required></label><label class="field"><span>Role</span><select name="role"><option value="faculty">Faculty</option><option value="academic_coordinator">Academic coordinator</option><option value="admissions_manager">Admissions manager</option><option value="counsellor">Counsellor</option><option value="front_desk">Front desk</option><option value="accounts">Accounts</option><option value="storekeeper">Storekeeper</option></select></label><label class="field"><span>Temporary password</span><input name="password" type="password" minlength="10" required></label>${formError("user-form-error")}<button class="button button-primary button-large" type="submit">${icon("user")}Create user</button></form>`);
  $("#user-form").addEventListener("submit", async event => { event.preventDefault(); const form = new FormData(event.currentTarget), button = $('button[type="submit"]', event.currentTarget); button.disabled = true; try { await api("/api/settings/users", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) }); state.masters = await api("/api/settings/bootstrap"); closeDetail(); renderSettings(); toast("User created."); } catch (error) { showFormError("#user-form-error", error); button.disabled = false; } });
}

function openStudentAccessForm() {
  const linked = new Set((state.masters.studentAccess || []).map(item => item.studentId));
  const available = state.students.filter(item => !linked.has(item.id));
  openDrawer("Student portal access", `<form class="auth-form" id="student-access-form"><div class="inline-notice">${icon("shield")}<span>${state.masters.studentAccess?.length || 0} of 100 accounts active</span></div><label class="field"><span>Student</span><select name="studentId" required><option value="">Select student</option>${options(available, item => `${item.fullName} · ${item.admissionNumber}`)}</select></label><label class="field"><span>Login email</span><input name="email" type="email" required></label><label class="field"><span>Temporary password</span><input name="password" type="password" minlength="10" required></label>${formError("student-access-error")}<button class="button button-primary button-large" type="submit">${icon("user")}Create student access</button></form>`);
  $("#student-access-form").addEventListener("submit", async event => { event.preventDefault(); const form=new FormData(event.currentTarget),button=$("button[type=submit]",event.currentTarget);button.disabled=true;try{await api("/api/settings/student-access",{method:"POST",body:JSON.stringify(Object.fromEntries(form.entries()))});state.masters=await api("/api/settings/bootstrap");closeDetail();renderSettings();toast("Student portal access created.");}catch(error){showFormError("#student-access-error",error);button.disabled=false;} });
}

function openParentAccessForm() {
  openDrawer("Parent portal access", `<form class="auth-form" id="parent-access-form"><div class="inline-notice">${icon("shield")}<span>Create a separate parent login linked to one student record.</span></div><label class="field"><span>Student</span><select name="studentId" required><option value="">Select student</option>${options(state.students, item => `${item.fullName} · ${item.admissionNumber}`)}</select></label><label class="field"><span>Contact name</span><input name="fullName" autocomplete="name" required></label><label class="field"><span>Contact type</span><select name="contactType"><option value="primary_contact">Primary contact</option><option value="secondary_contact">Secondary contact</option></select></label><label class="field"><span>Login email</span><input name="email" type="email" autocomplete="email" required></label><label class="field"><span>Temporary password</span><input name="password" type="password" minlength="10" autocomplete="new-password" required></label>${formError("parent-access-error")}<button class="button button-primary button-large" type="submit">${icon("user")}Create parent access</button></form>`);
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
  if (!isOwner()) { toast("Owner access is required.", "error"); return; }
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
      <div class="form-pair"><label class="field"><span>Student status</span><select name="status">${ownerStatusOptions(["active","draft","inactive","forfeited"], item.status)}</select></label><label class="field"><span>Data quality</span><select name="dataQualityStatus">${ownerStatusOptions(["ready","review","blocked"], item.dataQualityStatus)}</select></label></div>
      <div class="form-pair"><label class="field"><span>Program</span><input name="program" value="${esc(item.enrollment?.program || "")}"></label><label class="field"><span>Batch</span><input name="batch" value="${esc(item.enrollment?.batch || "")}"></label></div>
      <label class="field"><span>Enrollment date</span><input name="enrollmentDate" type="date" value="${esc(item.enrollment?.enrollmentDate || "")}"></label>`;
  } else if (kind === "lead") {
    title = "Edit enquiry";
    fields = `<div class="form-pair"><label class="field"><span>Student name</span><input name="student" value="${esc(item.student)}" required></label><label class="field"><span>Mobile</span><input name="mobile" value="${esc(item.mobile)}" required></label></div>
      <div class="form-pair"><label class="field"><span>Email</span><input name="email" type="email" value="${esc(item.email || "")}"></label><label class="field"><span>Program</span><input name="program" value="${esc(item.program)}" required></label></div>
      <div class="form-pair"><label class="field"><span>Parent / guardian</span><input name="parent" value="${esc(item.parent)}" required></label><label class="field"><span>Parent mobile</span><input name="parentMobile" value="${esc(item.parentMobile || "")}"></label></div>
      <div class="form-pair"><label class="field"><span>Source</span><select name="source">${ownerStatusOptions(["walk-in","website","phone","whatsapp","referral","campaign","seminar","social media"], item.source)}</select></label><label class="field"><span>Counsellor</span><input name="counsellor" value="${esc(item.counsellor)}" required></label></div>
      <div class="form-pair"><label class="field"><span>Stage</span><select name="stage">${state.stages.map(value => `<option${selected(value,item.stage)}>${esc(value)}</option>`).join("")}</select></label><label class="field"><span>Priority</span><select name="priority">${ownerStatusOptions(["low","medium","high","urgent"], item.priority)}</select></label></div>
      <label class="field"><span>Next action</span><input name="nextAction" value="${esc(item.nextAction)}" required></label>
      <label class="field"><span>Next follow-up</span><input name="nextFollowUpAt" type="datetime-local" value="${item.nextFollowUpAt ? localInputValue(new Date(item.nextFollowUpAt)) : ""}"></label>
      <label class="field"><span>Summary</span><textarea name="summary">${esc(item.summary || "")}</textarea></label>`;
  } else if (kind === "agreement") {
    title = `Edit fee agreement · ${item.studentName}`;
    fields = `<div class="form-pair"><label class="field"><span>Agreed fee</span><input name="agreedAmount" type="number" min="0" value="${item.agreedAmount}" required></label><label class="field"><span>Registration total</span><input name="legacyRegistrationTotal" type="number" min="0" value="${item.legacyRegistrationTotal}" required></label></div><div class="form-pair"><label class="field"><span>Currency</span><input name="currency" value="${esc(item.currency)}" maxlength="3" required></label><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["active","draft","inactive","completed"], item.status)}</select></label></div>`;
  } else if (kind === "payment") {
    title = `Review staged payment · ${item.studentName}`;
    fields = `<div class="immutable-record-note">${icon("shield")}<span>${money(item.amount)} · ${formatDate(item.date)} · ${esc(item.method || "Unknown mode")}<small>Source amounts and dates remain immutable. Only the review classification can change.</small></span></div><label class="field"><span>Review classification</span><select name="reconciliationStatus">${ownerStatusOptions(["ready","review","do_not_import"], item.reconciliationStatus)}</select></label>`;
  } else if (kind === "session") {
    title = "Edit class";
    fields = `<label class="field"><span>Batch</span><select name="batchId">${state.timetable.batches.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.batchId)}>${esc(row.name)} · ${esc(row.program)}</option>`).join("")}</select></label><label class="field"><span>Subject</span><select name="subjectId">${state.timetable.subjects.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.subjectId)}>${esc(row.name)}</option>`).join("")}</select></label><div class="form-pair"><label class="field"><span>Faculty</span><select name="facultyId">${state.timetable.faculty.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.facultyId)}>${esc(row.fullName)}</option>`).join("")}</select></label><label class="field"><span>Room</span><select name="roomId">${state.timetable.rooms.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.roomId)}>${esc(row.name)}</option>`).join("")}</select></label></div><div class="form-pair"><label class="field"><span>Starts</span><input name="startsAt" type="datetime-local" value="${localInputValue(new Date(item.startsAt))}" required></label><label class="field"><span>Ends</span><input name="endsAt" type="datetime-local" value="${localInputValue(new Date(item.endsAt))}" required></label></div><div class="form-pair"><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["scheduled","completed","cancelled"], item.status)}</select></label><label class="check-field"><input name="allowOverride" type="checkbox"><span>Allow schedule override</span></label></div><label class="field"><span>Notes</span><textarea name="notes">${esc(item.notes || "")}</textarea></label><label class="field"><span>Override reason</span><textarea name="overrideReason">${esc(item.overrideReason || "")}</textarea></label>`;
  } else if (kind === "assignment") {
    title = "Edit assignment";
    fields = `<label class="field"><span>Title</span><input name="title" value="${esc(item.title)}" required></label><div class="form-pair"><label class="field"><span>Batch</span><select name="batchId">${state.timetable.batches.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.batchId)}>${esc(row.name)}</option>`).join("")}</select></label><label class="field"><span>Subject</span><select name="subjectId">${state.timetable.subjects.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.subjectId)}>${esc(row.name)}</option>`).join("")}</select></label></div><label class="field"><span>Due</span><input name="dueAt" type="datetime-local" value="${localInputValue(new Date(item.dueAt))}" required></label><label class="field"><span>Material link</span><input name="externalUrl" type="url" value="${esc(item.externalUrl)}" required></label><label class="field"><span>Instructions</span><textarea name="instructions">${esc(item.instructions || "")}</textarea></label><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["draft","published"], item.status)}</select></label>`;
  } else if (kind === "notice") {
    title = "Edit notice";
    fields = `<label class="field"><span>Title</span><input name="title" value="${esc(item.title)}" required></label><label class="field"><span>Message</span><textarea name="body" required>${esc(item.body)}</textarea></label><div class="form-pair"><label class="field"><span>Audience</span><select name="audience">${ownerStatusOptions(["all","parents","students","faculty","batch"], item.audience)}</select></label><label class="field"><span>Channel</span><select name="channel">${ownerStatusOptions(["in_app","email","sms","whatsapp"], item.channel)}</select></label></div><label class="field"><span>Batch</span><select name="batchId"><option value="">Not selected</option>${state.timetable.batches.map(row => `<option value="${esc(row.id)}"${selected(row.id,item.batchId)}>${esc(row.name)}</option>`).join("")}</select></label><label class="field"><span>Status</span><select name="status">${ownerStatusOptions(["draft","published"], item.status)}</select></label>`;
  } else if (kind === "user" || kind === "access-user") {
    title = "Edit user access";
    fields = `<label class="field"><span>Full name</span><input name="fullName" value="${esc(item.fullName)}" required></label><label class="field"><span>Email</span><input name="email" type="email" value="${esc(item.email)}" required></label><div class="form-pair"><label class="field"><span>Role</span><select name="role">${ownerStatusOptions(["owner","admissions_manager","counsellor","front_desk","accounts","academic_coordinator","faculty","storekeeper","student","parent","parent_student"], item.role)}</select></label><label class="check-field"><input name="isActive" type="checkbox"${checked(item.isActive)}><span>Account active</span></label></div><label class="field"><span>New password</span><input name="password" type="password" minlength="10" autocomplete="new-password"><small>Leave blank to keep the existing password.</small></label>`;
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
  if (kind === "student") { endpoint = `/api/students/${id}`; payload.email ||= null; payload.mobile ||= null; payload.secondaryMobile ||= null; payload.previousSchool ||= null; payload.program ||= null; payload.batch ||= null; payload.enrollmentDate ||= null; }
  else if (kind === "lead") { endpoint = `/api/admissions/leads/${id}`; payload.email ||= null; payload.parentMobile ||= null; payload.nextFollowUpAt = payload.nextFollowUpAt ? new Date(payload.nextFollowUpAt).toISOString() : null; }
  else if (kind === "agreement") { endpoint = `/api/finance/agreements/${id}`; payload.agreedAmount = Number(payload.agreedAmount); payload.legacyRegistrationTotal = Number(payload.legacyRegistrationTotal); }
  else if (kind === "payment") endpoint = `/api/finance/staged-payments/${id}/review`;
  else if (kind === "session") { endpoint = `/api/timetable/sessions/${id}`; payload.startsAt = new Date(payload.startsAt).toISOString(); payload.endsAt = new Date(payload.endsAt).toISOString(); payload.allowOverride = form.elements.allowOverride.checked; }
  else if (kind === "assignment") { endpoint = `/api/academics/assignments/${id}`; payload.dueAt = new Date(payload.dueAt).toISOString(); }
  else if (kind === "notice") { endpoint = `/api/communication/notices/${id}`; payload.batchId ||= null; }
  else if (kind === "user" || kind === "access-user") { endpoint = `/api/settings/users/${id}`; payload.isActive = form.elements.isActive.checked; payload.password ||= null; }
  else { endpoint = `/api/settings/${{ batch: "batches", subject: "subjects", room: "rooms" }[kind]}/${id}`; payload.isActive = form.elements.isActive.checked; if (kind === "room") payload.capacity = Number(payload.capacity); }
  try {
    await api(endpoint, { method: "PATCH", body: JSON.stringify(payload) });
    if (kind === "student") state.students = await fetchAll("/api/students");
    else if (kind === "lead") state.leads = await fetchAll("/api/admissions/leads");
    else if (kind === "agreement") state.agreements = await fetchAll("/api/finance/agreements");
    else if (kind === "payment") state.payments = await fetchAll("/api/finance/staged-payments");
    else if (kind === "session") { state.timetable = await api("/api/timetable/bootstrap"); state.sessions = state.timetable.sessions; state.attendanceSessions = await api("/api/attendance/sessions"); }
    else if (kind === "assignment") state.assignments = await api("/api/academics/assignments");
    else if (kind === "notice") state.notices = await api("/api/communication/notices");
    else { state.masters = await api("/api/settings/bootstrap"); state.timetable = await api("/api/timetable/bootstrap"); state.sessions = state.timetable.sessions; }
    closeDetail(); renderAll(); toast("Changes saved.");
  } catch (error) { showFormError("#owner-edit-error", error); button.disabled = false; }
}

const viewTitles = { dashboard: "Overview", admissions: "Enquiries", students: "Students", finance: "Finance", attendance: "Attendance", academics: "Academics", timetable: "Faculty & timetable", communication: "Communication", reports: "Reports", settings: "Settings & audit" };
function showView(view) {
  if (!$("#" + view)) return; state.view = view;
  if (view === "finance") closeStudentLedger(false);
  $$(".app-view").forEach(node => node.classList.toggle("active", node.id === view));
  $$(".nav-item").forEach(node => { const active = node.dataset.view === view; node.classList.toggle("active", active); active ? node.setAttribute("aria-current", "page") : node.removeAttribute("aria-current"); });
  $("#page-title").textContent = viewTitles[view];
  closeSidebar(); closeCommand(); $("#main-content").focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
}

function renderCommandResults(query = "") {
  const needle = query.trim().toLowerCase();
  const views = Object.entries(viewTitles).filter(([, title]) => !needle || title.toLowerCase().includes(needle)).slice(0, 7);
  const students = state.students.filter(item => !needle || [item.fullName, item.admissionNumber, item.mobile].some(value => String(value || "").toLowerCase().includes(needle))).slice(0, needle ? 7 : 3);
  $("#command-results").innerHTML = `<p>${needle ? "Results" : "Navigate"}</p>${views.map(([key, title]) => `<button class="command-item" type="button" data-command-view="${key}"><span>${icon(key === "dashboard" ? "grid" : key === "finance" ? "wallet" : key === "students" ? "users" : "arrow-right")}</span><strong>${esc(title)}</strong><span>${icon("chevron-right")}</span></button>`).join("")}${students.length ? `<p>Students</p>${students.map(student => `<button class="command-item" type="button" data-command-student="${esc(student.id)}"><span>${icon("user")}</span><span><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)} · ${esc(student.program)}</small></span><span>${icon("chevron-right")}</span></button>`).join("")}` : needle ? emptyState("search", "No results") : ""}`;
}
function syncBodyScrollLock() {
  const overlayOpen = $("#detail-drawer").classList.contains("open") || !$("#command-overlay").classList.contains("hidden") || $("#sidebar").classList.contains("open");
  document.body.classList.toggle("no-scroll", overlayOpen);
}
function openCommand() { $("#command-overlay").classList.remove("hidden"); $("#global-search").value = ""; renderCommandResults(); syncBodyScrollLock(); setTimeout(() => $("#global-search").focus(), 10); }
function closeCommand() { $("#command-overlay").classList.add("hidden"); syncBodyScrollLock(); }
function openSidebar() { $("#sidebar").classList.add("open"); $("#drawer-scrim").classList.add("open"); $("#menu-button").setAttribute("aria-expanded", "true"); syncBodyScrollLock(); }
function closeSidebar() { $("#sidebar").classList.remove("open"); $("#drawer-scrim").classList.remove("open"); $("#menu-button").setAttribute("aria-expanded", "false"); syncBodyScrollLock(); }

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
  $(".password-toggle").addEventListener("click", event => { const field = $("#auth-password"), visible = field.type === "text"; field.type = visible ? "password" : "text"; event.currentTarget.setAttribute("aria-label", visible ? "Show password" : "Hide password"); });
  document.addEventListener("click", event => {
    const view = event.target.closest("[data-view], [data-view-target]")?.dataset; if (view) showView(view.view || view.viewTarget);
    const treeButton = event.target.closest("[data-student-tree-toggle]"), treeToggle = treeButton?.dataset.studentTreeToggle;
    if (treeButton && treeToggle) {
      const expanded = treeButton.getAttribute("aria-expanded") !== "true";
      if (expanded) studentHierarchyState.open.add(treeToggle); else studentHierarchyState.open.delete(treeToggle);
      const content = document.getElementById(treeButton.getAttribute("aria-controls"));
      treeButton.setAttribute("aria-expanded", String(expanded));
      if (content) content.hidden = !expanded;
    }
    const ownerEdit = event.target.closest("[data-owner-edit]");
    if (ownerEdit) openOwnerEdit(ownerEdit.dataset.ownerEdit, ownerEdit.dataset.editId);
    const viewPayments = event.target.closest("[data-view-payments]")?.dataset.viewPayments;
    if (viewPayments) showStudentPayments(viewPayments);
    const ledgerButton = event.target.closest("[data-open-ledger]");
    if (ledgerButton) openStudentLedger(ledgerButton.dataset.openLedger, ledgerButton);
    const student = event.target.closest("[data-student-id]")?.dataset.studentId; if (student) openStudent(student);
    const commandView = event.target.closest("[data-command-view]")?.dataset.commandView; if (commandView) showView(commandView);
    const commandStudent = event.target.closest("[data-command-student]")?.dataset.commandStudent; if (commandStudent) { closeCommand(); openStudent(commandStudent); }
    const attendance = event.target.closest("[data-attendance-id]")?.dataset.attendanceId; if (attendance) openAttendance(attendance);
    if (!event.target.closest("#account-menu, #user-menu-button, #topbar-profile-button")) closeAccountMenu();
  });
  $("#menu-button").addEventListener("click", openSidebar); $("#sidebar-close").addEventListener("click", closeSidebar); $("#drawer-scrim").addEventListener("click", closeSidebar);
  $("#detail-close").addEventListener("click", closeDetail); $("#detail-overlay").addEventListener("click", closeDetail);
  $("#search-trigger").addEventListener("click", openCommand); $("#command-overlay").addEventListener("click", event => { if (event.target === event.currentTarget) closeCommand(); });
  $("#global-search").addEventListener("input", event => renderCommandResults(event.target.value));
  $("#theme-toggle").addEventListener("click", toggleTheme);
  [$("#user-menu-button"), $("#topbar-profile-button")].forEach(button => button.addEventListener("click", event => toggleAccountMenu(event.currentTarget)));
  $("#logout-button").addEventListener("click", () => logout());
  $("#student-search").addEventListener("input", renderStudentRows); $("#student-program-filter").addEventListener("change", renderStudentRows); $("#student-quality-filter").addEventListener("change", renderStudentRows);
  $("#agreement-search").addEventListener("input", renderAgreementRows); $("#agreement-balance-filter").addEventListener("change", renderAgreementRows); $("#payment-search").addEventListener("input", renderPaymentRows); $("#payment-status-filter").addEventListener("change", renderPaymentRows);
  $("#clear-payment-student-filter").addEventListener("click", () => { financeStudentFilter = ""; renderPaymentRows(); });
  $("#ledger-back").addEventListener("click", () => closeStudentLedger());
  $("#ledger-payment-register").addEventListener("click", () => { const studentId = ledgerCurrentStudentId; if (studentId) showStudentPayments(studentId); });
  $("#print-student-ledger").addEventListener("click", () => window.print());
  $("#lead-search").addEventListener("input", renderLeadRows); $("#lead-stage-filter").addEventListener("change", renderLeadRows); $("#refresh-leads").addEventListener("click", async () => { try { state.leads = await fetchAll("/api/admissions/leads"); renderAdmissions(); toast("Enquiries refreshed."); } catch (error) { toast(error.message, "error"); } });
  $("#new-lead-button").addEventListener("click", openLeadForm); $("#export-students").addEventListener("click", exportStudents);
  $("#new-session").addEventListener("click", openSessionForm); $("#new-assignment").addEventListener("click", openAssignmentForm); $("#new-notice").addEventListener("click", openNoticeForm); $("#new-user").addEventListener("click", openUserForm); $("#new-student-access").addEventListener("click", openStudentAccessForm); $("#new-parent-access").addEventListener("click", openParentAccessForm); $("#new-master").addEventListener("click", openMasterForm);
  $("#academic-import-file").addEventListener("change", importAcademicData);
  $("#refresh-attendance").addEventListener("click", async () => { try { state.attendanceSessions = await api("/api/attendance/sessions"); renderAttendance(); toast("Attendance refreshed."); } catch (error) { toast(error.message, "error"); } });
  $("#refresh-reports").addEventListener("click", async () => { try { state.report = await api("/api/reports/overview"); renderReports(); toast("Reports refreshed."); } catch (error) { toast(error.message, "error"); } });
  $$("[data-finance-tab]").forEach(button => button.addEventListener("click", () => activateFinanceTab(button.dataset.financeTab)));
  $(".segmented-control[role='tablist']").addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    const buttons = $$("[data-finance-tab]");
    const current = buttons.indexOf(document.activeElement);
    if (current < 0) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
    activateFinanceTab(buttons[next].dataset.financeTab, true);
  });
  document.addEventListener("keydown", event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); openCommand(); } if (event.key === "Escape") { closeStudentLedger(); closeCommand(); closeDetail(); closeSidebar(); closeAccountMenu(true); } });
}

initialize();
