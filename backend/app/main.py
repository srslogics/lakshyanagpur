import asyncio
from pathlib import Path
from uuid import uuid4
from contextlib import asynccontextmanager
from contextlib import suppress
from functools import cache
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import settings
from .database import SessionLocal, get_db
from .assignment_materials import purge_expired_assignment_materials
from .routers import academics, admissions, attendance, auth, biometric_attendance, communication, examinations, faculty, finance, inventory, portal, push, reports, settings as settings_router, students, timetable, workspace
from .push_notifications import dispatch_pending
from .seed import seed_development_data

async def _assignment_material_cleanup_loop():
    while True:
        with SessionLocal() as db:
            try:
                if purge_expired_assignment_materials(db):
                    db.commit()
            except SQLAlchemyError:
                db.rollback()
        await asyncio.sleep(3600)


async def _push_delivery_loop():
    while True:
        try:
            await asyncio.to_thread(dispatch_pending)
        except Exception:
            # One provider or configuration failure must not permanently stop
            # later delivery attempts for the lifetime of the web process.
            pass
        await asyncio.sleep(20)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.seed_demo_data:
        with SessionLocal() as db: seed_development_data(db)
    cleanup_task = asyncio.create_task(_assignment_material_cleanup_loop())
    push_task = asyncio.create_task(_push_delivery_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        push_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task
        with suppress(asyncio.CancelledError):
            await push_task

app = FastAPI(title="Lakshya Operations API", version="1.0.0", lifespan=lifespan)
FRONTEND_DIR = Path(__file__).resolve().parents[2]
STUDENT_APP_DIR = FRONTEND_DIR / "student-app"
PARENT_APP_DIR = FRONTEND_DIR / "parent-app"
FACULTY_APP_DIR = FRONTEND_DIR / "faculty-app"
ATTENDANCE_APP_DIR = FRONTEND_DIR / "attendance-app"
LAKSHYA_SITE_DIR = FRONTEND_DIR / "lakshya-site"
LEGAL_DIR = FRONTEND_DIR / "legal"
PUBLIC_SITE_PAGES = frozenset({
    "about",
    "contact",
    "dmit",
    "lgsat",
    "programs",
    "results",
    "system",
})
PUBLIC_SITE_ROOT_FILES = frozenset({"script.js", "styles.css", "sw.js"})
PUBLIC_ROOT_FILES = frozenset({
    "app.js",
    "apple-touch-icon.png",
    "auth-shared.css",
    "index.html",
    "lakshya-logo-576.png",
    "lakshya-logo.png",
    "manifest.webmanifest",
    "portal-shared.css",
    "push-client.js",
    "push-shared.css",
    "push-service-worker.js",
    "pwa-icon-192.png",
    "pwa-icon-512.png",
    "runtime-config.js",
    "share-card.png",
    "styles.css",
    "sw.js",
})
OPERATIONS_VIEWS = frozenset({
    "admissions",
    "students",
    "finance",
    "attendance",
    "academics",
    "examinations",
    "timetable",
    "communication",
    "inventory",
    "reports",
    "settings",
})


@cache
def expected_database_revisions() -> frozenset[str]:
    """Read the migration heads shipped with this release.

    Keeping this dynamic prevents a new migration from silently making the
    readiness endpoint unhealthy because of a stale hard-coded revision.
    """
    alembic_config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    return frozenset(ScriptDirectory.from_config(alembic_config).get_heads())


app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
app.include_router(auth.router)
app.include_router(admissions.router)
app.include_router(students.router)
app.include_router(finance.router)
app.include_router(timetable.router)
app.include_router(academics.router)
app.include_router(examinations.router)
app.include_router(attendance.router)
app.include_router(biometric_attendance.router)
app.include_router(communication.router)
app.include_router(inventory.router)
app.include_router(faculty.router)
app.include_router(reports.router)
app.include_router(settings_router.router)
app.include_router(portal.router)
app.include_router(portal.parent_router)
app.include_router(push.router)
app.include_router(workspace.router)

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers.update({
        "x-request-id": request_id,
        "x-lakshya-release": settings.release,
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
        "referrer-policy": "strict-origin-when-cross-origin",
        "permissions-policy": "camera=(), microphone=(), geolocation=()",
        "content-security-policy": (
            "default-src 'self'; "
            "base-uri 'self'; "
            "connect-src 'self'; "
            "font-src 'self' https://fonts.gstatic.com; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "img-src 'self' data:; "
            "manifest-src 'self'; "
            "object-src 'none'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "worker-src 'self'"
        ),
    })
    if request.url.scheme == "https" or request.headers.get("x-forwarded-proto", "").lower() == "https":
        response.headers["strict-transport-security"] = "max-age=31536000; includeSubDomains"
    if request.url.path.startswith("/api/"):
        response.headers["cache-control"] = "no-store"
    elif request.url.path.endswith("/sw.js"):
        response.headers["cache-control"] = "no-cache"
    elif request.url.path.endswith(".webmanifest"):
        response.headers["cache-control"] = "public, max-age=3600, must-revalidate"
    elif Path(request.url.path).suffix.lower() in {
        ".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".ico",
    }:
        response.headers["cache-control"] = (
            "public, max-age=31536000, immutable"
            if request.query_params.get("v")
            else "public, max-age=2592000, stale-while-revalidate=86400"
        )
    else:
        response.headers["cache-control"] = "no-cache"
    return response

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    details = exc.errors()
    for item in details:
        item.pop("ctx", None)
    return JSONResponse(
        content={"error": {"code": "VALIDATION_ERROR", "message": "The request contains invalid data", "details": details}},
        status_code=422,
    )

@app.api_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
def health():
    """Process-level liveness check for Render and external uptime monitors."""
    return {"status": "ok", "service": "lakshya-erp", "release": settings.release}


@app.api_route("/api/health", methods=["GET", "HEAD"])
def readiness(db=Depends(get_db)):
    """Database-aware readiness check for operational diagnostics."""
    try:
        db.execute(text("SELECT 1"))
        if settings.is_render or settings.environment in {"production", "prod"}:
            revisions = frozenset(db.execute(text("SELECT version_num FROM alembic_version")).scalars().all())
            if revisions != expected_database_revisions():
                raise HTTPException(
                    503,
                    detail={
                        "code": "SCHEMA_NOT_READY",
                        "message": "Database migrations are not current",
                    },
                )
    except HTTPException:
        raise
    except SQLAlchemyError as error:
        raise HTTPException(
            503,
            detail={"code": "DATABASE_UNAVAILABLE", "message": "Database health check failed"},
        ) from error
    return {"status": "ok", "service": "lakshya-erp", "release": settings.release}

for static_dir in ("assets", "src"):
    directory = FRONTEND_DIR / static_dir
    if directory.exists(): app.mount(f"/{static_dir}", StaticFiles(directory=directory), name=static_dir)

if STUDENT_APP_DIR.exists():
    app.mount("/student-app", StaticFiles(directory=STUDENT_APP_DIR, html=True), name="student-app")

if PARENT_APP_DIR.exists():
    app.mount("/parent-app", StaticFiles(directory=PARENT_APP_DIR, html=True), name="parent-app")

if FACULTY_APP_DIR.exists():
    app.mount("/faculty-app", StaticFiles(directory=FACULTY_APP_DIR, html=True), name="faculty-app")

if ATTENDANCE_APP_DIR.exists():
    app.mount("/attendance-app", StaticFiles(directory=ATTENDANCE_APP_DIR, html=True), name="attendance-app")

if LEGAL_DIR.exists():
    app.mount("/legal", StaticFiles(directory=LEGAL_DIR, html=True), name="legal")

if LAKSHYA_SITE_DIR.exists():
    app.mount(
        "/lakshya-site/assets",
        StaticFiles(directory=LAKSHYA_SITE_DIR / "assets"),
        name="lakshya-site-assets",
    )


@app.api_route("/lakshya-site", methods=["GET", "HEAD"], include_in_schema=False)
def public_site_root_redirect():
    return RedirectResponse(url="/lakshya-site/", status_code=308)


@app.api_route("/lakshya-site/", methods=["GET", "HEAD"], include_in_schema=False)
def public_site_index():
    return FileResponse(LAKSHYA_SITE_DIR / "index.html")


@app.api_route(
    "/lakshya-site/{site_path:path}",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
def public_site_routes(site_path: str):
    if site_path.endswith(".html"):
        page = site_path.removesuffix(".html")
        if page == "index":
            return RedirectResponse(url="/lakshya-site/", status_code=308)
        if page in PUBLIC_SITE_PAGES:
            return RedirectResponse(url=f"/lakshya-site/{page}", status_code=308)
        raise HTTPException(status_code=404, detail="Not found")
    if site_path in PUBLIC_SITE_PAGES:
        return FileResponse(LAKSHYA_SITE_DIR / f"{site_path}.html")
    if site_path in PUBLIC_SITE_ROOT_FILES:
        return FileResponse(LAKSHYA_SITE_DIR / site_path)
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/attendence", include_in_schema=False)
@app.get("/attendence/", include_in_schema=False)
@app.get("/attendance", include_in_schema=False)
@app.get("/attendance/", include_in_schema=False)
def attendance_app_redirect():
    return RedirectResponse(url="/attendance-app/", status_code=308)

@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def frontend_index(): return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/operations", include_in_schema=False)
@app.get("/operations/", include_in_schema=False)
def operations_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/operations/{view}", include_in_schema=False)
def operations_view(view: str):
    if view not in OPERATIONS_VIEWS:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/operations/students/{student_id}", include_in_schema=False)
def operations_student(student_id: str):
    if not student_id or "/" in student_id:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/operations/finance/ledger/{student_id}", include_in_schema=False)
def operations_student_ledger(student_id: str):
    if not student_id or "/" in student_id:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/{file_path:path}", include_in_schema=False)
def frontend_routes(file_path: str):
    if file_path not in PUBLIC_ROOT_FILES:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(FRONTEND_DIR / file_path)
