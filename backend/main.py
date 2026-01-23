"""Minimal working FastAPI backend for MyDost"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    return {"message": "MyDost API Working", "version": "1.0.0", "time": datetime.now().isoformat()}

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok", "healthy": True}

# ============= CHAT ENDPOINT =============

@app.post("/api/chat")
async def chat(request: dict):
    """Chat with Claude"""
    try:
        from anthropic import Anthropic
        
        message = request.get("message", "")
        if not message:
            return {"error": "No message"}
        
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": message}],
        )
        
        text = response.content[0].text if response.content else "No response"
        
        return {
            "response": text,
            "sources": [],
            "conversation_id": request.get("conversation_id", f"conv_{datetime.now().timestamp()}"),
            "user_id": request.get("user_id", "anonymous"),
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"error": str(e), "response": "Error processing request"}

# ============= CONVERSATIONS ENDPOINT =============

@app.get("/api/conversations")
def get_conversations(user_id: str = "anonymous-user"):
    """Get conversations for user"""
    return {"conversations": []}

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
