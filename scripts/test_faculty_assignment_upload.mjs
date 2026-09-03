import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../faculty-app/app.js", import.meta.url), "utf8");
function section(start, end) {
  const first = source.indexOf(start);
  const last = source.indexOf(end, first);
  assert.ok(first >= 0 && last > first, `Missing section: ${start}`);
  return source.slice(first, last);
}
const network = section("async function resilientFetch(", "async function downloadProtectedFile(");
const saving = section("async function saveAssignment(", "function openExaminationModal(");
const constants = section("const MAX_ASSIGNMENT_PDF_BYTES", "const $ =");

class File {
  constructor(size = 1024) { this.size = size; this.name = "worksheet.pdf"; }
}
class FormData {
  constructor(form) { this.values = new Map(Object.entries(form?.values || {})); }
  get(key) { return this.values.get(key) ?? ""; }
  append(key, value) { this.values.set(key, value); }
}

function networkHarness() {
  const timers = new Map();
  const requests = [];
  let timerId = 0;
  let now = 0;
  const context = vm.createContext({
    AbortController, FormData, navigator:{onLine:true}, state:{token:"test-token"},
    apiUrl:path => path, setConnectionState() {}, clearSession() {}, showLogin() {},
    setTimeout(fn, delay) { const id = ++timerId; timers.set(id, {fn, at:now + delay}); return id; },
    clearTimeout(id) { timers.delete(id); },
    fetch(path, options) {
      return new Promise((resolve, reject) => {
        requests.push({path, options, resolve});
        options.signal.addEventListener("abort", () => reject(Object.assign(new Error("timeout"), {name:"AbortError"})), {once:true});
      });
    },
  });
  vm.runInContext(`${constants}\n${network}`, context);
  return {
    context, requests, timers,
    advance(ms) {
      now += ms;
      for (const [id, timer] of timers) if (timer.at <= now) { timers.delete(id); timer.fn(); }
    },
  };
}

test("PDF POST survives the old 15-second deadline; multipart auth is preserved", async () => {
  const h = networkHarness();
  const pending = vm.runInContext('api("/material", {method:"POST", body:new FormData(), timeoutMs:ASSIGNMENT_UPLOAD_TIMEOUT_MS})', h.context);
  h.advance(20000);
  assert.equal(h.requests[0].options.signal.aborted, false);
  assert.equal(h.requests[0].options.timeoutMs, undefined);
  assert.equal(h.requests[0].options.headers.Authorization, "Bearer test-token");
  assert.equal(h.requests[0].options.headers["Content-Type"], undefined);
  h.requests[0].resolve({status:200, ok:true, json:async () => ({available:true})});
  assert.equal((await pending).available, true);
  assert.equal(h.timers.size, 0);
});

test("PDF timeout is bounded at three minutes and POST is never automatically retried", async () => {
  const h = networkHarness();
  const pending = vm.runInContext('api("/material", {method:"POST", body:new FormData(), timeoutMs:ASSIGNMENT_UPLOAD_TIMEOUT_MS})', h.context);
  const rejected = assert.rejects(pending, error => error.transient && error.status === 0);
  h.advance(179999);
  assert.equal(h.requests[0].options.signal.aborted, false);
  h.advance(1);
  await rejected;
  assert.equal(h.requests.length, 1);
  assert.equal(h.timers.size, 0);
});

test("ordinary requests retain the 15-second timeout", async () => {
  const h = networkHarness();
  const pending = h.context.api("/assignment", {method:"POST"});
  const rejected = assert.rejects(pending, /server took too long/);
  h.advance(15000);
  await rejected;
  assert.equal(h.requests.length, 1);
});

test("GET still retries once without leaving an abort timer behind", async () => {
  const h = networkHarness();
  const pending = h.context.api("/bootstrap");
  h.requests[0].resolve({status:503});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.requests.length, 2);
  h.requests[1].resolve({status:200, ok:true, json:async () => ({ready:true})});
  assert.equal((await pending).ready, true);
  assert.equal(h.timers.size, 0);
});

function formHarness({material = new File(), status = "published", handler, refreshError = false} = {}) {
  const elements = new Map();
  const calls = [];
  const messages = [];
  const state = {editingAssignment:null, savingAssignment:false};
  let resets = 0;
  let closes = 0;
  const form = {
    values:{pair:"batch|subject", material, title:"Worksheet", instructions:"Complete it", dueAt:"2026-09-04T12:00", status, externalUrl:""},
    reportValidity:() => true, reset() { resets += 1; },
  };
  const context = vm.createContext({
    File, FormData, state,
    $:selector => {
      if (!elements.has(selector)) {
        const classes = new Set(["hidden"]);
        elements.set(selector, {textContent:"", disabled:false, classList:{
          add:value => classes.add(value), remove:value => classes.delete(value), contains:value => classes.has(value),
        }});
      }
      return elements.get(selector);
    },
    indiaInputToISOString:value => value,
    async api(path, options) {
      calls.push({path, ...options});
      return handler ? handler(path, options, calls.length) : {id:"saved-id"};
    },
    closeModal() { closes += 1; state.editingAssignment = null; },
    async refreshPortal(message) { if (refreshError) throw new Error("Refresh unavailable"); messages.push(message); },
    toast:message => messages.push(message),
  });
  vm.runInContext(`${constants}\n${saving}`, context);
  return {context, calls, messages, state, elements, form, save:() => context.saveAssignment({preventDefault() {}, currentTarget:form}), get resets() {return resets;}, get closes() {return closes;}};
}

test("uncertain upload retains the file and assignment ID, and retry uses PATCH", async () => {
  let uploads = 0;
  const h = formHarness({handler(path) {
    if (path.endsWith("/material") && ++uploads === 1) throw Object.assign(new Error("timeout"), {transient:true});
    return {id:"saved-id"};
  }});
  await h.save();
  assert.equal(h.state.editingAssignment, "saved-id");
  assert.equal(h.elements.get("#assignment-modal-title").textContent, "Edit assignment");
  assert.equal(h.elements.get("#assignment-submit").disabled, false);
  assert.match(h.elements.get("#assignment-error").textContent, /could not be confirmed/);
  assert.equal(h.resets, 0);
  assert.equal(h.closes, 0);
  assert.equal(h.calls[1].timeoutMs, 180000);
  await h.save();
  assert.equal(h.calls[2].method, "PATCH");
  assert.equal(h.calls[2].path, "/api/academics/assignments/saved-id");
  assert.equal(h.calls.filter(call => call.path === "/api/academics/assignments" && call.method === "POST").length, 1);
  assert.equal(h.closes, 1);
});

test("server validation errors preserve the saved assignment and explain the PDF failure", async () => {
  const h = formHarness({handler(path) {
    if (path.endsWith("/material")) throw Object.assign(new Error("Invalid PDF"), {status:415});
    return {id:"saved-id"};
  }});
  await h.save();
  assert.match(h.elements.get("#assignment-error").textContent, /PDF upload failed: Invalid PDF/);
  assert.equal(h.state.editingAssignment, "saved-id");
  assert.equal(h.resets, 0);
});

test("save failure does not claim an assignment or PDF was saved", async () => {
  const h = formHarness({handler() { throw new Error("Invalid title"); }});
  await h.save();
  assert.equal(h.elements.get("#assignment-error").textContent, "Invalid title");
  assert.equal(h.state.editingAssignment, null);
  assert.equal(h.calls.length, 1);
});

test("successful PDF with failed list refresh is reported as saved, not upload failure", async () => {
  const h = formHarness({refreshError:true});
  await h.save();
  assert.equal(h.resets, 1);
  assert.equal(h.closes, 1);
  assert.match(h.messages[0], /Assignment and PDF published/);
  assert.match(h.messages[0], /list could not refresh/);
  assert.equal(h.elements.get("#assignment-error").classList.contains("hidden"), true);
});

test("draft PDF upload is not described as published", async () => {
  const h = formHarness({status:"draft"});
  await h.save();
  assert.match(h.messages[0], /saved as draft/);
  assert.doesNotMatch(h.messages[0], /published/);
});

test("15 MB is accepted; larger PDF is blocked before creating an assignment", async () => {
  const accepted = formHarness({material:new File(15 * 1024 * 1024)});
  await accepted.save();
  assert.equal(accepted.calls.length, 2);
  const rejected = formHarness({material:new File(15 * 1024 * 1024 + 1)});
  await rejected.save();
  assert.equal(rejected.calls.length, 0);
  assert.match(rejected.elements.get("#assignment-error").textContent, /15 MB or smaller/);
});

test("double submission during an upload does not create another assignment", async () => {
  let finish;
  const h = formHarness({handler:() => new Promise(resolve => {finish = resolve;})});
  const pending = h.save();
  await h.save();
  assert.equal(h.calls.length, 1);
  finish({id:"saved-id"});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.calls.length, 2);
  await h.save();
  assert.equal(h.calls.length, 2);
  finish({available:true});
  await pending;
  assert.equal(h.state.savingAssignment, false);
});

test("assignment without PDF only saves metadata", async () => {
  const h = formHarness({material:new File(0)});
  await h.save();
  assert.equal(h.calls.length, 1);
  assert.equal(h.messages[0], "Assignment created.");
});

test("closing a pending upload cannot discard its saved assignment ID", () => {
  const state = {savingAssignment:true, editingAssignment:"saved-id"};
  const messages = [];
  const context = vm.createContext({state, toast:message => messages.push(message)});
  vm.runInContext(section("function closeModal(", "function openNoticeModal("), context);
  context.closeModal("assignment-modal");
  assert.equal(state.editingAssignment, "saved-id");
  assert.match(messages[0], /keep this page open/);
});

test("HTML and offline cache ship the same new faculty script", () => {
  const html = readFileSync(new URL("../faculty-app/index.html", import.meta.url), "utf8");
  const sw = readFileSync(new URL("../faculty-app/sw.js", import.meta.url), "utf8");
  const version = html.match(/app\.js\?v=(\d+)/)?.[1];
  assert.ok(version);
  assert.ok(sw.includes(`./app.js?v=${version}`));
  assert.ok(sw.includes('const CACHE = "lakshya-faculty-v34"'));
});
