export const PAYMENT_YEAR = 2026;

const asText = value => value == null ? "" : String(value).trim();

export const paymentParts = remark => asText(remark)
  .split(/\s*\+\s*|\n+/)
  .map(value => value.trim())
  .filter(Boolean);

export const amountFrom = part => {
  const thousands = part.match(/(\d+(?:\.\d+)?)\s*k\b/i);
  if (thousands) return Math.round(Number(thousands[1]) * 1000);

  const amountBeforeMode = part.match(
    /(\d+(?:\.\d+)?)\s*(?=upi|cash|online|bank|card|cheque|check|gpay|phonepe|neft|imps|rtgs)/i,
  );
  if (!amountBeforeMode) return null;
  const value = Number(amountBeforeMode[1]);
  return Math.round(value <= 100 ? value * 1000 : value);
};

export const paymentDate = part => {
  const matches = [...part.matchAll(/\b(\d{1,2})[-/.](\d{1,2})(?:[-/.](\d{2,4}))?\b/g)];
  if (!matches.length) return null;
  const match = matches[matches.length - 1];
  const day = Number(match[1]);
  const month = Number(match[2]);
  let year = match[3] ? Number(match[3]) : PAYMENT_YEAR;
  if (year < 100) year += 2000;
  const parsed = new Date(Date.UTC(year, month - 1, day));
  if (
    parsed.getUTCFullYear() !== year
    || parsed.getUTCMonth() !== month - 1
    || parsed.getUTCDate() !== day
  ) return null;
  return parsed;
};

export const paymentMode = part => {
  if (/cash/i.test(part)) return "Cash";
  if (/upi|gpay|phonepe/i.test(part)) return "UPI";
  if (/neft|imps|rtgs|bank/i.test(part)) return "Bank";
  if (/cheque|check/i.test(part)) return "Cheque";
  if (/card/i.test(part)) return "Card";
  if (/online/i.test(part)) return "Online";
  return "Unknown";
};

export const parsePaymentRemark = remark => paymentParts(remark).map((raw, index) => ({
  line: index + 1,
  raw,
  amount: amountFrom(raw),
  date: paymentDate(raw),
  mode: paymentMode(raw),
  isIncentive: /incentive/i.test(raw),
}));
