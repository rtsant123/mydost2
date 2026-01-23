"""Main FastAPI application entry point."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging

# Import routers
from routers import chat, ocr, pdf, image_edit, admin, auth, sports
from services.sports_scheduler import scheduler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Multi-Domain Conversational AI",
    description="A Claude-like conversational AI with RAG, multiple domains, and admin panel",
    version="1.0.0"
)

# Add CORS middleware - Allow requests from all origins in development, specific in production
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://www.mydost.in",
    "https://mydost.in",
    "https://mydost2-frontend-production.up.railway.app",
]

# Allow all origins if in development mode
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(ocr.router, prefix="/api", tags=["ocr"])
app.include_router(pdf.router, prefix="/api", tags=["pdf"])
app.include_router(image_edit.router, prefix="/api", tags=["image_editing"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(sports.router, prefix="/api", tags=["sports"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Multi-Domain Conversational AI",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Multi-Domain Conversational AI API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "ocr": "/api/ocr",
            "pdf": "/api/pdf",
            "image_editing": "/api/image/edit",
            "admin": "/api/admin",
            "health": "/health",
        },
        "documentation": "/docs",
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Multi-Domain Conversational AI Backend")
    logger.info("Configuration loaded successfully")
    
    # Start background scheduler for sports data
    try:
        scheduler.start()
        logger.info("✅ Sports Data Scheduler started")
    except Exception as e:
        logger.warning(f"⚠️ Could not start scheduler: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Multi-Domain Conversational AI Backend")
    
    # Stop scheduler
    try:
        scheduler.stop()
        logger.info("✅ Sports Data Scheduler stopped")
    except Exception as e:
        logger.warning(f"⚠️ Error stopping scheduler: {e}")
    logger.info("Shutting down Multi-Domain Conversational AI Backend")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true",
    )
