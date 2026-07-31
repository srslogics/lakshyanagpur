"use strict";

const icons = {
  arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',
  eye:'<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  "eye-off":'<path d="m3 3 18 18M10.6 5.2A11.4 11.4 0 0 1 12 5c6.5 0 10 7 10 7a16 16 0 0 1-2.1 3.2M6.6 6.6C3.6 8.6 2 12 2 12s3.5 7 10 7a10.7 10.7 0 0 0 4.1-.8M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
  logout:'<path d="m10 17 5-5-5-5m5 5H3m12-9h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"/>',
  search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  check:'<path d="m5 12 4 4L19 6"/>',
  close:'<path d="m6 6 12 12M18 6 6 18"/>',
  calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4m8-4v4M3 10h18"/>',
  "chevron-left":'<path d="m15 18-6-6 6-6"/>',
  "chevron-right":'<path d="m9 18 6-6-6-6"/>'
};

const state = {
  token: localStorage.getItem("lakshya_attendance_token"),
  data: null,
  selectedDate: localDateKey(),
  filter: "action",
  search: "",
  activeSession: null,
  roster: [],
  rosterSearch: "",
  locked: false,
  upcoming: false,
  lastFocus: null,
  confirmTimer: null,
  identity: (() => { try { return JSON.parse(localStorage.getItem("lakshya_attendance_user") || "null"); } catch { return null; } })(),
  online: navigator.onLine
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.check}</svg>`;
const esc = (value = "") => String(value ?? "").replace(/[&<>'"]/g, character => ({
  "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;"
}[character]));
const initials = name => String(name || "AO").split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join("").toUpperCase();
const asInstant = value => {
  if (value instanceof Date) return value;
  const text = String(value || "");
  return new Date(/[zZ]$|[+-]\d{2}:?\d{2}$/.test(text) ? text : `${text}Z`);
};

function localDateKey(date = new Date()) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone:"Asia/Kolkata", year:"numeric", month:"2-digit", day:"2-digit"
  }).formatToParts(date);
  const value = type => parts.find(part => part.type === type)?.value || "";
  return `${value("year")}-${value("month")}-${value("day")}`;
}

function dateLong(value) {
  return new Intl.DateTimeFormat("en-IN", {
    timeZone:"Asia/Kolkata", weekday:"short", day:"numeric", month:"short", year:"numeric"
  }).format(asInstant(value));
}

function timeText(value) {
  return new Intl.DateTimeFormat("en-IN", {
    timeZone:"Asia/Kolkata", hour:"2-digit", minute:"2-digit"
  }).format(asInstant(value));
}

function shiftDate(dateKey, amount) {
  const date = new Date(`${dateKey}T12:00:00+05:30`);
  date.setUTCDate(date.getUTCDate() + amount);
  return localDateKey(date);
}

function injectIcons(root = document) {
  $$("[data-icon]", root).forEach(node => { node.innerHTML = icon(node.dataset.icon); });
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
    const error = new Error(typeof detail === "string" ? detail : detail?.message || body?.error?.message || (response.status >= 500 ? "The service is temporarily unavailable. Try again." : "Unable to complete this request."));
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
  localStorage.removeItem("lakshya_attendance_token");
  localStorage.removeItem("lakshya_attendance_user");
}

function showLogin(message = "") {
  $("#boot-screen").classList.add("hidden");
  $("#password-change-screen").classList.add("hidden");
  $("#attendance-shell").classList.add("hidden");
  $("#login-screen").classList.remove("hidden");
  $("#login-password").value = "";
  $("#login-error").textContent = message;
  $("#login-error").classList.toggle("hidden", !message);
  requestAnimationFrame(() => $("#login-mobile").focus());
}

function showPasswordChange(identity) {
  state.identity = identity;
  $("#boot-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#attendance-shell").classList.add("hidden");
  $("#password-change-screen").classList.remove("hidden");
  $("#password-change-form").reset();
  $("#password-change-error").classList.add("hidden");
  requestAnimationFrame(() => $("[name=currentPassword]", $("#password-change-form")).focus());
}

function showStartupError(error) {
  $("#login-screen").classList.add("hidden");
  $("#password-change-screen").classList.add("hidden");
  $("#attendance-shell").classList.add("hidden");
  const boot = $("#boot-screen");
  boot.classList.remove("hidden");
  let panel = $("#startup-error");
  if (!panel) {
    panel = document.createElement("div");
    panel.id = "startup-error";
    panel.className = "startup-error";
    panel.innerHTML = '<strong>Attendance Desk is temporarily unavailable</strong><p></p><button type="button">Retry</button>';
    boot.append(panel);
    $("button", panel).addEventListener("click", () => location.reload());
  }
  $("p", panel).textContent = error.message;
}

function toast(message) {
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  $("#toast-region").append(node);
  setTimeout(() => node.remove(), 3000);
}

function empty(title, copy = "") {
  return `<div class="empty"><div><span>${icon("calendar")}</span><strong>${esc(title)}</strong>${copy ? `<p>${esc(copy)}</p>` : ""}</div></div>`;
}

async function initialize() {
  injectIcons();
  bindEvents();
  setConnectionState(navigator.onLine);
  $("#working-date").value = state.selectedDate;
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  if (!state.token) return showLogin();
  try {
    const identity = state.identity || await api("/api/auth/me");
    if (identity.role !== "attendance_operator") {
      const error = new Error("This account is not assigned to the Attendance Desk.");
      error.status = 403;
      throw error;
    }
    state.identity = identity;
    localStorage.setItem("lakshya_attendance_user", JSON.stringify(identity));
    if (identity.mustChangePassword) return showPasswordChange(identity);
    await loadDesk();
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
  if (!event.currentTarget.reportValidity()) return;
  const button = $("#login-button");
  const label = $("#login-button-label");
  button.disabled = true;
  label.textContent = "Signing in…";
  $("#login-error").classList.add("hidden");
  try {
    const form = new FormData(event.currentTarget);
    const result = await api("/api/auth/login", {
      method:"POST",
      body:JSON.stringify({
        mobile:String(form.get("mobile")).trim(),
        password:String(form.get("password"))
      })
    });
    if (result.user.role !== "attendance_operator") {
      throw new Error("This account is not assigned to the Attendance Desk.");
    }
    state.token = result.access_token;
    state.identity = result.user;
    localStorage.setItem("lakshya_attendance_token", state.token);
    localStorage.setItem("lakshya_attendance_user", JSON.stringify(result.user));
    if (result.user.mustChangePassword) {
      showPasswordChange(result.user);
      return;
    }
    await loadDesk();
  } catch (error) {
    if (state.token && error.status !== 401 && (error.transient || error.status === 0)) {
      showStartupError(error);
    } else {
      clearSession();
      showLogin(error.message);
    }
  } finally {
    button.disabled = false;
    label.textContent = "Sign in";
  }
}

async function changePassword(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  const currentPassword = String(data.get("currentPassword"));
  const newPassword = String(data.get("newPassword"));
  const error = $("#password-change-error");
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
  const button = $("#password-change-button");
  const idle = button.innerHTML;
  button.disabled = true;
  button.textContent = "Saving…";
  error.classList.add("hidden");
  try {
    const mobile = state.identity?.mobile || "";
    await api("/api/auth/change-password", {method:"POST", body:JSON.stringify({currentPassword, newPassword})});
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

async function loadDesk(message = "") {
  state.data = await api(`/api/attendance/bootstrap?day=${encodeURIComponent(state.selectedDate)}`);
  const profile = state.data.profile;
  $("#operator-name").textContent = profile.fullName;
  $("#menu-name").textContent = profile.fullName;
  $("#menu-mobile").textContent = profile.mobile ? `+91 ${profile.mobile}` : "Mobile not assigned";
  $("#operator-avatar").textContent = initials(profile.fullName);
  $("#working-date").value = state.selectedDate;
  renderDesk();
  $("#boot-screen").classList.add("hidden");
  $("#login-screen").classList.add("hidden");
  $("#attendance-shell").classList.remove("hidden");
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
  closeAccountMenu();
  showLogin();
  toast("Signed out securely.");
}

function metric(label, value, attention = false) {
  return `<article class="metric-card ${attention ? "attention" : ""}"><span>${esc(label)}</span><strong>${esc(value)}</strong></article>`;
}

function sessionState(item) {
  if (item.status !== "scheduled") return "cancelled";
  if (item.registerStatus === "submitted") return "submitted";
  if (asInstant(item.startsAt).getTime() > Date.now()) return "upcoming";
  return "action";
}

function stateLabel(value, item) {
  if (value === "action") return item.registerStatus === "draft" ? "Draft saved" : "Needs action";
  if (value === "submitted") return "Submitted";
  if (value === "upcoming") return "Upcoming";
  return "Cancelled";
}

function renderDesk() {
  const summary = state.data.summary;
  $("#metric-grid").innerHTML = [
    metric("Scheduled", String(summary.scheduled)),
    metric("Needs action", String(summary.pending), summary.pending > 0),
    metric("Upcoming", String(summary.upcoming)),
    metric("Submitted", String(summary.submitted))
  ].join("");
  renderManualPicker();
  renderSessions();
}

function optionMarkup(rows, placeholder) {
  return `<option value="">${esc(placeholder)}</option>${rows.map(item => `<option value="${esc(item.name)}">${esc(item.name)} · ${item.studentCount}</option>`).join("")}`;
}

function manualSelection() {
  const group = (state.data?.catalog?.groups || []).find(item => item.name === $("#manual-batch").value);
  const stream = group?.streams.find(item => item.name === $("#manual-stream").value);
  const subject = stream?.subjects.find(item => item.name === $("#manual-subject").value);
  return {group, stream, subject};
}

function updateManualSummary() {
  const {group, stream, subject} = manualSelection();
  const summary = $("#manual-roster-summary");
  const button = $("#open-manual-register");
  summary.className = "quick-register-status";
  if (!(state.data?.catalog?.groups || []).length) {
    summary.textContent = "Academic student data is not loaded.";
    summary.classList.add("error");
    button.disabled = true;
    button.textContent = "Load roster";
    return;
  }
  if (subject) {
    summary.textContent = `${subject.studentCount} students · ${group.name} · ${stream.name} · ${subject.name}`;
    summary.classList.add("ready");
    button.disabled = false;
    button.textContent = `Load ${subject.studentCount} students`;
    return;
  }
  summary.textContent = stream
    ? "Select a subject."
    : group
      ? "Select a course and subject."
      : "Select a group, course and subject.";
  button.disabled = true;
  button.textContent = "Load roster";
}

function populateManualSubjects(preferred = "") {
  const {stream} = manualSelection();
  const select = $("#manual-subject");
  const rows = stream?.subjects || [];
  select.innerHTML = optionMarkup(rows, "Select subject");
  select.disabled = !rows.length;
  if (rows.some(item => item.name === preferred)) select.value = preferred;
  updateManualSummary();
}

function populateManualStreams(preferredStream = "", preferredSubject = "") {
  const group = (state.data?.catalog?.groups || []).find(item => item.name === $("#manual-batch").value);
  const select = $("#manual-stream");
  const rows = group?.streams || [];
  select.innerHTML = optionMarkup(rows, "Select course");
  select.disabled = !rows.length;
  if (rows.some(item => item.name === preferredStream)) select.value = preferredStream;
  populateManualSubjects(preferredSubject);
}

function renderManualPicker() {
  const previous = {
    batch: $("#manual-batch").value,
    stream: $("#manual-stream").value,
    subject: $("#manual-subject").value
  };
  const catalog = state.data?.catalog || {studentCount:0, groups:[]};
  $("#catalog-student-count").textContent = `${catalog.studentCount || 0} students`;
  $("#manual-batch").innerHTML = optionMarkup(catalog.groups || [], "Select group");
  if ((catalog.groups || []).some(item => item.name === previous.batch)) {
    $("#manual-batch").value = previous.batch;
  }
  populateManualStreams(previous.stream, previous.subject);
}

function renderSessions() {
  const query = state.search.trim().toLowerCase();
  const rows = state.data.sessions.filter(item => {
    const itemState = sessionState(item);
    const matchesFilter = state.filter === "all" || itemState === state.filter;
    const searchable = `${item.batch} ${item.program || ""} ${item.subject} ${item.faculty} ${item.room}`.toLowerCase();
    return matchesFilter && (!query || searchable.includes(query));
  });
  $("#class-count").textContent = `${rows.length} ${rows.length === 1 ? "class" : "classes"}`;
  $("#session-list").innerHTML = rows.length ? rows.map(sessionCard).join("") : empty(
    state.search ? "No matching classes" : state.filter === "action" ? "Nothing needs attention" : "No classes in this view",
    state.search ? "Try a different batch, subject, faculty or room." : "Use another filter or working date."
  );
}

function sessionCard(item) {
  const itemState = sessionState(item);
  const progress = item.studentCount ? Math.min(100, Math.round((item.markedCount / item.studentCount) * 100)) : 0;
  const action = itemState === "submitted" ? "View register" : item.registerStatus === "draft" ? "Continue register" : "Open register";
  return `
    <article class="session-card">
      <div class="session-time"><strong>${timeText(item.startsAt)}</strong><small>${timeText(item.endsAt)}</small></div>
      <div class="session-main">
        <h3>${esc(item.subject)} · ${esc(item.batch)} · ${esc(item.program || "")}</h3>
        <p>${esc(item.faculty)} · ${esc(item.room)}</p>
        <div class="session-meta"><span class="tag">${item.studentCount} students</span><span class="status-pill ${itemState}">${esc(stateLabel(itemState, item))}</span></div>
      </div>
      <div class="session-progress">
        <span><b>${item.markedCount} marked</b><b>${progress}%</b></span>
        <div class="progress-track"><i style="width:${progress}%"></i></div>
      </div>
      <button class="session-action ${itemState === "submitted" ? "locked" : itemState === "upcoming" ? "secondary" : ""}" type="button" data-open-register="${esc(item.id)}" ${itemState === "cancelled" || !item.studentCount ? "disabled" : ""}>${esc(action)}</button>
    </article>
  `;
}

async function openRegister(sessionId, trigger) {
  const session = state.data.sessions.find(item => item.id === sessionId);
  if (!session) return;
  state.activeSession = session;
  state.roster = [];
  state.rosterSearch = "";
  state.lastFocus = trigger;
  $("#roster-search").value = "";
  $("#register-title").textContent = `${session.subject} · ${session.batch} · ${session.program || session.stream || ""}`;
  $("#register-meta").textContent = `${dateLong(session.startsAt)} · ${timeText(session.startsAt)}–${timeText(session.endsAt)} · ${session.faculty} · ${session.room}`;
  $("#roster-list").innerHTML = empty("Loading class roster");
  $("#attendance-error").classList.add("hidden");
  $("#register-dialog").classList.remove("hidden");
  document.body.style.overflow = "hidden";
  $("#close-register").focus();
  try {
    const result = await api(`/api/attendance/sessions/${encodeURIComponent(sessionId)}`);
    applyRegister(result);
  } catch (error) {
    $("#roster-list").innerHTML = empty("Unable to load roster", error.message);
  }
}

function applyRegister(result) {
  state.activeSession = result.session;
  state.roster = result.entries.map(item => ({...item}));
  state.locked = result.session.registerStatus === "submitted";
  state.upcoming = result.session.registerKind !== "manual"
    && asInstant(result.session.startsAt).getTime() > Date.now();
  $("#register-title").textContent = `${result.session.subject} · ${result.session.batch} · ${result.session.program || result.session.stream || ""}`;
  $("#register-meta").textContent = result.session.registerKind === "manual"
    ? `${dateLong(result.session.startsAt)} · ${result.session.stream} · selected roster`
    : `${dateLong(result.session.startsAt)} · ${timeText(result.session.startsAt)}–${timeText(result.session.endsAt)} · ${result.session.faculty} · ${result.session.room}`;
  renderRoster();
}

async function openManualRegister(event) {
  event.preventDefault();
  if (!event.currentTarget.reportValidity()) return;
  const {group, stream, subject} = manualSelection();
  if (!group || !stream || !subject) return updateManualSummary();
  const button = $("#open-manual-register");
  const idle = button.textContent;
  button.disabled = true;
  button.textContent = "Loading roster…";
  $("#manual-roster-summary").classList.remove("error");
  try {
    const result = await api("/api/attendance/manual-registers", {
      method:"POST",
      body:JSON.stringify({
        date:state.selectedDate,
        batch:group.name,
        stream:stream.name,
        subject:subject.name
      })
    });
    state.lastFocus = button;
    state.rosterSearch = "";
    $("#roster-search").value = "";
    $("#attendance-error").classList.add("hidden");
    $("#register-dialog").classList.remove("hidden");
    document.body.style.overflow = "hidden";
    applyRegister(result);
    $("#close-register").focus();
  } catch (error) {
    const summary = $("#manual-roster-summary");
    summary.textContent = error.message;
    summary.className = "quick-register-status error";
  } finally {
    button.disabled = false;
    button.textContent = idle;
  }
}

function rosterCounts() {
  return state.roster.reduce((counts, item) => {
    counts[item.status] = (counts[item.status] || 0) + 1;
    return counts;
  }, {present:0, late:0, absent:0, excused:0});
}

function renderRoster() {
  const counts = rosterCounts();
  const query = state.rosterSearch.trim().toLowerCase();
  const visible = state.roster.filter(item => `${item.fullName} ${item.admissionNumber}`.toLowerCase().includes(query));
  $("#roster-count").textContent = `${state.roster.length} ${state.roster.length === 1 ? "student" : "students"}`;
  $("#marked-summary").textContent = `${counts.present} present · ${counts.late} late · ${counts.absent} absent · ${counts.excused} excused`;
  $("#register-note").textContent = state.locked
    ? "This register has been submitted and is read-only. Corrections must be completed by an authorised coordinator."
    : state.upcoming
      ? "You may prepare and save a draft. Final submission opens when the class begins."
      : "Review every student before submitting. Submitted registers are locked.";
  $("#register-note").className = `register-note ${state.locked ? "locked" : state.upcoming ? "warning" : ""}`;
  $("#mark-all-present").disabled = state.locked;
  $("#save-draft").classList.toggle("hidden", state.locked);
  $("#submit-register").classList.toggle("hidden", state.locked);
  $("#submit-register").disabled = state.upcoming;
  $("#roster-list").innerHTML = visible.length ? visible.map(rosterRow).join("") : empty("No matching students");
}

function rosterRow(item) {
  const statuses = ["present", "late", "absent", "excused"];
  return `
    <div class="roster-row" data-student-id="${esc(item.studentId)}">
      <span class="student-copy"><strong>${esc(item.fullName)}</strong><small>${esc(item.admissionNumber)}</small></span>
      ${statuses.map(status => `<button class="status-option ${item.status === status ? "active" : ""}" type="button" data-status="${status}" aria-pressed="${item.status === status}" ${state.locked ? "disabled" : ""}>${status[0].toUpperCase() + status.slice(1)}</button>`).join("")}
      <input class="reason-input" data-reason type="text" maxlength="1000" value="${esc(item.reason || "")}" placeholder="Note (optional)" aria-label="Attendance note for ${esc(item.fullName)}" ${state.locked ? "disabled" : ""}>
    </div>
  `;
}

function closeRegister() {
  $("#register-dialog").classList.add("hidden");
  document.body.style.overflow = "";
  resetSubmitConfirmation();
  state.lastFocus?.focus();
  state.lastFocus = null;
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

function syncVisibleReasons() {
  $$("[data-student-id]", $("#roster-list")).forEach(row => {
    const student = state.roster.find(item => item.studentId === row.dataset.studentId);
    if (student) student.reason = $("[data-reason]", row).value;
  });
}

async function saveAttendance(submit = false) {
  if (!state.activeSession || !state.roster.length || state.locked) return;
  syncVisibleReasons();
  const button = submit ? $("#submit-register") : $("#save-draft");
  const idle = submit ? "Submit register" : "Save draft";
  button.disabled = true;
  button.textContent = submit ? "Submitting…" : "Saving…";
  $("#attendance-error").classList.add("hidden");
  try {
    const resource = state.activeSession.registerKind === "manual"
      ? "manual-registers"
      : "sessions";
    await api(`/api/attendance/${resource}/${encodeURIComponent(state.activeSession.id)}${submit ? "/submit" : ""}`, {
      method:submit ? "POST" : "PUT",
      body:JSON.stringify(attendancePayload())
    });
    closeRegister();
    await loadDesk(submit ? "Attendance register submitted." : "Attendance draft saved.");
  } catch (error) {
    $("#attendance-error").textContent = error.message;
    $("#attendance-error").classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.textContent = idle;
  }
}

function resetSubmitConfirmation() {
  clearTimeout(state.confirmTimer);
  state.confirmTimer = null;
  const button = $("#submit-register");
  button.classList.remove("confirming");
  button.textContent = "Submit register";
  button.dataset.confirming = "";
}

function requestSubmit(event) {
  event.preventDefault();
  const button = $("#submit-register");
  if (button.dataset.confirming === "true") {
    resetSubmitConfirmation();
    saveAttendance(true);
    return;
  }
  button.dataset.confirming = "true";
  button.classList.add("confirming");
  button.textContent = "Tap again to confirm";
  state.confirmTimer = setTimeout(resetSubmitConfirmation, 4000);
}

function togglePassword() {
  const input = $("#login-password");
  const button = $("#password-toggle");
  const show = input.type === "password";
  input.type = show ? "text" : "password";
  button.setAttribute("aria-label", show ? "Hide password" : "Show password");
  $("[data-icon]", button).dataset.icon = show ? "eye-off" : "eye";
  injectIcons(button);
}

function toggleAccountMenu() {
  const menu = $("#account-menu");
  const open = menu.classList.contains("hidden");
  menu.classList.toggle("hidden", !open);
  $("#account-button").setAttribute("aria-expanded", String(open));
}

function closeAccountMenu() {
  $("#account-menu").classList.add("hidden");
  $("#account-button").setAttribute("aria-expanded", "false");
}

function setDate(date) {
  state.selectedDate = date;
  $("#working-date").value = date;
  loadDesk().catch(error => toast(error.message));
}

function bindEvents() {
  $("#login-form").addEventListener("submit", login);
  $("#password-change-form").addEventListener("submit", changePassword);
  $("#password-toggle").addEventListener("click", togglePassword);
  $("#account-button").addEventListener("click", event => { event.stopPropagation(); toggleAccountMenu(); });
  $("#signout-button").addEventListener("click", logout);
  $("#previous-day").addEventListener("click", () => setDate(shiftDate(state.selectedDate, -1)));
  $("#next-day").addEventListener("click", () => setDate(shiftDate(state.selectedDate, 1)));
  $("#today-button").addEventListener("click", () => setDate(localDateKey()));
  $("#working-date").addEventListener("change", event => { if (event.target.value) setDate(event.target.value); });
  $("#manual-register-form").addEventListener("submit", openManualRegister);
  $("#manual-batch").addEventListener("change", () => populateManualStreams());
  $("#manual-stream").addEventListener("change", () => populateManualSubjects());
  $("#manual-subject").addEventListener("change", updateManualSummary);
  window.addEventListener("online", () => setConnectionState(true));
  window.addEventListener("offline", () => setConnectionState(false));
  $("#class-search").addEventListener("input", event => { state.search = event.target.value; renderSessions(); });
  $("#roster-search").addEventListener("input", event => { syncVisibleReasons(); state.rosterSearch = event.target.value; renderRoster(); });
  $("#close-register").addEventListener("click", closeRegister);
  $("#cancel-register").addEventListener("click", closeRegister);
  $("#save-draft").addEventListener("click", () => saveAttendance(false));
  $("#attendance-form").addEventListener("submit", requestSubmit);
  $("#mark-all-present").addEventListener("click", () => {
    syncVisibleReasons();
    state.roster.forEach(item => { item.status = "present"; item.reason = ""; });
    renderRoster();
  });
  document.addEventListener("click", event => {
    if (!event.target.closest(".operator")) closeAccountMenu();
    const filter = event.target.closest("[data-filter]")?.dataset.filter;
    if (filter) {
      state.filter = filter;
      $$("[data-filter]").forEach(button => {
        const active = button.dataset.filter === filter;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
      });
      renderSessions();
    }
    const register = event.target.closest("[data-open-register]");
    if (register) openRegister(register.dataset.openRegister, register);
    const statusButton = event.target.closest(".status-option");
    if (statusButton && !statusButton.disabled) {
      syncVisibleReasons();
      const row = statusButton.closest("[data-student-id]");
      const student = state.roster.find(item => item.studentId === row.dataset.studentId);
      if (student) student.status = statusButton.dataset.status;
      renderRoster();
    }
    if (event.target === $("#register-dialog")) closeRegister();
  });
  document.addEventListener("input", event => {
    if (!event.target.matches("[data-reason]")) return;
    const row = event.target.closest("[data-student-id]");
    const student = state.roster.find(item => item.studentId === row.dataset.studentId);
    if (student) student.reason = event.target.value;
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !$("#register-dialog").classList.contains("hidden")) {
      closeRegister();
      return;
    }
    if (event.key !== "Tab" || $("#register-dialog").classList.contains("hidden")) return;
    const focusable = $$("button:not([disabled]),input:not([disabled])", $("#register-dialog"));
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
}

initialize();
