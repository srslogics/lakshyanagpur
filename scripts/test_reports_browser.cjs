// REPORT_FIXTURE_DIR points to the synthetic workbooks emitted by test_report_exports.py.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright-core');
const root = path.resolve(__dirname, '..');
const fixtures = process.env.REPORT_FIXTURE_DIR;
assert.ok(fixtures, 'Set REPORT_FIXTURE_DIR to the synthetic report test outputs');
const catalog = JSON.parse(fs.readFileSync(path.join(fixtures, 'catalog.json'), 'utf8'));
const exported = [];
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const report = catalog.find(item => url.pathname === `/api/reports/export/${item.id}`)?.id;
  if (report) {
    exported.push({report, format:url.searchParams.get('format'), from:url.searchParams.get('from'), to:url.searchParams.get('to'), month:url.searchParams.get('month'), authorized:req.headers.authorization === 'Bearer synthetic-test'});
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename="lakshya-${report}.xlsx"`);
    res.end(fs.readFileSync(path.join(fixtures, `${report}.xlsx`)));
    return;
  }
  if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(url.pathname === '/api/reports/overview' ? {exports:catalog, metrics:{students:0, recordedPayments:0}, leadFunnel:[], attendance:[], recentAudit:[]} : {}));
    return;
  }
  const filename = path.join(root, url.pathname === '/operations' ? 'index.html' : url.pathname);
  if (!filename.startsWith(root + path.sep) || !fs.existsSync(filename) || !fs.statSync(filename).isFile()) {
    res.writeHead(404); res.end(); return;
  }
  res.setHeader('Content-Type', {'.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.png':'image/png'}[path.extname(filename)] || 'application/octet-stream');
  fs.createReadStream(filename).pipe(res);
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({headless:true, ...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {})});
  try {
    const context = await browser.newContext({acceptDownloads:true, serviceWorkers:'block'});
    await context.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
    await context.addInitScript(() => {
      sessionStorage.setItem('lakshya_token', 'synthetic-test');
      sessionStorage.setItem('lakshya_user', JSON.stringify({id:'test-owner', fullName:'Test Owner', role:'owner'}));
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`http://127.0.0.1:${server.address().port}/operations`);
    await page.locator('#app-shell:not(.hidden)').waitFor();
    await page.locator('[data-push-later]').click();
    await page.locator('.nav-item[data-view="reports"]').click();
    await page.locator('[data-report-export="students"]').waitFor();
    assert.match(await page.locator('#report-month').inputValue(), /^\d{4}-\d{2}$/);
    await page.locator('#report-search').fill('work time');
    assert.equal(await page.locator('[data-report-export]').count(), 1);
    await page.locator('#report-search').fill('');
    await page.locator('#report-module').selectOption('finance');
    assert.equal(await page.locator('[data-report-export]').count(), 3);
    await page.locator('#report-module').selectOption('');
    await page.locator('#report-month').fill('2026-08');
    for (const {id:report} of catalog) {
      console.log(`Checking download: ${report}`);
      const pending = page.waitForEvent('download', {timeout:10000}).catch(async error => {
        console.error(await page.locator('body').innerText());
        throw error;
      });
      await page.locator(`[data-report-export="${report}"]`).click();
      const download = await pending;
      assert.equal(download.suggestedFilename(), `lakshya-${report}.xlsx`);
      assert.equal(await download.failure(), null);
      const downloaded = fs.readFileSync(await download.path());
      assert.deepEqual(downloaded, fs.readFileSync(path.join(fixtures, `${report}.xlsx`)));
      await page.locator(`[data-report-export="${report}"]:enabled`).waitFor();
      // Chrome throttles bursts of ten automatic downloads per second.
      await page.waitForTimeout(1100);
    }
    assert.equal(exported.length, catalog.length);
    assert.ok(exported.every(item => item.format === 'xlsx' && item.authorized));
    assert.equal(exported.find(item => item.report === 'payroll').month, '2026-08');
    await page.locator('#report-from').fill('2026-08-01');
    await page.locator('#report-to').fill('2026-08-31');
    for (const report of ['payments', 'students']) {
      const pending = page.waitForEvent('download');
      await page.locator(`[data-report-export="${report}"]`).click();
      await pending;
      await page.locator(`[data-report-export="${report}"]:enabled`).waitFor();
      assert.equal(exported.at(-1).from, report === 'payments' ? '2026-08-01' : null);
    }
    for (const width of [1280, 390, 320]) {
      await page.setViewportSize({width, height:900});
      await page.locator('.report-downloads').scrollIntoViewIfNeeded();
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true, `No horizontal overflow at ${width}px`);
      await page.screenshot({path:path.join(fixtures, `reports-${width}.png`), fullPage:true});
    }
    assert.deepEqual(errors, []);
    console.log(`Browser downloaded all ${catalog.length} Excel reports, verified date/month filters and mobile layouts.`);
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode = 1;}).finally(() => server.close());
