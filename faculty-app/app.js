"use strict";

const icons = {
  arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',
  home:'<path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1v-9Z"/>',
  calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4m8-4v4M3 10h18"/>',
  book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
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
  data: null,
  view: "dashboard",
  attendanceFilter: "action",
  assignmentFilter: "active",
  scheduleDate: "all",
  activeSession: null,
  roster: [],
  rosterLocked: false,
  rosterUpcoming: false,
  publishingAssignment: null,
  lastFocus: null
};
const PORTAL_VIEWS = new Set(["dashboard", "attendance", "assignments", "schedule", "batches", "notices", "profile", "more"]);
const OVERFLOW_VIEWS = new Set(["batches", "notices", "profile", "more"]);

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.spark}</svg>`;
const esc = (value = "") => String(value ?? "").replace(/[&<>'"]/g, character => ({
  "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;"
}[character]));
const initials = name => String(name || "LF").split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join("").toUpperCase();
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const asDate = value => new Date(value);
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
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
};
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

async function api(path, options = {}) {
  const headers = {"Content-Type":"application/json", ...(options.headers || {})};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, {...options, headers});
  let body = {};
  try { body = await response.json(); } catch {}
  if (response.status === 401) {
    clearSession();
    showLogin("Your session expired. Sign in again.");
  }
  if (!response.ok) {
    const detail = body?.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : detail?.message || body?.error?.message || "Unable to complete this request."
    );
  }
  return body;
}

function clearSession() {
  state.token = null;
  state.data = null;
  localStorage.removeItem("lakshya_faculty_token");
}

function showLogin(message = "") {
  $("#startup-screen").classList.add("hidden");
  $("#faculty-shell").classList.add("hidden");
  $("#login-screen").classList.remove("hidden");
  $("#login-password").value = "";
  if (message) {
    $("#login-error").textContent = message;
    $("#login-error").classList.remove("hidden");
  } else {
    $("#login-error").classList.add("hidden");
  }
  requestAnimationFrame(() => $("#login-email").focus());
}

function toast(message) {
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  $("#toast-region").append(node);
  setTimeout(() => node.remove(), 3200);
}

function empty(name, title, copy = "") {
  return `<div class="empty"><div><span>${icon(name)}</span><strong>${esc(title)}</strong>${copy ? `<p>${esc(copy)}</p>` : ""}</div></div>`;
}

async function initialize() {
  injectIcons();
  bindEvents();
  $("#assignment-due").value = localInputValue();
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
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const button = $("#login-button");
  const label = $("#login-button-label");
  button.disabled = true;
  label.textContent = "Signing in…";
  $("#login-error").classList.add("hidden");
  try {
    const data = new FormData(form);
    const result = await api("/api/auth/login", {
      method:"POST",
      body:JSON.stringify({
        email:String(data.get("email")).trim(),
        password:String(data.get("password"))
      })
    });
    state.token = result.access_token;
    localStorage.setItem("lakshya_faculty_token", state.token);
    await loadPortal();
  } catch (error) {
    clearSession();
    showLogin(error.message.includes("permission") ? "This account does not have Faculty access." : error.message);
  } finally {
    button.disabled = false;
    label.textContent = "Sign in";
  }
}

async function loadPortal() {
  state.data = await api("/api/faculty/bootstrap");
  $("#startup-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#faculty-shell").classList.remove("hidden");
  renderAll();
  const hashView = location.hash.slice(1);
  showView(PORTAL_VIEWS.has(hashView) ? hashView : "dashboard", false);
}

async function refreshPortal(message = "") {
  state.data = await api("/api/faculty/bootstrap");
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
  const titles = {dashboard:"Today", attendance:"Attendance", assignments:"Assignments", schedule:"Schedule", batches:"Batches", notices:"Notices", profile:"Profile", more:"More"};
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
    : "Your timetable assignments will appear here.";
  $("#header-avatar").textContent = initials(profile.fullName);
  $("#sidebar-avatar").textContent = initials(profile.fullName);
  $("#sidebar-name").textContent = profile.fullName;
  $("#hero-attendance-count").textContent = `${summary.attendanceActions} pending`;
  $("#attendance-view-count").textContent = `${summary.attendanceActions} pending`;
  for (const badge of [$("#attendance-badge"), $("#sidebar-attendance-badge")]) {
    badge.textContent = summary.attendanceActions;
    badge.classList.toggle("hidden", !summary.attendanceActions);
  }
  renderDashboard();
  renderAttendance();
  renderAssignments();
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

function pendingAttendanceSessions() {
  const now = Date.now();
  return state.data.sessions.filter(item => item.status === "scheduled" && new Date(item.startsAt).getTime() <= now && item.registerStatus !== "submitted");
}

function renderDashboard() {
  const {summary, sessions, assignments, notices} = state.data;
  $("#dashboard-metrics").innerHTML = [
    metric("Classes today", String(summary.todayClasses)),
    metric("Attendance due", String(summary.attendanceActions), summary.attendanceActions > 0),
    metric("Open assignments", String(summary.openAssignments)),
    metric("Active batches", String(summary.activeBatches))
  ].join("");

  const next = sessions.find(item => item.status === "scheduled" && new Date(item.endsAt).getTime() >= Date.now());
  $("#next-class").innerHTML = next ? classCard(next) : empty("calendar", "No upcoming class", "Your next scheduled class will appear here.");
  $("#dashboard-attendance").innerHTML = pendingAttendanceSessions().slice(0, 3).map(item => compactSession(item)).join("")
    || empty("check", "Attendance is up to date");
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
  const canMark = item.registerStatus !== "submitted" && item.studentCount > 0 && new Date(item.startsAt).getTime() <= Date.now();
  return `
    <article class="class-card">
      <div class="class-time"><strong>${timeText(item.startsAt)}</strong><span>${dateLong(item.startsAt)}</span></div>
      <div>
        <h3>${esc(item.subject)}</h3>
        <p>${esc(item.batch)} · ${esc(item.room)}</p>
        <footer>
          <span class="tag">${esc(item.subjectCode)}</span>
          <span class="tag">${item.studentCount} students</span>
          ${canMark ? `<button class="tag attendance-launch" type="button" data-open-attendance="${esc(item.id)}">Mark attendance</button>` : ""}
        </footer>
      </div>
    </article>
  `;
}

function compactSession(item) {
  return `
    <button class="compact-row" type="button" data-open-attendance="${esc(item.id)}">
      <span class="row-icon">${icon("check")}</span>
      <span><strong>${esc(item.subject)} · ${esc(item.batch)}</strong><small>${dateLong(item.startsAt)} · ${timeText(item.startsAt)}</small></span>
      <time>${item.markedCount}/${item.studentCount}</time>
    </button>
  `;
}

function sessionCard(item) {
  const submitted = item.registerStatus === "submitted";
  const upcoming = new Date(item.startsAt).getTime() > Date.now();
  const actionText = submitted ? "View register" : upcoming ? "Open roster" : item.registerStatus === "draft" ? "Continue" : "Mark attendance";
  const actionClass = submitted || upcoming ? "secondary" : "";
  return `
    <article class="session-card">
      <div class="session-date"><strong>${dateText(item.startsAt).split(" ")[0]}</strong><small>${dateText(item.startsAt).split(" ")[1]}</small></div>
      <div>
        <h3>${esc(item.subject)} · ${esc(item.batch)}</h3>
        <p>${timeText(item.startsAt)}–${timeText(item.endsAt)} · ${esc(item.room)}</p>
        <div class="session-meta">
          <span class="tag">${item.studentCount} students</span>
          <span class="tag">${submitted ? "Submitted" : item.registerStatus === "draft" ? `${item.markedCount} marked` : "Not started"}</span>
        </div>
      </div>
      <button class="session-action ${actionClass}" type="button" data-open-attendance="${esc(item.id)}" ${item.studentCount ? "" : "disabled"}>${actionText}</button>
    </article>
  `;
}

function renderAttendance() {
  const now = Date.now();
  const filter = state.attendanceFilter;
  const sessions = state.data.sessions.filter(item => item.status === "scheduled");
  const actionCount = sessions.filter(item => new Date(item.startsAt).getTime() <= now && item.registerStatus !== "submitted").length;
  const upcomingCount = sessions.filter(item => new Date(item.startsAt).getTime() > now).length;
  const submittedCount = sessions.filter(item => item.registerStatus === "submitted").length;
  $("#attendance-metrics").innerHTML = [
    metric("Needs action", String(actionCount), actionCount > 0),
    metric("Upcoming", String(upcomingCount)),
    metric("Submitted", String(submittedCount))
  ].join("");
  const rows = sessions.filter(item => {
    if (filter === "action") return new Date(item.startsAt).getTime() <= now && item.registerStatus !== "submitted";
    if (filter === "upcoming") return new Date(item.startsAt).getTime() > now;
    if (filter === "submitted") return item.registerStatus === "submitted";
    return true;
  }).sort((a, b) => {
    if (filter === "action") return new Date(b.startsAt) - new Date(a.startsAt);
    return new Date(a.startsAt) - new Date(b.startsAt);
  });
  $("#attendance-session-list").innerHTML = rows.length
    ? rows.map(sessionCard).join("")
    : empty("check", filter === "action" ? "Nothing needs attention" : "No classes in this view");
}

function assignmentState(item) {
  if (item.status === "draft") return "draft";
  return new Date(item.dueAt).getTime() < Date.now() ? "overdue" : "active";
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
      <footer>
        <span><strong>${esc(item.batch)} · ${esc(item.subject)}</strong>Due ${dateLong(item.dueAt)} · ${item.recipientCount} students</span>
        <div class="assignment-actions">
          ${resourceUrl ? `<a href="${esc(resourceUrl)}" target="_blank" rel="noopener">Material ${icon("external")}</a>` : ""}
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

function renderSchedule() {
  const rows = state.data.sessions.filter(item => item.status === "scheduled");
  const dates = [...new Set(rows.map(item => dateKey(item.startsAt)))];
  const upcoming = rows.filter(item => new Date(item.startsAt).getTime() >= Date.now());
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
      <span class="timeline-state state-${esc(item.registerStatus)}">${esc(titleCase(item.registerStatus))}</span>
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
    const next = matchingSessions.find(session => new Date(session.startsAt).getTime() >= Date.now());
    return `
      <article class="faculty-batch-card">
        <header><span class="subject-mark">${esc(item.subjectCode)}</span><span>${item.studentCount} students</span></header>
        <h2>${esc(item.batch)}</h2>
        <p>${esc(item.subject)} · ${esc(item.program)}</p>
        <dl><div><dt>Classes</dt><dd>${matchingSessions.length}</dd></div><div><dt>Next class</dt><dd>${next ? `${dateLong(next.startsAt)} · ${timeText(next.startsAt)}` : "Not scheduled"}</dd></div></dl>
        <button type="button" data-go="schedule">View timetable</button>
      </article>`;
  }).join("") : empty("users", "No assigned batches", "Teaching assignments appear after classes are added to the timetable.");
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
    <span><strong>${esc(profile.fullName)}</strong><span>${esc(profile.email)}</span><span>Faculty account</span></span>
  `;
  const details = [
    ["Full name", profile.fullName],
    ["Portal login", profile.email],
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
  $("#more-profile-copy").textContent = profile.email;
}

function openModal(id, trigger) {
  state.lastFocus = trigger || document.activeElement;
  const modal = $("#" + id);
  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  requestAnimationFrame(() => $("input,select,button", modal)?.focus());
}

function closeModal(id) {
  $("#" + id).classList.add("hidden");
  document.body.style.overflow = "";
  state.lastFocus?.focus?.();
  state.lastFocus = null;
}

function openAssignmentModal(trigger) {
  const pairs = state.data.teachingPairs;
  if (!pairs.length) {
    toast("A timetable assignment is required before publishing work.");
    return;
  }
  $("#assignment-pair").innerHTML = pairs.map(item => `
    <option value="${esc(item.batchId)}|${esc(item.subjectId)}">${esc(item.batch)} · ${esc(item.subject)}</option>
  `).join("");
  $("#assignment-error").classList.add("hidden");
  $("#assignment-due").value = localInputValue();
  openModal("assignment-modal", trigger);
}

async function createAssignment(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const button = $("#assignment-submit");
  const data = new FormData(form);
  const [batchId, subjectId] = String(data.get("pair")).split("|");
  button.disabled = true;
  button.textContent = "Creating…";
  $("#assignment-error").classList.add("hidden");
  try {
    await api("/api/academics/assignments", {
      method:"POST",
      body:JSON.stringify({
        batchId,
        subjectId,
        title:String(data.get("title")).trim(),
        instructions:String(data.get("instructions")).trim(),
        dueAt:new Date(String(data.get("dueAt"))).toISOString(),
        externalUrl:String(data.get("externalUrl")).trim(),
        status:String(data.get("status"))
      })
    });
    form.reset();
    closeModal("assignment-modal");
    await refreshPortal("Assignment created.");
  } catch (error) {
    $("#assignment-error").textContent = error.message;
    $("#assignment-error").classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.textContent = "Create assignment";
  }
}

async function openAttendance(sessionId, trigger) {
  const session = state.data.sessions.find(item => item.id === sessionId);
  if (!session) return;
  state.activeSession = session;
  $("#attendance-error").classList.add("hidden");
  $("#attendance-modal-title").textContent = `${session.subject} · ${session.batch}`;
  $("#attendance-modal-meta").textContent = `${dateLong(session.startsAt)} · ${timeText(session.startsAt)} · ${session.room}`;
  $("#roster-list").innerHTML = empty("users", "Loading roster");
  openModal("attendance-modal", trigger);
  try {
    const result = await api(`/api/attendance/sessions/${encodeURIComponent(sessionId)}`);
    state.roster = result.entries.map(item => ({...item}));
    state.rosterLocked = result.session.registerStatus === "submitted";
    state.rosterUpcoming = new Date(result.session.startsAt).getTime() > Date.now();
    renderRoster();
  } catch (error) {
    $("#roster-list").innerHTML = empty("users", "Unable to load roster", error.message);
  }
}

function renderRoster() {
  const locked = state.rosterLocked;
  const statuses = ["present", "late", "absent", "excused"];
  $("#attendance-progress").textContent = `${state.roster.length} ${state.roster.length === 1 ? "student" : "students"}`;
  $("#mark-all-present").disabled = locked;
  $("#save-attendance").classList.toggle("hidden", locked);
  $("#submit-attendance").classList.toggle("hidden", locked);
  $("#submit-attendance").disabled = state.rosterUpcoming;
  $("#attendance-window-note").textContent = locked ? "This register is submitted and read-only." : state.rosterUpcoming ? "You can prepare a draft now. Submission opens when the class begins." : "Review every student before submitting.";
  $("#attendance-window-note").classList.toggle("warning", state.rosterUpcoming);
  $("#roster-list").innerHTML = state.roster.length ? state.roster.map(item => `
    <div class="roster-row" data-student-id="${esc(item.studentId)}">
      <span class="roster-student"><strong>${esc(item.fullName)}</strong><small>${esc(item.admissionNumber)}</small></span>
      ${statuses.map(status => `<button class="status-option ${item.status === status ? "active" : ""}" type="button" data-status="${status}" aria-pressed="${item.status === status}" ${locked ? "disabled" : ""}>${status[0].toUpperCase() + status.slice(1)}</button>`).join("")}
    </div>
  `).join("") : empty("users", "No active students in this batch");
}

function attendancePayload() {
  return {
    entries:state.roster.map(item => ({
      studentId:item.studentId,
      status:item.status,
      reason:item.reason || ""
    }))
  };
}

async function saveAttendance(submit = false) {
  if (!state.activeSession || !state.roster.length) return;
  const button = submit ? $("#submit-attendance") : $("#save-attendance");
  const idle = button.textContent;
  button.disabled = true;
  button.textContent = submit ? "Submitting…" : "Saving…";
  $("#attendance-error").classList.add("hidden");
  try {
    await api(`/api/attendance/sessions/${encodeURIComponent(state.activeSession.id)}${submit ? "/submit" : ""}`, {
      method:submit ? "POST" : "PUT",
      body:JSON.stringify(attendancePayload())
    });
    closeModal("attendance-modal");
    await refreshPortal(submit ? "Attendance submitted." : "Attendance draft saved.");
  } catch (error) {
    $("#attendance-error").textContent = error.message;
    $("#attendance-error").classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.textContent = idle;
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
  $("#password-toggle").addEventListener("click", togglePassword);
  $("#signout-button").addEventListener("click", logout);
  $("#sidebar-signout").addEventListener("click", logout);
  $("#profile-button").addEventListener("click", () => showView("profile"));
  $("#assignment-form").addEventListener("submit", createAssignment);
  $("#attendance-form").addEventListener("submit", event => {
    event.preventDefault();
    saveAttendance(true);
  });
  $("#save-attendance").addEventListener("click", () => saveAttendance(false));
  $("#mark-all-present").addEventListener("click", () => {
    state.roster.forEach(item => { item.status = "present"; item.reason = ""; });
    renderRoster();
  });
  document.addEventListener("click", event => {
    const view = event.target.closest("[data-view]")?.dataset.view || event.target.closest("[data-go]")?.dataset.go;
    if (view) showView(view);

    const attendanceTrigger = event.target.closest("[data-open-attendance]");
    if (attendanceTrigger) openAttendance(attendanceTrigger.dataset.openAttendance, attendanceTrigger);

    const assignmentTrigger = event.target.closest("[data-open-assignment]");
    if (assignmentTrigger) openAssignmentModal(assignmentTrigger);

    const publishTrigger = event.target.closest("[data-publish-assignment]");
    if (publishTrigger) publishAssignment(publishTrigger.dataset.publishAssignment);

    const closeTrigger = event.target.closest("[data-close-modal]");
    if (closeTrigger) closeModal(closeTrigger.dataset.closeModal);

    const attendanceFilter = event.target.closest("[data-attendance-filter]")?.dataset.attendanceFilter;
    if (attendanceFilter) {
      state.attendanceFilter = attendanceFilter;
      $$("[data-attendance-filter]").forEach(node => {
        const active = node.dataset.attendanceFilter === attendanceFilter;
        node.classList.toggle("active", active);
        node.setAttribute("aria-pressed", String(active));
      });
      renderAttendance();
    }

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

    const scheduleDate = event.target.closest("[data-schedule-date]")?.dataset.scheduleDate;
    if (scheduleDate) {
      state.scheduleDate = scheduleDate;
      renderSchedule();
    }

    const statusButton = event.target.closest(".status-option");
    if (statusButton && !statusButton.disabled) {
      const row = statusButton.closest("[data-student-id]");
      const student = state.roster.find(item => item.studentId === row.dataset.studentId);
      if (student) student.status = statusButton.dataset.status;
      renderRoster();
    }

    const backdrop = event.target.classList.contains("modal-backdrop") ? event.target : null;
    if (backdrop) closeModal(backdrop.id);
  });
  document.addEventListener("keydown", event => {
    if (event.key !== "Escape") return;
    const open = $$(".modal-backdrop:not(.hidden)").at(-1);
    if (open) closeModal(open.id);
  });
  window.addEventListener("popstate", () => {
    const view = location.hash.slice(1);
    if (state.data && PORTAL_VIEWS.has(view)) showView(view, false);
  });
}

initialize();
