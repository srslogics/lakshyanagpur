import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../app.js", import.meta.url), "utf8");
const rendering = source.slice(source.indexOf("function isDirectorAttendance("), source.indexOf("function activateAttendanceTab("));
assert.ok(rendering.includes("function renderAttendance("));

function render(records, selectedDate = "2026-09-02") {
  const elements = new Map();
  const context = vm.createContext({
    state: { attendanceSessions: [], staffAttendance: { records } },
    attendanceRegisterFilter: "current",
    staffAttendanceDate: selectedDate,
    $: selector => {
      if (!elements.has(selector)) elements.set(selector, {});
      return elements.get(selector);
    },
    asInstant: value => new Date(value),
    indiaDateKey: value => new Date(value).toISOString().slice(0, 10),
    formatDate: value => value,
    formatInstantDate: value => value || "—",
    classTime: value => value || "—",
    collectionWindow: (_, rows) => ({ rows, shown: rows.length, total: rows.length }),
    compactMetrics: values => JSON.stringify(values),
    esc: value => String(value ?? ""),
    emptyState: (_, heading) => heading,
    settingsAccountLabel: role => role,
  });
  vm.runInContext(`${rendering}\nrenderAttendance();`, context);
  return elements;
}

const director = { fullName: "Vinay Barhate", designation: "Director", role: "staff", attendanceGroup: "directors", deviceUserId: "003", date: "2026-09-02", arrivalAt: "2026-09-02T06:37:00Z", departureAt: "2026-09-02T09:18:00Z" };
const staff = Array.from({ length: 7 }, (_, index) => ({ fullName: `Employee ${index}`, role: "staff", attendanceGroup: "staff", deviceUserId: String(index + 10), date: "2026-09-02", arrivalAt: "2026-09-02T05:00:00Z", departureAt: null }));

for (const person of [director, { ...director, attendanceGroup: undefined }, { ...director, attendanceGroup: undefined, designation: null, role: "director" }]) {
  const elements = render([...staff, person]);
  for (const suffix of ["table-body", "mobile-list"]) {
    assert.match(elements.get(`#director-attendance-${suffix}`).innerHTML, /Vinay Barhate/);
    assert.doesNotMatch(elements.get(`#staff-attendance-${suffix}`).innerHTML, /Vinay Barhate/);
    assert.doesNotMatch(elements.get(`#director-attendance-${suffix}`).innerHTML, /Employee/);
  }
  assert.equal(elements.get("#staff-attendance-count").textContent, "7 staff members");
  assert.equal(elements.get("#director-attendance-count").textContent, "1 director");
  const metrics = JSON.parse(elements.get("#staff-attendance-metrics").innerHTML);
  assert.equal(metrics[0].value, "7");
  assert.equal(metrics[1].value, "0"); // The director's completed shift is not a staff shift.
  assert.equal(metrics[2].value, "7");
  assert.equal(metrics[3].value, staff[0].arrivalAt);
}

const emptyDay = render([...staff, director], "2026-09-01");
assert.equal(emptyDay.get("#staff-attendance-count").textContent, "0 staff members");
assert.equal(emptyDay.get("#director-attendance-count").textContent, "0 directors");
assert.match(emptyDay.get("#director-attendance-table-body").innerHTML, /No director attendance/);
assert.equal(render(staff).get("#director-attendance-surface").hidden, true);
assert.equal(render([director]).get("#staff-attendance-count").textContent, "0 staff members");
assert.equal(render([]).get("#director-attendance-surface").hidden, true);
console.log("Attendance group rendering checks passed (desktop, mobile, counts, legacy data, empty dates).");
