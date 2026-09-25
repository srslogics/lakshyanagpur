const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

for (const [file, functionName, fieldPrefix] of [
  ['app.js', 'examinationMarksPayload', 'exam'],
  ['faculty-app/app.js', 'examinationResultsPayload', 'result'],
]) {
  const source = fs.readFileSync(path.join(__dirname, '..', file), 'utf8');
  const start = source.indexOf(`function ${functionName}(`);
  const end = source.indexOf('\nasync function ', start);
  assert.ok(start >= 0 && end > start);
  const input = source.match(new RegExp(`<input[^>]*data-${fieldPrefix}-marks[^>]*>`));
  assert.ok(input, `${file}: marks input exists`);
  assert.ok(!/\bmin="0"/.test(input[0]), `${file}: negative scores allowed by input`);
  const form = { dataset: { maxMarks: '100' } };
  const row = { dataset: { examStudent: 'student-1' } };
  let status = 'graded';
  let value = '-4.25';
  const context = vm.createContext({
    state: { activeExam: { maxMarks: 100 } },
    $$: () => [row],
    $: selector => {
      if (selector.startsWith('#')) return form;
      if (selector.includes('status')) return { value: status };
      if (selector.includes('marks')) return { value };
      return { value: '' };
    },
  });
  vm.runInContext(source.slice(start, end), context);
  const payload = () => context[functionName](form)[0];
  for (const score of [-4.25, -1, 0, 100]) {
    value = String(score);
    assert.equal(payload().marksObtained, score);
  }
  value = '101';
  assert.throws(payload, /cannot exceed/);
  value = '';
  assert.throws(payload, /Enter marks/);
  value = 'invalid';
  assert.throws(payload, /valid numeric/);
  status = 'absent';
  assert.equal(payload().marksObtained, null);
  status = 'withheld';
  assert.equal(payload().marksObtained, null);
  console.log(`${file}: negative marks and validation checks passed`);
}
