import crypto from "node:crypto";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const run = promisify(execFile);
const sourcePath = "/Users/shubhamsingh/Desktop/Lakshaya-Docs/Demo Attendance.xlsx";
const admissionManifestPath = new URL("../backend/data/imports/admission_2026_27.json", import.meta.url);
const outputPath = new URL("../backend/data/imports/demo_attendance_2026.json", import.meta.url);
const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "lakshya-attendance-"));
const normalizedDir = path.join(tempDir, "normalized");
await fs.mkdir(normalizedDir, { recursive: true });

const officeCandidates = [
  "/Applications/LibreOffice.app/Contents/MacOS/soffice",
  "soffice",
];
let office = null;
for (const candidate of officeCandidates) {
  try {
    if (candidate.includes("/")) await fs.access(candidate);
    office = candidate;
    break;
  } catch {}
}
if (!office) throw new Error("LibreOffice is required to normalize this workbook before inspection");
await run(office, ["--headless", "--convert-to", "xlsx", "--outdir", normalizedDir, sourcePath]);

const normalizedPath = path.join(normalizedDir, path.basename(sourcePath));
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(normalizedPath));
const sourceHash = crypto.createHash("sha256").update(await fs.readFile(sourcePath)).digest("hex");
const admissions = JSON.parse(await fs.readFile(admissionManifestPath, "utf8"));

const text = value => value == null ? "" : String(value).trim();
const canonical = value => text(value).toLowerCase().replace(/[^a-z0-9]/g, "");
const jsonValue = value => value instanceof Date ? value.toISOString() : value;
const jsonRow = row => row.map(jsonValue);
const admissionByName = new Map(
  admissions.records.map(record => [canonical(record.normalized.student_name), record]),
);
const normalizeProgram = value => text(value).toLowerCase() === "boards"
  ? "Boards 11th & 12th Tuition"
  : text(value);
const phones = value => text(value).split(/\s+/).map(part => part.replace(/\D/g, "")).filter(Boolean);
const dateLabel = value => {
  if (typeof value === "number" && value > 30000) {
    const parsed = new Date(Date.UTC(1899, 11, 30 + value));
    return `${parsed.getUTCMonth() + 1}-${parsed.getUTCDate()}`;
  }
  return text(value);
};
const slug = value => value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const valuesFor = sheetName => workbook.worksheets.getItem(sheetName).getUsedRange().values;

const mentorRows = valuesFor("Mentor").slice(1).filter(row => text(row[0]));
const mentorByCode = new Map(mentorRows.map(row => [text(row[0]), {
  name: text(row[1]),
  mobile: text(row[2]),
  mentor: text(row[3]),
}]));
const subjectRows = valuesFor("Subject").slice(2).filter(row => text(row[0]));
const subjectByCode = new Map(subjectRows.map(row => [text(row[0]), row]));

const students = [];
for (const config of [
  { sheet: "Tatva Attendance", batch: "Tatva", start: 3, end: 27 },
  { sheet: "Essential Attendance", batch: "Essential", start: 3, end: 43 },
]) {
  const rows = valuesFor(config.sheet);
  const headers = rows[2];
  for (let index = config.start; index < config.end; index += 1) {
    const row = rows[index];
    const code = text(row[0]);
    const name = text(row[1]);
    const admission = admissionByName.get(canonical(name));
    if (!admission) throw new Error(`No exact admission match for ${code} ${name}`);
    const mentor = mentorByCode.get(code);
    const subject = subjectByCode.get(code);
    if (!mentor || !subject) throw new Error(`Academic mapping is incomplete for ${code}`);
    if (canonical(mentor.name) !== canonical(name) || canonical(subject[1]) !== canonical(name)) {
      throw new Error(`Name mismatch across workbook sheets for ${code}`);
    }
    const contactNumbers = phones(row[2]);
    const sourceStream = text(subject[2]);
    const issues = [];
    if (normalizeProgram(sourceStream) !== admission.normalized.program) {
      issues.push(
        `Workbook stream ${sourceStream} differs from admission program ${admission.normalized.program}; admission program was not overwritten`,
      );
    }
    if (!text(subject[7])) issues.push("School / college is blank in the Subject sheet");
    if (contactNumbers.some(number => number.length !== 10)) {
      issues.push("Source mobile is not 10 digits and was preserved without correction");
    }
    const attendance = [];
    for (let column = 5; column < row.length; column += 1) {
      const mark = text(row[column]).toUpperCase();
      if (!["P", "A", "X"].includes(mark)) continue;
      attendance.push({
        source_column: column + 1,
        source_date_label: dateLabel(headers[column]),
        attendance_date: null,
        raw_status: mark,
        normalized_status: mark === "P" ? "present" : mark === "A" ? "absent" : null,
      });
    }
    students.push({
      source_student_code: code,
      admission_legacy_id: admission.legacy_id,
      student_name: name,
      batch: config.batch,
      source_sheet: config.sheet,
      source_row: index + 1,
      source_stream: sourceStream || null,
      mentor_name: text(mentor.mentor) || null,
      source_school_name: text(subject[7]) || null,
      source_primary_mobile: contactNumbers[0] || null,
      source_secondary_mobile: contactNumbers[1] || null,
      subjects: ["Maths", "Chemistry", "Physics", "Biology"]
        .map((name, offset) => ({ name, source_value: text(subject[3 + offset]) }))
        .filter(item => item.source_value),
      attendance,
      issues,
    });
  }
}

const linkedIssues = new Map(students.map(student => [student.source_student_code, student.issues]));
const sourceRecords = [];
for (const sheet of workbook.worksheets.items) {
  const rows = sheet.getUsedRange().values;
  rows.forEach((row, index) => {
    if (!row.some(value => value != null && value !== "")) return;
    const firstCode = row.map(text).find(value => /^(T|E)-\d{2}$/.test(value)) || null;
    let recordType = "workbook_context";
    const issues = [];
    if (["Tatva Attendance", "Essential Attendance"].includes(sheet.name) && index >= 3 && firstCode) {
      recordType = linkedIssues.has(firstCode) ? "current_student_attendance" : "historical_roster_status";
    } else if (sheet.name === "Mentor" && index >= 1) {
      recordType = "mentor_mapping";
    } else if (sheet.name === "Subject" && index >= 2) {
      recordType = "subject_selection";
    } else if (sheet.name === "Upto 30 June Attendance" && index >= 4) {
      if (text(row[1])) {
        recordType = "historical_attendance_or_lead";
        issues.push("Staged for review; this row was not assumed to be a student or an enquiry");
      } else {
        recordType = "historical_placeholder";
      }
    } else if (sheet.name === "TimeTable") {
      recordType = "timetable_template";
      issues.push("Staged for review; recurrence days and superseded versions were not inferred");
    } else if (sheet.name === "Attendance Sheet") {
      recordType = "printable_attendance_roster";
    } else if (sheet.name === "Pivot Table 5") {
      recordType = "derived_pivot_summary";
      issues.push("Preserved as a derived summary; not used as the authoritative mentor count");
    }
    if (
      ["Tatva Attendance", "Essential Attendance"].includes(sheet.name)
      && index === 2
    ) {
      issues.push("Displayed July day labels do not contain a confirmed year; dates remain undated");
      issues.push("The meaning of X is unconfirmed; X remains unclassified");
    }
    const linked = firstCode && linkedIssues.has(firstCode) ? firstCode : null;
    sourceRecords.push({
      id: `ACAD-${sourceHash.slice(0, 12)}-${slug(sheet.name).slice(0, 30)}-${String(index + 1).padStart(3, "0")}`,
      source_sheet: sheet.name,
      source_row: index + 1,
      record_type: recordType,
      source_key: linked,
      raw: { cells: jsonRow(row) },
      normalized: linked ? {
        source_student_code: linked,
        student_name: students.find(student => student.source_student_code === linked)?.student_name,
      } : {},
      issues: [...issues, ...(linked ? linkedIssues.get(linked) : [])],
    });
  });
}

const attendance = students.flatMap(student => student.attendance);
const marks = Object.fromEntries(["P", "A", "X"].map(mark => [
  mark,
  attendance.filter(entry => entry.raw_status === mark).length,
]));
const batchCounts = Object.fromEntries(["Tatva", "Essential"].map(batch => [
  batch,
  students.filter(student => student.batch === batch).length,
]));
const manifest = {
  schema_version: 1,
  source: {
    name: path.basename(sourcePath),
    sha256: sourceHash,
    sheets: workbook.worksheets.items.map(sheet => sheet.name),
  },
  expected: {
    active_students: students.length,
    batch_counts: batchCounts,
    mentor_assignments: students.filter(student => student.mentor_name).length,
    subject_selections: students.reduce((sum, student) => sum + student.subjects.length, 0),
    attendance_entries: attendance.length,
    attendance_marks: marks,
    source_records: sourceRecords.length,
    unresolved_items: students.reduce((sum, student) => sum + student.issues.length, 0)
      + sourceRecords.reduce((sum, record) => sum + record.issues.length, 0),
  },
  students,
  source_records: sourceRecords,
};
await fs.mkdir(path.dirname(outputPath.pathname), { recursive: true });
await fs.writeFile(outputPath, JSON.stringify(manifest, null, 2));
console.log(JSON.stringify({ outputPath: outputPath.pathname, ...manifest.expected }, null, 2));
