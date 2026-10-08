const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../app.js'), 'utf8');
function extract(name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start >= 0);
  return (source.slice(start - 6, start) === 'async ' ? 'async ' : '') + source.slice(start, source.indexOf('\n}', start) + 2);
}
const button = {};
let posts = 0, errors = 0, closed = 0;
const keys = [];
const context = vm.createContext({
  crypto: require('node:crypto'), loadedResources: new Set(['reports']), state: {},
  FormData: class { get(k) { return { studentId: 'one', transactionDate: '2026-08-01', amount: '1000', method: 'cash' }[k]; } },
  $: () => button, requireStudentPicker: () => true,
  api: async (path, options) => { posts++; keys.push(options.headers['Idempotency-Key']); return {receiptNumber:'receipt'}; },
  fetchAll: async () => { throw Error('offline after save'); },
  closeDetail: () => closed++, renderAll() {}, activateFinanceTab() {}, toast() {},
  showFormError: () => errors++,
});
vm.runInContext(['financeRequestHeaders', 'refreshSavedFinance', 'submitPayment'].map(extract).join('\n'), context);
(async () => {
  const form = {dataset:{}};
  await context.submitPayment({preventDefault(){},currentTarget:form});
  assert.equal(posts, 1);
  assert.equal(closed, 1);
  assert.equal(errors, 0, 'refresh failure must not be shown as posting failure');
  assert.equal(context.loadedResources.has('reports'), false);
  const key = context.financeRequestHeaders(form)['Idempotency-Key'];
  assert.equal(key, keys[0], 'uncertain retries must keep the original key');
  console.log('Financial save feedback, stable retry key and report invalidation passed.');
})().catch(error => { console.error(error); process.exitCode=1; });
