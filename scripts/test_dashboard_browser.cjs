// Requires playwright-core; set CHROME_PATH to a Chrome executable. All API data is synthetic/local.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright-core');
const root = path.resolve(__dirname, '..');
const workspace = {
  students: ['active', 'active', 'draft', 'inactive'].map((status, index) => ({
    id: `student-${index}`, fullName: `Test Student ${index + 1}`, status,
    admissionNumber: `TEST-${index}`, batch: 'Essential', program: 'JEE',
    dataQualityStatus: 'ready', enrollmentDate: '2026-09-01',
  })),
  agreements: [{ id: 'agreement', studentId: 'student-0', studentName: 'Test Student 1', agreedAmount: 2500000, status: 'active', studentStatus: 'active' }],
  payments: [{ id: 'payment', studentId: 'student-0', feeAgreementId: 'agreement', amount: 100000, signedAmount: 100000, receivedAmount: 100000, status: 'posted', type: 'payment', reconciliationStatus: 'ready', date: '2026-09-01' }],
  installments: [], leads: [], admissionsMeta: { stageOrder: [] },
  navigationCounts: { inventory: 7, examinations: 3 },
};
const server = http.createServer((req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  if (pathname.startsWith('/api/') || pathname === '/health') {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(pathname === '/api/workspace/bootstrap' ? workspace : {}));
    return;
  }
  const file = path.join(root, pathname === '/operations' ? 'index.html' : pathname);
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    res.writeHead(404); res.end(); return;
  }
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png' };
  res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, serviceWorkers: 'block' });
    await context.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
    await context.addInitScript(() => {
      sessionStorage.setItem('lakshya_token', 'local-test');
      sessionStorage.setItem('lakshya_user', JSON.stringify({ id: 'owner', fullName: 'Test Owner', role: 'owner' }));
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`http://127.0.0.1:${server.address().port}/operations`);
    await page.locator('#app-shell:not(.hidden)').waitFor();
    await page.locator('[data-push-later]').click();
    assert.deepEqual(await page.locator('#dashboard-metrics .metric-value').allTextContents(), ['2', '₹25,00,000', '₹1,00,000', '₹24,00,000']);
    assert.equal(await page.locator('#nav-inventory-count').textContent(), '7');
    assert.equal(await page.locator('#nav-examinations-count').textContent(), '3');
    await page.locator('.nav-item[data-view="finance"]').click();
    assert.deepEqual(await page.locator('#finance-metrics strong').allTextContents(), ['₹24,00,000', '₹1,00,000', '1']);
    await page.locator('.nav-item[data-view="dashboard"]').click();
    if (process.env.DASHBOARD_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.DASHBOARD_SCREENSHOT_DIR, 'dashboard-desktop.png'), fullPage: true, animations: 'disabled' });
    await page.locator('.nav-item[data-view="students"]').click();
    assert.equal(await page.locator('[data-student-batch="Essential"] strong').textContent(), '2');
    assert.equal(await page.locator('[data-student-batch="Drafts"] strong').textContent(), '1');
    await page.locator('.nav-item[data-view="dashboard"]').click();
    workspace.students[2].status = 'active';
    await page.locator('#refresh-dashboard').click();
    await page.waitForFunction(() => document.querySelector('#dashboard-metrics .metric-value').textContent === '3');
    await page.setViewportSize({ width: 390, height: 844 });
    if (process.env.DASHBOARD_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.DASHBOARD_SCREENSHOT_DIR, 'dashboard-mobile.png'), fullPage: true, animations: 'disabled' });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'mobile page must not overflow');
    for (const value of await page.locator('#dashboard-metrics .metric-value').all()) {
      assert.ok(await value.evaluate(node => node.scrollWidth <= node.clientWidth), 'exact financial total fits its card');
    }
    await page.evaluate(() => { state.user = { role: 'counsellor' }; renderDashboard(); });
    assert.equal(await page.locator('#dashboard-metrics .metric-label').textContent(), 'Enquiries · all stages');
    assert.equal(await page.locator('#finance-pulse-body').isVisible(), false);
    assert.equal(await page.locator('#program-chart').isVisible(), false);
    assert.deepEqual(errors, []);
    console.log('Dashboard browser checks passed: totals, sidebar counts, draft separation, refresh, and mobile layout.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; }).finally(() => server.close());
