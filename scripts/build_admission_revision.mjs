import fs from "node:fs/promises";
import crypto from "node:crypto";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
import {
  amountFrom,
  paymentDate,
  paymentMode,
  paymentParts,
} from "./admission_payment_parser.mjs";

const projectRoot = path.resolve(import.meta.dirname, "..");
const defaultSources = [
  "/Users/shubhamsingh/Desktop/Admission Sheet .xlsx",
  "/Users/shubhamsingh/Desktop/Admission Sheet  (1).xlsx",
];
const sourcePaths = process.argv.slice(2).filter(value => !value.startsWith("--"));
const inputs = sourcePaths.length ? sourcePaths : defaultSources;
const outputArgument = process.argv.find(value => value.startsWith("--output="));
const outputPath = outputArgument
  ? path.resolve(outputArgument.slice("--output=".length))
  : path.join(projectRoot, "backend/data/imports/admission_revision_2026_08_13.json");
const baselinePath = path.join(projectRoot, "backend/data/imports/client_snapshot_2026_08_03.json");
const originalPath = path.join(projectRoot, "backend/data/imports/admission_2026_27.json");

const asText = value => value == null ? "" : String(value).trim();
const nameKey = value => asText(value).toLowerCase().replace(/[^a-z0-9]/g, "");
const phones = value => [...new Set((asText(value).match(/\d{10,15}/g) || []).map(number => number.slice(-10)))];
const excelDate = serial => new Date(Date.UTC(1899, 11, 30 + Number(serial)));
const parseDate = value => {
  if (value instanceof Date) return value;
  if (typeof value === "number" && value > 30000) return excelDate(value);
  const match = asText(value).match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})$/);
  if (!match) return null;
  let year = Number(match[3]);
  if (year < 100) year += 2000;
  const parsed = new Date(Date.UTC(year, Number(match[2]) - 1, Number(match[1])));
  return Number.isNaN(parsed.valueOf()) ? null : parsed;
};
const isoDate = value => value ? value.toISOString().slice(0, 10) : null;
const canonicalProgram = value => {
  const normalized = asText(value).toUpperCase().replaceAll("_", " ");
  if (normalized === "BOARD" || normalized.startsWith("BOARDS")) return "Boards";
  if (normalized.startsWith("MHT-CET") || normalized.startsWith("MHT CET")) return "MHT-CET";
  if (normalized.startsWith("JEE")) return "JEE";
  if (normalized.startsWith("NEET")) return "NEET";
  return asText(value);
};
const contentHash = value => crypto.createHash("sha256").update(JSON.stringify(value)).digest("hex");

async function readAdmission(sourcePath) {
  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
  const admission = workbook.worksheets.getItem("Admission");
  const balances = workbook.worksheets.getItem("balaces as on 3rd Aug");
  if (!admission || !balances) throw new Error(`${sourcePath} is missing a required sheet`);
  return {
    source: {
      name: path.basename(sourcePath),
      sha256: crypto.createHash("sha256").update(await fs.readFile(sourcePath)).digest("hex"),
    },
    admission: admission.getUsedRange().values,
    balances: balances.getUsedRange().values,
  };
}

const workbooks = [];
for (const sourcePath of inputs) workbooks.push(await readAdmission(sourcePath));
const canonicalContent = workbooks.map(book => ({ admission: book.admission, balances: book.balances }));
for (let index = 1; index < canonicalContent.length; index += 1) {
  if (JSON.stringify(canonicalContent[0]) !== JSON.stringify(canonicalContent[index])) {
    throw new Error("The supplied workbooks do not contain identical client data");
  }
}

const original = JSON.parse(await fs.readFile(originalPath, "utf8"));
const baseline = JSON.parse(await fs.readFile(baselinePath, "utf8"));
const originalByName = new Map(original.records.map(row => [nameKey(row.normalized.student_name), row]));
const baselineByName = new Map(baseline.activeStudents.map(row => [nameKey(row.name), row]));
const values = workbooks[0].admission;
let section = "active";
const records = [];
for (let index = 2; index < values.length; index += 1) {
  const sourceRow = index + 1;
  const row = values[index];
  if (asText(row[0]).toLowerCase().startsWith("cancelled")) {
    section = "cancelled";
    continue;
  }
  if (!asText(row[2])) continue;
  const contacts = phones(row[4]);
  const admissionDate = parseDate(row[1]);
  const payments = paymentParts(row[9]).map((raw, lineIndex) => {
    const parsedDate = paymentDate(raw);
    return {
      lineNumber: lineIndex + 1,
      transactionDate: isoDate(parsedDate),
      amount: amountFrom(raw),
      method: paymentMode(raw).toLowerCase(),
      transactionType: /refund/i.test(raw) ? "refund_review" : /incentive/i.test(raw) ? "incentive_review" : "payment",
      sourceNote: raw,
    };
  });
  const originalRow = originalByName.get(nameKey(row[2]));
  const baselineRow = baselineByName.get(nameKey(row[2]));
  const baselinePaid = baselineRow && originalRow
    ? Number(originalRow.normalized.agreed_fee) - Number(baselineRow.balance)
    : null;
  const issues = [];
  if (!admissionDate) issues.push("Admission date is missing or invalid");
  if (!contacts.length) issues.push("Primary mobile is missing");
  if (!canonicalProgram(row[5])) issues.push("Course is missing");
  const newPaid = Number(row[8] || 0);
  const afterCutoff = payments.filter(payment => payment.transactionType === "payment" && payment.transactionDate > "2026-08-03");
  const afterCutoffTotal = afterCutoff.reduce((sum, payment) => sum + Number(payment.amount || 0), 0);
  if (baselinePaid != null && newPaid - baselinePaid !== afterCutoffTotal) {
    issues.push(`Post-3-Aug payment lines total ${afterCutoffTotal}, but the paid-total change is ${newPaid - baselinePaid}`);
  }
  if (originalRow && canonicalProgram(originalRow.normalized.program) !== canonicalProgram(row[5])) {
    issues.push(`Course changed from ${canonicalProgram(originalRow.normalized.program)} to ${canonicalProgram(row[5])}`);
  }
  if (payments.some(payment => payment.transactionType === "refund_review")) {
    issues.push("Refund is mentioned in remarks and requires receipt-level confirmation");
  }
  records.push({
    sourceRow,
    recordStatus: section,
    originalLegacyId: originalRow?.legacy_id || null,
    action: originalRow
      ? originalRow.record_status === section ? "update" : "status_change"
      : "create",
    raw: {
      serialNumber: row[0],
      admissionDate: row[1],
      studentName: row[2],
      schoolName: row[3],
      contactNumber: row[4],
      course: row[5],
      admissionLead: row[6],
      fees: row[7],
      registrationAmount: row[8],
      remarks: row[9],
    },
    normalized: {
      admissionDate: isoDate(admissionDate),
      studentName: asText(row[2]),
      previousSchool: asText(row[3]) || null,
      primaryMobile: contacts[0] || null,
      secondaryMobile: contacts[1] || null,
      program: canonicalProgram(row[5]),
      admissionLeadRaw: asText(row[6]) || null,
      agreedFee: Number(row[7] || 0),
      registrationTotal: newPaid,
      baselinePaid,
    },
    payments,
    issues,
  });
}

const currentNames = new Set(records.map(row => nameKey(row.normalized.studentName)));
const retainedMissingRecords = original.records
  .filter(row => row.record_status === "active" && !currentNames.has(nameKey(row.normalized.student_name)))
  .map(row => ({
    studentName: row.normalized.student_name,
    originalLegacyId: row.legacy_id,
    reason: "Absent from the revised admission register but retained because no cancellation is recorded",
  }));
const active = records.filter(row => row.recordStatus === "active");
const cancelled = records.filter(row => row.recordStatus === "cancelled");
const revisionHash = contentHash(canonicalContent[0]);
const manifest = {
  schemaVersion: 1,
  revisionId: `ADMISSION-REVISION-2026-08-13-${revisionHash.slice(0, 12)}`,
  effectiveDate: "2026-08-13",
  paymentCutoff: "2026-08-03",
  source: {
    sheet: "Admission",
    contentSha256: revisionHash,
    files: workbooks.map(book => book.source),
    identicalCopies: workbooks.length,
  },
  baseline: {
    snapshotId: baseline.snapshotId,
    source: baseline.sources.balances,
  },
  controls: {
    activeRows: active.length,
    cancelledRows: cancelled.length,
    studentRows: records.length,
    activeFeeTotal: active.reduce((sum, row) => sum + row.normalized.agreedFee, 0),
    activeRegistrationTotal: active.reduce((sum, row) => sum + row.normalized.registrationTotal, 0),
    explicitStatusChanges: records.filter(row => row.action === "status_change").length,
    newActiveStudents: active.filter(row => row.action === "create").length,
    retainedMissingStudents: retainedMissingRecords.length,
  },
  records,
  retainedMissingRecords,
};

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, `${JSON.stringify(manifest, null, 2)}\n`);
console.log(JSON.stringify({ outputPath, revisionId: manifest.revisionId, controls: manifest.controls }, null, 2));
