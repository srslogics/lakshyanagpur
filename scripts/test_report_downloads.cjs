// Exercise the actual download handler without accessing production data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../app.js'), 'utf8');
const start = source.indexOf('async function downloadReport(');
const implementation = source.slice(start, source.indexOf('\n}', start) + 2);
const saved = [];
const messages = [];
let requests = [];
let expired = false;
let response;
const fields = {'#report-from':{value:''}, '#report-to':{value:''}, '#report-month':{value:'2026-08'}};
const context = vm.createContext({
  $: selector => fields[selector],
  state: { token: 'synthetic-token', user: {role: 'owner'} },
  apiUrl: path => path,
  fetch: async (path, options) => { requests.push({path, options}); return response; },
  URL: { createObjectURL: () => 'blob:synthetic', revokeObjectURL: () => {} },
  document: {body: {append: () => {}}, createElement: () => ({click() {saved.push(this.download);}, remove() {}})},
  toast: (message, kind) => messages.push({message, kind}),
  setTimeout: callback => callback(), Blob,
  expireSession: () => { expired = true; },
});
vm.runInContext(implementation, context);
(async () => {
  for (const name of ['students', 'fees', 'attendance', 'audit']) {
    response = {ok: true, headers: {get: header => header === 'content-type' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' : `attachment; filename="lakshya-${name}.xlsx"`}, blob: async () => new Blob(['synthetic'])};
    const button = {disabled: false};
    await context.downloadReport(name, button);
    assert.equal(button.disabled, false);
    assert.equal(saved.at(-1), `lakshya-${name}.xlsx`);
    assert.equal(requests.at(-1).path, `/api/reports/export/${name}?format=xlsx`);
    assert.equal(requests.at(-1).options.cache, 'no-store');
    assert.equal(requests.at(-1).options.headers.Authorization, 'Bearer synthetic-token');
  }
  response = {ok: true, headers: {get: () => 'text/html'}};
  await context.downloadReport('students', {disabled: false});
  assert.equal(saved.length, 4, 'never save HTML/errors as a workbook');
  assert.equal(messages.at(-1).kind, 'error');
  response = {ok: false, status: 401, json: async () => ({detail: 'Unauthorized'})};
  const button = {disabled: false};
  await context.downloadReport('students', button);
  assert.equal(expired, true);
  assert.equal(button.disabled, false);
  assert.match(messages.at(-1).message, /session expired/);
  fields['#report-from'].value = '2026-08-31';
  fields['#report-to'].value = '2026-08-01';
  requests = [];
  await context.downloadReport('payments', {disabled:false, dataset:{reportPeriod:'range'}});
  assert.equal(requests.length, 0, 'invalid date range must not request a report');
  assert.match(messages.at(-1).message, /From date/);
  context.state.user.role = 'demo';
  requests = [];
  await context.downloadReport('students', button);
  assert.equal(requests.length, 0, 'demo exports must never request real records');
  console.log('All four report download handlers, error handling and demo isolation passed.');
})().catch(error => {console.error(error); process.exitCode = 1;});
