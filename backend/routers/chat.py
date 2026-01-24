"""Chat API routes for conversational interaction."""
from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from services.llm_service import llm_service
from services.vector_store import vector_store
from services.embedding_service import embedding_service
from services.search_service import search_service
from models.user import user_db
from models.sports_data import sports_db
from utils.config import config
from utils.language_detect import detect_language, translate_system_message
from utils.cache import get_cached_response, cache_query_response

router = APIRouter()


async def get_personalized_system_prompt(user_id: str) -> str:
    """Get personalized system prompt based on user preferences from database."""
    try:
        # Skip preferences for guest users (they don't exist in users table)
        if user_id.startswith('guest_'):
            preferences = {}
        else:
            # Fetch user preferences directly from database
            prefs_data = user_db.get_preferences(user_id)
            preferences = prefs_data.get("preferences", {})
    except:
        preferences = {}
    
    # Base system prompt
    base_prompt = config.SYSTEM_PROMPT
    
    # Customize based on preferences
    if preferences:
        language = preferences.get("language", "english")
        tone = preferences.get("tone", "friendly")
        interests = preferences.get("interests", [])
        response_style = preferences.get("response_style", "balanced")
        
        # Language instruction
        if language == "hindi":
            base_prompt += "\n\nIMPORTANT: Respond primarily in Hindi (हिंदी). Use Devanagari script."
        elif language == "assamese":
            base_prompt += "\n\nIMPORTANT: Respond primarily in Assamese (অসমীয়া). Use Bengali script."
        
        # Tone customization
        tone_instructions = {
            "friendly": "Use a warm, casual, and friendly tone. Be conversational like talking to a friend.",
            "professional": "Maintain a clear, formal, and professional tone. Be precise and businesslike.",
            "supportive": "Be empathetic, caring, and encouraging. Provide emotional support when needed.",
        }
        base_prompt += f"\n\nTone: {tone_instructions.get(tone, tone_instructions['friendly'])}"
        
        # Response style
        style_instructions = {
            "concise": "Keep responses short and to the point. Maximum 2-3 sentences unless more detail is explicitly requested.",
            "balanced": "Provide moderate detail. Balance brevity with completeness.",
            "detailed": "Provide comprehensive, in-depth explanations with examples and additional context.",
        }
        base_prompt += f"\n\nResponse Style: {style_instructions.get(response_style, style_instructions['balanced'])}"
        
        # Interests context
        if interests:
            base_prompt += f"\n\nUser's main interests: {', '.join(interests)}. Tailor responses to align with these interests when relevant."
    
    return base_prompt


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
    try:
        # Get query embedding
        query_embedding = await embedding_service.embed_text(query)
        
        # Search user's personal memories
        user_memories = vector_store.search_similar(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=3,
        )
        
        # Also search Hinglish dataset (public knowledge)
        hinglish_memories = vector_store.search_similar(
            user_id="hinglish_dataset",
            query_embedding=query_embedding,
            limit=2,
        )
        
        # Combine memories
        all_memories = user_memories + hinglish_memories
        
        if not all_memories:
            return ""
        
        context = "Relevant information:\n"
        for i, memory in enumerate(all_memories, 1):
            content = memory.get('content', '')
            source = memory.get('metadata', {}).get('source', 'conversation')
            context += f"\n[{i}] {content}\n"
        
        return context
    except Exception as e:
        print(f"Error building RAG context: {e}")
        return ""


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


async def get_sports_context(query: str) -> str:
    """Get sports context (matches, teer data) from database if question is about sports."""
    query_lower = query.lower()
    
    # Check if it's a sports/cricket question
    sports_keywords = ["match", "cricket", "ipl", "t20", "india", "australia", "pakistan", 
                      "win", "prediction", "h2h", "teer", "lottery", "team", "plays", "vs", 
                      "versus", "predicts", "forecast", "odds"]
    
    is_sports_question = any(keyword in query_lower for keyword in sports_keywords)
    
    if not is_sports_question:
        return ""
    
    context = ""
    
    # Get upcoming matches from database
    try:
        upcoming_matches = sports_db.get_upcoming_matches(days_ahead=7)
        if upcoming_matches:
            context += "\n📋 UPCOMING MATCHES (from database):\n"
            for match in upcoming_matches[:5]:  # Top 5
                context += f"- {match.get('team_1')} vs {match.get('team_2')} on {match.get('match_date')} at {match.get('venue')}\n"
    except:
        pass
    
    # Get teer results from database
    try:
        teer_results = sports_db.get_teer_results(days_back=7)
        if teer_results:
            context += "\n🎯 RECENT TEER RESULTS:\n"
            for result in teer_results[:3]:  # Last 3
                context += f"- {result.get('date')}: First: {result.get('first_round')}, Second: {result.get('second_round')}\n"
    except:
        pass
    
    return context


def should_trigger_web_search(message: str) -> bool:
    """Auto-detect if web search should be triggered based on keywords."""
    message_lower = message.lower()
    
    # Keywords that indicate current/recent information needed
    time_keywords = [
        'latest', 'recent', 'today', 'now', 'current', 'this week', 'this month',
        'yesterday', 'tonight', 'right now', 'currently', '2026', '2025',
        'breaking', 'update', 'news', 'live'
    ]
    
    # Question words that often need web search
    info_keywords = [
        'what is happening', 'what happened', 'who won', 'who is',
        'when is', 'where is', 'how much', 'price of', 'cost of',
        'weather in', 'temperature', 'forecast', 'result'
    ]
    
    # Domain-specific keywords
    domain_keywords = [
        'stock', 'market', 'cryptocurrency', 'bitcoin', 'election',
        'match', 'score', 'game', 'tournament', 'movie', 'release',
        'restaurant', 'hotel', 'flight', 'ticket', 'teer result'
    ]
    
    # Check for any matching keywords
    all_keywords = time_keywords + info_keywords + domain_keywords
    
    for keyword in all_keywords:
        if keyword in message_lower:
            return True
    
    return False



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
async def chat(request: ChatRequest, http_request: Request):
    """
    Send a chat message and get a response.
    
    Features:
    - Multilingual support (auto-detection)
    - RAG retrieval from memory
    - Optional web search
    - Feature module detection
    - Free limit checking for guests (when enabled)
    """
    try:
        # Validate user
        if not request.user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Check free limits if enabled and user is guest/anonymous
        if config.ENABLE_FREE_LIMITS and (request.user_id == "anonymous-user" or request.user_id.startswith("guest-")):
            # Get client fingerprint
            user_agent = http_request.headers.get("user-agent", "unknown")
            ip = http_request.headers.get("x-forwarded-for", http_request.client.host).split(",")[0]
            fingerprint = config.get_client_fingerprint(user_agent, ip)
            
            # Check current count
            count = user_db.get_guest_usage(fingerprint)
            
            if count >= config.FREE_CHAT_LIMIT:
                raise HTTPException(
                    status_code=403, 
                    detail={
                        "error": "free_limit_exceeded",
                        "message": f"You've used your {config.FREE_CHAT_LIMIT} free messages. Please sign up to continue!",
                        "limit": config.FREE_CHAT_LIMIT,
                        "count": count,
                        "upgrade_required": True
                    }
                )
            
            # Track this message
            user_db.track_guest_usage(fingerprint, ip)
        
        # Check subscription limits for registered users
        elif config.ENABLE_FREE_LIMITS and request.user_id not in ["anonymous-user", "guest"]:
            limit_check = user_db.check_and_increment_message(request.user_id)
            
            if not limit_check.get("allowed", True):
                tier = limit_check.get("tier", "free")
                reason = limit_check.get("reason")
                
                if reason == "lifetime_limit":
                    message = f"You've used all {limit_check['limit']} free messages. Upgrade to continue!"
                elif reason == "daily_limit":
                    message = f"You've reached your daily limit of {limit_check['limit']} messages. Upgrade for more!"
                else:
                    message = "Message limit reached. Please upgrade your plan!"
                
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "subscription_limit_exceeded",
                        "message": message,
                        "tier": tier,
                        "reason": reason,
                        "used": limit_check.get("used", 0),
                        "limit": limit_check.get("limit", 0),
                        "reset_at": limit_check.get("reset_at"),
                        "upgrade_required": True,
                        "plans": {
                            "limited": {"name": "Limited", "price": 399, "messages": "50/day"},
                            "unlimited": {"name": "Unlimited", "price": 999, "messages": "Unlimited"}
                        }
                    }
                )
        
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
        
        # Initialize sources list (must be before conditional blocks)
        sources = []
        
        # Check cache first
        cached_response = get_cached_response(request.message)
        if cached_response:
            response_text = cached_response
            tokens_used = 0
        else:
            # Build context
            rag_context = await build_rag_context(request.user_id, request.message)
            
            # Get sports context from database
            sports_context = await get_sports_context(request.message)
            
            # Auto-detect if web search is needed OR user manually enabled it
            auto_search = should_trigger_web_search(request.message)
            
            web_search_context = ""
            # Trigger web search if: user toggled it ON, auto-detected, or sports question
            if request.include_web_search or auto_search or sports_context:
                web_search_context, sources = await get_web_search_context(request.message)
            
            # Build final context
            context = ""
            if rag_context:
                context += rag_context + "\n"
            if sports_context:
                context += sports_context + "\n"
            if web_search_context:
                context += web_search_context
            
            # Prepare messages for LLM
            system_prompt = await get_personalized_system_prompt(request.user_id)
            
            # Add sports instruction if sports context exists
            if sports_context:
                system_prompt += """

🏏 FOR CRICKET/SPORTS PREDICTIONS:
When answering about sports/cricket/matches:
- Reference the database match data provided
- Analyze H2H records and team performance
- Use web search data for latest odds and news
- Give specific confidence percentage
- Cite your sources: database, web search, historical data"""
            
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
        try:
            message_embedding = await embedding_service.embed_text(request.message)
            vector_store.add_memory(
                user_id=request.user_id,
                content=request.message,
                embedding=message_embedding,
                conversation_id=conversation_id,
                memory_type="message",
                metadata={
                    "language": detected_language,
                    "response": response_text[:500],  # Store partial response as context
                }
            )
        except Exception as e:
            print(f"Error storing memory: {e}")
        
        # Track usage in database per user (disabled for testing)
        # user_db.increment_usage(
        #     user_id=request.user_id,
        #     api_calls=1,
        #     tokens=tokens_used,
        #     web_searches=1 if request.include_web_search and sources else 0
        # )
        
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
