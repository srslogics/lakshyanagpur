const data = {
  dashboardStats: [
    { label: "New Enquiries", value: "186", note: "42 from website this week" },
    { label: "Admissions Closed", value: "74", note: "39.7% funnel conversion" },
    { label: "Fees Due", value: "Rs 4.8L", note: "61 students need follow-up" },
    { label: "Tests Scheduled", value: "12", note: "3 full syllabus mocks" }
  ],
  priorities: [
    { title: "Call 18 hot leads from NEET seminar campaign", note: "Counsellor Priya has 6 parents waiting for fee plan discussion." },
    { title: "Approve discount requests above 10%", note: "7 cases pending owner approval in scholarship + conversion bucket." },
    { title: "Review absent students from top JEE batch", note: "Auto parent alerts sent. 3 need academic mentor callback." },
    { title: "Check month-end cashflow projection", note: "Expected shortfall reduces if 14 overdue instalments are collected this week." }
  ],
  funnel: [
    { stage: "Enquiries", count: 186 },
    { stage: "Counselling Done", count: 124 },
    { stage: "Demo Class", count: 91 },
    { stage: "Fee Discussion", count: 82 },
    { stage: "Admissions", count: 74 }
  ],
  batchMix: [
    { name: "NEET Repeaters", students: 380, fill: 88 },
    { name: "JEE Main + Advanced", students: 315, fill: 79 },
    { name: "MHT-CET", students: 264, fill: 72 },
    { name: "Foundation 9-10", students: 325, fill: 85 }
  ],
  alerts: [
    "14 fee instalments overdue for more than 10 days.",
    "Physics faculty load exceeds 92% for two consecutive weeks.",
    "Batch NEET-R3 average score dropped 6% in last mock test.",
    "8 new web leads still not contacted within 30 minutes."
  ],
  leadSources: [
    { source: "Website Forms", leads: 42, conversion: "36%" },
    { source: "Seminars in Schools", leads: 51, conversion: "48%" },
    { source: "Parent Referrals", leads: 27, conversion: "63%" },
    { source: "Instagram / Meta Ads", leads: 39, conversion: "28%" },
    { source: "Walk-ins", leads: 27, conversion: "52%" }
  ],
  admissions: [
    ["Aarav Thakre", "JEE 11th", "Website", "Priya", "Hot", "Parent meeting at 6:30 PM"],
    ["Saanvi Mohod", "NEET Repeater", "Seminar", "Rahul", "Demo Booked", "Attend biology demo tomorrow"],
    ["Vedant Zade", "MHT-CET", "Instagram", "Kiran", "Negotiation", "Owner discount approval"],
    ["Khushi Agrawal", "Foundation", "Referral", "Priya", "Won", "Admission fee paid"],
    ["Yash Bisen", "NEET 12th", "Walk-in", "Rahul", "Follow-up", "Share test schedule and fee plan"]
  ],
  students: [
    ["Ananya Deshmukh", "NEET-R2", "Mrs. Deshmukh", "96%", "Clear", "612 / 720"],
    ["Rudra Sakhare", "JEE-A1", "Mr. Sakhare", "89%", "Instalment due", "211 / 300"],
    ["Prisha Tiwari", "Foundation 10-A", "Mrs. Tiwari", "98%", "Clear", "91 / 100"],
    ["Atharv Kale", "MHT-CET-P1", "Mr. Kale", "84%", "2 dues", "148 / 200"],
    ["Myra Jain", "NEET-12 Elite", "Mrs. Jain", "93%", "Clear", "645 / 720"]
  ],
  studentProfile: [
    {
      title: "Ananya Deshmukh",
      body: "NEET Repeater batch. Target score 650+. Parent app active. 96% attendance, all fees paid, strongest in Biology, needs speed improvement in Physics numericals."
    },
    {
      title: "Parent Notes",
      body: "Mother prefers weekly progress summary on WhatsApp every Sunday evening. Escalate only if attendance drops below 90% or if two tests decline in a row."
    },
    {
      title: "Academic Action",
      body: "Auto-enrolled in Monday doubt-solving clinic and Friday speed-test series based on weak-area analytics."
    }
  ],
  attendanceSummary: [
    { label: "Marked Today", value: "1,211", note: "Out of 1,284 students" },
    { label: "Present", value: "1,144", note: "94.2% attendance" },
    { label: "Late", value: "28", note: "Gate scan after cutoff" },
    { label: "Absent", value: "39", note: "Parent alerts triggered" }
  ],
  attendanceRows: [
    ["NEET-R2", "120", "113", "2", "5", "WhatsApp alert + mentor call"],
    ["JEE-A1", "96", "90", "3", "3", "Absence trend normal"],
    ["MHT-CET-P1", "82", "74", "4", "4", "Send parent note for repeat latecomers"],
    ["Foundation 10-A", "64", "62", "1", "1", "No escalation needed"],
    ["NEET-12 Elite", "72", "68", "0", "4", "Academic coordinator to review"]
  ],
  fees: [
    ["Rudra Sakhare", "Quarterly", "Rs 1,45,000", "Rs 95,000", "Rs 50,000", "08 Jul 2026"],
    ["Atharv Kale", "Monthly", "Rs 72,000", "Rs 48,000", "Rs 24,000", "05 Jul 2026"],
    ["Saanvi Mohod", "Full Payment", "Rs 1,20,000", "Rs 1,20,000", "Rs 0", "-"],
    ["Yash Bisen", "Installments", "Rs 1,05,000", "Rs 35,000", "Rs 70,000", "12 Jul 2026"],
    ["Prisha Tiwari", "Quarterly", "Rs 68,000", "Rs 68,000", "Rs 0", "-"]
  ],
  financeSummary: [
    "Fee collection this month: Rs 18.6L against target of Rs 20.2L.",
    "Outstanding receivables: Rs 4.8L, with Rs 2.1L overdue by more than 7 days.",
    "Scholarship impact: 11.4% effective discount across fresh admissions.",
    "Expected collection if reminders convert: Rs 3.2L within 5 days."
  ],
  examCalendar: [
    { title: "NEET Full Syllabus Mock", note: "4 July, OMR + analytics + parent summary." },
    { title: "JEE Advanced Problem Marathon", note: "6 July, paper discussion by senior faculty." },
    { title: "Foundation Weekly Olympiad", note: "8 July, auto-rank generation." },
    { title: "MHT-CET Speed Test", note: "10 July, chapter-level accuracy trends." }
  ],
  academics: [
    ["NEET-12 Elite", "Mock 07", "612 / 720", "688 / 720", "Physics", "Push speed drills"],
    ["JEE-A1", "PCM Grand Test", "214 / 300", "276 / 300", "Organic Chemistry", "Add revision block"],
    ["MHT-CET-P1", "CET Sprint 05", "151 / 200", "182 / 200", "Maths", "Assign formula recap"],
    ["Foundation 10-A", "Olympiad 04", "87 / 100", "98 / 100", "Mental ability", "Extra worksheet"]
  ],
  faculty: [
    ["Dr. Meenal Joshi", "Biology", "NEET-R2, NEET-12 Elite", "28", "86%", "Today 4:00 PM"],
    ["Prof. Rohan Bhave", "Physics", "JEE-A1, NEET-R2", "33", "92%", "Today 2:30 PM"],
    ["Prof. Ketan Kadu", "Mathematics", "JEE-A1, MHT-CET-P1", "30", "84%", "Tomorrow 8:00 AM"],
    ["Mrs. Vaishali Wankhede", "Chemistry", "Foundation 10-A, NEET-12 Elite", "26", "74%", "Today 5:30 PM"]
  ],
  timetableNotes: [
    "Physics load is highest. Add one backup faculty slot before peak season.",
    "Sunday doubt sessions are 91% utilized and can be upsold as premium support.",
    "Room 204 is underbooked in afternoon hours and can host extra CET revision batches.",
    "Faculty attendance and class completion can be linked to payroll in the live version."
  ],
  messageFlows: [
    { title: "New Lead Journey", note: "Instant WhatsApp acknowledgement, brochure, counsellor assignment, 3 follow-up nudges." },
    { title: "Attendance Alert", note: "Parent message at 15 minutes after class start, mentor call if 2nd absence this week." },
    { title: "Fee Reminder", note: "Gentle reminder 3 days before due date, payment link on due date, escalation after 5 days." },
    { title: "Test Result Broadcast", note: "Scorecard, percentile, weak subjects, next action plan to parent + student app." }
  ],
  communications: [
    ["NEET Parents", "Mock test result summary", "WhatsApp", "Yesterday 8:15 PM", "98.1%", "Academic team"],
    ["All New Leads", "Seminar invitation", "SMS + WhatsApp", "Yesterday 11:00 AM", "94.6%", "Admissions"],
    ["Fee Due Students", "Payment reminder", "WhatsApp", "Today 9:30 AM", "97.4%", "Accounts"],
    ["Foundation Parents", "PTM reminder", "SMS", "Today 1:00 PM", "99.2%", "Admin desk"]
  ],
  reports: [
    "Daily admissions tracker",
    "Batch occupancy report",
    "Faculty utilization report",
    "Fee due ageing report",
    "Student performance trend report",
    "Parent communication audit"
  ],
  executiveBoard: [
    { title: "Revenue", note: "Collections are at 92% of target. Biggest lift opportunity is overdue instalment recovery." },
    { title: "Admissions", note: "School seminar leads convert best. Double down on that channel in July." },
    { title: "Academics", note: "NEET flagship batches are strong, but JEE chemistry intervention is needed." },
    { title: "Operations", note: "Attendance automation is saving front-desk time and improving parent trust." }
  ],
  parentFeatures: [
    "Daily attendance status with absent and late alerts",
    "Fee receipts, due reminders, and online payment links",
    "Test scores, rank, percentile, and weak topic breakdown",
    "Timetable, homework, doubt sessions, and PTM updates",
    "Direct two-way communication with academic mentor"
  ],
  adminSettings: [
    "Branch setup, courses, batches, subjects, and fee plans",
    "Role-based access for owner, counsellor, admin, faculty, accounts",
    "Lead source mapping and campaign tracking",
    "Automated reminders, templates, and escalation rules",
    "Audit logs, user activity, and export permissions"
  ],
  rollout: [
    { title: "Week 1: Discovery", note: "Import student, fee, batch and lead data from Excel and existing tools." },
    { title: "Week 2: Core Setup", note: "Configure admissions, courses, fee plans, roles, and parent communication templates." },
    { title: "Week 3: Pilot Branch", note: "Run one branch or one department live with attendance + fees + reports." },
    { title: "Week 4: Full Go-Live", note: "Train team, enable dashboards for owner, and switch off manual registers." }
  ]
};

const viewTitle = document.getElementById("view-title");
const navItems = document.querySelectorAll(".nav-item");
const views = document.querySelectorAll(".content-view");
const installButton = document.getElementById("install-app");
const appStatus = document.getElementById("app-status");
const menuToggle = document.getElementById("menu-toggle");
const drawerBackdrop = document.getElementById("drawer-backdrop");
let deferredInstallPrompt = null;

function setStatusClass(value) {
  const text = String(value).toLowerCase();
  if (text.includes("clear") || text.includes("won") || text.includes("healthy")) return "green";
  if (text.includes("due") || text.includes("hot") || text.includes("demo") || text.includes("negotiation")) return "orange";
  if (text.includes("absent") || text.includes("overdue")) return "red";
  return "green";
}

function renderStats(targetId, items) {
  const el = document.getElementById(targetId);
  el.innerHTML = items.map(item => `
    <div class="stat-card">
      <span>${item.label}</span>
      <strong>${item.value}</strong>
      <small>${item.note}</small>
    </div>
  `).join("");
}

function renderTimeline(targetId, items) {
  const el = document.getElementById(targetId);
  el.innerHTML = items.map(item => `
    <div class="timeline-item">
      <strong>${item.title}</strong>
      <span>${item.note}</span>
    </div>
  `).join("");
}

function renderSimpleList(targetId, items) {
  const el = document.getElementById(targetId);
  el.innerHTML = items.map(item => `<li><strong>${item}</strong></li>`).join("");
}

function renderFunnel() {
  const max = data.funnel[0].count;
  const el = document.getElementById("funnel");
  el.innerHTML = data.funnel.map(item => `
    <div class="funnel-step">
      <div class="funnel-label">${item.stage}</div>
      <div class="funnel-bar" style="width:${(item.count / max) * 100}%"></div>
      <strong>${item.count}</strong>
    </div>
  `).join("");
}

function renderBatchMix() {
  const el = document.getElementById("batch-mix");
  el.innerHTML = data.batchMix.map(item => `
    <div class="batch-row">
      <div class="batch-row-head">
        <strong>${item.name}</strong>
        <span>${item.students} students</span>
      </div>
      <div class="batch-track">
        <div class="batch-fill" style="width:${item.fill}%"></div>
      </div>
    </div>
  `).join("");
}

function renderLeadSources() {
  const el = document.getElementById("lead-sources");
  el.innerHTML = data.leadSources.map(item => `
    <div class="source-item">
      <div>
        <strong>${item.source}</strong>
        <span>${item.leads} leads</span>
      </div>
      <strong>${item.conversion}</strong>
    </div>
  `).join("");
}

function renderTableRows(targetId, rows, options = {}) {
  const el = document.getElementById(targetId);
  el.innerHTML = rows.map(row => {
    const cells = row.map((cell, index) => {
      if (options.statusIndex === index) {
        return `<td><span class="status ${setStatusClass(cell)}">${cell}</span></td>`;
      }
      return `<td>${cell}</td>`;
    }).join("");
    return `<tr>${cells}</tr>`;
  }).join("");
}

function renderProfile() {
  const el = document.getElementById("student-profile");
  el.innerHTML = data.studentProfile.map(item => `
    <div class="profile-block">
      <h4>${item.title}</h4>
      <p>${item.body}</p>
    </div>
  `).join("");
}

function renderReportList() {
  const el = document.getElementById("report-list");
  el.innerHTML = data.reports.map(item => `
    <li>
      <strong>${item}</strong>
      <span>Export as PDF / Excel for owner, accounts, faculty or counsellors.</span>
    </li>
  `).join("");
}

function renderBoard() {
  const el = document.getElementById("executive-board");
  el.innerHTML = data.executiveBoard.map(item => `
    <div class="board-item">
      <strong>${item.title}</strong>
      <span>${item.note}</span>
    </div>
  `).join("");
}

function bindNavigation() {
  navItems.forEach(item => {
    item.addEventListener("click", () => {
      navItems.forEach(nav => nav.classList.remove("active"));
      views.forEach(view => view.classList.remove("active"));

      item.classList.add("active");
      const target = document.getElementById(item.dataset.view);
      target.classList.add("active");
      viewTitle.textContent = item.textContent;
      closeDrawer();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
}

function openDrawer() {
  document.body.classList.add("drawer-open");
  menuToggle.setAttribute("aria-expanded", "true");
}

function closeDrawer() {
  document.body.classList.remove("drawer-open");
  menuToggle.setAttribute("aria-expanded", "false");
}

function bindDrawer() {
  if (!menuToggle || !drawerBackdrop) return;

  menuToggle.addEventListener("click", () => {
    if (document.body.classList.contains("drawer-open")) {
      closeDrawer();
    } else {
      openDrawer();
    }
  });

  drawerBackdrop.addEventListener("click", closeDrawer);

  window.addEventListener("resize", () => {
    if (window.innerWidth > 720) {
      closeDrawer();
    }
  });
}

function updateAppStatus(text, tone = "") {
  appStatus.textContent = text;
  appStatus.classList.remove("success", "warn");
  if (tone) {
    appStatus.classList.add(tone);
  }
}

function setupInstallPrompt() {
  window.addEventListener("beforeinstallprompt", event => {
    event.preventDefault();
    deferredInstallPrompt = event;
    installButton.classList.remove("hidden");
    updateAppStatus("Installable App Ready");
  });

  installButton.addEventListener("click", async () => {
    if (!deferredInstallPrompt) return;

    deferredInstallPrompt.prompt();
    const choice = await deferredInstallPrompt.userChoice;
    if (choice.outcome === "accepted") {
      updateAppStatus("App Installation Started", "success");
    } else {
      updateAppStatus("Install Prompt Dismissed", "warn");
    }
    deferredInstallPrompt = null;
    installButton.classList.add("hidden");
  });

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    installButton.classList.add("hidden");
    updateAppStatus("Installed as App", "success");
  });
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    updateAppStatus("Offline Mode Not Supported Here");
    return;
  }

  if (!window.isSecureContext) {
    updateAppStatus("Offline Mode Works After HTTPS Deployment");
    return;
  }

  try {
    const registration = await navigator.serviceWorker.register("./sw.js");
    if (registration) {
      updateAppStatus("Offline App Support Active", "success");
      return;
    }
    updateAppStatus("Offline Mode Ready After Refresh");
  } catch (error) {
    const message = String(error && error.message ? error.message : error).toLowerCase();
    if (message.includes("unsupported") || message.includes("secure") || message.includes("context")) {
      updateAppStatus("Offline Mode Works After HTTPS Deployment");
      return;
    }

    if (message.includes("script") || message.includes("scope") || message.includes("mime")) {
      updateAppStatus("Offline Setup Needs Review", "warn");
      return;
    }

    updateAppStatus("Offline Mode Temporarily Unavailable");
  }
}

function updateEnvironmentBadges() {
  const pills = document.querySelectorAll(".topbar-actions .pill");
  if (pills[0]) {
    pills[0].textContent = "Session 2026-27";
  }
  if (pills[1]) {
    pills[1].textContent = window.isSecureContext ? "Live Demo Mode" : "Preview Mode";
  }
}

function initAppChrome() {
  updateEnvironmentBadges();
  setupInstallPrompt();
  registerServiceWorker();
}

function init() {
  renderStats("dashboard-stats", data.dashboardStats);
  renderTimeline("priority-list", data.priorities);
  renderFunnel();
  renderBatchMix();
  renderSimpleList("alerts", data.alerts);
  renderLeadSources();
  renderTableRows("admission-rows", data.admissions, { statusIndex: 4 });
  renderTableRows("student-rows", data.students);
  renderProfile();
  renderStats("attendance-summary", data.attendanceSummary);
  renderTableRows("attendance-rows", data.attendanceRows);
  renderTableRows("fee-rows", data.fees);
  renderSimpleList("finance-summary", data.financeSummary);
  renderTimeline("exam-calendar", data.examCalendar);
  renderTableRows("academic-rows", data.academics);
  renderTableRows("faculty-rows", data.faculty);
  renderSimpleList("timetable-notes", data.timetableNotes);
  renderTimeline("message-flows", data.messageFlows);
  renderTableRows("communication-rows", data.communications);
  renderReportList();
  renderBoard();
  renderSimpleList("parent-features", data.parentFeatures);
  renderSimpleList("admin-settings", data.adminSettings);
  renderTimeline("rollout-plan", data.rollout);
  bindNavigation();
  bindDrawer();
  initAppChrome();
}

init();
