from fastapi import FastAPI

from .auth.router import router as auth_router
from .content.router import router as content_router
from .quiz.router import router as quiz_router
from .reports.router import router as reports_router

app = FastAPI(title="AI-Powered Educational System")

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(content_router, prefix="/api/v1/content", tags=["content"])
app.include_router(quiz_router, prefix="/api/v1/quiz", tags=["quiz"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])


@app.get("/")
async def root():
    """Root endpoint for health checks."""
    return {"message": "AI-Powered Educational System"}
