"""Main FastAPI application entry point."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app FIRST before adding middleware
app = FastAPI(
    title="Multi-Domain Conversational AI",
    description="A Claude-like conversational AI with RAG, multiple domains, and admin panel",
    version="1.0.0"
)

# Add CORS middleware FIRST - before any routes
allowed_origins = ["*"]  # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple test endpoints that ALWAYS work
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MyDost API is running", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health():
    """Health check - always responds."""
    return {"status": "ok", "healthy": True, "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def api_health():
    """API health check."""
    return {"status": "ok", "service": "chat-api", "timestamp": datetime.now().isoformat()}


# Try to import and include routers
try:
    from routers import chat, ocr, pdf, image_edit, admin, auth, sports
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(ocr.router, prefix="/api", tags=["ocr"])
    app.include_router(pdf.router, prefix="/api", tags=["pdf"])
    app.include_router(image_edit.router, prefix="/api", tags=["image_editing"])
    app.include_router(admin.router, prefix="/api", tags=["admin"])
    app.include_router(sports.router, prefix="/api", tags=["sports"])
    logger.info("✅ All routers loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Could not load routers: {e}")
    logger.warning("App will run with minimal endpoints only")

# Try to load sports services
try:
    from services.sports_scheduler import scheduler
    from models.sports_data import sports_db
    logger.info("✅ Sports services initialized")
except Exception as e:
    logger.warning(f"⚠️ Could not initialize sports services: {e}")
    scheduler = None
    sports_db = None


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
    
    # Start background scheduler for sports data (gracefully handle failure)
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info("✅ Sports Data Scheduler started")
    except Exception as e:
        logger.warning(f"⚠️ Could not start scheduler: {e}")
        logger.warning("App will continue running without background jobs")


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
