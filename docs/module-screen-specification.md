# Lakshya ERP: Module Screen Specification

## Purpose

This document converts the approved functional architecture into build-ready product requirements. It defines what each role sees, the records each screen needs, the actions it can perform, and the handoff to the next module.

## Product-wide rules

- Every operational record has an ID, created time, last updated time, and acting user.
- A user can only see records allowed by their role, branch, and assigned workload.
- Every list view supports search, filters, pagination, empty state, loading state, error state, and clear success feedback.
- Every important change is written to the audit log. Financial, conversion, stock, and permission changes need a visible audit history.
- Desktop uses tables where useful. Mobile converts each record into a compact card with status and one primary action.
- Primary actions appear once per screen. Destructive actions require a confirmation and a reason.

## Shared records and navigation

The shared records are **lead**, **student**, **parent**, **course**, **batch**, **enrollment**, **faculty member**, **invoice**, **stock item**, and **user**. A module links to those records instead of creating duplicates.

All detail screens use the same structure:

1. Record identity and current status.
2. Primary action and permitted secondary actions.
3. Tabs for related records and history.
4. Timeline/audit panel where a trace is important.

## 1. Admissions CRM

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Admissions dashboard | Daily leads, due/overdue follow-ups, funnel, source quality, counsellor conversion | Open queue, assign owner, approve exception | Owner, admissions manager |
| Lead queue | Searchable list with student, parent, program, source, owner, stage, priority, next action | Create lead, filter, bulk assign | Manager, counsellor, front desk |
| New lead form | Student and guardian basics, course interest, source, branch, owner, first note | Save lead and schedule first follow-up | Manager, counsellor, front desk |
| Lead detail | Profile, timeline, notes, documents checklist, stage, follow-up history | Log contact, schedule follow-up, change stage, convert, mark lost | Assigned staff and managers |
| Follow-up workspace | Due today, overdue, upcoming, completed follow-ups | Complete, reschedule, escalate | Counsellor, manager |
| Conversion review | Lead facts, selected course/batch, documents, admission date, fee-plan handoff | Confirm conversion | Manager, authorised counsellor |

### Required lead fields

- Student name, guardian name, primary mobile, alternate mobile, preferred program, current class, preferred branch, source, enquiry date, assigned counsellor, stage, priority, and next action date.
- Optional: email, address area, school/college, target examination, campaign, referral source, and initial note.

### Validation and handoff

- Phone number, student name, guardian contact, course interest, source, and assigned owner are required before a lead becomes active.
- Duplicate mobile numbers show existing matching leads before save.
- A lead cannot be converted until course, branch, admission date, responsible guardian, and required document status are confirmed.
- Conversion creates the student, parent link, enrollment draft, fee-plan handoff, and an audit event. Existing lead data is never copied by hand.

## 2. Student Records and Enrollment

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Student directory | Student ID, name, program, batch, status, guardian, fee/attendance flags | Create profile, open record, export permitted list | Admin, coordinator, accounts |
| Student profile | Identity, guardians, enrollment, documents, attendance, finance, academics, communication history | Edit permitted details, add document reference, transfer batch | Admin, coordinator |
| Enrollment workspace | Program, branch, batch, dates, current status and transfer history | Allocate/transfer batch, suspend or close enrollment | Admin, coordinator |
| Document checklist | Required document type, received status, reference link, verification state | Mark verified, request correction | Admin, front desk |

### Required student fields

- Student ID, legal name, date of birth where required, primary guardian, guardian mobile, branch, course/program, active enrollment, batch, admission date, and status.

### Validation and handoff

- A student must have one active enrollment per course/batch combination.
- Batch capacity and timetable compatibility are checked during allocation.
- Parent access is linked only after guardian and student relationship verification.
- Attendance, fee, academic, inventory issue, and communication records reference this single student ID.

## 3. Attendance

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Daily attendance | Selected class session, student roster, present/late/absent/excused state | Mark all, save exceptions, submit register | Faculty, coordinator |
| Attendance exceptions | Late, absent, repeated absence and unmarked registers | Add reason, request correction, notify guardian | Faculty, coordinator |
| Batch attendance review | Percentage, trend, absentee list and unmarked sessions | Open student, export permitted report | Coordinator, owner |
| Student attendance tab | Session-by-session history and percentage | View reason and related communication | Staff with record access; parent read-only |

### Rules

- Attendance can only be marked by faculty assigned to the class session or by an authorised coordinator.
- A register is locked after the configured cutoff; corrections require a reason and create an audit event.
- Repeated absence triggers a review task and may create a parent-notification candidate. Sending remains subject to consent and communication rules.

## 4. Fees and Finance

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Finance dashboard | Collections, dues, upcoming installments, concessions awaiting approval | Open collection queue, approve exception | Owner, accounts lead |
| Fee-plan setup | Course/batch fee plan, installments, due dates, concession policy | Publish plan | Accounts lead |
| Student fee ledger | Invoices, payments, balance, receipts, concession and refund history | Create invoice, record payment, issue receipt | Accounts |
| Due collection queue | Overdue amount, next due date, contact state, assigned follow-up | Record contact, send approved reminder | Accounts, manager |
| Approval queue | Discount, concession, refund or adjustment request with reason | Approve or reject | Owner, authorised accounts lead |

### Rules

- Payments cannot be deleted. Reversals and refunds are separate auditable transactions.
- Receipt numbers are unique and generated by the system.
- A concession or manual adjustment needs the correct approval before it changes the balance.
- Confirmed payments update the student ledger, parent receipt view, collection reporting, and permitted communication reminders.

## 5. Academics, Assignments, Exams and Results

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Batch workspace | Calendar, active students, subjects, faculty, upcoming sessions, assignments and results | Open session, publish assignment, review risk | Faculty, coordinator |
| Assignment composer | Assigned batch, subject, title, instructions, external file link and due date | Publish assignment | Assigned faculty |
| Assignment tracker | Student status: published, viewed, submitted, overdue, reviewed | Mark reviewed, extend due date, send permitted reminder | Faculty, coordinator |
| Exam setup | Exam date, batches, subjects, mark scheme and result publication date | Create exam, assign subjects | Coordinator |
| Marks entry | Eligible student list, marks, absence and remarks | Save draft, publish when approved | Assigned faculty, coordinator |
| Performance review | Batch results, weak topics, student trend and intervention list | Create action note, open student | Faculty, coordinator, owner summary |

### Assignment rules

- A teacher may publish only to batches and subjects they are assigned to.
- The ERP stores assignment metadata, batch eligibility, due date, external Drive link, and student-level status. Assignment files stay outside Supabase Storage to control recurring storage cost.
- Publishing resolves active students in the selected batch. Eligible students see the assignment; parents receive visibility and optional approved notification.
- External file links must be access-controlled by the institute. The system does not expose a general public link by default.

## 6. Faculty and Timetable

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Faculty directory | Profile, subjects, availability, workload and assigned batches | Add/update faculty profile | Coordinator, admin |
| Timetable board | Day/week grid by batch, room and faculty | Create session, move session, request substitute | Coordinator |
| Faculty workspace | Today’s classes, attendance, assignment and class notes shortcuts | Mark attendance, publish assignment | Faculty |
| Conflict review | Faculty, room and batch conflicts before publishing | Resolve conflict, publish timetable | Coordinator |

### Rules

- Published timetable sessions require a valid batch, subject, room, faculty member, date, and duration.
- The system prevents overlapping room and faculty allocation unless an authorised override is recorded.
- Timetable changes create a communication candidate for affected students/parents and update the attendance session roster.

## 7. Inventory and Material Control

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Stock dashboard | Current stock, low-stock alerts, recent inward/issue movements, exceptions | Open low-stock list, create inward | Storekeeper, accounts, owner summary |
| Item master | Item code, category, unit, vendor, opening balance, reorder level and active state | Create/edit item | Storekeeper, admin |
| Purchase inward | Vendor, invoice reference, item lines, quantity, rate, received date | Record inward | Storekeeper, accounts |
| Issue and return register | Issue target, quantity, purpose, batch/student/faculty link, return status | Issue item, accept return, request adjustment | Storekeeper, faculty request |
| Adjustment approval | Difference, reason, evidence and requested quantity | Approve/reject adjustment | Storekeeper lead, accounts/owner per policy |
| Stock history | Immutable movement history with source, destination, actor and time | Filter/export permitted history | Storekeeper, accounts, owner |

### Required controls

- Unique item code, unit of measure, current balance, reorder level, vendor reference, and movement reason.
- Negative stock is blocked. Manual adjustments require reason and approval.
- Every inward, issue, return, write-off, and adjustment creates an immutable stock movement.
- Inward provides finance visibility; issue may link material to a batch, a student, faculty, or an internal department; low stock appears in the owner and storekeeper workspace.

## 8. Communication Hub

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Communication dashboard | Delivery counts, failures, queued journeys and consent exceptions | Open delivery log, pause journey | Admin, manager |
| Template library | Approved templates by purpose and channel | Draft, submit for approval, archive | Admin, manager |
| Message composer | Audience criteria, template, preview, channel and scheduled time | Send test, schedule/send authorised message | Authorised staff |
| Delivery log | Recipient, source event, channel, status, time and retry state | Inspect/retry permitted failures | Admin |

### Rules

- Every message references a source event, recipient, channel, acting user or automation, delivery status, and consent state.
- WhatsApp, SMS, email, and payment messaging are optional adapters. The ERP remains usable before any paid integration is enabled.
- Event candidates include new lead, attendance absence, fee due, published result, timetable change, assignment due, and approved notice.

## 9. Parent App

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Parent home | Linked child selector, attendance, fees, timetable, assignments, results and notices | Open child record, view next action | Parent |
| Attendance and timetable | Daily status, percentage, current timetable and changes | View class details | Parent |
| Fees and receipts | Invoice list, payment status, receipts and permitted payment path | Download receipt, open approved payment link | Parent |
| Learning | Assignments, due dates, external download links, result and teacher notices | Open controlled link | Parent/student |
| Requests | PTM, support or document-related request | Submit request, view response | Parent |

### Rules

- A parent sees only their verified linked child or children.
- Parent views are read-only except for approved request workflows.
- Mobile uses a drawer, large touch targets, compact cards, clear saved/error states, and does not rely on hover-only controls.

## 10. Reporting, Settings and Audit

### Screens

| Screen | Main content | Primary actions | Access |
| --- | --- | --- | --- |
| Owner cockpit | Admissions funnel, collections, attendance, academic risk, faculty load, inventory health and watchlist | Drill into permitted report | Owner, director |
| Report library | Role-aware exports and saved views | Generate/export permitted report | Managers, authorised staff |
| User and role settings | User status, role, branch scope and last access | Invite, deactivate, change role | System admin |
| Master settings | Branches, programs, batches, rooms, fee plans, templates and approval policy | Create/update controlled configuration | System admin, delegated manager |
| Audit explorer | Who changed what, when, source record and before/after context where relevant | Filter/export authorised audit trail | Owner, system admin |

### Rules

- Dashboards summarize; they do not replace operational queues.
- Reports use the same permission boundary as source records.
- Role changes, financial changes, conversion, stock movements, and manual overrides are always auditable.

## API and implementation acceptance

Each implemented screen must have a corresponding backend boundary under `/api`, a schema validation layer, role checks, and test coverage for its main success and failure cases.

Before a feature is accepted, confirm:

1. The user role can perform the intended action and cannot perform restricted actions.
2. Required data, validation, duplicate behavior, loading, empty, error, and success states are visible.
3. The action updates only the shared source record and creates its audit trail.
4. Related modules receive the intended handoff without manual re-entry.
5. The page works on desktop and mobile, with keyboard and readable focus behavior.
