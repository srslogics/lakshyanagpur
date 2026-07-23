import fs from "node:fs/promises";
import crypto from "node:crypto";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const sourcePath = "/Users/shubhamsingh/Desktop/Lakshaya-Docs/Admission Sheet .xlsx";
const outputDir = "/Users/shubhamsingh/Documents/New project/lakshinstitution/institution-erp/output/imports";
const manifestDir = "/Users/shubhamsingh/Documents/New project/lakshinstitution/institution-erp/backend/data/imports";
const previewDir = "/tmp/lakshya-admission-staging-previews";
await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(manifestDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const sourceHash = crypto.createHash("sha256").update(await fs.readFile(sourcePath)).digest("hex");
const source = workbook.worksheets.getItem("Admission");
const raw = source.getRange("A1:J80").values;

const asText = value => value == null ? "" : String(value).trim();
const excelDate = serial => new Date(Date.UTC(1899, 11, 30 + Number(serial)));
const parseDate = value => {
  if (value instanceof Date) return value;
  if (typeof value === "number" && value > 30000) return excelDate(value);
  const match = asText(value).match(/^(\d{1,2})[-\/.](\d{1,2})[-\/.](\d{2,4})$/);
  if (!match) return null;
  let year = Number(match[3]); if (year < 100) year += 2000;
  return new Date(Date.UTC(year, Number(match[2]) - 1, Number(match[1])));
};
const phones = value => [...new Set((asText(value).match(/\d{10,15}/g) || []).map(x => x.slice(-10)))];
const paymentParts = remark => asText(remark).split(/\s*\+\s*|\n+/).map(x => x.trim()).filter(Boolean);
const amountFrom = part => {
  const match = part.match(/(\d+(?:\.\d+)?)\s*k\b/i);
  if (match) return Math.round(Number(match[1]) * 1000);
  const plain = part.match(/(\d+(?:\.\d+)?)\s*(?=upi|cash|online|bank|card|cheque|check|gpay|phonepe|neft|imps|rtgs)/i);
  if (!plain) return null;
  const value = Number(plain[1]);
  return Math.round(value <= 100 ? value * 1000 : value);
};
const paymentDate = part => {
  const matches = [...part.matchAll(/\b(\d{1,2})[-\/.](\d{1,2})(?:[-\/.](\d{2,4}))?\b/g)];
  if (!matches.length) return null;
  const match = matches[matches.length - 1];
  let year = match[3] ? Number(match[3]) : 2026; if (year < 100) year += 2000;
  return new Date(Date.UTC(year, Number(match[2]) - 1, Number(match[1])));
};
const paymentMode = part => {
  if (/cash/i.test(part)) return "Cash";
  if (/upi|gpay|phonepe/i.test(part)) return "UPI";
  if (/neft|imps|rtgs|bank/i.test(part)) return "Bank";
  if (/cheque|check/i.test(part)) return "Cheque";
  if (/card/i.test(part)) return "Card";
  if (/online/i.test(part)) return "Online";
  return "Unknown";
};
const normalizeCourse = value => ({"JEE":"JEE", "NEET":"NEET", "MHT-CET":"MHT-CET", "BOARDS":"Boards 11th & 12th Tuition"}[asText(value).toUpperCase()] || asText(value));
const canonicalName = value => asText(value).toLowerCase().replace(/[^a-z0-9]/g, "");
const clientManualPaymentDateStudents = new Set([
  "Aaron Sonkar", "Md. Zaid Ali", "Md. Daniyal Ali", "Nawaz Baig",
  "Rushada Tabhane", "Priyanshi Wahane", "Abhas Gajbhiye", "Snehlata Mohadikar",
].map(canonicalName));

let section = "active";
const records = [];
for (let i = 2; i < raw.length; i++) {
  const row = raw[i];
  if (asText(row[0]).toLowerCase().startsWith("cancelled")) { section = "cancelled"; continue; }
  if (!asText(row[2])) continue;
  const contactList = phones(row[4]);
  const issues = [];
  if (!parseDate(row[1])) issues.push("Admission date missing or invalid");
  if (!contactList.length) issues.push("Contact number missing");
  if (!asText(row[3])) issues.push("School missing");
  if (!asText(row[5])) issues.push("Course missing");
  if (!asText(row[6])) issues.push("Admission lead/counsellor missing");
  if (/incentive/i.test(asText(row[9]))) issues.push("Separate incentive from payment; approval required");
  const parsedTotal = paymentParts(row[9]).map(amountFrom).filter(v => v != null).reduce((a,b) => a+b, 0);
  if (section === "active" && parsedTotal && Number(row[8] || 0) !== parsedTotal) issues.push(`Payment details total ${parsedTotal} does not match registration amount ${Number(row[8] || 0)}`);
  const blocker = !parseDate(row[1]) || !contactList.length || !asText(row[5]);
  records.push({
    sourceRow: i + 1,
    status: section,
    legacyId: `LEGACY-ADM-2026-${section === "active" ? "A" : "C"}-${String(row[0]).padStart(3,"0")}`,
    admissionDate: parseDate(row[1]), student: asText(row[2]), school: asText(row[3]),
    primaryMobile: contactList[0] || "", secondaryMobile: contactList[1] || "",
    course: normalizeCourse(row[5]), leadRaw: asText(row[6]), feeTotal: Number(row[7] || 0),
    registrationTotal: Number(row[8] || 0), remarks: asText(row[9]), issues,
    readiness: blocker ? "BLOCKED" : issues.length ? "REVIEW" : "READY",
    parsedTotal,
  });
}

const active = records.filter(x => x.status === "active");
const cancelled = records.filter(x => x.status === "cancelled");
const allPhones = new Map();
for (const record of records) for (const phone of [record.primaryMobile, record.secondaryMobile].filter(Boolean)) {
  if (!allPhones.has(phone)) allPhones.set(phone, []); allPhones.get(phone).push(record.legacyId);
}
for (const record of records) {
  const duplicates = [record.primaryMobile, record.secondaryMobile].filter(p => p && allPhones.get(p).length > 1);
  if (duplicates.length) { record.issues.push(`Duplicate contact across student rows: ${duplicates.join(", ")}`); record.readiness = "BLOCKED"; }
}

const payments = [];
for (const record of records) {
  paymentParts(record.remarks).forEach((part, index) => {
    const amount = amountFrom(part);
    if (!amount && record.status === "active") return;
    const incentive = /incentive/i.test(part);
    const date = paymentDate(part);
    const clientManualDate = !date && !incentive && clientManualPaymentDateStudents.has(canonicalName(record.student));
    payments.push({
      legacyId: record.legacyId, sourceRow: record.sourceRow, line: index + 1, student: record.student,
      status: record.status, date, amount: amount || 0, mode: paymentMode(part),
      kind: incentive ? "Incentive / concession review" : "Payment", raw: part,
      readiness: record.status === "cancelled" ? "DO NOT IMPORT" : incentive || !date || paymentMode(part) === "Unknown" ? "REVIEW" : "READY",
      dateEntryStatus: clientManualDate ? "manual_client_entry" : date ? "source_date" : "unresolved",
      reviewerNote: clientManualDate ? "Unknown — client to enter manually" : "",
    });
  });
}

const manifest = {
  schema_version: 2,
  source: { name: "Admission Sheet .xlsx", sheet: "Admission", sha256: sourceHash, reporting_period: "2026-27" },
  expected: {
    active_rows: active.length,
    cancelled_rows: cancelled.length,
    student_rows: records.length,
    fee_total: active.reduce((sum, row) => sum + row.feeTotal, 0),
    registration_total: active.reduce((sum, row) => sum + row.registrationTotal, 0),
    staged_payment_total: payments.filter(row => row.status === "active" && row.kind === "Payment").reduce((sum, row) => sum + row.amount, 0),
  },
  records: records.map(record => ({
    legacy_id: record.legacyId,
    source_row: record.sourceRow,
    record_status: record.status,
    import_readiness: record.readiness,
    issues: record.issues,
    raw: {
      serial_number: raw[record.sourceRow - 1][0],
      date: raw[record.sourceRow - 1][1],
      student_name: raw[record.sourceRow - 1][2],
      school_name: raw[record.sourceRow - 1][3],
      contact_number: raw[record.sourceRow - 1][4],
      course: raw[record.sourceRow - 1][5],
      admission_lead: raw[record.sourceRow - 1][6],
      fees: raw[record.sourceRow - 1][7],
      registration_amount: raw[record.sourceRow - 1][8],
      remarks: raw[record.sourceRow - 1][9],
    },
    normalized: {
      admission_date: record.admissionDate?.toISOString().slice(0, 10) || null,
      student_status: record.status === "cancelled" ? "forfeited" : "active",
      legacy_serial_number: raw[record.sourceRow - 1][0],
      student_name: record.student,
      previous_school: record.school || null,
      primary_mobile: record.primaryMobile || null,
      secondary_mobile: record.secondaryMobile || null,
      program: record.course || null,
      admission_lead_raw: record.leadRaw || null,
      agreed_fee: record.feeTotal,
      registration_total: record.registrationTotal,
      payment_details_total: record.parsedTotal,
    },
    payments: payments.filter(payment => payment.legacyId === record.legacyId).map(payment => ({
      line_number: payment.line,
      transaction_date: payment.date?.toISOString().slice(0, 10) || null,
      amount: payment.amount,
      method: payment.mode.toLowerCase(),
      transaction_type: payment.kind === "Payment" ? "payment" : "incentive_review",
      source_note: payment.raw,
      date_entry_status: payment.dateEntryStatus,
      reconciliation_status: payment.readiness.toLowerCase().replaceAll(" ", "_"),
    })),
  })),
};
const manifestPath = `${manifestDir}/admission_2026_27.json`;
await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2));

const mapping = workbook.worksheets.getItem("Sheet2");
mapping.name = "ERP Mapping";
const summary = workbook.worksheets.add("Import Summary");
const students = workbook.worksheets.add("Students Import");
const paymentSheet = workbook.worksheets.add("Payment Review");
const exceptions = workbook.worksheets.add("Exceptions");

const titleStyle = { fill: "#173F35", font: { bold: true, color: "#FFFFFF", size: 16 }, verticalAlignment: "center" };
const headerStyle = { fill: "#E9B949", font: { bold: true, color: "#17201D" }, verticalAlignment: "center", wrapText: true, borders: { preset: "inside", style: "thin", color: "#D6C28A" } };
const sectionStyle = { fill: "#DDECE6", font: { bold: true, color: "#173F35" } };
const moneyFormat = '"₹"#,##0';

mapping.getRange("A1:F1").merge(); mapping.getRange("A1").values = [["ERP field mapping and import decisions"]]; mapping.getRange("A1:F1").format = titleStyle; mapping.getRange("A1:F1").format.rowHeight = 30;
mapping.getRange("A3:F3").values = [["Source column","ERP entity","ERP field","Transformation","Import rule","Notes"]]; mapping.getRange("A3:F3").format = headerStyle;
mapping.getRange("A4:F13").values = [
  ["Sr. No","Migration audit","legacy_serial_number","Preserve source serial and generate a separate ERP admission number","Always","Source serial remains an auditable legacy reference"],
  ["Date","Enrollment","enrollment_date","Normalize mixed text/Excel dates","Required","Report year is 2026-27"],
  ["Student Name","Student","full_name","Trim whitespace","Required","Central student record"],
  ["School Name","Student profile","previous_school","Trim; standardize later","Review if blank","School spellings are inconsistent"],
  ["Contact number","Student","primary_mobile + secondary_mobile","First number is Primary; second is Secondary","Block if blank","Do not create guardian relationships from these numbers"],
  ["Course","Program/Enrollment","program_code","Map JEE, NEET, MHT-CET; Boards = 11th & 12th tuition","Required","Batch is absent and remains unassigned"],
  ["Admission Lead","Lead/User attribution","legacy_admission_lead","Preserve raw; map staff aliases","Review if blank","Contains staff combinations, referrals and walk-ins"],
  ["Fees","Finance","agreed_fee_total","Numeric rupees","Required","Creates fee agreement, not a receipt"],
  ["Registration amount","Finance","legacy_paid_total","Numeric rupees","Required","Must reconcile to verified payment lines"],
  ["Remarks","Payment staging","raw_payment_note","Split +/line-separated entries; normalize Cash, UPI, Online, Bank, Card and Cheque","Manual review","Confirmed missing payment dates stay blank for client entry; never use admission date"],
];
mapping.getRange("A15:F15").merge(); mapping.getRange("A15").values = [["Import sequence"]]; mapping.getRange("A15:F15").format = sectionStyle;
mapping.getRange("A16:F20").values = [
  ["1","Student","Create central student record","All source rows","Cancelled source rows become Forfeited students",null],
  ["2","Contacts","Store Primary and Secondary numbers","With the student record","No guardian relationship is created",null],
  ["3","Enrollment","Create enrollment with batch unassigned","After program mapping","Forfeited students receive an inactive enrollment when a course is present",null],
  ["4","Finance","Create agreed fee ledger","After enrollment","No synthetic receipts",null],
  ["5","Payments","Create immutable transactions","Only verified Payment Review rows","Incentives become separate adjustments after approval",null],
];
mapping.getRange("A:F").format.font = { name: "Aptos", size: 10 }; mapping.getRange("A3:F20").format.wrapText = true; mapping.getRange("A:F").format.columnWidth = 20; mapping.getRange("D:F").format.columnWidth = 28; mapping.freezePanes.freezeRows(3); mapping.showGridLines = false;

summary.getRange("A1:H1").merge(); summary.getRange("A1").values = [["Lakshya ERP admission import readiness"]]; summary.getRange("A1:H1").format = titleStyle; summary.getRange("A1:H1").format.rowHeight = 32;
summary.getRange("A3:B3").values = [["Metric","Value"]]; summary.getRange("A3:B3").format = headerStyle;
summary.getRange("A4:A12").values = [["Active admissions"],["Forfeited admissions"],["Active fee agreements"],["Active registration total"],["Ready rows"],["Review rows"],["Blocked rows"],["Missing contact numbers"],["Secondary contacts"]];
summary.getRange("B4:B12").formulas = [["=COUNTIF('Students Import'!$B$4:$B$73,\"Active\")"],["=COUNTIF('Students Import'!$B$4:$B$73,\"Forfeited\")"],["=SUMIF('Students Import'!$B$4:$B$73,\"Active\",'Students Import'!$K$4:$K$73)"],["=SUMIF('Students Import'!$B$4:$B$73,\"Active\",'Students Import'!$L$4:$L$73)"],["=COUNTIF('Students Import'!$N$4:$N$73,\"READY\")"],["=COUNTIF('Students Import'!$N$4:$N$73,\"REVIEW\")"],["=COUNTIF('Students Import'!$N$4:$N$73,\"BLOCKED\")"],["=COUNTBLANK('Students Import'!$G$4:$G$73)"],["=SUM('Students Import'!$R$4:$R$73)"]];
summary.getRange("B6:B7").format.numberFormat = moneyFormat;
summary.getRange("D3:H3").merge(); summary.getRange("D3").values = [["Important migration decisions"]]; summary.getRange("D3:H3").format = headerStyle;
summary.getRange("D4:H10").merge(true); summary.getRange("D4:D10").values = [["All cancelled source rows create Forfeited students; five receive inactive enrollments and the blank course remains unassigned."],["Rows without a contact number remain blank and are flagged for data-quality review."],["The first contact is Primary and the second is Secondary; no guardian relationship is inferred."],["Admission Lead is attribution data, not a reliable enquiry source. Raw values are preserved for mapping."],["Batch, guardian name, guardian relationship, receipt number, and verified payment reference are absent."],["Incentives must become approved adjustments, not payment receipts."],["ERP admission numbers are generated separately; the sheet serial remains the legacy reference."]];
summary.getRange("A3:B12").format.borders = { preset: "inside", style: "thin", color: "#D7E0DD" }; summary.getRange("D4:H10").format.wrapText = true; summary.getRange("A:H").format.font = { name: "Aptos", size: 10 }; summary.getRange("A:A").format.columnWidth = 28; summary.getRange("B:B").format.columnWidth = 18; summary.getRange("D:H").format.columnWidth = 16; summary.showGridLines = false;

const studentHeaders = ["Legacy ID","Record Status","Source Row","Admission Date","Student Name","Previous School","Primary Mobile","Secondary Mobile","Program","Admission Lead (raw)","Agreed Fee","Registration Total","Payment Detail Parsed","Import Readiness","Issues / Required Action","ERP Student ID","ERP Enrollment ID","Secondary Contact Count"];
students.getRange("A1:R1").merge(); students.getRange("A1").values = [["Student, enrollment and fee agreement import staging"]]; students.getRange("A1:R1").format = titleStyle;
students.getRange("A3:R3").values = [studentHeaders]; students.getRange("A3:R3").format = headerStyle;
students.getRangeByIndexes(3,0,records.length,studentHeaders.length).values = records.map(r => [r.legacyId,r.status === "active" ? "Active" : "Forfeited",r.sourceRow,r.admissionDate,r.student,r.school,r.primaryMobile,r.secondaryMobile,r.course,r.leadRaw,r.feeTotal,r.registrationTotal,r.parsedTotal,r.readiness,r.issues.join("; "),"","",0]);
students.getRange("R4").formulas = [["=IF(H4=\"\",0,1)"]]; students.getRange(`R4:R${3+records.length}`).fillDown();
students.getRange(`D4:D${3+records.length}`).format.numberFormat = "dd-mm-yyyy"; students.getRange(`K4:M${3+records.length}`).format.numberFormat = moneyFormat; students.getRange(`G4:H${3+records.length}`).format.numberFormat = "@";
students.getRange(`N4:N${3+records.length}`).dataValidation = { rule: { type: "list", values: ["READY","REVIEW","BLOCKED","DO NOT IMPORT"] } };
students.tables.add(`A3:R${3+records.length}`, true, "StudentImportTable").style = "TableStyleMedium4";
students.freezePanes.freezeRows(3); students.freezePanes.freezeColumns(5); students.getRange("A:R").format.font = { name: "Aptos", size: 9 }; students.getRange("A:R").format.columnWidth = 15; students.getRange("A:A").format.columnWidth = 27; students.getRange("E:F").format.columnWidth = 25; students.getRange("J:J").format.columnWidth = 24; students.getRange("O:O").format.columnWidth = 50; students.getRange("O:O").format.wrapText = true; students.getRange(`O4:O${3+records.length}`).format.autofitRows(); students.showGridLines = false;

const paymentHeaders = ["Legacy ID","Source Row","Line","Student","Record Status","Payment Date","Amount","Mode","Transaction Type","Raw Source Text","Import Readiness","ERP Transaction ID","Reviewer Note"];
paymentSheet.getRange("A1:M1").merge(); paymentSheet.getRange("A1").values = [["Payment transaction review — no receipts should be imported before verification"]]; paymentSheet.getRange("A1:M1").format = titleStyle;
paymentSheet.getRange("A3:M3").values = [paymentHeaders]; paymentSheet.getRange("A3:M3").format = headerStyle;
paymentSheet.getRangeByIndexes(3,0,payments.length,paymentHeaders.length).values = payments.map(p => [p.legacyId,p.sourceRow,p.line,p.student,p.status === "active" ? "Active" : "Forfeited",p.date,p.amount,p.mode,p.kind,p.raw,p.readiness,"",p.reviewerNote]);
paymentSheet.getRange(`F4:F${3+payments.length}`).format.numberFormat = "dd-mm-yyyy"; paymentSheet.getRange(`G4:G${3+payments.length}`).format.numberFormat = moneyFormat;
paymentSheet.getRange(`K4:K${3+payments.length}`).dataValidation = { rule: { type: "list", values: ["READY","REVIEW","DO NOT IMPORT"] } };
paymentSheet.tables.add(`A3:M${3+payments.length}`, true, "PaymentReviewTable").style = "TableStyleMedium4";
paymentSheet.freezePanes.freezeRows(3); paymentSheet.freezePanes.freezeColumns(4); paymentSheet.getRange("A:M").format.font = { name: "Aptos", size: 9 }; paymentSheet.getRange("A:M").format.columnWidth = 15; paymentSheet.getRange("A:A").format.columnWidth = 27; paymentSheet.getRange("D:D").format.columnWidth = 24; paymentSheet.getRange("J:J").format.columnWidth = 38; paymentSheet.getRange("M:M").format.columnWidth = 34; paymentSheet.getRange("J:M").format.wrapText = true; paymentSheet.showGridLines = false;

const exceptionRows = records.filter(r => r.issues.length);
exceptions.getRange("A1:G1").merge(); exceptions.getRange("A1").values = [["Exceptions requiring review before ERP import"]]; exceptions.getRange("A1:G1").format = titleStyle;
exceptions.getRange("A3:G3").values = [["Legacy ID","Source Row","Student","Readiness","Issue / Decision Required","Resolved?","Resolution Note"]]; exceptions.getRange("A3:G3").format = headerStyle;
const exceptionLines = exceptionRows.flatMap(r => r.issues.map(issue => [r.legacyId,r.sourceRow,r.student,r.readiness,issue,"No",""]));
exceptions.getRangeByIndexes(3,0,exceptionLines.length,7).values = exceptionLines;
exceptions.getRange(`F4:F${3+exceptionLines.length}`).dataValidation = { rule: { type: "list", values: ["No","Yes","Not applicable"] } };
exceptions.tables.add(`A3:G${3+exceptionLines.length}`, true, "ExceptionTable").style = "TableStyleMedium4";
exceptions.freezePanes.freezeRows(3); exceptions.getRange("A:G").format.font = { name: "Aptos", size: 9 }; exceptions.getRange("A:G").format.columnWidth = 16; exceptions.getRange("A:A").format.columnWidth = 27; exceptions.getRange("C:C").format.columnWidth = 24; exceptions.getRange("E:E").format.columnWidth = 55; exceptions.getRange("G:G").format.columnWidth = 35; exceptions.getRange("E:G").format.wrapText = true; exceptions.getRange(`E4:G${3+exceptionLines.length}`).format.rowHeight = 30; exceptions.showGridLines = false;

source.freezePanes.freezeRows(2);
const output = await SpreadsheetFile.exportXlsx(workbook);
const outputPath = `${outputDir}/Lakshya_Admission_ERP_Import_Staging.xlsx`;
await output.save(outputPath);

const checks = {};
for (const [sheetName, range] of [["Import Summary","A1:H12"],["ERP Mapping","A1:F20"],["Students Import",`A1:R${Math.min(18,3+records.length)}`],["Payment Review",`A1:M${Math.min(18,3+payments.length)}`],["Exceptions",`A1:G${Math.min(18,3+exceptionLines.length)}`],["Admission","A1:J80"]]) {
  checks[sheetName] = (await workbook.inspect({ kind: "table", range: `${sheetName}!${range.split("!").pop()}`, include: "values,formulas", tableMaxRows: 20, tableMaxCols: 18, maxChars: 7000 })).ndjson;
  const preview = await workbook.render({ sheetName, range: range.split("!").pop(), scale: 1.2, format: "png" });
  await fs.writeFile(`${previewDir}/${sheetName.replace(/[^a-z0-9]+/gi,"_")}.png`, new Uint8Array(await preview.arrayBuffer()));
}
checks["Payment Review — manual dates"] = (await workbook.inspect({ kind: "table", range: "Payment Review!A28:M92", include: "values,formulas", tableMaxRows: 70, tableMaxCols: 13, maxChars: 12000 })).ndjson;
const manualDatePreview = await workbook.render({ sheetName: "Payment Review", range: "A28:M92", scale: 1.2, format: "png" });
await fs.writeFile(`${previewDir}/Payment_Review_Manual_Dates.png`, new Uint8Array(await manualDatePreview.arrayBuffer()));
const errors = (await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan" })).ndjson;
await fs.writeFile(`${previewDir}/checks.json`, JSON.stringify({ counts: { active: active.length, cancelled: cancelled.length, payments: payments.length, exceptions: exceptionLines.length, feeTotal: active.reduce((a,r)=>a+r.feeTotal,0), registrationTotal: active.reduce((a,r)=>a+r.registrationTotal,0), ready: records.filter(r=>r.readiness==="READY").length, review: records.filter(r=>r.readiness==="REVIEW").length, blocked: records.filter(r=>r.readiness==="BLOCKED").length }, errors, checks }, null, 2));
console.log(JSON.stringify({ outputPath, manifestPath, sourceHash, active: active.length, cancelled: cancelled.length, payments: payments.length, stagedPaymentTotal: manifest.expected.staged_payment_total, exceptions: exceptionLines.length, feeTotal: active.reduce((a,r)=>a+r.feeTotal,0), registrationTotal: active.reduce((a,r)=>a+r.registrationTotal,0), ready: records.filter(r=>r.readiness==="READY").length, review: records.filter(r=>r.readiness==="REVIEW").length, blocked: records.filter(r=>r.readiness==="BLOCKED").length, errors }, null, 2));
