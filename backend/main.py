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

# Add CORS middleware BEFORE importing routers - Allow requests from production domains
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://www.mydost.in",
    "https://mydost.in",
    "https://mydost2-frontend-production.up.railway.app",
    "https://mydost2-backend-production.up.railway.app",
    "*",  # Allow all for now to debug
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Import routers AFTER middleware is added
try:
    from routers import chat, ocr, pdf, image_edit, admin, auth, sports
    print("✅ All routers imported successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not import some routers: {e}")
    print("Some endpoints may not be available")

try:
    from services.sports_scheduler import scheduler
    from models.sports_data import sports_db
    print("✅ Services initialized")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize services: {e}")
    scheduler = None
    sports_db = None

# Include routers - wrap each in try-catch to prevent one bad router from crashing the app
try:
    app.include_router(auth.router, prefix="/api", tags=["auth"])
except Exception as e:
    logger.warning(f"Could not include auth router: {e}")

try:
    app.include_router(chat.router, prefix="/api", tags=["chat"])
except Exception as e:
    logger.warning(f"Could not include chat router: {e}")

try:
    app.include_router(ocr.router, prefix="/api", tags=["ocr"])
except Exception as e:
    logger.warning(f"Could not include ocr router: {e}")

try:
    app.include_router(pdf.router, prefix="/api", tags=["pdf"])
except Exception as e:
    logger.warning(f"Could not include pdf router: {e}")

try:
    app.include_router(image_edit.router, prefix="/api", tags=["image_editing"])
except Exception as e:
    logger.warning(f"Could not include image_edit router: {e}")

try:
    app.include_router(admin.router, prefix="/api", tags=["admin"])
except Exception as e:
    logger.warning(f"Could not include admin router: {e}")

try:
    app.include_router(sports.router, prefix="/api", tags=["sports"])
except Exception as e:
    logger.warning(f"Could not include sports router: {e}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint - always available."""
    return {
        "status": "healthy",
        "service": "Multi-Domain Conversational AI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Multi-Domain Conversational AI API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "ocr": "/api/ocr",
            "pdf": "/api/pdf",
            "image_editing": "/api/image/edit",
            "admin": "/api/admin",
            "sports": "/api/sports",
            "docs": "/docs",
        }
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
