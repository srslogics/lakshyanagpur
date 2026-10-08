# Finance safety changes — 8 October 2026

## Deployment requirement

Apply migration `f91a20c8d631` (after `e73b91c8f240`) before serving the updated frontend. It adds the request replay table used by finance and inventory; it does not rewrite existing payments or balances. Publish the versioned operations and parent assets together with the backend. Deployment remains a separate step.

## Included

- Persistent replay protection for payment, refund/reversal and instalment creation when the updated client supplies its stable request key.
- Per-receipt database locking while checking and posting corrections.
- Successful saves are distinguished from list-refresh failures.
- Append-only compensation for historical offsets when imports are excluded, reapproved, redated, voided or reversed. Real refunds retain their financial effect.
- Imported approval rejects future dates; closed accounts cannot restore cancelled instalments.
- Fee amendments are recorded prospectively with dates, shown in ledger history, and included in exports. Previous amendments made before this release are not reconstructed.
- Consistent current agreement selection; explicit account ledger buttons preserve the chosen agreement.
- Parent history shows signed refund/correction amounts and account credits, excluding unapproved/excluded imports.
- Report cache invalidation, stable same-day ledger ordering and corrected reconciliation labels.

## Verification

Full backend suite: 254 passed, with one dependency deprecation warning. Frontend parser, attendance grouping, assignment upload, dashboard, timetable, finance safety, negative marks, report downloads and lifecycle checks pass. New migration upgrade/downgrade tested on isolated SQLite.

The follow-up audit fixes also repair parent provisioning and isolate test throttling, preserve saved payroll history after device linkage, deduplicate staff workdays, block conflicting payroll evidence, fetch historical staff attendance by month, apply subject-aware class rosters, and avoid fabricated arrival times. Operations PDF attachments and half-day payroll previews are corrected. Transaction-scoped PostgreSQL locks protect examination publication, attendance submission and timetable conflict checks; attendance submission now commits once.

## Remaining rollout checks and policy boundaries

- Production PostgreSQL concurrent-request testing and browser end-to-end acceptance remain to be performed before production sign-off. SQLite tests do not prove PostgreSQL concurrency behavior.
- No live account balances were reconciled or repaired. Existing bad data must be reviewed before any compensating entries are posted.
- Historical payments at/before a confirmed client snapshot continue to follow the existing “already included” policy. Genuinely omitted historical payments require an explicit client reconciliation decision.
- Instalments remain payment schedules, not per-instalment receipt allocation. No new payment-allocation policy was invented.
- Existing whole-rupee precision remains unchanged.
