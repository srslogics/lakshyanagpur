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
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>', trend: '<path d="m3 17 6-6 4 4 8-9M15 6h6v6"/>',
  alert: '<path d="M10.3 4.5 2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.5a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  "chevron-right": '<path d="m9 18 6-6-6-6"/>', user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>', logout: '<path d="M10 17l5-5-5-5M15 12H3M15 3h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"/>'
};

const cachedUser = (() => {
  try { return JSON.parse(sessionStorage.getItem("lakshya_user") || "null"); }
  catch { return null; }
})();
const state = { token: sessionStorage.getItem("lakshya_token"), user: cachedUser, setupRequired: false, view: "dashboard", students: [], agreements: [], payments: [], leads: [], stages: [], sessions: [], timetable: { batches: [], subjects: [], rooms: [], faculty: [] }, assignments: [], attendanceSessions: [], notices: [], report: null, masters: { users: [], batches: [], subjects: [], rooms: [], studentAccess: [], parentAccess: [] }, audit: [] };
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
  $("#nav-finance-count").textContent = reviewCount;
  $("#payment-review-count").textContent = reviewCount;
  renderDashboard(); renderStudents(); renderFinance(); renderAdmissions(); renderTimetable(); renderAcademics(); renderAttendance(); renderCommunication(); renderReports(); renderSettings(); renderCommandResults(); injectIcons();
}

function metricCard(label, value, iconName, featured = false) {
  return `<article class="metric-card ${featured ? "metric-card-featured" : ""}"><div class="metric-card-head"><span class="metric-label">${esc(label)}</span><span class="metric-icon">${icon(iconName)}</span></div><p class="metric-value">${esc(value)}</p></article>`;
}

function renderDashboard() {
  const agreed = state.agreements.reduce((sum, item) => sum + Number(item.agreedAmount || 0), 0);
  const registration = state.agreements.reduce((sum, item) => sum + Number(item.legacyRegistrationTotal || 0), 0);
  $("#dashboard-metrics").innerHTML = [
    metricCard("Active students", String(state.students.length), "users", true),
    metricCard("Agreed fees", shortMoney(agreed), "wallet"),
    metricCard("Registration", shortMoney(registration), "receipt"),
    metricCard("Enquiries", String(state.leads.length), "spark")
  ].join("");

  const programs = state.students.reduce((map, item) => map.set(item.program || "Unassigned", (map.get(item.program || "Unassigned") || 0) + 1), new Map());
  const sortedPrograms = [...programs.entries()].sort((a, b) => b[1] - a[1]);
  const max = Math.max(...sortedPrograms.map(([, count]) => count), 1);
  $("#program-chart").innerHTML = sortedPrograms.length ? sortedPrograms.map(([program, count]) => `<div class="program-row"><span title="${esc(program)}">${esc(program)}</span><div class="program-track"><div class="program-fill" style="width:${Math.round(count / max * 100)}%"></div></div><strong>${count}</strong></div>`).join("") : emptyState("users", "No enrollments");

  const quality = ["review", "blocked"].map(kind => ({ kind, count: state.students.filter(item => item.dataQualityStatus === kind).length })).filter(item => item.count);
  const paymentReview = state.payments.filter(item => item.reconciliationStatus !== "ready").length;
  if (paymentReview) quality.push({ kind: "payment review", count: paymentReview });
  $("#attention-count").textContent = quality.reduce((sum, item) => sum + item.count, 0);
  $("#attention-list").innerHTML = quality.length ? quality.map(item => `<button class="attention-item" type="button" data-view-target="${item.kind === "payment review" ? "finance" : "students"}"><span>${icon("alert")}</span><strong>${esc(item.kind.replace(/\b\w/g, c => c.toUpperCase()))}</strong><em>${item.count}</em></button>`).join("") : `<div class="attention-item"><span>${icon("shield")}</span><strong>No review items</strong></div>`;

  const recent = [...state.students].sort((a, b) => String(b.enrollmentDate).localeCompare(String(a.enrollmentDate))).slice(0, 5);
  $("#recent-students").innerHTML = recent.length ? recent.map(student => `<button class="record-item" type="button" data-student-id="${esc(student.id)}"><span class="record-avatar">${initials(student.fullName)}</span><span><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)}</small></span><span class="record-program">${esc(student.program)}</span><span class="record-date">${formatDate(student.enrollmentDate)}</span>${status(student.dataQualityStatus)}</button>`).join("") : emptyState("users", "No admissions");

  const stagedTotal = state.payments.filter(item => item.type === "payment").reduce((sum, item) => sum + Number(item.amount || 0), 0);
  const readyPayments = state.payments.filter(item => item.reconciliationStatus === "ready").length;
  const readyPercent = state.payments.length ? Math.round(readyPayments / state.payments.length * 100) : 0;
  $("#finance-pulse-body").innerHTML = `<div class="finance-pulse-body"><div class="finance-total">${money(stagedTotal)}<small>${state.payments.length} staged entries</small></div><div class="reconcile-bar"><div class="reconcile-track"><span style="width:${readyPercent}%"></span><span style="width:${100 - readyPercent}%"></span></div><div class="reconcile-labels"><span>${readyPayments} ready</span><span>${state.payments.length - readyPayments} review</span></div></div><button class="button button-secondary" type="button" data-view-target="finance">View ledger ${icon("arrow-right")}</button></div>`;
}

function compactMetrics(items) { return items.map(item => `<div class="compact-metric"><span>${esc(item.label)}</span><strong>${esc(item.value)}</strong></div>`).join(""); }
function studentPrimary(name, detail = "") { return `<div class="table-primary"><span class="record-avatar">${initials(name)}</span><span><strong>${esc(name)}</strong><small>${esc(detail)}</small></span></div>`; }
function emptyState(iconName, title, copy = "") { return `<div class="empty-state"><span class="empty-icon">${icon(iconName)}</span><div><h3>${esc(title)}</h3>${copy ? `<p>${esc(copy)}</p>` : ""}</div></div>`; }

function filteredStudents() {
  const search = $("#student-search").value.trim().toLowerCase(), program = $("#student-program-filter").value, quality = $("#student-quality-filter").value;
  return state.students.filter(item => (!search || [item.fullName, item.mobile, item.admissionNumber].some(value => String(value || "").toLowerCase().includes(search))) && (!program || item.program === program) && (!quality || item.dataQualityStatus === quality));
}

function renderStudents() {
  const programs = [...new Set(state.students.map(item => item.program).filter(Boolean))].sort();
  const programFilter = $("#student-program-filter"); const current = programFilter.value;
  programFilter.innerHTML = `<option value="">All programs</option>${programs.map(program => `<option>${esc(program)}</option>`).join("")}`; programFilter.value = current;
  $("#student-metrics").innerHTML = compactMetrics([
    { label: "Active records", value: String(state.students.length) }, { label: "Import ready", value: String(state.students.filter(item => item.dataQualityStatus === "ready").length) },
    { label: "Needs review", value: String(state.students.filter(item => item.dataQualityStatus === "review").length) }, { label: "Programs", value: String(programs.length) }
  ]);
  renderStudentRows();
}

function renderStudentRows() {
  const rows = filteredStudents(); $("#student-result-count").textContent = `${rows.length} of ${state.students.length} students`;
  $("#students-table-body").innerHTML = rows.length ? rows.map(student => `<tr><td>${studentPrimary(student.fullName, student.previousSchool || "School not captured")}</td><td><strong>${esc(student.admissionNumber)}</strong></td><td>${esc(student.program)}<br><small>${esc(student.batch || "—")}</small></td><td>${esc(student.mobile || "—")}</td><td>${formatDate(student.enrollmentDate)}</td><td>${status(student.dataQualityStatus)}</td><td><button class="icon-button table-action" type="button" aria-label="View ${esc(student.fullName)}" data-student-id="${esc(student.id)}">${icon("chevron-right")}</button></td></tr>`).join("") : `<tr><td colspan="7">${emptyState("search", "No matching students", "Try clearing one of the directory filters.")}</td></tr>`;
  $("#students-mobile-list").innerHTML = rows.map(student => `<article class="mobile-record-card"><div>${studentPrimary(student.fullName, student.admissionNumber)}${status(student.dataQualityStatus)}</div><div class="mobile-record-meta"><div><span>Program</span><strong>${esc(student.program)}</strong></div><div><span>Mobile</span><strong>${esc(student.mobile || "—")}</strong></div></div><button class="button button-secondary" type="button" data-student-id="${esc(student.id)}">View record</button></article>`).join("");
}

function renderFinance() {
  const agreed = state.agreements.reduce((sum, item) => sum + Number(item.agreedAmount || 0), 0), registration = state.agreements.reduce((sum, item) => sum + Number(item.legacyRegistrationTotal || 0), 0);
  const paymentTotal = state.payments.filter(item => item.type === "payment").reduce((sum, item) => sum + Number(item.amount || 0), 0), review = state.payments.filter(item => item.reconciliationStatus !== "ready").length;
  $("#finance-metrics").innerHTML = compactMetrics([{ label: "Agreed fees", value: shortMoney(agreed) }, { label: "Registration", value: shortMoney(registration) }, { label: "Staged payments", value: shortMoney(paymentTotal) }, { label: "Review lines", value: String(review) }]);
  renderAgreementRows(); renderPaymentRows();
}

function renderAgreementRows() {
  const search = $("#agreement-search").value.trim().toLowerCase();
  const rows = state.agreements.filter(item => !search || [item.studentName, item.admissionNumber].some(value => String(value || "").toLowerCase().includes(search)));
  $("#agreements-table-body").innerHTML = rows.map(item => `<tr><td>${studentPrimary(item.studentName)}</td><td>${esc(item.admissionNumber)}</td><td class="currency">${money(item.agreedAmount)}</td><td class="currency">${money(item.legacyRegistrationTotal)}</td><td>${status(item.status)}</td></tr>`).join("");
  $("#agreements-mobile-list").innerHTML = rows.map(item => `<article class="mobile-record-card"><div>${studentPrimary(item.studentName, item.admissionNumber)}${status(item.status)}</div><div class="mobile-record-meta"><div><span>Agreed fee</span><strong>${money(item.agreedAmount)}</strong></div><div><span>Registration</span><strong>${money(item.legacyRegistrationTotal)}</strong></div></div></article>`).join("");
}

function renderPaymentRows() {
  const filter = $("#payment-status-filter").value;
  const rows = state.payments.filter(item => !filter || item.reconciliationStatus === filter);
  $("#payments-table-body").innerHTML = rows.map(item => `<tr><td>${studentPrimary(item.studentName, `Line ${item.line || "—"}`)}</td><td>${formatDate(item.date)}</td><td class="currency">${money(item.amount)}</td><td>${esc(item.method || "Not captured")}</td><td title="${esc(item.sourceNote || "")}">${esc((item.sourceNote || "—").slice(0, 42))}</td><td>${status(item.reconciliationStatus)}</td></tr>`).join("");
  $("#payments-mobile-list").innerHTML = rows.map(item => `<article class="mobile-record-card"><div>${studentPrimary(item.studentName, formatDate(item.date))}${status(item.reconciliationStatus)}</div><div class="mobile-record-meta"><div><span>Amount</span><strong>${money(item.amount)}</strong></div><div><span>Mode</span><strong>${esc(item.method || "Not captured")}</strong></div></div></article>`).join("");
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
  $("#leads-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td>${studentPrimary(item.student, item.mobile)}</td><td>${esc(item.program || "—")}</td><td>${esc(item.counsellor || "Unassigned")}</td><td>${status(item.stage)}</td><td>${esc(item.nextAction || "—")}</td><td><span class="icon-button table-action">${icon("chevron-right")}</span></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("spark", state.leads.length ? "No matching enquiries" : "No enquiries", state.leads.length ? "Clear a filter." : "Create an enquiry to begin.")}</td></tr>`;
  $("#leads-mobile-list").innerHTML = rows.map(item => `<article class="mobile-record-card"><div>${studentPrimary(item.student, item.mobile)}${status(item.stage)}</div><div class="mobile-record-meta"><div><span>Program</span><strong>${esc(item.program || "—")}</strong></div><div><span>Next action</span><strong>${esc(item.nextAction || "—")}</strong></div></div></article>`).join("");
}

function renderTimetable() {
  const now = Date.now(), today = new Date().toDateString();
  $("#timetable-metrics").innerHTML = compactMetrics([{ label: "Classes", value: String(state.sessions.length) }, { label: "Today", value: String(state.sessions.filter(item => new Date(item.startsAt).toDateString() === today).length) }, { label: "Upcoming", value: String(state.sessions.filter(item => new Date(item.startsAt).getTime() >= now).length) }, { label: "Faculty", value: String(state.timetable.faculty?.length || 0) }]);
  const rows = [...state.sessions].sort((a, b) => new Date(a.startsAt) - new Date(b.startsAt));
  $("#sessions-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td><strong>${formatDateTime(item.startsAt)}</strong><br><small>${formatDateTime(item.endsAt).split(", ").pop()}</small></td><td>${esc(item.batch)}<br><small>${esc(item.program)}</small></td><td>${esc(item.subject)}</td><td>${esc(item.faculty)}</td><td>${esc(item.room)}</td><td>${status(item.status)}</td></tr>`).join("") : `<tr><td colspan="6">${emptyState("clock", "No classes scheduled")}</td></tr>`;
  $("#sessions-mobile-list").innerHTML = rows.length ? rows.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.subject)}</h3><p>${formatDateTime(item.startsAt)}</p></div>${status(item.status)}</div><div class="mobile-record-meta"><div><span>Batch</span><strong>${esc(item.batch)}</strong></div><div><span>Faculty</span><strong>${esc(item.faculty)}</strong></div><div><span>Room</span><strong>${esc(item.room)}</strong></div><div><span>Ends</span><strong>${formatDateTime(item.endsAt)}</strong></div></div></article>`).join("") : emptyState("clock", "No classes scheduled");
}

function renderAcademics() {
  const now = Date.now();
  $("#academics-metrics").innerHTML = compactMetrics([{ label: "Assignments", value: String(state.assignments.length) }, { label: "Published", value: String(state.assignments.filter(item => item.status === "published").length) }, { label: "Due", value: String(state.assignments.filter(item => new Date(item.dueAt).getTime() >= now).length) }, { label: "Recipients", value: String(state.assignments.reduce((sum, item) => sum + Number(item.recipientCount || 0), 0)) }]);
  $("#assignments-table-body").innerHTML = state.assignments.length ? state.assignments.map(item => `<tr><td><strong>${esc(item.title)}</strong><br><small><a href="${esc(item.externalUrl)}" target="_blank" rel="noopener">Open material</a></small></td><td>${esc(item.batch)}</td><td>${esc(item.subject)}</td><td>${formatDateTime(item.dueAt)}</td><td>${item.recipientCount}</td><td>${status(item.status)}</td></tr>`).join("") : `<tr><td colspan="6">${emptyState("book", "No assignments")}</td></tr>`;
  $("#assignments-mobile-list").innerHTML = state.assignments.length ? state.assignments.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.title)}</h3><p>${esc(item.subject)} · ${esc(item.batch)}</p></div>${status(item.status)}</div><div class="mobile-record-meta"><div><span>Due</span><strong>${formatDateTime(item.dueAt)}</strong></div><div><span>Students</span><strong>${item.recipientCount}</strong></div></div><a class="button button-secondary" href="${esc(item.externalUrl)}" target="_blank" rel="noopener">Open material</a></article>`).join("") : emptyState("book", "No assignments");
}

function renderAttendance() {
  const submitted = state.attendanceSessions.filter(item => item.registerStatus === "submitted").length;
  $("#attendance-metrics").innerHTML = compactMetrics([{ label: "Classes", value: String(state.attendanceSessions.length) }, { label: "Submitted", value: String(submitted) }, { label: "Draft", value: String(state.attendanceSessions.filter(item => item.registerStatus === "draft").length) }, { label: "Pending", value: String(state.attendanceSessions.length - submitted) }]);
  $("#attendance-table-body").innerHTML = state.attendanceSessions.length ? state.attendanceSessions.map(item => `<tr><td><strong>${esc(item.subject)}</strong><br><small>${esc(item.batch)} · ${formatDateTime(item.startsAt)}</small></td><td>${esc(item.faculty)}</td><td>${esc(item.room)}</td><td>${item.markedCount}/${item.studentCount}</td><td>${status(item.registerStatus)}</td><td><button class="button button-secondary button-small" type="button" data-attendance-id="${esc(item.id)}">Open</button></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("calendar-check", "No attendance registers")}</td></tr>`;
  $("#attendance-mobile-list").innerHTML = state.attendanceSessions.length ? state.attendanceSessions.map(item => `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(item.subject)}</h3><p>${esc(item.batch)} · ${formatDateTime(item.startsAt)}</p></div>${status(item.registerStatus)}</div><div class="mobile-record-meta"><div><span>Faculty</span><strong>${esc(item.faculty)}</strong></div><div><span>Marked</span><strong>${item.markedCount}/${item.studentCount}</strong></div></div><button class="button button-secondary" type="button" data-attendance-id="${esc(item.id)}">Open register</button></article>`).join("") : emptyState("calendar-check", "No attendance registers");
}

function renderCommunication() {
  $("#communication-metrics").innerHTML = compactMetrics([{ label: "Notices", value: String(state.notices.length) }, { label: "Published", value: String(state.notices.filter(item => item.status === "published").length) }, { label: "Batch", value: String(state.notices.filter(item => item.audience === "batch").length) }, { label: "Channels", value: String(new Set(state.notices.map(item => item.channel)).size) }]);
  $("#notice-list").innerHTML = state.notices.length ? state.notices.map(item => `<article class="surface notice-card"><div class="notice-card-head"><span class="icon-tile">${icon("message")}</span>${status(item.status)}</div><h3>${esc(item.title)}</h3><p>${esc(item.body)}</p><footer><span>${esc(item.batch || item.audience)}</span><span>${esc(item.channel.replaceAll("_", " "))}</span><time>${formatDateTime(item.publishedAt || item.createdAt)}</time></footer></article>`).join("") : emptyState("message", "No notices");
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
  $("#settings-users").innerHTML = masterRows(masters.users || [], item => [item.fullName, item.role.replaceAll("_", " "), item.isActive ? "active" : "inactive"]);
  $("#student-access-count").textContent = `${masters.studentAccess?.length || 0} / 100`;
  $("#settings-student-access").innerHTML = masterRows(masters.studentAccess || [], item => [item.fullName, `${item.admissionNumber} · ${item.email}`, item.isActive ? "active" : "inactive"]);
  $("#parent-access-count").textContent = `${masters.parentAccess?.length || 0}`;
  $("#settings-parent-access").innerHTML = masterRows(masters.parentAccess || [], item => [`${item.fullName} → ${item.studentName}`, `${item.admissionNumber} · ${item.email}`, item.contactType === "secondary_contact" ? "secondary" : "primary"]);
  $("#settings-batches").innerHTML = masterRows(masters.batches || [], item => [item.name, item.program, item.isActive ? "active" : "inactive"]);
  $("#settings-subjects").innerHTML = masterRows(masters.subjects || [], item => [item.name, `${item.code} · ${item.program}`, item.isActive ? "active" : "inactive"]);
  $("#settings-rooms").innerHTML = masterRows(masters.rooms || [], item => [item.name, `${item.capacity} seats`, item.isActive ? "active" : "inactive"]);
  $("#settings-audit").innerHTML = auditRows(state.audit);
}

function masterRows(rows, map) { return rows.length ? rows.map(item => { const [title, detail, stateValue] = map(item); return `<div class="master-row"><span><strong>${esc(title)}</strong><small>${esc(detail)}</small></span>${status(stateValue)}</div>`; }).join("") : `<div class="master-empty">No records</div>`; }

async function openStudent(studentId) {
  const drawer = $("#detail-drawer"), body = $("#detail-drawer-body");
  drawer.classList.add("open"); $("#detail-overlay").classList.add("open"); drawer.setAttribute("aria-hidden", "false");
  syncBodyScrollLock();
  body.innerHTML = '<div class="skeleton-line"></div>';
  try {
    const student = await api(`/api/students/${encodeURIComponent(studentId)}`); $("#drawer-title").textContent = student.fullName;
    const issues = student.migration?.issues || [];
    body.innerHTML = `<div class="profile-hero"><span class="record-avatar">${initials(student.fullName)}</span><h3>${esc(student.fullName)}</h3><p>${esc(student.admissionNumber)} · ${esc(student.enrollment?.program || "Program not assigned")}</p></div>
      <section class="detail-section"><h4>Student &amp; enrollment</h4><div class="detail-grid">${detailField("Primary mobile", student.mobile)}${detailField("Secondary mobile", student.secondaryMobile)}${detailField("Previous school", student.previousSchool)}${detailField("Enrollment date", formatDate(student.enrollment?.enrollmentDate))}${detailField("Batch", student.enrollment?.batch)}${detailField("Status", student.status)}</div></section>
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

const viewTitles = { dashboard: "Overview", admissions: "Enquiries", students: "Students", finance: "Finance", attendance: "Attendance", academics: "Academics", timetable: "Faculty & timetable", communication: "Communication", reports: "Reports", settings: "Settings & audit" };
function showView(view) {
  if (!$("#" + view)) return; state.view = view;
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
  $("#agreement-search").addEventListener("input", renderAgreementRows); $("#payment-status-filter").addEventListener("change", renderPaymentRows);
  $("#lead-search").addEventListener("input", renderLeadRows); $("#lead-stage-filter").addEventListener("change", renderLeadRows); $("#refresh-leads").addEventListener("click", async () => { try { state.leads = await fetchAll("/api/admissions/leads"); renderAdmissions(); toast("Enquiries refreshed."); } catch (error) { toast(error.message, "error"); } });
  $("#new-lead-button").addEventListener("click", openLeadForm); $("#export-students").addEventListener("click", exportStudents);
  $("#new-session").addEventListener("click", openSessionForm); $("#new-assignment").addEventListener("click", openAssignmentForm); $("#new-notice").addEventListener("click", openNoticeForm); $("#new-user").addEventListener("click", openUserForm); $("#new-student-access").addEventListener("click", openStudentAccessForm); $("#new-parent-access").addEventListener("click", openParentAccessForm); $("#new-master").addEventListener("click", openMasterForm);
  $("#refresh-attendance").addEventListener("click", async () => { try { state.attendanceSessions = await api("/api/attendance/sessions"); renderAttendance(); toast("Attendance refreshed."); } catch (error) { toast(error.message, "error"); } });
  $("#refresh-reports").addEventListener("click", async () => { try { state.report = await api("/api/reports/overview"); renderReports(); toast("Reports refreshed."); } catch (error) { toast(error.message, "error"); } });
  $$("[data-finance-tab]").forEach(button => button.addEventListener("click", () => { $$("[data-finance-tab]").forEach(item => item.classList.toggle("active", item === button)); $$(".finance-tab").forEach(panel => panel.classList.toggle("active", panel.id === `finance-${button.dataset.financeTab}-panel`)); }));
  document.addEventListener("keydown", event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); openCommand(); } if (event.key === "Escape") { closeCommand(); closeDetail(); closeSidebar(); closeAccountMenu(true); } });
}

initialize();
