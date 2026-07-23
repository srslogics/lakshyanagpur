# Lakshya ERP

This repository is now the product foundation for the real Lakshya ERP application, with the frontend and FastAPI backend deployable together as one service.

## Current direction

- Build admissions first as the primary working module
- Keep the interface modular and product-ready
- Replace presentation-oriented screens with operational workflows
- Move toward reusable state, forms, role behavior, and backend-ready structure

## Product blueprint

- [Software architecture](docs/software-architecture.md): modules, data model, API boundaries, roles, deployment, and delivery order.
- [Product design system](docs/design-system.md): UI rules, colour and typography tokens, responsive layout, components, and accessibility baseline.
- [Admissions module blueprint](docs/admissions-module-blueprint.md): detailed first-module workflow and data requirements.

## Current product areas

- Dashboard shell
- Admissions CRM workspace
- Student records shell
- Attendance shell
- Fees and finance shell
- Academics and exams shell
- Faculty and timetable shell
- Communication shell
- Reports shell
- Parent app and settings shell

## How to run locally

Run the FastAPI backend from the `backend` directory. It now serves the frontend as well.

Backend:

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

- `http://127.0.0.1:8000/docs` for API docs
- `http://127.0.0.1:8000/` for the product UI
- `http://127.0.0.1:8000/student-app/` for the student portal
- `http://127.0.0.1:8000/parent-app/` for the parent portal
- `http://127.0.0.1:8000/faculty-app/` for the faculty portal

Do not open an app by double-clicking its `index.html` file. The student, parent, and faculty portals require the server above for authentication, API access, and PWA features.

## Deploy on Render

This app can be deployed as a single Render web service.

Render settings:

- Root directory: `backend`
- Runtime: `Python`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/api/health`

Required environment variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ORIGINS` (the deployed Render URL)

Optional:

- `APP_HOST=0.0.0.0`
- `APP_PORT=10000`
- `ACCESS_TOKEN_MINUTES=480`
- `SEED_DEMO_DATA=false` (keep false outside local development)

Database migrations run automatically during the Render build. For local work, run `alembic upgrade head` from `backend` before starting the API. The application does not create production tables implicitly.

## Implemented production foundation

- Signed bearer authentication with PBKDF2 password hashing
- Backend-enforced admissions roles and counsellor ownership filtering
- Validated lead sources, stages, mobile numbers, priorities, and follow-up dates
- Duplicate active-mobile detection with a stable conflict response
- Immutable lead activities and audit events
- Atomic, idempotent conversion from confirmed lead to student, guardian link, enrollment draft, and finance handoff
- Alembic migration for shared users, leads, students, guardians, enrollments, finance handoffs, and audit records
- Automated checks for conversion, duplicate detection, permission denial, and bypass prevention
- Idempotent Excel admissions importer with source-row preservation and full financial reconciliation
- Student and finance read APIs for imported enrollments, fee agreements, and staged payments

## Admission workbook import

The reviewed workbook is converted to a canonical manifest with the staging builder. The manifest is intentionally ignored by Git because it contains student personal data.

```bash
node scripts/build_admission_import_staging.mjs
cd backend
alembic upgrade head
python -m app.importers.legacy_admissions data/imports/admission_2026_27.json --dry-run
python -m app.importers.legacy_admissions data/imports/admission_2026_27.json
```

The importer is idempotent by source-file hash. Active rows create central students, enrollments, finance handoffs, and fee agreements. Cancelled rows remain migration-audit records only. Parsed payment entries remain immutable `staged` transactions until Accounts verifies them; they are not receipts.

The other interface areas remain product shells. Finance transactions, attendance locking, inventory movements, academics, communication adapters, and reporting still need their domain migrations and APIs before those modules should be treated as production-complete.

You can deploy either by using the included `render.yaml` blueprint or by creating the web service manually in the Render dashboard.

## Build approach

1. Finish admissions as the first usable module.
2. Keep admissions connected to the FastAPI + Postgres backend.
3. Add reusable patterns for tables, forms, filters, notes, and profile panels.
4. Expand the same system into the remaining institute modules.
