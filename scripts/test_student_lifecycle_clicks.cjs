const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../app.js'), 'utf8');
const start = source.indexOf('  document.addEventListener("click", event => {', source.indexOf('function bindEvents()'));
assert.ok(start >= 0);
const end = source.indexOf('\n  });', start) + 6;
let click;
const opened = [];
const context = {
  document: { addEventListener: (_, handler) => { click = handler; } },
  openStudent: id => opened.push(id), closeAccountMenu: () => {},
};
vm.runInNewContext(source.slice(start, end), context);
const form = { dataset: { studentId: 'test-student' } };
// Both mouse and keyboard-generated clicks bubble from controls to the form.
for (const control of ['reason textarea', 'confirm submit button']) {
  click({ target: { closest: selector => selector === '[data-student-id]' ? form : null } });
  assert.equal(opened.length, 0, `${control} must not replace the lifecycle form`);
}
for (const label of ['recent student', 'directory student']) {
  const button = { dataset: { studentId: label } };
  click({ target: { closest: selector => ['[data-student-id]', 'button[type="button"][data-student-id]'].includes(selector) ? button : null } });
}
assert.deepEqual(opened, ['recent student', 'directory student']);
console.log('Lifecycle form clicks preserved; student navigation still works.');
