// Exercise the actual frontend calculations with independent financial examples.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../app.js'), 'utf8');
function implementation(name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start >= 0, name);
  return source.slice(start, source.indexOf('\n}', start) + 2);
}
const context = vm.createContext({ state: { agreements: [], payments: [] }, STUDENT_BATCH_ORDER: ['Essential', 'Tatva'], needsPaymentReview: () => false });
vm.runInContext(['studentBatchKey', 'studentDirectoryGroup', 'studentPayments', 'studentAccount', 'financeTotals'].map(implementation).join('\n'), context);
context.state.agreements = [
  { id: 'current', studentId: 'one', agreedAmount: 40000, legacyRegistrationTotal: 5000, status: 'active', studentStatus: 'active' },
  { id: 'old', studentId: 'one', agreedAmount: 20000, status: 'inactive', studentStatus: 'active' },
  { id: 'opted-out', studentId: 'two', agreedAmount: 10000, status: 'inactive', studentStatus: 'inactive' },
  { id: 'overpaid', studentId: 'three', agreedAmount: 10000, status: 'active', studentStatus: 'active' },
];
context.state.payments = [
  { studentId: 'one', feeAgreementId: 'current', type: 'payment', amount: 12000, signedAmount: 12000, receivedAmount: 12000, status: 'posted', reconciliationStatus: 'ready' },
  { studentId: 'one', feeAgreementId: 'current', type: 'refund', amount: 2000, signedAmount: -2000, receivedAmount: -2000, status: 'posted', reconciliationStatus: 'ready' },
  { studentId: 'one', feeAgreementId: 'current', type: 'balance_credit', amount: 5000, signedAmount: 5000, receivedAmount: 0, status: 'posted', reconciliationStatus: 'ready' },
  { studentId: 'one', feeAgreementId: 'old', type: 'payment', amount: 20000, signedAmount: 20000, receivedAmount: 20000, status: 'staged', reconciliationStatus: 'ready' },
  { studentId: 'one', feeAgreementId: 'current', type: 'payment', amount: 9000, signedAmount: 0, receivedAmount: 0, status: 'staged', reconciliationStatus: 'review' },
  { studentId: 'two', feeAgreementId: 'opted-out', type: 'payment', amount: 1000, signedAmount: 1000, receivedAmount: 1000, status: 'posted', reconciliationStatus: 'ready' },
  { studentId: 'three', feeAgreementId: 'overpaid', type: 'payment', amount: 11000, signedAmount: 11000, receivedAmount: 11000, status: 'posted', reconciliationStatus: 'ready' },
];
const totals = context.financeTotals();
assert.equal(totals.agreed, 50000);
assert.equal(totals.collected, 42000, 'historical collections counted once; refunds deducted; credits excluded');
assert.equal(totals.outstanding, 25000, 'old agreements and overpayments do not offset another account due');
assert.equal(totals.dueAccounts, 1);
assert.equal(context.studentAccount(context.state.agreements[0]).paid, 10000);
assert.equal(context.studentDirectoryGroup({ status: 'active', batch: 'Essential' }), 'Essential');
assert.equal(context.studentDirectoryGroup({ status: 'draft', batch: 'Essential' }), 'Drafts');
assert.equal(context.studentDirectoryGroup({ status: 'inactive', batch: 'Essential' }), 'Opted out');

// Refresh requests are coalesced and bounded; session changes cannot restore old data.
const nodes = new Map();
context.$ = key => { if (!nodes.has(key)) nodes.set(key, {}); return nodes.get(key); };
context.renderCore = () => {};
context.renderNavigationCounts = () => {};
vm.runInContext('let workspaceUpdatedAt = 0; let workspaceRefresh = null; let navigationCounts = {};', context);
vm.runInContext(['loadInitialWorkspace', 'refreshOverview'].map(name => `async ${implementation(name)}`).join('\n'), context);
(async () => {
  context.state.token = 'session-a'; context.state.user = { role: 'owner' };
  let calls = 0;
  let resolveRequest;
  context.api = () => { calls++; return new Promise(resolve => { resolveRequest = resolve; }); };
  const first = context.refreshOverview(true);
  const second = context.refreshOverview(true);
  assert.equal(calls, 1);
  resolveRequest({ students: [{ id: 'fresh' }] });
  await Promise.all([first, second]);
  assert.equal(context.state.students[0].id, 'fresh');
  await context.refreshOverview();
  assert.equal(calls, 1, 'no polling or repeated fresh bootstrap');
  const stale = context.refreshOverview(true);
  context.state.token = 'session-b';
  resolveRequest({ students: [{ id: 'previous-user' }] });
  await stale;
  assert.equal(context.state.students[0].id, 'fresh');
  context.api = async () => { throw new Error('offline'); };
  await assert.rejects(context.refreshOverview(true), /offline/);
  assert.match(nodes.get('#dashboard-sync').textContent, /previously loaded/);
  assert.equal(nodes.get('#refresh-dashboard').disabled, false);
  console.log('Dashboard totals, student scope, refresh coalescing, and failure checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
