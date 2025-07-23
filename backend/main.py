"""Backend entry point for FastAPI server.
Run with:
    uvicorn backend.main:app --reload
or simply:
    python -m backend.main
"""

from pathlib import Path
import sys
import uvicorn
from dotenv import load_dotenv

from backend.app.config import get_settings
from backend.app.auth import router as auth_router
from backend.app.content import router as content_router
from backend.app.quiz import router as quiz_router
from backend.app.reports import router as reports_router

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

# ----------------------------------------------------------------------------
# FastAPI application
# ----------------------------------------------------------------------------
app = FastAPI(
    title=get_settings().app_name,
    description="AI-Powered Educational System for Content Generation and Automated Grading",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(
    content_router.router, prefix="/api/v1/content", tags=["Content Generation"]
)
app.include_router(quiz_router.router, prefix="/api/v1/quiz", tags=["Quiz Assessment"])
app.include_router(reports_router.router, prefix="/api/v1/reports", tags=["Reports"])


# Health endpoints
@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Backend is running", "status": "healthy"}


@app.get("/api/v1/health", tags=["Health Check"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error", "detail": str(exc)},
    )


# ----------------------------------------------------------------------------
# Uvicorn helper
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
