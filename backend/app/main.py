from pathlib import Path
from uuid import uuid4
from contextlib import asynccontextmanager
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
from .routers import academics, admissions, attendance, auth, communication, examinations, faculty, finance, inventory, portal, reports, settings as settings_router, students, timetable
from .seed import seed_development_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.seed_demo_data:
        with SessionLocal() as db: seed_development_data(db)
    yield

app = FastAPI(title="Lakshya Operations API", version="1.0.0", lifespan=lifespan)
FRONTEND_DIR = Path(__file__).resolve().parents[2]
STUDENT_APP_DIR = FRONTEND_DIR / "student-app"
PARENT_APP_DIR = FRONTEND_DIR / "parent-app"
FACULTY_APP_DIR = FRONTEND_DIR / "faculty-app"
ATTENDANCE_APP_DIR = FRONTEND_DIR / "attendance-app"
PUBLIC_ROOT_FILES = frozenset({
    "app.js",
    "apple-touch-icon.png",
    "auth-shared.css",
    "index.html",
    "lakshya-logo-576.png",
    "lakshya-logo.png",
    "manifest.webmanifest",
    "portal-shared.css",
    "pwa-icon-192.png",
    "pwa-icon-512.png",
    "share-card.png",
    "styles.css",
    "sw.js",
})
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
app.include_router(communication.router)
app.include_router(inventory.router)
app.include_router(faculty.router)
app.include_router(reports.router)
app.include_router(settings_router.router)
app.include_router(portal.router)
app.include_router(portal.parent_router)

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers.update({
        "x-request-id": request_id,
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
        "referrer-policy": "strict-origin-when-cross-origin",
        "permissions-policy": "camera=(), microphone=(), geolocation=()",
        "content-security-policy": (
            "default-src 'self'; "
            "base-uri 'self'; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "img-src 'self' data:; "
            "manifest-src 'self'; "
            "object-src 'none'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
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
@app.api_route("/api/health", methods=["GET", "HEAD"])
def health(db=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        if settings.is_render or settings.environment in {"production", "prod"}:
            revision = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
            if revision != "d31f7a9c2e10":
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
    return {"status": "ok", "service": "lakshya-erp"}

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

@app.get("/attendence", include_in_schema=False)
@app.get("/attendence/", include_in_schema=False)
@app.get("/attendance", include_in_schema=False)
@app.get("/attendance/", include_in_schema=False)
def attendance_app_redirect():
    return RedirectResponse(url="/attendance-app/", status_code=308)

@app.get("/", include_in_schema=False)
def frontend_index(): return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/{file_path:path}", include_in_schema=False)
def frontend_routes(file_path: str):
    if file_path not in PUBLIC_ROOT_FILES:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(FRONTEND_DIR / file_path)
