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

const state = { token: sessionStorage.getItem("lakshya_token"), user: null, setupRequired: false, view: "dashboard", students: [], agreements: [], payments: [], leads: [], stages: [] };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const esc = (value = "") => String(value ?? "").replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
const initials = name => String(name || "Lakshya").split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join("").toUpperCase();
const normalize = value => String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.info}</svg>`;
const money = value => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value || 0));
const shortMoney = value => Number(value || 0) >= 100000 ? `₹${(Number(value) / 100000).toFixed(2)}L` : money(value);
const formatDate = value => value ? new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(`${value}T00:00:00`)) : "—";
const status = value => `<span class="status status-${normalize(value) || "neutral"}">${esc(String(value || "Unknown").replaceAll("_", " "))}</span>`;

function injectIcons(root = document) {
  $$('[data-icon]', root).forEach(node => { if (icons[node.dataset.icon]) node.innerHTML = icon(node.dataset.icon); });
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  let body = null;
  try { body = await response.json(); } catch { body = {}; }
  if (response.status === 401 && state.token) { logout(false); throw new Error("Your session expired. Please sign in again."); }
  if (!response.ok) {
    const detail = body?.detail;
    throw new Error(typeof detail === "string" ? detail : detail?.message || body?.error?.message || "Something went wrong. Please try again.");
  }
  return body;
}

function toast(message, tone = "success") {
  const node = document.createElement("div");
  node.className = "toast";
  node.innerHTML = `<span class="status status-${tone === "error" ? "blocked" : "ready"}">${tone === "error" ? "Issue" : "Done"}</span><span>${esc(message)}</span>`;
  $("#toast-region").append(node);
  setTimeout(() => node.remove(), 3600);
}

function setAuthMode(setup) {
  state.setupRequired = setup;
  $$(".setup-only").forEach(node => node.classList.toggle("hidden", !setup));
  $("#auth-kicker").textContent = setup ? "First-time setup" : "Secure workspace";
  $("#auth-title").textContent = setup ? "Create the owner account" : "Welcome back";
  $("#auth-description").textContent = setup ? "Set up the first accountable administrator for Lakshya ERP." : "Sign in to continue to institution operations.";
  $("#auth-submit-label").textContent = setup ? "Create owner workspace" : "Sign in securely";
  $("#password-help").textContent = setup ? "Use at least 10 characters." : "Use at least 8 characters.";
  $("#auth-password").autocomplete = setup ? "new-password" : "current-password";
}

async function initialize() {
  injectIcons();
  initializeTheme();
  bindEvents();
  renderPlaceholders();
  try {
    const setup = await api("/api/auth/bootstrap-status");
    setAuthMode(setup.setupRequired);
    if (state.token) {
      try { state.user = await api("/api/auth/me"); await enterWorkspace(); }
      catch { showAuth(); }
    } else showAuth();
  } catch (error) {
    showAuth();
    $("#auth-error").textContent = "The ERP service is unavailable. Please start the backend and refresh.";
    $("#auth-error").classList.remove("hidden");
  }
}

function showAuth() { $("#auth-screen").classList.remove("hidden"); $("#app-shell").classList.add("hidden"); }

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
  const button = $("#auth-submit"); button.disabled = true; $("#auth-submit-label").textContent = state.setupRequired ? "Creating workspace…" : "Signing in…";
  try {
    const payload = state.setupRequired ? { fullName, email, password } : { email, password };
    const result = await api(state.setupRequired ? "/api/auth/bootstrap" : "/api/auth/login", { method: "POST", body: JSON.stringify(payload) });
    state.token = result.access_token; sessionStorage.setItem("lakshya_token", state.token);
    state.user = await api("/api/auth/me");
    await enterWorkspace();
  } catch (error) {
    $("#auth-error").textContent = error.message; $("#auth-error").classList.remove("hidden");
  } finally {
    button.disabled = false; $("#auth-submit-label").textContent = state.setupRequired ? "Create owner workspace" : "Sign in securely";
  }
}

async function enterWorkspace() {
  $("#auth-screen").classList.add("hidden"); $("#app-shell").classList.remove("hidden");
  const name = state.user?.fullName || "Lakshya Director";
  const label = state.user?.role?.replaceAll("_", " ") || "Owner";
  $("#sidebar-user-name").textContent = name; $("#sidebar-user-role").textContent = label.replace(/\b\w/g, c => c.toUpperCase());
  $("#greeting-name").textContent = name.split(" ")[0];
  [$("#user-avatar"), $("#topbar-avatar")].forEach(node => node.textContent = initials(name));
  await loadWorkspace();
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

async function loadWorkspace() {
  try {
    const [students, agreements, payments, leads, admissionMeta] = await Promise.all([
      fetchAll("/api/students"), fetchAll("/api/finance/agreements"), fetchAll("/api/finance/staged-payments"), fetchAll("/api/admissions/leads"), api("/api/admissions/bootstrap")
    ]);
    Object.assign(state, { students, agreements, payments, leads, stages: admissionMeta.stageOrder || [] });
    renderAll();
  } catch (error) { toast(error.message, "error"); }
}

function renderAll() {
  $("#nav-students-count").textContent = state.students.length;
  $("#nav-leads-count").textContent = state.leads.length;
  const reviewCount = state.payments.filter(item => item.reconciliationStatus !== "ready").length;
  $("#nav-finance-count").textContent = reviewCount;
  $("#payment-review-count").textContent = reviewCount;
  renderDashboard(); renderStudents(); renderFinance(); renderAdmissions(); renderCommandResults(); injectIcons();
}

function metricCard(label, value, note, iconName, featured = false) {
  return `<article class="metric-card ${featured ? "metric-card-featured" : ""}"><div class="metric-card-head"><span class="metric-label">${esc(label)}</span><span class="metric-icon">${icon(iconName)}</span></div><div><p class="metric-value">${esc(value)}</p><span class="metric-note">${esc(note)}</span></div></article>`;
}

function renderDashboard() {
  const agreed = state.agreements.reduce((sum, item) => sum + Number(item.agreedAmount || 0), 0);
  const registration = state.agreements.reduce((sum, item) => sum + Number(item.legacyRegistrationTotal || 0), 0);
  const review = state.students.filter(item => item.dataQualityStatus !== "ready").length;
  $("#dashboard-metrics").innerHTML = [
    metricCard("Active students", String(state.students.length), "Imported from the 2026–27 admission sheet", "users", true),
    metricCard("Agreed fees", shortMoney(agreed), `${state.agreements.length} verified agreements`, "wallet"),
    metricCard("Registration total", shortMoney(registration), "Legacy registration entries", "receipt"),
    metricCard("Quality review", String(review), review ? "Records need a decision" : "All records are import-ready", "alert")
  ].join("");

  const programs = state.students.reduce((map, item) => map.set(item.program || "Unassigned", (map.get(item.program || "Unassigned") || 0) + 1), new Map());
  const sortedPrograms = [...programs.entries()].sort((a, b) => b[1] - a[1]);
  const max = Math.max(...sortedPrograms.map(([, count]) => count), 1);
  $("#program-chart").innerHTML = sortedPrograms.length ? sortedPrograms.map(([program, count]) => `<div class="program-row"><span title="${esc(program)}">${esc(program)}</span><div class="program-track"><div class="program-fill" style="width:${Math.round(count / max * 100)}%"></div></div><strong>${count}</strong></div>`).join("") : emptyState("users", "No enrollments yet", "Imported enrollments will appear here.");

  const quality = ["review", "blocked"].map(kind => ({ kind, count: state.students.filter(item => item.dataQualityStatus === kind).length })).filter(item => item.count);
  const paymentReview = state.payments.filter(item => item.reconciliationStatus !== "ready").length;
  if (paymentReview) quality.push({ kind: "payment review", count: paymentReview });
  $("#attention-count").textContent = quality.reduce((sum, item) => sum + item.count, 0);
  $("#attention-list").innerHTML = quality.length ? quality.map(item => `<button class="attention-item" type="button" data-view-target="${item.kind === "payment review" ? "finance" : "students"}"><span>${icon("alert")}</span><span><strong>${esc(item.kind.replace(/\b\w/g, c => c.toUpperCase()))}</strong><small>${item.kind === "payment review" ? "Staged ledger lines" : "Student source records"}</small></span><em>${item.count} ${item.count === 1 ? "item" : "items"}</em></button>`).join("") : `<div class="attention-item"><span>${icon("shield")}</span><span><strong>Import checks complete</strong><small>No blocked or review records</small></span>${status("ready")}</div>`;

  const recent = [...state.students].sort((a, b) => String(b.enrollmentDate).localeCompare(String(a.enrollmentDate))).slice(0, 5);
  $("#recent-students").innerHTML = recent.map(student => `<button class="record-item" type="button" data-student-id="${esc(student.id)}"><span class="record-avatar">${initials(student.fullName)}</span><span><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)}</small></span><span class="record-program">${esc(student.program)}</span><span class="record-date">${formatDate(student.enrollmentDate)}</span>${status(student.dataQualityStatus)}</button>`).join("");

  const stagedTotal = state.payments.filter(item => item.type === "payment").reduce((sum, item) => sum + Number(item.amount || 0), 0);
  const readyPayments = state.payments.filter(item => item.reconciliationStatus === "ready").length;
  const readyPercent = state.payments.length ? Math.round(readyPayments / state.payments.length * 100) : 0;
  $("#finance-pulse-body").innerHTML = `<div class="finance-pulse-body"><div class="finance-total">${money(stagedTotal)}<small>${state.payments.length} payment and adjustment lines staged from Excel</small></div><div class="reconcile-bar"><div class="reconcile-track"><span style="width:${readyPercent}%"></span><span style="width:${100 - readyPercent}%"></span></div><div class="reconcile-labels"><span>${readyPayments} ready</span><span>${state.payments.length - readyPayments} need review</span></div></div><button class="button button-secondary" type="button" data-view-target="finance">Open finance control ${icon("arrow-right")}</button></div>`;
}

function compactMetrics(items) { return items.map(item => `<div class="compact-metric"><span>${esc(item.label)}</span><strong>${esc(item.value)}</strong></div>`).join(""); }
function studentPrimary(name, detail = "") { return `<div class="table-primary"><span class="record-avatar">${initials(name)}</span><span><strong>${esc(name)}</strong><small>${esc(detail)}</small></span></div>`; }
function emptyState(iconName, title, copy) { return `<div class="empty-state"><span class="empty-icon">${icon(iconName)}</span><div><h3>${esc(title)}</h3><p>${esc(copy)}</p></div></div>`; }

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
  $("#students-mobile-list").innerHTML = rows.map(student => `<article class="mobile-record-card"><div>${studentPrimary(student.fullName, student.admissionNumber)}${status(student.dataQualityStatus)}</div><div class="mobile-record-meta"><div><span>Program</span><strong>${esc(student.program)}</strong></div><div><span>Mobile</span><strong>${esc(student.mobile || "—")}</strong></div></div><button class="button button-secondary" type="button" data-student-id="${esc(student.id)}">View complete record</button></article>`).join("");
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
  $("#leads-table-body").innerHTML = rows.length ? rows.map(item => `<tr><td>${studentPrimary(item.student, item.mobile)}</td><td>${esc(item.program || "—")}</td><td>${esc(item.counsellor || "Unassigned")}</td><td>${status(item.stage)}</td><td>${esc(item.nextAction || "—")}</td><td><span class="icon-button table-action">${icon("chevron-right")}</span></td></tr>`).join("") : `<tr><td colspan="6">${emptyState("spark", state.leads.length ? "No matching enquiries" : "Your enquiry pipeline is ready", state.leads.length ? "Change the search or stage filter." : "Create the first enquiry here; imported admissions remain in the student directory.")}</td></tr>`;
  $("#leads-mobile-list").innerHTML = rows.map(item => `<article class="mobile-record-card"><div>${studentPrimary(item.student, item.mobile)}${status(item.stage)}</div><div class="mobile-record-meta"><div><span>Program</span><strong>${esc(item.program || "—")}</strong></div><div><span>Next action</span><strong>${esc(item.nextAction || "—")}</strong></div></div></article>`).join("");
}

async function openStudent(studentId) {
  const drawer = $("#detail-drawer"), body = $("#detail-drawer-body");
  drawer.classList.add("open"); $("#detail-overlay").classList.add("open"); drawer.setAttribute("aria-hidden", "false");
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
function closeDetail() { $("#detail-drawer").classList.remove("open"); $("#detail-overlay").classList.remove("open"); $("#detail-drawer").setAttribute("aria-hidden", "true"); }

function openLeadForm() {
  const drawer = $("#detail-drawer"); drawer.classList.add("open"); $("#detail-overlay").classList.add("open"); drawer.setAttribute("aria-hidden", "false"); $("#drawer-title").textContent = "New enquiry";
  $("#detail-drawer-body").innerHTML = `<form class="auth-form" id="lead-create-form"><label class="field"><span>Student name</span><input name="student" required></label><label class="field"><span>Mobile number</span><input name="mobile" inputmode="numeric" required></label><label class="field"><span>Program</span><input name="program" required></label><label class="field"><span>Parent / guardian</span><input name="parent" required></label><label class="field"><span>Counsellor</span><input name="counsellor" value="${esc(state.user?.fullName || "Admissions desk")}" required></label><label class="field"><span>Source</span><select name="source" required><option value="walk-in">Walk-in</option><option value="phone">Phone</option><option value="whatsapp">WhatsApp</option><option value="website">Website</option><option value="referral">Referral</option><option value="campaign">Campaign</option><option value="seminar">Seminar</option><option value="social media">Social media</option></select></label><label class="field"><span>Next action</span><input name="nextAction" placeholder="Call, campus visit, counselling…" required></label><div class="auth-error hidden" id="lead-form-error" role="alert"></div><button class="button button-primary button-large" type="submit">${icon("plus")}Create enquiry</button></form>`;
  $("#lead-create-form").addEventListener("submit", createLead);
}

async function createLead(event) {
  event.preventDefault(); const form = new FormData(event.currentTarget); const button = $("button[type=submit]", event.currentTarget); button.disabled = true;
  const payload = Object.fromEntries([...form.entries()].map(([key, value]) => [key, String(value).trim()]));
  try { const lead = await api("/api/admissions/leads", { method: "POST", body: JSON.stringify(payload) }); state.leads.unshift(lead); closeDetail(); renderAdmissions(); $("#nav-leads-count").textContent = state.leads.length; toast("Enquiry created and added to the pipeline."); }
  catch (error) { $("#lead-form-error").textContent = error.message; $("#lead-form-error").classList.remove("hidden"); button.disabled = false; }
}

const viewTitles = { dashboard: ["Operations / Today", "Command center"], admissions: ["Workspace / Admissions", "Admissions"], students: ["Workspace / Records", "Students"], finance: ["Workspace / Finance", "Fees & finance"], attendance: ["Workspace / Delivery", "Attendance"], academics: ["Workspace / Delivery", "Academics"], timetable: ["Workspace / Resources", "Faculty & timetable"], communication: ["Control / Engagement", "Communication"], reports: ["Control / Intelligence", "Reports"], settings: ["Control / Governance", "Settings & audit"] };
function showView(view) {
  if (!$("#" + view)) return; state.view = view;
  $$(".app-view").forEach(node => node.classList.toggle("active", node.id === view));
  $$(".nav-item").forEach(node => node.classList.toggle("active", node.dataset.view === view));
  $("#page-kicker").textContent = viewTitles[view][0]; $("#page-title").textContent = viewTitles[view][1];
  closeSidebar(); closeCommand(); $("#main-content").focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderPlaceholders() {
  const moduleIcons = { Attendance: "calendar-check", Academics: "book", "Faculty & timetable": "clock", Communication: "message", Reports: "chart", "Settings & audit": "settings" };
  $$(".placeholder-view").forEach(node => { const name = node.dataset.module; node.innerHTML = `<article class="module-ready-card"><span class="module-ready-icon">${icon(moduleIcons[name])}</span><p class="overline">Production roadmap</p><h2>${esc(name)}</h2><p>${esc(node.dataset.description)} The shared navigation, access control and data foundation are already in place.</p><div class="module-readiness"><div><strong>Foundation ready</strong><span>Authenticated workspace</span></div><div><strong>Data model aligned</strong><span>Built for ERP records</span></div><div><strong>Next release</strong><span>Workflow implementation</span></div></div></article>`; });
}

function renderCommandResults(query = "") {
  const needle = query.trim().toLowerCase();
  const views = Object.entries(viewTitles).filter(([, values]) => !needle || values.join(" ").toLowerCase().includes(needle)).slice(0, 7);
  const students = state.students.filter(item => !needle || [item.fullName, item.admissionNumber, item.mobile].some(value => String(value || "").toLowerCase().includes(needle))).slice(0, needle ? 7 : 3);
  $("#command-results").innerHTML = `<p>${needle ? "Matching results" : "Quick navigation"}</p>${views.map(([key, values]) => `<button class="command-item" type="button" data-command-view="${key}"><span>${icon(key === "dashboard" ? "grid" : key === "finance" ? "wallet" : key === "students" ? "users" : "arrow-right")}</span><span><strong>${esc(values[1])}</strong><small>${esc(values[0])}</small></span><span>${icon("chevron-right")}</span></button>`).join("")}${students.length ? `<p>Students</p>${students.map(student => `<button class="command-item" type="button" data-command-student="${esc(student.id)}"><span>${icon("user")}</span><span><strong>${esc(student.fullName)}</strong><small>${esc(student.admissionNumber)} · ${esc(student.program)}</small></span><span>${icon("chevron-right")}</span></button>`).join("")}` : needle ? emptyState("search", "No student records found", "Try a name, mobile number or admission ID.") : ""}`;
}
function openCommand() { $("#command-overlay").classList.remove("hidden"); $("#global-search").value = ""; renderCommandResults(); setTimeout(() => $("#global-search").focus(), 10); }
function closeCommand() { $("#command-overlay").classList.add("hidden"); }
function openSidebar() { $("#sidebar").classList.add("open"); $("#drawer-scrim").classList.add("open"); $("#menu-button").setAttribute("aria-expanded", "true"); }
function closeSidebar() { $("#sidebar").classList.remove("open"); $("#drawer-scrim").classList.remove("open"); $("#menu-button").setAttribute("aria-expanded", "false"); }

function initializeTheme() {
  const saved = localStorage.getItem("lakshya_theme") || "light"; document.documentElement.dataset.theme = saved; updateThemeIcon();
}
function updateThemeIcon() { const dark = document.documentElement.dataset.theme === "dark"; $("#theme-toggle").dataset.icon = dark ? "sun" : "moon"; $("#theme-toggle").setAttribute("aria-label", dark ? "Use light appearance" : "Use dark appearance"); injectIcons($("#theme-toggle")); }
function toggleTheme() { const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = next; localStorage.setItem("lakshya_theme", next); updateThemeIcon(); }
function logout(notify = true) { state.token = null; state.user = null; sessionStorage.removeItem("lakshya_token"); showAuth(); if (notify) toast("You have been signed out."); }

function exportStudents() {
  const rows = filteredStudents(), fields = [["Admission number", "Student", "Mobile", "Previous school", "Program", "Batch", "Enrollment date", "Data quality"], ...rows.map(item => [item.admissionNumber, item.fullName, item.mobile, item.previousSchool, item.program, item.batch, item.enrollmentDate, item.dataQualityStatus])];
  const csv = fields.map(row => row.map(value => `"${String(value || "").replaceAll('"', '""')}"`).join(",")).join("\n");
  const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" })); link.download = `lakshya-students-${new Date().toISOString().slice(0, 10)}.csv`; link.click(); URL.revokeObjectURL(link.href); toast(`${rows.length} student records exported.`);
}

function bindEvents() {
  $("#auth-form").addEventListener("submit", handleAuth);
  $(".password-toggle").addEventListener("click", event => { const field = $("#auth-password"), visible = field.type === "text"; field.type = visible ? "password" : "text"; event.currentTarget.setAttribute("aria-label", visible ? "Show password" : "Hide password"); });
  document.addEventListener("click", event => {
    const view = event.target.closest("[data-view], [data-view-target]")?.dataset; if (view) showView(view.view || view.viewTarget);
    const student = event.target.closest("[data-student-id]")?.dataset.studentId; if (student) openStudent(student);
    const commandView = event.target.closest("[data-command-view]")?.dataset.commandView; if (commandView) showView(commandView);
    const commandStudent = event.target.closest("[data-command-student]")?.dataset.commandStudent; if (commandStudent) { closeCommand(); openStudent(commandStudent); }
  });
  $("#menu-button").addEventListener("click", openSidebar); $("#sidebar-close").addEventListener("click", closeSidebar); $("#drawer-scrim").addEventListener("click", closeSidebar);
  $("#detail-close").addEventListener("click", closeDetail); $("#detail-overlay").addEventListener("click", closeDetail);
  $("#search-trigger").addEventListener("click", openCommand); $("#command-overlay").addEventListener("click", event => { if (event.target === event.currentTarget) closeCommand(); });
  $("#global-search").addEventListener("input", event => renderCommandResults(event.target.value));
  $("#theme-toggle").addEventListener("click", toggleTheme); $("#user-menu-button").addEventListener("click", () => logout());
  $("#student-search").addEventListener("input", renderStudentRows); $("#student-program-filter").addEventListener("change", renderStudentRows); $("#student-quality-filter").addEventListener("change", renderStudentRows);
  $("#agreement-search").addEventListener("input", renderAgreementRows); $("#payment-status-filter").addEventListener("change", renderPaymentRows);
  $("#lead-search").addEventListener("input", renderLeadRows); $("#lead-stage-filter").addEventListener("change", renderLeadRows); $("#refresh-leads").addEventListener("click", async () => { try { state.leads = await fetchAll("/api/admissions/leads"); renderAdmissions(); toast("Admissions pipeline refreshed."); } catch (error) { toast(error.message, "error"); } });
  $("#new-lead-button").addEventListener("click", openLeadForm); $("#export-students").addEventListener("click", exportStudents);
  $$("[data-finance-tab]").forEach(button => button.addEventListener("click", () => { $$("[data-finance-tab]").forEach(item => item.classList.toggle("active", item === button)); $$(".finance-tab").forEach(panel => panel.classList.toggle("active", panel.id === `finance-${button.dataset.financeTab}-panel`)); }));
  document.addEventListener("keydown", event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); openCommand(); } if (event.key === "Escape") { closeCommand(); closeDetail(); closeSidebar(); } });
}

initialize();
