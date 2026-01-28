from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.routers import upload, assignments, export
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    settings.upload_dir.mkdir(exist_ok=True)
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    description="Upload syllabi and extract assignments with AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["assignments"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/")
async def root():
    return {"message": "Syllabus Parser API", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
