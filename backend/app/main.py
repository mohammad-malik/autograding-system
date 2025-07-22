from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from .config import get_settings
from .auth import router as auth_router
from .content import router as content_router
from .quiz import router as quiz_router
from .reports import router as reports_router

# Initialize FastAPI app
app = FastAPI(
    title=get_settings().app_name,
    description="AI-Powered Educational System for Content Generation and Automated Grading",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(content_router.router, prefix="/api/v1/content", tags=["Content Generation"])
app.include_router(quiz_router.router, prefix="/api/v1/quiz", tags=["Quiz Assessment"])
app.include_router(reports_router.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/", tags=["Health Check"])
async def root():
    """Root endpoint for health check."""
    return {"message": "AI-Powered Educational System API is running", "status": "healthy"}

@app.get("/api/v1/health", tags=["Health Check"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred", "detail": str(exc)},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 