"""Chat API routes for conversational interaction."""
from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import re
import psycopg2
from psycopg2.extras import RealDictCursor

from services.llm_service import llm_service
from services.vector_store import vector_store
from services.embedding_service import embedding_service
from services.search_service import search_service
from models.user import user_db
from models.sports_data import sports_db
from models.predictions_db import PredictionsDB
from utils.config import config
from utils.language_detect import detect_language, translate_system_message
from utils.cache import get_cached_response, cache_query_response, get_cached_search_results, get_web_search_count, increment_web_search_count

router = APIRouter()
predictions_db = PredictionsDB()  # Initialize predictions cache


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


async def learn_user_preferences(
    user_id: str,
    message: str,
    response: str,
    detected_language: str
) -> None:
    """
    Learn and extract user preferences, interests, likes/dislikes from conversation.
    
    This function analyzes the conversation to build a user profile over time.
    """
    try:
        msg_lower = message.lower()
        
        # Extract preferences (what user explicitly states)
        preferences = {}
        interests = []
        
        # Detect language preference
        if detected_language:
            preferences["preferred_language"] = detected_language
        
        # Detect personal info
        if "my name is" in msg_lower:
            name = message.split("my name is")[-1].strip().split()[0]
            preferences["name"] = name
        elif "call me" in msg_lower:
            name = message.split("call me")[-1].strip().split()[0]
            preferences["name"] = name
        
        # Detect location
        if "i live in" in msg_lower or "i'm from" in msg_lower:
            location = message.split("live in" if "live in" in msg_lower else "from")[-1].strip().split(",")[0]
            preferences["location"] = location
        
        # Detect interests from keywords
        sports = ["cricket", "football", "basketball", "tennis", "sports", "match", "game"]
        tech = ["technology", "coding", "programming", "python", "ai", "machine learning"]
        entertainment = ["movie", "film", "music", "song", "series", "show"]
        education = ["study", "exam", "course", "learning", "school", "college", "university"]
        
        for sport in sports:
            if sport in msg_lower:
                interests.append("sports")
                if sport != "sports":
                    interests.append(sport)
                break
        
        for t in tech:
            if t in msg_lower:
                interests.append("technology")
                break
        
        for e in entertainment:
            if e in msg_lower:
                interests.append("entertainment")
                break
        
        for edu in education:
            if edu in msg_lower:
                interests.append("education")
                break
        
        # Detect likes/dislikes
        if "i like" in msg_lower or "i love" in msg_lower:
            liked_thing = message.split("like" if "like" in msg_lower else "love")[-1].strip().split(".")[0]
            if "likes" not in preferences:
                preferences["likes"] = []
            preferences["likes"].append(liked_thing[:100])
        
        if "i hate" in msg_lower or "i don't like" in msg_lower:
            disliked_thing = message.split("hate" if "hate" in msg_lower else "don't like")[-1].strip().split(".")[0]
            if "dislikes" not in preferences:
                preferences["dislikes"] = []
            preferences["dislikes"].append(disliked_thing[:100])
        
        # Update profile if we learned something
        if preferences or interests:
            vector_store.update_user_profile(
                user_id=user_id,
                preferences=preferences,
                interests=list(set(interests)),  # Remove duplicates
                increment_messages=True
            )
            print(f"🧠 Updated user profile - Preferences: {preferences}, Interests: {interests}")
    
    except Exception as e:
        print(f"⚠️ Error learning user preferences: {e}")


async def should_use_rag(query: str) -> bool:
    """
    Smart classification: Determine if RAG memory search is needed.
    Minimize API costs by only searching when query requires personal/historical context.
    """
    query_lower = query.lower()
    
    # 🎯 ALWAYS USE RAG for these query types:
    memory_triggers = [
        # Personal info - Name queries (English + Hinglish + Hindi)
        'my name', 'who am i', 'about me', 'remember me', 'you know me',
        'mera naam', 'naam batao', 'naam bata', 'naam kya', 'naam hai',
        'मेरा नाम', 'नाम बताओ', 'नाम क्या', 'मैं कौन', 'main kaun',
        'mere naam', 'apna naam', 'aapka naam', 'tumhara naam',
        'tell me my name', 'what is my name', "what's my name", 'do you know my name',
        'naam yaad', 'bhool gaye', 'याद है', 'भूल गए',
        
        # Personal info - Name queries (Assamese)
        'মোৰ নাম', 'নাম কওক', 'মই কোন',
        
        # Personal info - Location & Details
        'where do i live', 'my location', 'my city', 'kaha rehta', 'कहाँ रहता',
        'my age', 'how old', 'kitne saal', 'कितने साल', 'meri umar', 'मेरी उम्र',
        'my job', 'what do i do', 'kya karta', 'क्या करता', 'mera kaam', 'मेरा काम',
        'my birthday', 'janmdin', 'जन्मदिन', 'date of birth',
        
        # Past conversation queries (English + Hindi)
        'we talked', 'we discussed', 'mentioned', 'said before', 'told you',
        'earlier', 'previously', 'last time', 'pichli baar', 'पिछली बार',
        'yesterday', 'kal', 'कल', 'last week', 'pichhle hafte', 'पिछले हफ्ते',
        'last month', 'pichhle mahine', 'पिछले महीने', 'ago', 'pehle', 'पहले',
        'history', 'itihaas', 'इतिहास', 'purani baatein', 'पुरानी बातें',
        
        # Memory/recall queries (English + Hindi)
        'remember', 'yaad hai', 'याद है', 'recall', 'yaad karo', 'याद करो',
        'forgot', 'bhool gaya', 'भूल गया', 'bhool gaye', 'भूल गए',
        'what did i', 'maine kya', 'मैंने क्या', 'did i tell', 'maine bataya',
        'told you', 'bataya tha', 'बताया था', 'mentioned', 'kaha tha', 'कहा था',
        'remember when', 'yaad hai jab', 'याद है जब',
        
        # Personal preferences (English + Hindi)
        'my favorite', 'my favourite', 'mera pasandida', 'मेरा पसंदीदा',
        'i like', 'i love', 'mujhe pasand', 'मुझे पसंद', 'mujhe achha', 'मुझे अच्छा',
        'i prefer', 'i want', 'mujhe chahiye', 'मुझे चाहिए',
        'my interest', 'meri dilchaspi', 'मेरी दिलचस्पी', 'mera shauk', 'मेरा शौक',
        'i hate', 'i dont like', "i don't like", 'mujhe nahi pasand', 'मुझे नहीं पसंद',
        
        # Context-dependent questions (English + Hindi)
        'what was', 'kya tha', 'क्या था', 'tell me about', 'mujhe batao', 'मुझे बताओ',
        'show me', 'dikhao', 'दिखाओ', 'find', 'dhundo', 'ढूंढो',
        'search', 'khojo', 'खोजो', 'check history', 'history dekho',
        
        # User profile queries
        'about myself', 'apne baare', 'अपने बारे', 'my profile', 'mera profile',
        'my details', 'meri jankari', 'मेरी जानकारी', 'my info', 'meri jaankari',
        'what do you know', 'tumhe kya pata', 'तुम्हें क्या पता', 'aapko pata hai',
        
        # Relationship & conversation continuity
        'continue', 'aage batao', 'आगे बताओ', 'phir kya', 'फिर क्या',
        'and then', 'uske baad', 'उसके बाद', 'after that', 'fir', 'फिर',
    ]
    
    if any(trigger in query_lower for trigger in memory_triggers):
        return True
    
    # ❌ SKIP RAG for these query types (save costs):
    skip_triggers = [
        # General knowledge (no personal context needed)
        'what is the definition', 'what does it mean', 'explain the concept',
        'how to make', 'how to create', 'how to build',
        # Math/calculations
        'calculate', 'compute', ' + ', ' - ', ' * ', ' / ', ' = ',
        # Very simple greetings only
        'hello', 'hi there', 'hey there', 'namaste', 'namaskar',
    ]
    
    # Only skip if it's clearly a general query AND short
    is_general = any(skip in query_lower for skip in skip_triggers)
    is_short = len(query.split()) < 5  # Reduced threshold
    
    if is_general and is_short:
        return False
    
    # Default: Use RAG for questions (better safe than miss context)
    if '?' in query or any(q in query_lower for q in [
        'who', 'what', 'when', 'where', 'why', 'how',  # English
        'kaun', 'kya', 'kab', 'kahan', 'kaise', 'kyun',  # Hinglish
        'कौन', 'क्या', 'कब', 'कहाँ', 'कैसे', 'क्यों',  # Hindi
        'কোন', 'কি', 'কেতিয়া', 'কত', 'কেনেকৈ'  # Assamese
    ]):
        return True
    
    return False  # Skip for statements/commands



async def build_rag_context(user_id: str, query: str) -> str:
    """
    SMART RAG: Advanced retrieval with hybrid search, re-ranking, and relevance filtering.
    Techniques: Semantic search + keyword matching + recency boost + relevance scoring
    """
    try:
        # 💰 COST OPTIMIZATION: Check if RAG is needed for this query
        needs_rag = await should_use_rag(query)
        
        # 🧠 ALWAYS LOAD USER PROFILE for personalized context (cheap, fast)
        user_profile = vector_store.get_user_profile(user_id)
        profile_context = ""
        
        if user_profile:
            prefs = user_profile.get('preferences', {})
            interests = user_profile.get('interests', [])
            
            # Build profile context if we have info
            if prefs.get('name'):
                profile_context = f"\n## Important: User's name is {prefs['name']}\n"
            
            if prefs or interests:
                if not profile_context:
                    profile_context = "\n## What I know about you:\n"
                if prefs.get('location'):
                    profile_context += f"- Location: {prefs['location']}\n"
                if prefs.get('preferred_language'):
                    profile_context += f"- Preferred language: {prefs['preferred_language']}\n"
                if interests:
                    profile_context += f"- Interests: {', '.join(interests)}\n"
                if prefs.get('likes'):
                    profile_context += f"- Things you like: {', '.join(prefs['likes'][:3])}\n"
        
        if not needs_rag:
            print(f"⚡ Skipping full RAG - Query doesn't need deep search (cost optimization)")
            return profile_context  # Return just profile
        
        print(f"🔍 Using full RAG - Query needs historical/personal context")
        
        # Check if user is premium
        user_subscription = None
        try:
            user_subscription = user_db.get_subscription_status(user_id)
        except:
            pass
        
        is_premium = user_subscription and user_subscription.get("tier") in ["limited", "unlimited"]
        
        # 1️⃣ QUERY EXPANSION - Generate semantic variations for better recall
        query_lower = query.lower()
        query_keywords = set(query_lower.split())  # Extract keywords for hybrid search
        
        # 2️⃣ GET QUERY EMBEDDING
        query_embedding = await embedding_service.embed_text(query)
        
        # 🎯 DETECT PERSONAL INFO QUERIES - Always prioritize personal facts
        personal_keywords = ['my name', 'i am', "i'm", 'call me', 'who am i', 'about me', 
                            'my birthday', 'my age', 'i live', 'my address', 'my job',
                            'remember', 'dont forget', "don't forget"]
        is_personal_query = any(kw in query_lower for kw in personal_keywords)
        
        # 3️⃣ HYBRID SEARCH - Combine semantic + keyword search
        # 🚀 COMPREHENSIVE SEARCH - Get ALL relevant memories across entire history
        memory_limit = 30 if is_premium else 20  # Much higher limit for comprehensive recall
        
        # Semantic search from user's personal memories (searches ALL user's memories)
        user_memories = vector_store.search_similar(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=memory_limit,
        )
        
        # Semantic search from Hinglish dataset (public knowledge)
        hinglish_memories = []
        try:
            hinglish_memories = vector_store.search_similar(
                user_id="hinglish_dataset",
                query_embedding=query_embedding,
                limit=3,
            )
        except Exception as e:
            print(f"Hinglish search error: {e}")
        
        # 4️⃣ CONVERSATION HISTORY - Recent context (recency-weighted)
        # 🔧 FIX: conversations dict is keyed by conversation_id, not user_id
        # We need to find ALL conversations belonging to this user
        conversation_memories = []
        history_limit = 30 if is_premium else 20  # Increased for better context
        
        # Find all conversations for this user_id
        user_conversations = [conv for conv in conversations.values() if conv.user_id == user_id]
        
        # Collect messages from all user's conversations
        all_user_messages = []
        for conv in user_conversations:
            all_user_messages.extend(conv.messages)
        
        # Sort by timestamp (most recent last) and take recent messages
        recent_messages = all_user_messages[-history_limit:] if all_user_messages else []
        
        if recent_messages:
            # Give higher weight to recent messages
            for idx, msg in enumerate(recent_messages):
                recency_score = (idx + 1) / len(recent_messages)  # 0.0 to 1.0
                
                if msg.role == 'user':
                    conversation_memories.append({
                        'content': msg.content,
                        'metadata': {
                            'source': 'conversation_history',
                            'type': 'user_query',
                            'recency_score': recency_score
                        }
                    })
                elif msg.role == 'assistant':
                    conversation_memories.append({
                        'content': msg.content,
                        'metadata': {
                            'source': 'conversation_history',
                            'type': 'assistant_response',
                            'recency_score': recency_score
                        }
                    })
        
        # 5️⃣ SMART RANKING - Score and re-rank all results
        all_results = []
        
        # Score user memories (semantic similarity is already calculated by vector store)
        for memory in user_memories:
            content = memory.get('content', '')
            metadata = memory.get('metadata', {})
            
            # Keyword matching bonus
            keyword_match_score = sum(1 for kw in query_keywords if kw in content.lower()) / max(len(query_keywords), 1)
            
            # 🎯 PERSONAL INFO BOOST - High priority for personal facts
            is_personal_info = metadata.get('is_personal_info', False)
            personal_boost = 0.3 if is_personal_info else 0.0
            
            # Check if content contains personal declarations
            content_lower = content.lower()
            if any(phrase in content_lower for phrase in ['my name is', 'i am', "i'm", 'call me']):
                personal_boost = 0.3
            
            # Final score: semantic similarity + keyword bonus + personal info boost
            score = 0.7 + (keyword_match_score * 0.3) + personal_boost
            
            all_results.append({
                'content': content,
                'source': memory.get('metadata', {}).get('source', 'memory'),
                'score': score,
                'type': 'memory',
                'is_personal': is_personal_info or personal_boost > 0
            })
        
        # Score Hinglish dataset
        for memory in hinglish_memories:
            content = memory.get('content', '')
            keyword_match_score = sum(1 for kw in query_keywords if kw in content.lower()) / max(len(query_keywords), 1)
            score = 0.6 + (keyword_match_score * 0.3)  # Slightly lower base score for public data
            
            all_results.append({
                'content': content,
                'source': 'hinglish_dataset',
                'score': score,
                'type': 'knowledge'
            })
        
        # Score conversation history (recency-weighted)
        for conv_mem in conversation_memories:
            content = conv_mem.get('content', '')
            recency_score = conv_mem.get('metadata', {}).get('recency_score', 0.5)
            keyword_match_score = sum(1 for kw in query_keywords if kw in content.lower()) / max(len(query_keywords), 1)
            
            # Recent + relevant = high score
            score = (0.4 * recency_score) + (0.3 * keyword_match_score) + 0.3
            
            all_results.append({
                'content': content,
                'source': conv_mem.get('metadata', {}).get('type', 'conversation'),
                'score': score,
                'type': 'conversation'
            })
        
        # 6️⃣ RE-RANK by composite score
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # 7️⃣ RELEVANCE FILTERING - Lower threshold for personal queries
        relevance_threshold = 0.4 if is_personal_query else 0.5  # Lower bar for personal info
        top_results = [r for r in all_results if r['score'] >= relevance_threshold]
        
        # Always include personal info at the top
        personal_results = [r for r in top_results if r.get('is_personal', False)]
        other_results = [r for r in top_results if not r.get('is_personal', False)]
        top_results = personal_results + other_results  # Personal info first
        
        # 8️⃣ DYNAMIC CONTEXT SIZE - Based on premium status
        max_results = 8 if is_premium else 5
        top_results = top_results[:max_results]
        
        if not top_results:
            return profile_context  # Return profile even if no search results
        
        # 9️⃣ FORMAT CONTEXT - Start with profile, then search results
        context = ""
        
        # Add user profile first (personalized context)
        if profile_context:
            context += profile_context + "\n"
        
        # Add search results
        context += f"\n📚 RELEVANT CONTEXT (Top {len(top_results)} from your history):\n"
        if is_premium:
            context += "✨ Premium: Enhanced search depth\n"
        
        for result in top_results:
            content = result['content']
            source_type = result['type']
            score = result['score']
            
            # Truncate long content to save tokens
            if len(content) > 300:
                content = content[:300] + "..."
            
            if source_type == 'memory':
                context += f"\n📝 Personal memory (relevance: {score:.2f}): {content}\n"
            elif source_type == 'knowledge':
                context += f"\n🌐 Knowledge base: {content}\n"
            elif source_type == 'conversation':
                context += f"\n💬 Recent context: {content}\n"
        
        return context
        
    except Exception as e:
        print(f"Error building RAG context: {e}")
        return ""


async def get_web_search_context(query: str, is_sports_query: bool = False) -> tuple[str, List[Dict[str, str]]]:
    """
    Get context from web search with smart predictions caching.
    For sports queries: Check cache first → Fetch ALL expert sites (crictracker, sportskeeda, etc.) → Analyze like RAG → Store for reuse
    """
    context = ""
    sources = []
    
    # SMART SPORTS PREDICTION CACHING
    if is_sports_query:
        # Extract match details for cache lookup
        match_details = extract_match_details(query)
        sport = detect_sport_type(query)
        query_type = detect_query_type(query)
        
        if match_details:
            # Check predictions cache FIRST (one fetch serves millions!)
            cached_prediction = predictions_db.get_cached_prediction(
                sport=sport,
                query_type=query_type,
                match_details=match_details
            )
            
            if cached_prediction:
                print(f"✅ SERVING FROM CACHE: {match_details} (viewed {cached_prediction.get('view_count', 0)} times)")
                # Increment view count
                predictions_db.increment_view_count(cached_prediction['id'])
                
                # Build context from cached data
                pred_data = cached_prediction['prediction_data']
                context = f"\n🏏 EXPERT ANALYSIS (analyzed from {len(pred_data.get('sources', []))} sources):\n\n"
                context += f"Match: {match_details}\n"
                context += f"Combined Analysis: {pred_data.get('analysis', 'N/A')}\n"
                
                if pred_data.get('sources'):
                    context += "\n📊 Expert Sources:\n"
                    for src in pred_data['sources']:
                        context += f"- {src.get('title')}: {src.get('snippet')}\n"
                    sources = pred_data['sources']
                
                return context, sources
    
    # No cache hit - fetch fresh data from expert sites
    # Enhance sports queries to fetch from ALL expert sites (crictracker, sportskeeda, topbookies, etc.)
    search_query = query
    if is_sports_query:
        search_query = enhance_sports_query(query)
    
    # Fetch from multiple sites for comprehensive analysis (like RAG)
    try:
        # Add 5 second timeout to prevent slow searches
        import asyncio
        search_results = await asyncio.wait_for(
            search_service.async_search(search_query, limit=8),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        print(f"⚠️ Web search timeout for: {search_query}")
        return "", []
    except Exception as e:
        print(f"⚠️ Web search error: {e}")
        return "", []
    
    if search_results and search_results.get("results"):
        results = search_results["results"]
        context = search_service.format_search_results_for_context(results)
        sources = search_service.extract_citations(results)
        
        # CACHE SPORTS PREDICTIONS for future users (analyzed from multiple expert sites)
        if is_sports_query and match_details:
            prediction_data = {
                "query": query,
                "analysis": context,
                "sources": sources,
                "search_results": results[:5],  # Store top 5 expert sources
                "sites_analyzed": ["crictracker", "sportskeeda", "topbookies", "cricbuzz", "espncricinfo"]
            }
            
            pred_id = predictions_db.cache_prediction(
                sport=sport,
                query_type=query_type,
                match_details=match_details,
                prediction_data=prediction_data,
                cache_hours=24  # Cache for 24 hours
            )
            if pred_id:
                print(f"💾 CACHED PREDICTION from {len(sources)} expert sites: {match_details} (ID: {pred_id})")
    
    return context, sources


def extract_match_details(query: str) -> Optional[str]:
    """Extract match details like 'India vs Australia' or 'PRS vs SYS'."""
    query_lower = query.lower()
    
    # Pattern: Team1 vs Team2 or Team1-Team2
    patterns = [
        r'([a-zA-Z\s]+?)\s+vs\s+([a-zA-Z\s]+)',
        r'([a-zA-Z]+)\s*-\s*([a-zA-Z]+)',
        r'([a-z]{3})\s+vs\s+([a-z]{3})',  # 3-letter codes like PRS vs SYS
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            return f"{team1} vs {team2}"
    
    return None


def detect_sport_type(query: str) -> str:
    """Detect if query is about cricket or football."""
    query_lower = query.lower()
    
    cricket_keywords = ['cricket', 'ipl', 't20', 'test match', 'odi', 'wicket', 'bowler', 'batsman']
    football_keywords = ['football', 'soccer', 'goal', 'striker', 'midfielder', 'premier league', 'la liga']
    
    if any(kw in query_lower for kw in cricket_keywords):
        return 'cricket'
    elif any(kw in query_lower for kw in football_keywords):
        return 'football'
    
    return 'cricket'  # Default


def detect_query_type(query: str) -> str:
    """Detect type of sports query."""
    query_lower = query.lower()
    
    if 'predict' in query_lower or 'outcome' in query_lower or 'who will win' in query_lower:
        return 'prediction'
    elif 'stats' in query_lower or 'statistics' in query_lower or 'performance' in query_lower:
        return 'stats'
    elif 'compare' in query_lower or 'comparison' in query_lower:
        return 'comparison'
    elif 'upcoming' in query_lower or 'schedule' in query_lower:
        return 'upcoming'
    elif 'head to head' in query_lower or 'h2h' in query_lower:
        return 'head_to_head'
    
    return 'prediction'  # Default


def enhance_sports_query(query: str) -> str:
    """Enhance sports query to fetch match previews and predictions from multiple expert sites."""
    match_details = extract_match_details(query)
    sport = detect_sport_type(query)
    
    if match_details:
        # Add multiple prediction/preview sites for comprehensive analysis
        expert_sites = "crictracker sportskeeda thetopbookies espncricinfo cricbuzz insidesport"
        return f"{match_details} {sport} match preview prediction analysis {expert_sites}"
    
    return query


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
            # Create new conversation
            conversations[conversation_id] = ConversationHistory(
                conversation_id=conversation_id,
                user_id=request.user_id,
                messages=[],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )
            
            # 🧠 LOAD COMPREHENSIVE HISTORY FROM VECTOR DB (for logged-in users)
            # This ensures user sees their previous conversations when they log in
            if not request.user_id.startswith("guest_"):
                try:
                    print(f"🧠 Loading conversation history for user: {request.user_id}")
                    
                    # Get recent messages from vector DB (last 50 messages for full context)
                    query_embedding = await embedding_service.embed_text("recent conversation history")
                    recent_memories = vector_store.search_similar(
                        user_id=request.user_id,
                        query_embedding=query_embedding,
                        limit=50,
                    )
                    
                    # Reconstruct conversation messages
                    loaded_count = 0
                    for memory in reversed(recent_memories):  # Reverse to get chronological order
                        content = memory.get('content', '')
                        metadata = memory.get('metadata', {})
                        role = metadata.get('role', 'user')
                        
                        # Extract actual message content (remove prefixes like "User asked:" or "MyDost replied:")
                        if content.startswith("User asked: "):
                            content = content.replace("User asked: ", "")
                        elif content.startswith("MyDost replied: "):
                            content = content.replace("MyDost replied: ", "")
                        
                        conversations[conversation_id].messages.append(
                            Message(role=role, content=content)
                        )
                        loaded_count += 1
                    
                    if loaded_count > 0:
                        print(f"✅ Loaded {loaded_count} previous messages from vector DB")
                    
                except Exception as e:
                    print(f"⚠️ Could not load conversation history: {e}")
        
        conversation = conversations[conversation_id]
        
        # Detect language
        detected_language = request.language or detect_language(request.message)
        
        # Add user message to history
        conversation.messages.append(Message(role="user", content=request.message))
        
        # Initialize sources list (must be before conditional blocks)
        sources = []
        
        # Check cache first
        cached_response = get_cached_response(request.user_id, request.message)
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
            
            # Check web search rate limits before allowing search
            can_use_web_search = False
            if request.include_web_search or auto_search or sports_context:
                print(f"🔍 Web search triggered: include_web_search={request.include_web_search}, auto_search={auto_search}, sports_context={bool(sports_context)}")
                
                # Get user subscription status if available
                user_subscription = None
                try:
                    user_subscription = user_db.get_subscription_status(request.user_id)
                except:
                    pass
                
                # Determine user's web search limit
                if request.user_id.startswith("guest_") or request.user_id == "anonymous-user":
                    daily_limit = config.WEB_SEARCH_LIMIT_GUEST
                elif user_subscription and user_subscription.get("tier") in ["limited", "unlimited"]:
                    daily_limit = config.WEB_SEARCH_LIMIT_PAID
                else:
                    daily_limit = config.WEB_SEARCH_LIMIT_FREE
                
                # Check current usage
                current_count = get_web_search_count(request.user_id)
                
                # Allow if cached result exists (no cost) OR within limit
                cached_exists = get_cached_search_results(request.message)
                if cached_exists or current_count < daily_limit:
                    can_use_web_search = True
                    print(f"✅ Web search ALLOWED: cached={bool(cached_exists)}, count={current_count}/{daily_limit}")
                    if not cached_exists:  # Only increment if actually searching
                        increment_web_search_count(request.user_id)
                else:
                    # Rate limit exceeded
                    response_text = f"⚠️ Daily analysis limit reached ({daily_limit}/day). "
                    if request.user_id.startswith("guest_"):
                        response_text += "Sign up for more daily analyses! "
                    elif user_subscription and user_subscription.get("tier") == "free":
                        response_text += "Upgrade to Limited Plan (₹399) for 50 analyses/day!"
                    response_text += "\n\nI can still answer from my knowledge. What would you like to know?"
                    
                    return ChatResponse(
                        user_id=request.user_id,
                        conversation_id=conversation_id,
                        message=request.message,
                        response=response_text,
                        language=detected_language,
                        tokens_used=0,
                        sources=[],
                        timestamp=datetime.now().isoformat()
                    )
            
            # Detect if this is a sports query for smart caching
            is_sports_query = any(kw in request.message.lower() for kw in ['cricket', 'football', 'match', 'prediction', 'vs', 'versus', 'team', 'ipl', 't20', 'odds', 'betting'])
            
            # RUN IN PARALLEL for faster response ⚡
            import asyncio
            
            print(f"⚡ Starting parallel tasks: RAG + {'Web Search' if can_use_web_search else 'No web search'}")
            start_time = datetime.now()
            
            # Prepare parallel tasks
            tasks = []
            task_names = []
            
            # Always fetch RAG context
            tasks.append(build_rag_context(request.user_id, request.message))
            task_names.append('rag')
            
            # Web search if allowed
            if can_use_web_search:
                tasks.append(get_web_search_context(request.message, is_sports_query))
                task_names.append('web_search')
            
            # Execute in parallel ⚡⚡⚡
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"⚡ Parallel tasks completed in {elapsed:.2f}s")
            
            # Parse results
            rag_context_result = results[0] if not isinstance(results[0], Exception) else ""
            web_search_context = ""
            sources = []
            
            if len(results) > 1 and not isinstance(results[1], Exception):
                web_search_context, sources = results[1]
            
            # Build final context
            context = ""
            if rag_context_result:
                context += rag_context_result + "\n"
            if sports_context:
                context += sports_context + "\n"
            if web_search_context:
                context += "\n� EXPERT DATA:\n" + web_search_context
            
            # Prepare messages for LLM
            system_prompt = await get_personalized_system_prompt(request.user_id)
            
            # Add instructions for using expert data
            if web_search_context:
                system_prompt += "\n\n✅ YOU HAVE EXPERT DATA - ANALYZE AND USE IT! ✅"
                
                # Check if it's sports analysis
                if is_sports_query:
                    system_prompt += "\n\n🏏 SPORTS ANALYSIS MODE:"
                    system_prompt += "\nYou have expert match previews from multiple sources (CricTracker, Sportskeeda, TopBookies, ESPNCricinfo, Cricbuzz)."
                    system_prompt += "\nAnalyze ALL sources - combine insights, compare predictions, provide comprehensive analysis."
                    system_prompt += "\nProvide: Team form, player analysis, pitch conditions, weather, head-to-head, predictions, win probability."
                    system_prompt += "\n\n🎯 CRITICAL: Say 'Based on my analysis...' or 'After analyzing the data...' - NEVER mention 'web search' or 'searching'."
                else:
                    system_prompt += "\nYou have information from multiple sources. Analyze and synthesize it."
                    system_prompt += "\n\n🎯 CRITICAL: Say 'Based on my analysis...' NEVER say 'web search', 'searching', or 'I cannot generate'."
                
                system_prompt += "\nYou ARE the expert analyzing the data. Don't mention the process, just provide insights!"
            
            # Add citation instructions if web search was used
            if web_search_context:
                system_prompt += "\n\n📌 CITATION REQUIREMENTS:\n"
                system_prompt += "- You MUST cite sources using [1], [2], [3] format when using web search information\n"
                system_prompt += "- Example: 'According to recent reports [1], India's economy...'\n"
                system_prompt += "- Place citations immediately after the fact or claim\n"
                system_prompt += "- Every major fact from web search MUST have a citation\n"
                system_prompt += "- Don't just list sources at the end - integrate them naturally\n"
            
            # Add citation instructions if live data was used
            if sources:
                system_prompt += "\n\n📚 CITATION INSTRUCTIONS:"
                system_prompt += "\nYou MUST cite sources using [1], [2], [3] format in your response."
                system_prompt += "\nExample: 'Based on my analysis, Team A has a 65% win probability [1][2]. Their recent form shows...[3]'"
                system_prompt += "\nAt the end, list all sources with their numbers and titles."
            
            # Add sports instruction if sports context exists
            if sports_context:
                system_prompt += """

🏏 FOR CRICKET/SPORTS PREDICTIONS:
When answering about sports/cricket/matches:
- Reference the database match data provided
- Analyze H2H records and team performance
- Combine insights from all expert sources
- Give specific confidence percentage
- Say "Based on my analysis of expert sources..." NOT "According to web search..."
- Cite your sources: [1], [2], [3]"""
            
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
                max_tokens=2000,  # Increased for complete responses
            )
            
            response_text = result.get("response", "")
            tokens_used = result.get("tokens_used", 0)
            
            # Cache the response
            cache_query_response(request.user_id, request.message, response_text)
        
        # Add assistant response to history
        conversation.messages.append(Message(role="assistant", content=response_text))
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now().isoformat()
        
        # 💾 AUTO-SAVE TO VECTOR DB FOR PERSISTENT MEMORY
        # Store both user message AND assistant response for full conversation memory
        try:
            # Only store for logged-in users (not guests)
            if not request.user_id.startswith("guest_"):
                print(f"💾 Storing conversation to vector DB for user: {request.user_id}")
                
                # 🎯 DETECT PERSONAL INFORMATION in user message
                msg_lower = request.message.lower()
                is_personal_info = any(phrase in msg_lower for phrase in [
                    'my name is', 'i am', "i'm", 'call me', 'remember', 
                    'dont forget', "don't forget", 'my birthday', 'i live in',
                    'my age', 'years old', 'my job', 'i work'
                ])
                
                # 1. Store user message
                message_embedding = await embedding_service.embed_text(request.message)
                vector_store.add_memory(
                    user_id=request.user_id,
                    content=f"User said: {request.message}",
                    embedding=message_embedding,
                    conversation_id=conversation_id,
                    memory_type="conversation",
                    metadata={
                        "role": "user",
                        "language": detected_language,
                        "timestamp": datetime.now().isoformat(),
                        "is_personal_info": is_personal_info,  # Flag for priority retrieval
                    }
                )
                
                if is_personal_info:
                    print(f"🎯 Detected personal information - flagged for priority retrieval")
                
                # 2. Store assistant response (for context in future queries)
                response_embedding = await embedding_service.embed_text(response_text)
                vector_store.add_memory(
                    user_id=request.user_id,
                    content=f"MyDost replied: {response_text[:800]}",  # Truncate long responses
                    embedding=response_embedding,
                    conversation_id=conversation_id,
                    memory_type="conversation",
                    metadata={
                        "role": "assistant",
                        "language": detected_language,
                        "timestamp": datetime.now().isoformat(),
                        "query": request.message[:200],  # Store what triggered this response
                    }
                )
                
                print(f"✅ Conversation stored: user message + assistant response")
                
                # 🧠 LEARN USER PREFERENCES AND INTERESTS
                # Extract and store preferences from conversation
                await learn_user_preferences(
                    user_id=request.user_id,
                    message=request.message,
                    response=response_text,
                    detected_language=detected_language
                )
                
            else:
                print(f"⏭️ Skipping vector storage for guest user")
                
        except Exception as e:
            print(f"⚠️ Error storing conversation memory: {e}")
            # Don't fail the request if storage fails
        
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
    """List all conversations for a user - from vector DB."""
    try:
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT conversation_id,
                   MIN(created_at) AS created_at,
                   MAX(created_at) AS updated_at,
                   COUNT(*) AS message_count
            FROM chat_vectors
            WHERE user_id = %s AND conversation_id IS NOT NULL
            GROUP BY conversation_id
            ORDER BY MAX(created_at) DESC
            LIMIT 50
        """, (user_id,))
        rows = cur.fetchall()

        user_convos = []
        for row in rows:
            cur.execute("""
                SELECT content FROM chat_vectors
                WHERE user_id = %s AND conversation_id = %s
                ORDER BY created_at ASC LIMIT 1
            """, (user_id, row['conversation_id']))
            preview_row = cur.fetchone()

            preview = preview_row['content'][:100] if preview_row else "Empty conversation"
            preview = preview.replace("User said: ", "").replace("User asked: ", "")

            user_convos.append({
                "id": row['conversation_id'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None,
                "message_count": row['message_count'],
                "preview": preview,
            })

        cur.close()
        conn.close()
        return {"conversations": user_convos}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation - from vector DB."""
    try:
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT content, metadata, created_at
            FROM chat_vectors
            WHERE conversation_id = %s
            ORDER BY created_at ASC
        """, (conversation_id,))
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = []
        created_at = None
        updated_at = None

        for row in rows:
            metadata = row['metadata'] or {}
            role = metadata.get('role', 'user')
            content = row['content']

            if content.startswith("User said: "):
                content = content.replace("User said: ", "")
            elif content.startswith("User asked: "):
                content = content.replace("User asked: ", "")
            elif content.startswith("MyDost replied: "):
                content = content.replace("MyDost replied: ", "")

            messages.append({"role": role, "content": content})

            if not created_at:
                created_at = row['created_at']
            updated_at = row['created_at']

        cur.close()
        conn.close()

        return {
            "conversation_id": conversation_id,
            "user_id": None,
            "messages": messages,
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""


# ==================== MEMORY MANAGEMENT ENDPOINTS ====================
# Users can view, search, and delete their stored memories

@router.get("/memories")
async def get_user_memories(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    memory_type: Optional[str] = None,
):
    """
    Get all memories for a user with pagination and filtering.
    
    Args:
        user_id: User ID to fetch memories for
        limit: Number of memories to return (default 50)
        offset: Offset for pagination (default 0)
        memory_type: Optional filter by type (conversation, user_memory, etc.)
    """
    try:
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT 
                id,
                content,
                metadata,
                conversation_id,
                type as memory_type,
                created_at,
                1.0 as relevance
            FROM chat_vectors
            WHERE user_id = %s
        """
        params = [user_id]
        
        if memory_type:
            query += " AND type = %s"
            params.append(memory_type)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        memories = []
        for row in rows:
            memories.append({
                "id": row['id'],
                "content": row['content'],
                "metadata": row['metadata'],
                "conversation_id": row['conversation_id'],
                "memory_type": row['memory_type'],
                "created_at": row['created_at'].isoformat(),
            })
        
        count_query = "SELECT COUNT(*) FROM chat_vectors WHERE user_id = %s"
        count_params = [user_id]
        if memory_type:
            count_query += " AND type = %s"
            count_params.append(memory_type)
        
        cur.execute(count_query, count_params)
        total = cur.fetchone()['count']

        cur.close()
        conn.close()
        
        return {
            "memories": memories,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    
    except Exception as e:
        print(f"❌ Error fetching memories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch memories: {str(e)}")


@router.delete("/memories/{memory_id}")
async def delete_memory(memory_id: int, user_id: str):
    """
    Delete a specific memory by ID.
    
    Args:
        memory_id: ID of the memory to delete
        user_id: User ID (for authorization)
    """
    try:
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM chat_vectors WHERE id = %s AND user_id = %s",
            (memory_id, user_id)
        )
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Memory not found or access denied")
        
        return {"message": "Memory deleted successfully", "memory_id": memory_id}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")


@router.delete("/memories")
async def delete_all_memories(user_id: str, confirm: bool = False):
    """
    Delete ALL memories for a user (requires confirmation).
    
    Args:
        user_id: User ID
        confirm: Must be True to actually delete (safety measure)
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=400, 
                detail="Set confirm=true to delete all memories. This action cannot be undone."
            )
        
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_vectors WHERE user_id = %s", (user_id,))
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": f"Successfully deleted {deleted_count} memories",
            "deleted_count": deleted_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting all memories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete memories: {str(e)}")


@router.get("/profile")
async def get_user_profile(user_id: str):
    """
    Get user profile with learned preferences, interests, and conversation stats.
    
    This shows what the AI has learned about the user over time.
    """
    try:
        profile = vector_store.get_user_profile(user_id)
        
        if not profile:
            # Create initial profile if doesn't exist
            vector_store.update_user_profile(
                user_id=user_id,
                preferences={},
                interests=[],
                increment_messages=False
            )
            profile = vector_store.get_user_profile(user_id)
        
        # Get total memories count
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM chat_vectors WHERE user_id = %s", (user_id,))
        memory_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return {
            "user_id": profile['user_id'],
            "preferences": profile['preferences'],
            "interests": profile['interests'],
            "stats": {
                "total_conversations": profile['conversation_count'],
                "total_messages": profile['total_messages'],
                "total_memories": memory_count,
                "first_seen": profile['first_seen'].isoformat(),
                "last_active": profile['last_active'].isoformat(),
            },
            "metadata": profile.get('metadata', {})
        }
    
    except Exception as e:
        print(f"❌ Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")


@router.post("/memories/search")
async def search_memories(
    user_id: str,
    query: str,
    limit: int = 20,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    """
    Search user's memories semantically with optional date filtering.
    
    Args:
        user_id: User ID
        query: Search query (semantic search)
        limit: Max results (default 20)
        date_from: ISO date string (e.g., "2026-01-01") - optional
        date_to: ISO date string - optional
    """
    try:
        query_embedding = await embedding_service.embed_text(query)
        
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        sql_query = """
            SELECT 
                id,
                content,
                metadata,
                conversation_id,
                type as memory_type,
                created_at,
                1 - (embedding <=> %s::vector) as similarity
            FROM chat_vectors
            WHERE user_id = %s
        """
        params = [query_embedding, user_id]
        
        if date_from:
            sql_query += " AND created_at >= %s"
            params.append(date_from)
        
        if date_to:
            sql_query += " AND created_at <= %s"
            params.append(date_to)
        
        sql_query += " ORDER BY similarity DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(sql_query, params)
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row['id'],
                "content": row['content'],
                "metadata": row['metadata'],
                "conversation_id": row['conversation_id'],
                "memory_type": row['memory_type'],
                "created_at": row['created_at'].isoformat(),
                "relevance": float(row['similarity'])
            })

        cur.close()
        conn.close()
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "date_from": date_from,
            "date_to": date_to
        }
    
    except Exception as e:
        print(f"❌ Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {str(e)}")
