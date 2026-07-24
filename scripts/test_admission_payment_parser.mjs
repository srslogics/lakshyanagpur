import assert from "node:assert/strict";

import {
  amountFrom,
  parsePaymentRemark,
  paymentDate,
  paymentMode,
} from "./admission_payment_parser.mjs";

const installments = parsePaymentRemark("5K Cash 21-1 + 5K Cash 28-3 + 20K UPI 6-6");
assert.deepEqual(
  installments.map(item => ({
    amount: item.amount,
    mode: item.mode,
    date: item.date?.toISOString().slice(0, 10),
  })),
  [
    { amount: 5_000, mode: "Cash", date: "2026-01-21" },
    { amount: 5_000, mode: "Cash", date: "2026-03-28" },
    { amount: 20_000, mode: "UPI", date: "2026-06-06" },
  ],
);

assert.equal(amountFrom("1.5 UPI 25-4"), 1_500);
assert.equal(paymentDate("1.5 UPI 25-4")?.toISOString().slice(0, 10), "2026-04-25");
assert.equal(paymentDate("5K Cash 31-2"), null);
assert.equal(paymentMode("10 K 04-7"), "Unknown");

console.log("Admission payment parser checks passed.");
