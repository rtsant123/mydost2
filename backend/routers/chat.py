"""Chat API routes for conversational interaction."""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from services.llm_service import llm_service
from services.vector_store import vector_store
from services.embedding_service import embedding_service
from services.search_service import search_service
from utils.config import config
from utils.language_detect import detect_language, translate_system_message
from utils.cache import get_cached_response, cache_query_response

router = APIRouter()


# Pydantic models
class Message(BaseModel):
    """Message model."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    include_web_search: bool = False
    language: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    user_id: str
    conversation_id: str
    message: str
    response: str
    language: str
    tokens_used: int
    sources: List[Dict[str, str]] = []
    timestamp: str


class ConversationHistory(BaseModel):
    """Conversation history model."""
    conversation_id: str
    user_id: str
    messages: List[Message]
    created_at: str
    updated_at: str


# In-memory storage (in production, use database)
conversations: Dict[str, ConversationHistory] = {}


async def build_rag_context(user_id: str, query: str) -> str:
    """Build context from vector database for RAG."""
    memories = vector_store.retrieve_memories(
        user_id=user_id,
        query_text=query,
        limit=config.MAX_RETRIEVAL_RESULTS,
    )
    
    if not memories:
        return ""
    
    context = "Relevant previous information:\n"
    for i, memory in enumerate(memories, 1):
        context += f"\n[{i}] {memory.get('text', '')}\n"
    
    return context


async def get_web_search_context(query: str) -> tuple[str, List[Dict[str, str]]]:
    """Get context from web search if needed."""
    context = ""
    sources = []
    
    search_results = await search_service.async_search(query, limit=5)
    if search_results and search_results.get("results"):
        results = search_results["results"]
        context = search_service.format_search_results_for_context(results)
        sources = search_service.extract_citations(results)
    
    return context, sources


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message and get a response.
    
    Features:
    - Multilingual support (auto-detection)
    - RAG retrieval from memory
    - Optional web search
    - Feature module detection
    """
    try:
        # Validate user
        if not request.user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        if conversation_id not in conversations:
            conversations[conversation_id] = ConversationHistory(
                conversation_id=conversation_id,
                user_id=request.user_id,
                messages=[],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )
        
        conversation = conversations[conversation_id]
        
        # Detect language
        detected_language = request.language or detect_language(request.message)
        
        # Add user message to history
        conversation.messages.append(Message(role="user", content=request.message))
        
        # Check cache first
        cached_response = get_cached_response(request.message)
        if cached_response:
            response_text = cached_response
            tokens_used = 0
        else:
            # Build context
            rag_context = await build_rag_context(request.user_id, request.message)
            
            web_search_context = ""
            sources = []
            if request.include_web_search:
                web_search_context, sources = await get_web_search_context(request.message)
            
            # Build final context
            context = rag_context + "\n" + web_search_context if (rag_context or web_search_context) else ""
            
            # Prepare messages for LLM
            system_prompt = config.SYSTEM_PROMPT
            
            # Add context if available
            if context:
                system_prompt += f"\n\nContext information:\n{context}"
            
            # Convert conversation history to message format
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in conversation.messages[-config.CONVERSATION_HISTORY_LIMIT:]
            ]
            
            # Get LLM response
            result = await llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000,
            )
            
            response_text = result.get("response", "")
            tokens_used = result.get("tokens_used", 0)
            
            # Cache the response
            cache_query_response(request.message, response_text)
        
        # Add assistant response to history
        conversation.messages.append(Message(role="assistant", content=response_text))
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now().isoformat()
        
        # Store user message in vector DB for future retrieval
        vector_store.add_memory(
            user_id=request.user_id,
            text=request.message,
            memory_type="message",
            metadata={
                "conversation_id": conversation_id,
                "language": detected_language,
                "response": response_text[:500],  # Store partial response as context
            }
        )
        
        # Update stats
        config.USAGE_STATS['total_messages'] += 1
        config.USAGE_STATS['total_api_calls'] += 1
        
        return ChatResponse(
            user_id=request.user_id,
            conversation_id=conversation_id,
            message=request.message,
            response=response_text,
            language=detected_language,
            tokens_used=tokens_used,
            sources=sources,
            timestamp=datetime.now().isoformat(),
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations(user_id: str):
    """List all conversations for a user."""
    try:
        user_convos = [
            {
                "id": conv.conversation_id,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": len(conv.messages),
                "preview": conv.messages[0].content[:100] if conv.messages else "Empty conversation",
            }
            for conv in conversations.values()
            if conv.user_id == user_id
        ]
        
        return {"conversations": user_convos}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation."""
    try:
        if conversation_id not in conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv = conversations[conversation_id]
        
        return {
            "conversation_id": conv.conversation_id,
            "user_id": conv.user_id,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in conv.messages
            ],
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    try:
        if conversation_id not in conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        del conversations[conversation_id]
        
        return {"success": True, "message": "Conversation deleted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
