"use strict";

const icons = {
  arrow: '<path d="M5 12h14m-6-6 6 6-6 6"/>',
  "arrow-left": '<path d="m15 18-6-6 6-6M9 12h10"/>',
  home: '<path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1v-9Z"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4m8-4v4M3 10h18"/>',
  book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
  check: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="m8 14 2.5 2.5L16 11"/>',
  more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  spark: '<path d="m12 3 1.4 4.1 4.1 1.4-4.1 1.4L12 14l-1.4-4.1-4.1-1.4 4.1-1.4L12 3Z"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  notice: '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z"/>',
  logout: '<path d="m10 17 5-5-5-5m5 5H3m12-9h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"/>',
  wallet: '<path d="M4 5h15a2 2 0 0 1 2 2v12H4a2 2 0 0 1-2-2V5.5A2.5 2.5 0 0 1 4.5 3H18"/><path d="M16 11h5v4h-5a2 2 0 0 1 0-4Z"/>',
  receipt: '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z"/><path d="M9 8h6m-6 4h6"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  "chevron-right": '<path d="m9 18 6-6-6-6"/>',
  external: '<path d="M14 4h6v6m0-6-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/>',
  eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  "eye-off": '<path d="m3 3 18 18M10.6 5.2A11.4 11.4 0 0 1 12 5c6.5 0 10 7 10 7a16 16 0 0 1-2.1 3.2M6.6 6.6C3.6 8.6 2 12 2 12s3.5 7 10 7a10.7 10.7 0 0 0 4.1-.8M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
};

const views = new Set(["home", "schedule", "assignments", "attendance", "fees", "notices", "profile", "more"]);
const overflowViews = new Set(["fees", "notices", "profile", "more"]);
const titles = {
  home: "Home",
  schedule: "Schedule",
  assignments: "Assignments",
  attendance: "Attendance",
  fees: "Fees",
  notices: "Notices",
  profile: "Profile",
  more: "More",
};

const hashView = () => (views.has(location.hash.slice(1)) ? location.hash.slice(1) : "home");
const state = {
  token: localStorage.getItem("lakshya_student_token"),
  data: null,
  view: hashView(),
  assignmentFilter: "open",
  scheduleDate: "all",
  savingAssignment: null,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
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
const money = (value) => new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
}).format(Number(value || 0));
const validDate = (value) => value && !Number.isNaN(new Date(value).getTime());
const dateKey = (value) => (validDate(value) ? new Date(value).toISOString().slice(0, 10) : "");
const dateText = (value, fallback = "Date pending") => validDate(value)
  ? new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value))
  : fallback;
const dateLong = (value, fallback = "Date pending") => validDate(value)
  ? new Intl.DateTimeFormat("en-IN", { weekday: "short", day: "numeric", month: "short" }).format(new Date(value))
  : fallback;
const timeText = (value) => validDate(value)
  ? new Intl.DateTimeFormat("en-IN", { hour: "2-digit", minute: "2-digit" }).format(new Date(value))
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

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { cache: "no-store", ...options, headers });
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
    throw new Error(typeof detail === "string" ? detail : detail?.message || body?.error?.message || "Unable to complete this request.");
  }
  return body;
}

function clearSession() {
  state.token = null;
  state.data = null;
  localStorage.removeItem("lakshya_student_token");
}

function showLogin(message = "") {
  $("#boot-screen").classList.add("hidden");
  $("#student-shell").classList.add("hidden");
  $("#login-screen").classList.remove("hidden");
  $("#login-password").value = "";
  $("#login-error").textContent = message;
  $("#login-error").classList.toggle("hidden", !message);
  requestAnimationFrame(() => $("#login-email").focus());
}

function toast(message) {
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  $("#toast-region").append(node);
  setTimeout(() => node.remove(), 2800);
}

async function initialize() {
  injectIcons();
  bindEvents();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  if (!state.token) {
    showLogin();
    return;
  }
  try {
    await loadPortal();
  } catch (error) {
    clearSession();
    showLogin(error.message);
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
        email: String(form.get("email")).trim(),
        password: String(form.get("password")),
      }),
    });
    state.token = result.access_token;
    const account = await api("/api/auth/me");
    if (!["student", "parent_student"].includes(account.role)) {
      throw new Error("This login is not assigned to the Student portal.");
    }
    localStorage.setItem("lakshya_student_token", state.token);
    await loadPortal();
  } catch (error) {
    clearSession();
    showLogin(error.message);
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
  $("#student-shell").classList.remove("hidden");
  showView(hashView(), false);
}

async function logout() {
  const token = state.token;
  if (token) {
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
  return validDate(item.dueAt) && new Date(item.dueAt).getTime() < Date.now() ? "overdue" : "open";
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
  renderAttendance();
  renderFees();
  renderNotices();
  renderProfile();
  renderMore();
  injectIcons();
}

function renderHome() {
  const { summary, schedule, assignments, notices } = state.data;
  const openAssignments = assignments.filter((item) => assignmentState(item) !== "completed");
  $("#summary-strip").innerHTML = [
    summaryCard("Upcoming classes", String(summary.upcomingClasses), false, "schedule"),
    summaryCard("Open assignments", String(openAssignments.length), openAssignments.length > 0, "assignments"),
    summaryCard("Attendance", summary.attendanceRate == null ? "Not recorded" : `${summary.attendanceRate}%`, false, "attendance"),
    summaryCard("Outstanding fees", money(summary.outstandingAmount), summary.outstandingAmount > 0, "fees"),
  ].join("");
  const next = schedule.find((item) => validDate(item.startsAt) && new Date(item.startsAt) >= new Date());
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
  const notice = notices[0];
  $("#latest-notice").innerHTML = notice
    ? `<article class="notice-preview"><strong>${esc(notice.title)}</strong><span>${esc(notice.body)}</span><time>${dateLong(notice.publishedAt)}</time></article>`
    : empty("notice", "No institute notices", "Published announcements will appear here.");
}

function renderSchedule() {
  const rows = [...state.data.schedule].sort((a, b) => new Date(a.startsAt) - new Date(b.startsAt));
  const upcoming = rows.filter((item) => validDate(item.startsAt) && new Date(item.startsAt) >= new Date());
  const dateKeys = [...new Set(upcoming.map((item) => dateKey(item.startsAt)).filter(Boolean))];
  const subjects = new Set(upcoming.map((item) => item.subject).filter(Boolean));
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
  const rows = state.assignmentFilter === "all"
    ? all
    : all.filter((item) => assignmentState(item) === state.assignmentFilter);
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
        </div>
        <footer>
          ${resourceUrl ? `<a href="${esc(resourceUrl)}" target="_blank" rel="noopener">Open resource ${icon("external")}</a>` : "<span>No external resource</span>"}
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

function renderAttendance() {
  const rows = state.data.attendance;
  const presentStatuses = new Set(["present", "late", "excused"]);
  const present = rows.filter((item) => presentStatuses.has(item.status)).length;
  const late = rows.filter((item) => item.status === "late").length;
  const absent = rows.filter((item) => item.status === "absent").length;
  const rate = rows.length ? Math.round((present / rows.length) * 1000) / 10 : null;
  $("#attendance-hero").innerHTML = `
    <div class="attendance-ring" style="--attendance:${rate ?? 0}%"><div><strong>${rate == null ? "—" : `${rate}%`}</strong><small>Overall</small></div></div>
    <div class="attendance-copy"><strong>${rows.length ? "Submitted class attendance" : "No attendance submitted"}</strong><p>${rows.length ? `${present} of ${rows.length} recorded classes count as attended.` : "This module will update after faculty submits your first attendance register."}</p></div>`;
  $("#attendance-metrics").innerHTML = [
    moduleMetric("Attended", String(present)),
    moduleMetric("Late", String(late)),
    moduleMetric("Absent", String(absent), absent > 0),
  ].join("");
  const grouped = rows.reduce((groups, item) => {
    const subject = item.subject || "Other";
    groups[subject] ||= [];
    groups[subject].push(item);
    return groups;
  }, {});
  $("#attendance-breakdown").innerHTML = Object.entries(grouped).length
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
  $("#attendance-list").innerHTML = rows.length
    ? rows.map((item) => `<article class="attendance-row">
      <time>${dateText(item.startsAt)}</time>
      <span><strong>${esc(item.subject)}</strong><small>${timeText(item.startsAt)}${item.reason ? ` · ${esc(item.reason)}` : ""}</small></span>
      <em class="status status-${esc(item.status)}">${esc(titleCase(item.status))}</em>
    </article>`).join("")
    : empty("check", "Attendance not recorded yet", "Records will appear after faculty submits attendance.");
}

function renderFees() {
  const { fees } = state.data;
  const hasAgreement = Number(fees.agreedAmount) > 0;
  const percent = hasAgreement ? Math.min(100, Math.round((Number(fees.paidAmount) / Number(fees.agreedAmount)) * 100)) : 0;
  const stateLabel = !hasAgreement ? "Not configured" : Number(fees.outstandingAmount) <= 0 ? "Paid" : `${percent}% paid`;
  $("#student-fee-hero").innerHTML = `<div class="fee-top">
    <span><span>Outstanding</span><strong>${money(fees.outstandingAmount)}</strong></span>
    <span class="fee-state">${esc(stateLabel)}</span>
  </div>
  <div class="fee-progress" aria-label="${percent}% of agreed fee paid"><span style="width:${percent}%"></span></div>
  <div class="fee-total">
    <span><span>Agreed fee</span><strong>${money(fees.agreedAmount)}</strong></span>
    <span><span>Amount paid</span><strong>${money(fees.paidAmount)}</strong></span>
  </div>
  ${!hasAgreement ? '<p class="fee-note">A fee agreement has not been recorded for this student.</p>' : ""}`;
  $("#student-payment-list").innerHTML = fees.payments.length
    ? fees.payments.map((payment) => `<article class="payment-row">
      <span class="payment-icon">${icon("receipt")}</span>
      <span><strong>${money(payment.amount)}</strong><small>${esc(titleCase(payment.method))} · ${esc(titleCase(payment.status))}</small></span>
      <time>${dateText(payment.date)}</time>
    </article>`).join("")
    : empty("receipt", "No payments recorded", hasAgreement ? "Payments will appear here after they are entered by the accounts team." : "A payment history will appear once the fee agreement is configured.");
}

function renderNotices() {
  const notices = state.data.notices;
  const batchNotices = notices.filter((item) => item.batch).length;
  $("#notice-metrics").innerHTML = [
    moduleMetric("Published", String(notices.length)),
    moduleMetric("For your batch", String(batchNotices)),
    moduleMetric("Latest", notices[0] ? dateText(notices[0].publishedAt) : "None"),
  ].join("");
  $("#notice-list").innerHTML = notices.length
    ? notices.map((item) => `<article class="notice-card">
      <div class="notice-card-top"><span>${esc(item.batch || "All students")}</span><time>${dateLong(item.publishedAt)}</time></div>
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
    ["Primary contact", profile.mobile],
    ["Secondary contact", profile.secondaryMobile],
    ["Student email", profile.email],
    ["Portal login", account?.email],
  ];
  $("#profile-details").innerHTML = details.map(([label, value]) => `<div><dt>${esc(label)}</dt><dd>${esc(displayValue(value))}</dd></div>`).join("");
}

function renderMore() {
  const { profile, fees, notices } = state.data;
  $("#more-fee-copy").textContent = Number(fees.agreedAmount) > 0 ? `${money(fees.outstandingAmount)} outstanding` : "Fee agreement not configured";
  $("#more-notice-copy").textContent = notices.length ? `${notices.length} published notice${notices.length === 1 ? "" : "s"}` : "No published notices";
  $("#more-profile-copy").textContent = [profile.admissionNumber, profile.batch].filter(Boolean).join(" · ") || "Student and login details";
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
  $("#password-toggle").addEventListener("click", togglePassword);
  $("#signout-button").addEventListener("click", logout);
  $("#sidebar-signout").addEventListener("click", logout);
  $("#profile-button").addEventListener("click", () => showView("profile"));
  window.addEventListener("popstate", () => state.data && showView(hashView(), false));
  document.addEventListener("keydown", (event) => {
    if ((event.key === "Enter" || event.key === " ") && event.target.matches("[role='button'][data-go]")) {
      event.preventDefault();
      showView(event.target.dataset.go);
    }
  });
  document.addEventListener("click", (event) => {
    const navigation = event.target.closest("[data-view],[data-go]");
    const view = navigation?.dataset.view || navigation?.dataset.go;
    if (view) {
      event.preventDefault();
      showView(view);
    }
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
    const assignmentButton = event.target.closest("[data-assignment-id][data-assignment-status]");
    if (assignmentButton) {
      updateAssignmentStatus(assignmentButton.dataset.assignmentId, assignmentButton.dataset.assignmentStatus);
    }
  });
}

initialize();
