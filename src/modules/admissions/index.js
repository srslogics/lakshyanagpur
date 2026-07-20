import { admissionsModuleData } from "./data.js";

const STAGE_ORDER = ["Fresh", "Counselling", "Hot", "Demo Booked", "Negotiation", "Follow-up", "Won"];

const state = {
  leads: admissionsModuleData.leads.map(lead => ({
    ...lead,
    tasks: [...lead.tasks],
    timeline: [...lead.timeline]
  })),
  search: "",
  stage: "all",
  counsellor: "all",
  selectedLeadId: admissionsModuleData.leads[0]?.id ?? null
};

function statusTone(value) {
  const text = String(value).toLowerCase();
  if (text.includes("won")) return "green";
  if (text.includes("follow")) return "red";
  if (text.includes("hot") || text.includes("demo") || text.includes("negotiation")) return "orange";
  return "green";
}

function getRefs() {
  return {
    kpis: document.getElementById("admissions-kpis"),
    stats: document.getElementById("admissions-stats"),
    pipeline: document.getElementById("admissions-pipeline"),
    sources: document.getElementById("lead-sources"),
    counsellorLoad: document.getElementById("counsellor-load"),
    queue: document.getElementById("admissions-queue"),
    checklist: document.getElementById("admissions-checklist"),
    rows: document.getElementById("admission-rows"),
    selected: document.getElementById("admissions-selected"),
    search: document.getElementById("admissions-search"),
    stage: document.getElementById("admissions-stage-filter"),
    counsellor: document.getElementById("admissions-counsellor-filter"),
    reset: document.getElementById("admissions-reset"),
    createForm: document.getElementById("admissions-create-form"),
    createCounsellor: document.getElementById("lead-counsellor"),
    rules: document.getElementById("admissions-rules")
  };
}

function renderCards(target, items) {
  if (!target) return;
  target.innerHTML = items.map(item => `
    <div class="kpi-card">
      <span>${item.label}</span>
      <strong>${item.value}</strong>
      <small>${item.note}</small>
    </div>
  `).join("");
}

function renderPipeline(target) {
  if (!target) return;
  const totalActive = Math.max(1, state.leads.length);
  const items = STAGE_ORDER.map(stage => {
    const count = state.leads.filter(lead => lead.stage === stage).length;
    return {
      stage,
      count,
      fill: Math.round((count / totalActive) * 100),
      note: stage === "Won"
        ? "Admissions confirmed and ready for onboarding"
        : `${count} lead${count === 1 ? "" : "s"} currently in this stage`
    };
  });

  target.innerHTML = items.map(item => `
    <div class="stage-card">
      <div class="stage-card-head">
        <strong>${item.stage}</strong>
        <span>${item.count}</span>
      </div>
      <p>${item.note}</p>
      <div class="stage-track">
        <div class="stage-fill" style="width:${item.fill}%"></div>
      </div>
    </div>
  `).join("");
}

function renderSourceList(target) {
  if (!target) return;
  const sourceMap = new Map();
  state.leads.forEach(lead => {
    const current = sourceMap.get(lead.source) ?? { source: lead.source, leads: 0, won: 0 };
    current.leads += 1;
    if (lead.stage === "Won") current.won += 1;
    sourceMap.set(lead.source, current);
  });

  const items = [...sourceMap.values()]
    .sort((a, b) => b.leads - a.leads)
    .map(item => ({
      source: item.source,
      leads: item.leads,
      conversion: `${Math.round((item.won / Math.max(1, item.leads)) * 100)}%`
    }));

  target.innerHTML = items.map(item => `
    <div class="source-item">
      <div>
        <strong>${item.source}</strong>
        <span>${item.leads} leads</span>
      </div>
      <strong>${item.conversion}</strong>
    </div>
  `).join("");
}

function renderTimeline(target, items) {
  if (!target) return;
  target.innerHTML = items.map(item => `
    <div class="timeline-item">
      <strong>${item.title}</strong>
      <span>${item.note}</span>
    </div>
  `).join("");
}

function renderChecklist(target) {
  if (!target) return;
  target.innerHTML = admissionsModuleData.checklist.map(item => `<li>${item}</li>`).join("");
}

function renderRules(target) {
  if (!target) return;
  target.innerHTML = admissionsModuleData.rules.map(item => `<li>${item}</li>`).join("");
}

function getFilteredLeads() {
  return state.leads.filter(lead => {
    const matchesSearch = !state.search || [
      lead.student,
      lead.parent,
      lead.program,
      lead.source,
      lead.counsellor
    ].some(value => value.toLowerCase().includes(state.search));

    const matchesStage = state.stage === "all" || lead.stage === state.stage;
    const matchesCounsellor = state.counsellor === "all" || lead.counsellor === state.counsellor;

    return matchesSearch && matchesStage && matchesCounsellor;
  });
}

function ensureSelectedLead(leads) {
  if (!leads.length) {
    state.selectedLeadId = null;
    return null;
  }

  const existing = leads.find(lead => lead.id === state.selectedLeadId);
  if (existing) return existing;

  state.selectedLeadId = leads[0].id;
  return leads[0];
}

function renderLeadsTable(target, leads) {
  if (!target) return;

  if (!leads.length) {
    target.innerHTML = `
      <tr>
        <td colspan="7">
          <div class="table-empty">
            <strong>No leads match the current filters.</strong>
            <span>Try another counsellor, stage, or search term.</span>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  target.innerHTML = leads.map(lead => `
    <tr class="lead-row${lead.id === state.selectedLeadId ? " selected" : ""}" data-lead-id="${lead.id}">
      <td>
        <strong>${lead.student}</strong>
      </td>
      <td>${lead.program}</td>
      <td>${lead.parent}</td>
      <td>${lead.source}</td>
      <td>${lead.counsellor}</td>
      <td><span class="status ${statusTone(lead.stage)}">${lead.stage}</span></td>
      <td>${lead.nextAction}</td>
    </tr>
  `).join("");
}

function renderSelectedLead(target, lead) {
  if (!target) return;

  if (!lead) {
    target.innerHTML = `
      <div class="feature-empty">
        <strong>No active lead selected</strong>
        <span>Choose a lead from the register to inspect the full profile.</span>
      </div>
    `;
    return;
  }

  target.innerHTML = `
    <div class="feature-card-top">
      <div>
        <strong>${lead.student}</strong>
        <span>${lead.program}</span>
      </div>
      <span class="status ${statusTone(lead.stage)}">${lead.stage}</span>
    </div>

    <div class="lead-meta-grid">
      <div class="lead-meta-card">
        <small>Parent</small>
        <strong>${lead.parent}</strong>
      </div>
      <div class="lead-meta-card">
        <small>Counsellor</small>
        <strong>${lead.counsellor}</strong>
      </div>
      <div class="lead-meta-card">
        <small>Commercial</small>
        <strong>${lead.budget}</strong>
      </div>
      <div class="lead-meta-card">
        <small>Last touch</small>
        <strong>${lead.lastTouch}</strong>
      </div>
    </div>

    <p>${lead.summary}</p>

    <div class="lead-detail-block">
      <h4>Immediate actions</h4>
      <ul class="feature-list">
        ${lead.tasks.map(item => `<li>${item}</li>`).join("")}
      </ul>
    </div>

    <div class="lead-detail-block">
      <h4>Stage actions</h4>
      <div class="stage-actions">
        ${STAGE_ORDER.map(stage => `
          <button class="pill${lead.stage === stage ? " pill-primary" : ""}" type="button" data-stage-action="${stage}">
            ${stage}
          </button>
        `).join("")}
      </div>
    </div>

    <div class="lead-detail-block">
      <h4>Notes and follow-up</h4>
      <form class="lead-note-form" id="admissions-note-form">
        <label class="control-field control-field-wide" for="lead-note-entry">
          <span>Internal note</span>
          <textarea id="lead-note-entry" name="note" rows="3" placeholder="Add counselling update, parent concern, or internal note"></textarea>
        </label>
        <label class="control-field control-field-wide" for="lead-next-action-entry">
          <span>Update next action</span>
          <input id="lead-next-action-entry" name="nextAction" type="text" value="${lead.nextAction}">
        </label>
        <div class="form-actions">
          <button class="pill pill-primary" type="submit">Save Update</button>
        </div>
      </form>
    </div>

    <div class="lead-detail-block">
      <h4>Recent movement</h4>
      <ul class="lead-mini-timeline">
        ${lead.timeline.map(item => `<li>${item}</li>`).join("")}
      </ul>
    </div>
  `;
}

function populateFilterOptions(refs) {
  if (!refs.stage || !refs.counsellor) return;

  const stages = [...new Set(state.leads.map(lead => lead.stage))];
  const counsellors = [...new Set(state.leads.map(lead => lead.counsellor))];

  refs.stage.innerHTML = `
    <option value="all">All stages</option>
    ${stages.map(stage => `<option value="${stage}">${stage}</option>`).join("")}
  `;

  refs.counsellor.innerHTML = `
    <option value="all">All counsellors</option>
    ${counsellors.map(name => `<option value="${name}">${name}</option>`).join("")}
  `;
}

function populateCounsellorInput(refs) {
  if (!refs.createCounsellor) return;
  const counsellors = [...new Set(state.leads.map(lead => lead.counsellor))];
  refs.createCounsellor.innerHTML = `
    <option value="">Assign counsellor</option>
    ${counsellors.map(name => `<option value="${name}">${name}</option>`).join("")}
  `;
}

function buildDynamicStats() {
  const total = state.leads.length;
  const won = state.leads.filter(lead => lead.stage === "Won").length;
  const hot = state.leads.filter(lead => lead.stage === "Hot").length;
  const demo = state.leads.filter(lead => lead.stage === "Demo Booked").length;
  const dueToday = state.leads.filter(lead => lead.stage !== "Won").length;

  return {
    kpis: [
      { label: "Hot Leads", value: String(hot), note: "Need same-day touch" },
      { label: "Demo Booked", value: String(demo), note: "Ready for parent visit" },
      { label: "Open Pipeline", value: String(dueToday), note: "Still in active conversion" }
    ],
    stats: [
      { label: "Total Leads", value: String(total), note: "Current working set" },
      { label: "Active Counselling", value: String(state.leads.filter(lead => ["Fresh", "Counselling", "Hot"].includes(lead.stage)).length), note: "Need counsellor discipline" },
      { label: "Won Admissions", value: String(won), note: `${Math.round((won / Math.max(1, total)) * 100)}% conversion` },
      { label: "Pending Follow-ups", value: String(state.leads.filter(lead => ["Follow-up", "Negotiation", "Demo Booked"].includes(lead.stage)).length), note: "Commercial or revisit pending" }
    ]
  };
}

function buildCounsellorLoad() {
  const counters = new Map();
  state.leads.forEach(lead => {
    const current = counters.get(lead.counsellor) ?? { total: 0, hot: 0, demos: 0, won: 0 };
    current.total += 1;
    if (lead.stage === "Hot") current.hot += 1;
    if (lead.stage === "Demo Booked") current.demos += 1;
    if (lead.stage === "Won") current.won += 1;
    counters.set(lead.counsellor, current);
  });

  return [...counters.entries()].map(([title, counts]) => ({
    title,
    note: `${counts.total} active leads | ${counts.hot} hot | ${counts.demos} demos | ${counts.won} won`
  }));
}

function buildQueue() {
  return state.leads
    .filter(lead => lead.stage !== "Won")
    .slice(0, 4)
    .map(lead => ({
      title: `${lead.student} · ${lead.stage}`,
      note: lead.nextAction
    }));
}

function renderWorkspace(refs) {
  const dynamic = buildDynamicStats();
  renderCards(refs.kpis, dynamic.kpis);
  renderCards(refs.stats, dynamic.stats);
  renderPipeline(refs.pipeline);
  renderSourceList(refs.sources);
  renderTimeline(refs.counsellorLoad, buildCounsellorLoad());
  renderTimeline(refs.queue, buildQueue());
  renderChecklist(refs.checklist);
  renderRules(refs.rules);

  const leads = getFilteredLeads();
  const selectedLead = ensureSelectedLead(leads);
  renderLeadsTable(refs.rows, leads);
  renderSelectedLead(refs.selected, selectedLead);
  populateFilterOptions(refs);
  populateCounsellorInput(refs);

  if (refs.stage) refs.stage.value = state.stage;
  if (refs.counsellor) refs.counsellor.value = state.counsellor;
}

function bindWorkspace(refs) {
  refs.search?.addEventListener("input", event => {
    state.search = event.target.value.trim().toLowerCase();
    renderWorkspace(refs);
  });

  refs.stage?.addEventListener("change", event => {
    state.stage = event.target.value;
    renderWorkspace(refs);
  });

  refs.counsellor?.addEventListener("change", event => {
    state.counsellor = event.target.value;
    renderWorkspace(refs);
  });

  refs.reset?.addEventListener("click", () => {
    state.search = "";
    state.stage = "all";
    state.counsellor = "all";
    state.selectedLeadId = admissionsModuleData.leads[0]?.id ?? null;

    if (refs.search) refs.search.value = "";
    if (refs.stage) refs.stage.value = "all";
    if (refs.counsellor) refs.counsellor.value = "all";

    renderWorkspace(refs);
  });

  refs.rows?.addEventListener("click", event => {
    const row = event.target.closest("[data-lead-id]");
    if (!row) return;
    state.selectedLeadId = row.dataset.leadId;
    renderWorkspace(refs);
  });

  refs.createForm?.addEventListener("submit", event => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const student = String(formData.get("student") || "").trim();
    const parent = String(formData.get("parent") || "").trim();
    const program = String(formData.get("program") || "").trim();
    const source = String(formData.get("source") || "").trim();
    const counsellor = String(formData.get("counsellor") || "").trim();
    const stage = String(formData.get("stage") || "Fresh").trim();
    const nextAction = String(formData.get("nextAction") || "").trim();
    const summary = String(formData.get("summary") || "").trim();

    if (!student || !parent || !program || !source || !counsellor || !nextAction) return;

    const newLead = {
      id: `lead-${student.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${Date.now()}`,
      student,
      parent,
      program,
      source,
      counsellor,
      stage,
      nextAction,
      score: "New intake",
      budget: "To be discussed",
      lastTouch: "Just now",
      campusVisit: "Not scheduled",
      summary: summary || "New enquiry captured from the admissions workspace.",
      tasks: [
        "Call parent and confirm counselling timing",
        "Share course and fee plan",
        "Move stage after first qualified discussion"
      ],
      timeline: [
        "Lead created from admissions workspace",
        `Initial next action: ${nextAction}`
      ]
    };

    state.leads.unshift(newLead);
    state.selectedLeadId = newLead.id;
    event.currentTarget.reset();
    renderWorkspace(refs);
  });

  refs.selected?.addEventListener("click", event => {
    const action = event.target.closest("[data-stage-action]");
    if (!action) return;

    const selectedLead = state.leads.find(lead => lead.id === state.selectedLeadId);
    if (!selectedLead) return;

    selectedLead.stage = action.dataset.stageAction;
    selectedLead.lastTouch = "Just now";
    selectedLead.timeline.unshift(`Stage moved to ${selectedLead.stage}`);
    renderWorkspace(refs);
  });

  refs.selected?.addEventListener("submit", event => {
    const form = event.target.closest("#admissions-note-form");
    if (!form) return;
    event.preventDefault();

    const selectedLead = state.leads.find(lead => lead.id === state.selectedLeadId);
    if (!selectedLead) return;

    const formData = new FormData(form);
    const note = String(formData.get("note") || "").trim();
    const nextAction = String(formData.get("nextAction") || "").trim();

    if (!note && !nextAction) return;

    if (note) {
      selectedLead.timeline.unshift(note);
    }

    if (nextAction) {
      selectedLead.nextAction = nextAction;
      selectedLead.tasks = [nextAction, ...selectedLead.tasks].slice(0, 4);
    }

    selectedLead.lastTouch = "Just now";
    form.reset();
    renderWorkspace(refs);
  });
}

export function initAdmissionsModule() {
  const refs = getRefs();
  if (!refs.rows) return;

  populateFilterOptions(refs);
  populateCounsellorInput(refs);
  bindWorkspace(refs);
  renderWorkspace(refs);
}
