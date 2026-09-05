"use strict";

const payrollMoney = value => value == null ? "Not set" : new Intl.NumberFormat("en-IN", {
  style:"currency", currency:"INR", minimumFractionDigits:2, maximumFractionDigits:2,
}).format(Number(value));
const payrollDuration = value => {
  const minutes = Math.max(0, Number(value) || 0);
  return minutes ? `${Math.floor(minutes / 60)}h ${String(minutes % 60).padStart(2, "0")}m` : "—";
};

function payrollDemoData() {
  payrollMonth ||= indiaDateKey(new Date()).slice(0, 7);
  const [year, month] = payrollMonth.split("-").map(Number);
  const days = new Date(year, month, 0).getDate();
  return {month:payrollMonth, daysInMonth:days, canFinalizeMonth:false,
    summary:{staffCount:1, finalizedCount:0, reviewCount:1, netPayable:"0"},
    rows:[{personKey:"demo", fullName:"Demo staff member", designation:"Staff", deviceIds:["DEMO"], presentDays:0, unrecordedDays:0, explicitAbsentDays:0, absenceLimit:0, presentDates:[], unrecordedDates:[], dailyWorkLog:[], totalWorkMinutes:0, overtimeMinutes:0, averageWorkMinutes:0, status:"not_prepared", calculation:null, attendanceChanged:false}]};
}

async function loadPayrollMonth() {
  payrollMonth ||= indiaDateKey(new Date()).slice(0, 7);
  const month = payrollMonth, sequence = ++payrollLoadSequence;
  $("#payroll").setAttribute("aria-busy", "true");
  $("#payroll-error").classList.add("hidden");
  try {
    const data = state.user?.role === "demo" ? payrollDemoData() : await api(`/api/payroll/bootstrap?month=${encodeURIComponent(month)}`);
    if (sequence !== payrollLoadSequence || month !== payrollMonth) return;
    payrollData = data;
    renderPayroll();
  } catch (error) {
    if (sequence === payrollLoadSequence) {
      payrollData = null;
      renderPayroll();
      $("#payroll-error").textContent = error.message;
      $("#payroll-error").classList.remove("hidden");
    }
    throw error;
  } finally {
    if (sequence === payrollLoadSequence) $("#payroll").removeAttribute("aria-busy");
  }
}

function payrollStatus(row) {
  if (row.attendanceChanged) return '<span class="status status-review">Attendance changed</span>';
  if (row.status === "finalized") return '<span class="status status-active">Finalised</span>';
  return `<span class="status status-review">${row.status === "draft" ? "Draft" : "Not prepared"}</span>`;
}

function renderPayroll() {
  if (!$("#payroll")) return;
  payrollMonth ||= indiaDateKey(new Date()).slice(0, 7);
  $("#payroll-month").value = payrollMonth;
  const data = payrollData;
  $("#payroll-period").textContent = data ? `${data.daysInMonth} calendar days` : "";
  $("#payroll-metrics").innerHTML = data ? compactMetrics([
    {label:"Staff members", value:data.summary.staffCount}, {label:"Prepared net payable", value:payrollMoney(data.summary.netPayable)},
    {label:"Recorded work time", value:payrollDuration(data.rows.reduce((sum, row) => sum + Number(row.totalWorkMinutes || 0), 0))},
    {label:"Finalised", value:data.summary.finalizedCount},
  ]) : "";
  const query = $("#payroll-search").value.trim().toLowerCase();
  const rows = (data?.rows || []).filter(row => row.fullName.toLowerCase().includes(query));
  $("#payroll-summary").textContent = data ? `${rows.length} staff · ${data.canFinalizeMonth ? "Ready to finalise" : "Draft estimates"}` : "Payroll is not loaded. Refresh attendance to retry.";
  const action = row => {
    const label = !canAccess("payroll", "edit") ? "View" : row.attendanceChanged ? "Review changes" : row.status === "finalized" ? "View final" : row.calculation ? "Review draft" : "Prepare";
    return `<button type="button" class="button button-secondary button-small payroll-row-action" data-payroll-person="${esc(row.personKey)}">${label}</button>`;
  };
  const attendance = row => `${row.presentDays} recorded · ${row.explicitAbsentDays || 0} absent · ${payrollDuration(row.totalWorkMinutes)} worked`;
  const attendanceCell = row => `<span class="payroll-attendance"><span><strong>${esc(row.presentDays)}</strong> recorded <i>·</i> <strong>${esc(row.explicitAbsentDays || 0)}</strong> absent</span><small>${payrollDuration(row.totalWorkMinutes)} worked${row.overtimeMinutes ? ` · ${payrollDuration(row.overtimeMinutes)} OT` : ""}</small></span>`;
  const moneyCell = value => value == null ? '<span class="payroll-muted">Not set</span>' : payrollMoney(value);
  $("#payroll-table-body").innerHTML = rows.length ? rows.map(row => {
    const c = row.calculation;
    return `<tr><td>${studentPrimary(row.fullName, row.designation)}</td><td>${attendanceCell(row)}</td><td class="payroll-number">${moneyCell(c?.monthlySalary)}</td><td class="payroll-number">${c ? `${c.absentDays} / ${c.payableDays}` : '<span class="payroll-muted">—</span>'}</td><td class="payroll-number">${c ? payrollMoney(c.advanceGiven) : '<span class="payroll-muted">—</span>'}</td><td class="payroll-number payroll-net"><strong>${c ? payrollMoney(c.netPayable) : '<span class="payroll-muted">—</span>'}</strong></td><td>${action(row)}</td></tr>`;
  }).join("") : `<tr><td colspan="7">${emptyState("wallet", "No matching staff", "Staff biometric mappings appear here after attendance import. Directors are separate and are not included.")}</td></tr>`;
  $("#payroll-mobile-list").innerHTML = rows.length ? rows.map(row => {
    const c = row.calculation;
    return `<article class="mobile-record-card"><div class="mobile-record-card-head"><div><h3>${esc(row.fullName)}</h3><p>${esc(row.designation)}</p></div>${payrollStatus(row)}</div><p>${esc(attendance(row))}</p><div class="mobile-record-meta"><div><span>Monthly salary</span><strong>${payrollMoney(c?.monthlySalary)}</strong></div><div><span>Absent / payable</span><strong>${c ? `${c.absentDays} / ${c.payableDays} days` : "—"}</strong></div><div><span>Advance</span><strong>${c ? payrollMoney(c.advanceGiven) : "—"}</strong></div><div><span>Net payable</span><strong>${c ? payrollMoney(c.netPayable) : "—"}</strong></div></div>${action(row)}</article>`;
  }).join("") : emptyState("wallet", "No matching staff");
}

// Exact integer-paise preview, matching server rounding without truncating the daily rate.
function payrollPreview(salary, absent, advance, days) {
  const cents = value => {
    if (!/^\d+(\.\d{1,2})?$/.test(value)) throw new Error("Enter valid amounts");
    const [whole, fraction = ""] = value.split(".");
    return BigInt(whole) * 100n + BigInt(fraction.padEnd(2, "0"));
  };
  if (!/^\d+(\.5)?$/.test(absent) || Number(absent) > days) throw new Error("Enter absent days in whole or half days");
  const amount = cents(salary), deduction = cents(advance), count = BigInt(days);
  const paid = days - Number(absent);
  const gross = (amount * BigInt(paid) * 2n + count) / (2n * count);
  return {payableDays:paid, perDayRate:Number(amount) / 100 / days, payableAmount:Number(gross) / 100, netPayable:Number(gross - deduction) / 100};
}

function openPayrollEntry(row) {
  const month = payrollData.month, days = payrollData.daysInMonth;
  const editable = canAccess("payroll", "edit") && state.user?.role !== "demo";
  const locked = row.status === "finalized" || !editable;
  const c = row.calculation;
  const saved = row.status === "finalized" ? row.savedAttendance : null;
  const dates = saved || row;
  const dateList = values => values.length ? values.map(value => esc(formatDate(value))).join(", ") : "None";
  const workLog = dates.dailyWorkLog || [];
  const workStatus = value => ({present:"Present", absent:"Absent", half_day:"Half day", weekly_off:"Weekly off", weekly_off_present:"Worked weekly off", weekly_off_half_day:"Half day on weekly off", holiday:"Holiday", leave:"Leave"})[value] || String(value || "Unrecorded").replaceAll("_", " ");
  openDrawer(`Payroll · ${row.fullName}`, `<form class="auth-form" id="payroll-entry-form">
    <p>${esc(month)} · ${days} calendar days · ${esc(row.designation)}</p>
    ${row.attendanceChanged ? '<div class="inline-notice">Biometric attendance changed since this calculation was saved. Review deductions; finalised amounts stay unchanged until explicitly reopened.</div>' : ""}
    <details class="payroll-evidence" open><summary>${payrollDuration(dates.totalWorkMinutes)} recorded work time · ${dates.explicitAbsentDays || 0} device-marked absent</summary><div class="payroll-work-summary"><span><small>Days with duration</small><strong>${dates.workDaysWithDuration || 0}</strong></span><span><small>Average work time</small><strong>${payrollDuration(dates.averageWorkMinutes)}</strong></span><span><small>Overtime recorded</small><strong>${payrollDuration(dates.overtimeMinutes)}</strong></span></div>${workLog.length ? `<div class="payroll-work-log">${workLog.map(item => `<div><time>${esc(formatDate(item.date))}</time><span>${esc(workStatus(item.status))}</span><strong>${payrollDuration(item.workMinutes)}</strong>${item.overtimeMinutes ? `<small>${payrollDuration(item.overtimeMinutes)} OT</small>` : ""}</div>`).join("")}</div>` : `<p><strong>Recorded:</strong> ${dateList(dates.presentDates)}</p>`}<p><strong>No device record on completed dates:</strong> ${dateList(dates.unrecordedDates)}</p><p>Device-marked absences are suggested below. Missing punches still need review and are never deducted automatically.</p></details>
    <fieldset ${locked ? "disabled" : ""} class="payroll-fields">
      <div class="form-pair"><label class="field"><span>Monthly salary (₹)</span><input name="monthlySalary" type="number" inputmode="decimal" min="0" max="999999999999.99" step="0.01" value="${esc(c?.monthlySalary ?? row.salarySuggestion ?? "")}" required></label><label class="field"><span>Advance given this month (₹)</span><input name="advanceGiven" type="number" inputmode="decimal" min="0" max="999999999999.99" step="0.01" value="${esc(c?.advanceGiven ?? "0")}" required></label></div>
      ${!c && row.salarySuggestion != null ? '<small>Salary carried forward from the most recent earlier payroll. Advance is not carried forward.</small>' : ""}
      <label class="field"><span>Confirmed absent days</span><input name="absentDays" type="number" inputmode="decimal" min="0" max="${row.absenceLimit}" step="0.5" value="${esc(c?.absentDays ?? row.explicitAbsentDays ?? "")}" required aria-describedby="payroll-absence-help"><small id="payroll-absence-help">The device report suggests ${esc(row.explicitAbsentDays || 0)} absent days. Confirm it after checking weekly offs, paid leave and missing imports.</small></label>
      <label class="field"><span>Payroll note (optional)</span><textarea name="notes" maxlength="1000" rows="2" placeholder="Leave adjustment or advance reference">${esc(row.notes || "")}</textarea></label>
    </fieldset>
    <div id="payroll-calculation" class="payroll-calculation" aria-live="polite"></div>
    ${!locked ? '<label class="payroll-confirm"><input type="checkbox" name="attendanceConfirmed"><span>I have checked the absence total, paid days and advance for this month.</span></label>' : ""}
    ${formError("payroll-entry-error")}
    ${!locked ? `<div class="payroll-actions"><button class="button button-secondary" type="submit" name="action" value="draft">Save draft</button><button class="button button-primary" type="submit" name="action" value="finalize" ${payrollData.canFinalizeMonth ? "" : "disabled"}>Finalise payroll</button></div>${!payrollData.canFinalizeMonth ? '<small>Finalisation is available after the month ends. This month’s amount is a full-month estimate.</small>' : ""}` : ""}
    <small>Finalising records payroll only. It does not make a payment.</small>
  </form>${row.status === "finalized" && editable ? '<form id="payroll-reopen-form" class="auth-form payroll-reopen"><label class="field"><span>Reason to reopen</span><input name="reason" minlength="3" maxlength="1000" required></label><button type="submit" class="button button-secondary">Reopen for correction</button></form>' : ""}`);
  const form = $("#payroll-entry-form");
  const update = () => {
    try {
      const result = payrollPreview(form.elements.monthlySalary.value, form.elements.absentDays.value, form.elements.advanceGiven.value, days);
      $("#payroll-calculation").innerHTML = compactMetrics([{label:"Payable days", value:result.payableDays}, {label:"Per-day rate (approx.)", value:payrollMoney(result.perDayRate)}, {label:"Payable amount", value:payrollMoney(result.payableAmount)}, {label:"Net payable", value:payrollMoney(result.netPayable)}]) + (result.netPayable < 0 ? '<p>Advance exceeds earned pay. This negative balance is shown exactly as calculated, not paid or carried forward automatically.</p>' : "");
    } catch { $("#payroll-calculation").textContent = "Enter salary and confirmed absent days to see the calculation."; }
  };
  form.addEventListener("input", update);
  update();
  let saving = false;
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (locked || saving || !form.reportValidity()) return;
    const finalize = event.submitter?.value === "finalize";
    if (finalize && !form.elements.attendanceConfirmed.checked) {
      showFormError("#payroll-entry-error", new Error("Confirm the absence total and advance before finalising.")); return;
    }
    const data = new FormData(form);
    saving = true;
    $$('button[type="submit"]', form).forEach(button => { button.disabled = true; });
    try {
      await api(`/api/payroll/${encodeURIComponent(month)}/staff/${encodeURIComponent(row.personKey)}`, {method:"PUT", body:JSON.stringify({
        monthlySalary:data.get("monthlySalary"), advanceGiven:data.get("advanceGiven"), absentDays:Number(data.get("absentDays")),
        notes:data.get("notes"), attendanceFingerprint:row.attendanceFingerprint, version:row.version,
        attendanceConfirmed:form.elements.attendanceConfirmed.checked, finalize,
      })});
      closeDetail();
      toast(finalize ? "Payroll finalised. No payment was made." : "Payroll draft saved.");
      await loadPayrollMonth().catch(() => toast("Saved. Refresh payroll to reload the register.", "error"));
    } catch (error) { showFormError("#payroll-entry-error", error); }
    finally {
      saving = false;
      $$('button[type="submit"]', form).forEach(button => {button.disabled = button.value === "finalize" && !payrollData?.canFinalizeMonth;});
    }
  });
  $("#payroll-reopen-form")?.addEventListener("submit", async event => {
    event.preventDefault();
    if (saving) return;
    saving = true;
    const button = $('button', event.currentTarget); button.disabled = true;
    try {
      await api(`/api/payroll/${encodeURIComponent(row.id)}/reopen`, {method:"POST", body:JSON.stringify({reason:new FormData(event.currentTarget).get("reason"), version:row.version})});
      closeDetail();
      toast("Payroll reopened. The correction is recorded in the audit history.");
      await loadPayrollMonth().catch(() => toast("Reopened. Refresh payroll to reload.", "error"));
    } catch (error) { toast(error.message, "error"); }
    finally { saving = false; button.disabled = false; }
  });
}

function bindPayrollEvents() {
  $("#payroll-month").addEventListener("change", async event => {
    if (!event.target.value || !event.target.checkValidity()) return;
    payrollMonth = event.target.value;
    payrollData = null; renderPayroll();
    await loadPayrollMonth().catch(() => {});
  });
  $("#payroll-refresh").addEventListener("click", () => loadPayrollMonth().catch(() => {}));
  $("#payroll-search").addEventListener("input", renderPayroll);
  $("#payroll").addEventListener("click", event => {
    const key = event.target.closest("[data-payroll-person]")?.dataset.payrollPerson;
    const row = payrollData?.rows.find(item => item.personKey === key);
    if (row) openPayrollEntry(row);
  });
}
