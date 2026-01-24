"""MyDost Backend - Full Production with RAG, Memory, and Multi-domain Support"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers for full feature support
from routers import chat, admin, auth, payment

# Create app
app = FastAPI(title="MyDost API - Production", version="2.0.0")

# Add CORS - allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with full RAG, memory, search capabilities
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(payment.router, prefix="/api", tags=["payment"])

# ============= BASIC ENDPOINTS =============

@app.get("/")
def root():
    """Root endpoint - API status"""
    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    db_url_set = bool(os.getenv("DATABASE_URL"))
    redis_url_set = bool(os.getenv("REDIS_URL"))
    search_key_set = bool(os.getenv("SEARCH_API_KEY"))
    
    return {
        "message": "MyDost API - Production Ready", 
        "version": "2.0.0", 
        "status": "active",
        "time": datetime.now().isoformat(),
        "features": {
            "rag_memory": True,
            "web_search": search_key_set,
            "multi_language": True,
            "vector_db": db_url_set,
            "caching": redis_url_set,
        },
        "api_configured": api_key_set
    }

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 50)
    logger.info("MyDost Backend - PRODUCTION MODE")
    logger.info("Features: RAG, Memory, Search, Multi-Language")
    logger.info("=" * 50)
    
    # Check configuration
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        logger.info(f"✅ ANTHROPIC_API_KEY configured")
    else:
        logger.warning("⚠️ ANTHROPIC_API_KEY not set")
    
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
    logger.info(f"🤖 Using model: {model}")
    
    if os.getenv("DATABASE_URL"):
        logger.info("✅ PostgreSQL/pgvector configured - RAG enabled")
    else:
        logger.warning("⚠️ DATABASE_URL not set - RAG features limited")
    
    if os.getenv("REDIS_URL"):
        logger.info("✅ Redis caching configured")
    else:
        logger.info("ℹ️ Redis not configured - using in-memory cache")
    
    if os.getenv("SEARCH_API_KEY"):
        logger.info("✅ Web search configured (Serper)")
    else:
        logger.info("ℹ️ Web search not configured")
    
    logger.info("=" * 50)

# ============= ERROR HANDLER =============

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    """Global error handler"""
    logger.error(f"Error: {exc}")
    return {"error": str(exc), "status": 500}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main_production:app", host="0.0.0.0", port=port, reload=False)
