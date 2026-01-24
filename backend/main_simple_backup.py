"""MyDost Backend - Full Production with RAG, Memory, and Multi-domain Support"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
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
from routers import chat, admin
# Uncomment these as you enable features:
# from routers import ocr, pdf, image_edit

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
# Add more routers as needed:
# app.include_router(ocr.router, prefix="/api", tags=["ocr"])
# app.include_router(pdf.router, prefix="/api", tags=["pdf"])

# ============= BASIC ENDPOINTS =============

@app.get("/")
def root():
    """Root endpoint"""
    # Debug: show if API key is set
    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "message": "MyDost API Working", 
        "version": "1.0.0", 
        "time": datetime.now().isoformat(),
        "api_key_configured": api_key_set
    }

@app.on_event("startup")
async def startup():
    """App startup"""
    logger.info("=" * 50)
    logger.info("MyDost Backend Starting")
    logger.info("=" * 50)
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        logger.info(f"✅ ANTHROPIC_API_KEY is set (length: {len(api_key)})")
    else:
        logger.warning("⚠️ ANTHROPIC_API_KEY not found in environment")
        # List all env vars that contain "KEY" or "API"
        for key, value in os.environ.items():
            if "KEY" in key.upper() or "API" in key.upper():
                logger.info(f"Found env var: {key} = {value[:20]}...")
    
    logger.info("=" * 50)

# ============= CHAT ENDPOINT =============

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Chat with Claude"""
    try:
        # Get API key FIRST before importing
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not set")
            return {
                "response": "Error: API key not configured",
                "sources": [],
                "conversation_id": req.conversation_id or f"conv_{datetime.now().timestamp()}",
                "user_id": req.user_id,
                "error": "API_KEY_NOT_SET"
            }
        
        # Now import and use Anthropic with explicit key
        from anthropic import Anthropic
        
        if not req.message:
            raise HTTPException(status_code=400, detail="Message required")
        
        # Create client with explicit API key
        client = Anthropic(api_key=api_key)
        
        # Get model from environment or use default
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
        
        # Get system prompt
        system_prompt = os.getenv("SYSTEM_PROMPT", """You are MyDost, a helpful and friendly AI assistant specialized in multiple domains.

**Your Capabilities:**
- Education: Answer questions across all subjects (history, science, math, etc.)
- Sports: Provide match predictions and analysis
- Teer: Analyze lottery results and provide predictions
- Astrology: Give daily horoscopes and astrological insights
- Web Search: Search the internet for current information
- OCR: Extract text from images
- PDF Processing: Read and answer questions from PDF documents
- News: Summarize latest news articles
- Personal Memory: Remember user preferences and past conversations

**How You Work:**
- You can search the web when you need current information
- You have access to long-term memory to recall past conversations
- You respond in the same language as the user (Assamese, Hindi, or English)
- You're warm, conversational, and supportive

**Important:**
- Your name is MyDost, NOT Claude
- Always cite sources when using web search results
- If a feature is disabled, politely inform the user

Be helpful, accurate, and admit when you're unsure!""")
        
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": req.message}],
        )
        
        text = response.content[0].text if response.content else "No response"
        
        return {
            "response": text,
            "sources": [],
            "conversation_id": req.conversation_id or f"conv_{datetime.now().timestamp()}",
            "user_id": req.user_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return {
            "response": f"Error: {str(e)}",
            "sources": [],
            "conversation_id": req.conversation_id or f"conv_{datetime.now().timestamp()}",
            "user_id": req.user_id,
            "error": str(e)
        }

# ============= CONVERSATIONS ENDPOINT =============

@app.get("/api/conversations")
def get_conversations(user_id: str = "anonymous-user"):
    """Get conversations for user"""
    try:
        # For now, return empty list - in production would query database
        return {"conversations": []}
    except Exception as e:
        logger.error(f"Conversations error: {e}")
        return {"conversations": [], "error": str(e)}

# ============= ERROR HANDLER =============

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    """Global error handler"""
    logger.error(f"Error: {exc}")
    return {"error": str(exc), "status": 500}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
