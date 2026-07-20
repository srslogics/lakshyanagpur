import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const source = "/Users/shubhamsingh/Desktop/Lakshaya-Docs/Admission Sheet .xlsx";
const previewDir = "/tmp/lakshya-admission-previews";
await fs.mkdir(previewDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(source));

const sheetInfo = JSON.parse((await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 20000 })).ndjson.split("\n").filter(Boolean).map(JSON.parse).find(x => x.type === "sheet_summary")?.data ? "null" : "null");
console.log((await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 16000, tableMaxRows: 8, tableMaxCols: 18, tableMaxCellChars: 100 })).ndjson);

const sheets = workbook.worksheets.items;
const manifest = [];
for (let i = 0; i < sheets.length; i++) {
  const sheet = sheets[i];
  const used = sheet.getUsedRange();
  const values = used?.values ?? [];
  const formulas = used?.formulas ?? [];
  const rows = values.length;
  const cols = rows ? Math.max(...values.map(r => r.length)) : 0;
  const nonEmptyRows = values.filter(r => r.some(v => v !== null && v !== "")).length;
  const formulaCount = formulas.flat().filter(Boolean).length;
  manifest.push({ index: i, name: sheet.name, rows, cols, nonEmptyRows, formulaCount, sample: values.slice(0, 12) });
  const preview = await workbook.render({ sheetName: sheet.name, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${String(i + 1).padStart(2, "0")}.png`, new Uint8Array(await preview.arrayBuffer()));
}
await fs.writeFile(`${previewDir}/manifest.json`, JSON.stringify(manifest, null, 2));
console.log(JSON.stringify(manifest, null, 2));
