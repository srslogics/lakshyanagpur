from pathlib import Path
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import SessionLocal
from .routers import admissions, auth, finance, students
from .seed import seed_development_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.seed_demo_data:
        with SessionLocal() as db: seed_development_data(db)
    yield

app = FastAPI(title="Lakshya Operations API", version="1.0.0", lifespan=lifespan)
FRONTEND_DIR = Path(__file__).resolve().parents[2]
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(admissions.router)
app.include_router(students.router)
app.include_router(finance.router)

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers.update({"x-request-id": request_id, "x-content-type-options": "nosniff", "x-frame-options": "DENY"})
    return response

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        content={"error": {"code": "VALIDATION_ERROR", "message": "The request contains invalid data", "details": exc.errors()}},
        status_code=422,
    )

@app.api_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
@app.api_route("/api/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok", "service": "lakshya-erp"}

for static_dir in ("assets", "src"):
    directory = FRONTEND_DIR / static_dir
    if directory.exists(): app.mount(f"/{static_dir}", StaticFiles(directory=directory), name=static_dir)

@app.get("/", include_in_schema=False)
def frontend_index(): return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/{file_path:path}", include_in_schema=False)
def frontend_routes(file_path: str):
    requested = FRONTEND_DIR / file_path
    return FileResponse(requested if requested.is_file() else FRONTEND_DIR / "index.html")
