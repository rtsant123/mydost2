"""Minimal working FastAPI backend for MyDost"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load .env if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    conversation_id: str = ""

# Create app
app = FastAPI(title="MyDost API", version="1.0.0")

# Add CORS - allow all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        from anthropic import Anthropic
        
        if not req.message:
            raise HTTPException(status_code=400, detail="Message required")
        
        # Get API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not set in environment")
            return {
                "response": "API key not configured on server. Please set ANTHROPIC_API_KEY environment variable.",
                "sources": [],
                "conversation_id": req.conversation_id or f"conv_{datetime.now().timestamp()}",
                "user_id": req.user_id,
                "error": "API_KEY_NOT_SET"
            }
        
        # Call Claude
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
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
