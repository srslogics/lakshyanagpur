const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('app.js', 'utf8');
const elements = new Map();
const context = vm.createContext({
  state: {timetable: {}, sessions: [{status:'scheduled', startsAt:'2026-08-01T09:00:00Z'}]},
  timetableSelectedDate: '2026-09-23', timetableView:'schedule',
  $: id => { if (!elements.has(id)) elements.set(id, {setAttribute(){}}); return elements.get(id); },
  indiaDateKey: value => new Date(value).toISOString().slice(0,10),
  asInstant: value => new Date(value), esc: String,
  timetableDateLabel: String, emptyState: (_, title) => title,
  activateTimetableView(){},
});
vm.runInContext(source.slice(source.indexOf('function renderTimetable()'), source.indexOf('function activateTimetableView(')), context);
vm.runInContext(source.slice(source.indexOf('function isDirectorAttendance('), source.indexOf('function renderAttendance(')), context);
context.renderTimetable();
assert.equal(elements.get('#timetable-date-picker').value, '2026-09-23');
assert.match(elements.get('#timetable-date-tabs').innerHTML, /2026-09-27/);
assert.doesNotMatch(elements.get('#timetable-date-tabs').innerHTML, /2026-08/);
assert.equal(elements.get('#operations-timetable-grid').innerHTML, 'No classes scheduled');
assert.equal(context.isFacultyAttendance({role:'faculty'}), true);
assert.equal(context.isFacultyAttendance({role:'faculty', designation:'Director'}), false);
assert.equal(context.isFacultyAttendance({role:'staff'}), false);
context.timetableSelectedDate = '2027-01-02';
context.renderTimetable();
assert.equal(elements.get('#timetable-date-picker').value, '2027-01-02');
assert.match(elements.get('#timetable-date-tabs').innerHTML, /2027-01-03/);
console.log('Faculty classification and cross-month/year timetable navigation passed.');
