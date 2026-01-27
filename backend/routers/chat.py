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
from services.scrape_service import scrape_service
from models.user import user_db
from models.sports_data import sports_db
from models.predictions_db import PredictionsDB
from utils.config import config
from utils.language_detect import detect_language, translate_system_message
from utils.cache import get_cached_response, cache_query_response, get_cached_search_results, get_web_search_count, increment_web_search_count
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter()
predictions_db = PredictionsDB()  # Initialize predictions cache
in_memory_profiles: Dict[str, Dict[str, Any]] = {}  # fallback when DB not available
in_memory_names: Dict[str, str] = {}  # quick name recall when DB unavailable
CONV_TABLE_READY = False


def _ensure_conv_table():
    """Create lightweight conversation_messages table if missing."""
    global CONV_TABLE_READY
    if CONV_TABLE_READY:
        return
    try:
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_conv_user ON conversation_messages(user_id);
            CREATE INDEX IF NOT EXISTS idx_conv_conv ON conversation_messages(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_conv_user_conv ON conversation_messages(user_id, conversation_id);
        """)
        conn.commit()
        cur.close()
        conn.close()
        CONV_TABLE_READY = True
    except Exception as e:
        print(f"⚠️ Could not ensure conversation_messages table: {e}")


def log_conversation_message(user_id: str, conversation_id: str, role: str, content: str):
    """Persist message for sidebar/history even if vector DB is unavailable."""
    if user_id.startswith("guest_"):
        return  # don't persist guest chats
    try:
        _ensure_conv_table()
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO conversation_messages (conversation_id, user_id, role, content)
            VALUES (%s, %s, %s, %s)
            """,
            (conversation_id, user_id, role, content[:4000])  # guard length
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Could not log conversation message: {e}")


def build_domain_prompt(domain: str) -> str:
    """Return domain-specific formatting instructions for consistent CTA/schema."""
    if domain == "prediction":
        return """
FORMAT AS:
1) Quick verdict: one line win probability or outcome.
2) Probable XIs: two bullet lists (Team A, Team B) with up to 11 names each.
3) Key factors (3 bullets): pitch/conditions, form, matchups.
4) Confidence: single % number.
5) Next actions (2 bullets): what the user can do/track.
Always cite sources with [n]. Keep concise."""
    if domain == "education":
        return """
FORMAT AS:
1) TL;DR: 2 sentences.
2) Steps: short numbered list.
3) Example/analogy: 2 sentences.
4) Visual idea: describe a diagram/animation in one sentence.
5) Practice next: 2 bullet prompts the user can try."""
    if domain == "news":
        return """
FORMAT AS:
1) Top 5 headlines (bullets with [n] source tags, include time if available).
2) One-liner takeaway for each.
3) If data is older than 24h, say 'latest available' and proceed.
4) End with 'Want business, sports, or local next?'"""
    if domain == "horoscope":
        return """
FORMAT AS:
1) Overall vibe (emoji + 1 line)
2) Lucky color/number
3) Focus for today
4) Watch out for
5) One-line action"""
    if domain == "notes":
        return """
FORMAT AS:
1) Title
2) Bullets (3-5 concise points)
3) Action items (checkbox style)
4) Tags (comma-separated)
Keep it short and ready to save."""
    return ""


async def get_personalized_system_prompt(user_id: str) -> str:
    """Get personalized system prompt based on user preferences from database."""
    # Start with in-memory (works for guests and as fallback)
    preferences = in_memory_profiles.get(user_id, {}).get("preferences", {})

    # Logged-in: merge DB prefs on top
    if not user_id.startswith('guest_'):
        try:
            prefs_data = user_db.get_preferences(user_id)
            db_prefs = prefs_data.get("preferences", {}) if prefs_data else {}
            preferences = {**preferences, **db_prefs}
        except Exception as e:
            print(f"⚠️ preferences DB fetch failed: {e}")
    
    # Base system prompt
    base_prompt = config.SYSTEM_PROMPT
    
    # Customize based on preferences
    if preferences:
        language = preferences.get("language", "english")
        tone = preferences.get("tone", "friendly")
        interests = preferences.get("interests", [])
        response_style = preferences.get("response_style", "balanced")
        if "name" in preferences:
            base_prompt += f"\n\nUser's name is {preferences['name']}."
        
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
            # Always update in-memory profile (works for guests and as fallback)
            profile = in_memory_profiles.get(user_id, {"preferences": {}, "interests": []})
            profile["preferences"].update(preferences)
            profile["interests"] = list(set(profile.get("interests", []) + interests))
            in_memory_profiles[user_id] = profile
            if "name" in preferences:
                in_memory_names[user_id] = preferences["name"]

            # Persist for logged-in users
            if not user_id.startswith("guest_"):
                try:
                    vector_store.update_user_profile(
                        user_id=user_id,
                        preferences=preferences,
                        interests=list(set(interests)),  # Remove duplicates
                        increment_messages=True
                    )
                except Exception as e:
                    print(f"⚠️ update_user_profile failed: {e}")

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
        else:
            # Fallback to in-memory session profile
            fallback_prefs = in_memory_profiles.get(user_id, {}).get("preferences", {})
            if fallback_prefs.get("name"):
                profile_context = f"\n## Important: User's name is {fallback_prefs['name']}\n"
            if fallback_prefs:
                profile_context += "\n## What I know about you (session):\n"
                if fallback_prefs.get('location'):
                    profile_context += f"- Location: {fallback_prefs['location']}\n"
                if fallback_prefs.get('preferred_language'):
                    profile_context += f"- Preferred language: {fallback_prefs['preferred_language']}\n"
            if not profile_context and in_memory_names.get(user_id):
                profile_context = f"\n## Important: User's name is {in_memory_names[user_id]}\n"
        
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
        # Quick inline name recall even if DB is down
        if not user_profile and user_conversations:
            found_name = _find_name_in_history(all_user_messages)
            if found_name:
                profile_context += f"\n## Important: User's name is {found_name}\n"
        
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


def _find_name_in_history(messages: List[Message]) -> Optional[str]:
    """Extract last stated name from message history."""
    try:
        for msg in reversed(messages):
            if msg.role != "user":
                continue
            text = msg.content.lower()
            if "my name is" in text:
                parts = msg.content.split("my name is", 1)[1].strip().split()
                if parts:
                    return parts[0].strip(",. ")
            if "call me" in text:
                parts = msg.content.split("call me", 1)[1].strip().split()
                if parts:
                    return parts[0].strip(",. ")
    except Exception:
        return None
    return None


async def get_web_search_context(query: str, is_sports_query: bool = False, user_id: str = None) -> tuple[str, List[Dict[str, str]]]:
    """
    Smart web context builder:
    - One search per freshness window (6h sports/prediction, 24h general)
    - Scrape top results, clean text, and feed concise evidence to the LLM
    - Cache predictions for reuse across users
    """
    context = ""
    sources: List[Dict[str, str]] = []
    freshness_hours = 6 if is_sports_query else 24
    ttl_seconds = freshness_hours * 3600

    match_details = extract_match_details(query) if is_sports_query else None
    sport = detect_sport_type(query) if is_sports_query else None
    query_type = detect_query_type(query) if is_sports_query else None

    # 1) Sports prediction cache (shared) - serves everyone
    if is_sports_query and match_details:
        cached_prediction = predictions_db.get_cached_prediction(
            sport=sport,
            query_type=query_type,
            match_details=match_details
        )
        if cached_prediction:
            print(f"✅ Sports cache hit for {match_details}")
            pred_data = cached_prediction["prediction_data"]
            context = pred_data.get("analysis", "")
            sources = pred_data.get("sources", [])
            predictions_db.increment_view_count(cached_prediction["id"])
            return context, sources

    # 2) Perform web search (one per freshness window) with refined query
    base_query = enhance_sports_query(query) if is_sports_query else query
    search_query = refine_search_query(base_query, is_sports_query=is_sports_query)
    try:
        import asyncio
        search_results = await asyncio.wait_for(
            search_service.async_search(search_query, limit=8, ttl=ttl_seconds),
            timeout=6.0
        )
    except asyncio.TimeoutError:
        print(f"⚠️ Web search timeout for: {search_query}")
        return "", []
    except Exception as e:
        print(f"⚠️ Web search error: {e}")
        return "", []

    if not (search_results and search_results.get("results")):
        print(f"⚠️ Web search returned no results for query: {search_query}")
        return "", []

    # Increment search count only when a real (non-cached) result set is returned
    if user_id and not search_results.get("from_cache"):
        increment_web_search_count(user_id)

    results = search_results["results"][:5]

    # 3) Scrape & condense each result (cached per URL)
    def is_search_engine(url: str) -> bool:
        try:
            host = urlparse(url).hostname or ""
            return any(engine in host for engine in ["google.", "duckduckgo", "bing.", "serper", "search.brave"])
        except:
            return True

    scraped_sources = []
    snippets_for_prompt = []
    idx_display = 1
    for result in results:
        url = result.get("url")
        if not url or is_search_engine(url):
            continue
        page = await scrape_service.fetch_and_parse(url, ttl_seconds=ttl_seconds)
        title = (page.get("title") if page else None) or result.get("title") or "Untitled"
        snippet_text = page.get("text", "") if page else result.get("snippet", "")
        snippet_text = (snippet_text or "")[:600]
        if snippet_text:
            snippets_for_prompt.append(f"[{idx_display}] {title}\n{snippet_text}\nSource: {url}")
            scraped_sources.append({
                "number": str(idx_display),
                "title": title,
                "url": url,
                "source": urlparse(url).hostname or "Unknown",
                "fetched_at": (page or {}).get("fetched_at", datetime.utcnow().isoformat() + "Z")
            })
            idx_display += 1
    
    # Build context chunk for LLM
    if snippets_for_prompt:
        context = "Web Evidence (fresh):\n\n" + "\n\n".join(snippets_for_prompt)
    else:
        context = search_service.format_search_results_for_context(results)
    
    # Prepare citations for UI (use scraped sources if any)
    sources = scraped_sources if scraped_sources else search_service.extract_citations(results)

    # 4) Cache sports prediction bundle for everyone
    if is_sports_query and match_details:
        prediction_data = {
            "query": query,
            "analysis": context,
            "sources": sources,
            "search_results": results,
            "sites_analyzed": [r.get("source") or r.get("url") for r in results if r],
        }
        pred_id = predictions_db.cache_prediction(
            sport=sport,
            query_type=query_type,
            match_details=match_details,
            prediction_data=prediction_data,
            cache_hours=freshness_hours
        )
        if pred_id:
            print(f"💾 Cached sports prediction {match_details} for {freshness_hours}h (ID: {pred_id})")

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
        'breaking', 'update', 'news', 'headline', 'top stories', 'live'
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


def refine_search_query(message: str, is_sports_query: bool = False) -> str:
    """
    Create a concise, search-friendly query instead of sending the full user message.
    - For sports: keep teams/match hints.
    - For general news: ask for today's top headlines.
    - Fallback: trim to key terms (first ~10 words).
    """
    msg = message.strip()
    lower = msg.lower()
    
    # Today's date for news freshness
    today_str = datetime.now().strftime("%B %d, %Y")
    
    if is_sports_query:
        details = extract_match_details(msg)
        if details:
            return f"{details} latest match news and probable XI {today_str}"
        return f"latest sports match updates and probable XI {today_str}"
    
    # If user asked for news / today
    if "news" in lower or "today" in lower or "headline" in lower or "breaking" in lower:
        return f"top news headlines {today_str}"
    
    # Generic fallback: keep only first 10 words
    words = msg.split()
    trimmed = " ".join(words[:10])
    return trimmed


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
        # Ensure user_id present; fallback to fingerprint-based guest ID
        if not request.user_id or request.user_id.strip() == "":
            user_agent = http_request.headers.get("user-agent", "unknown")
            ip = http_request.headers.get("x-forwarded-for", http_request.client.host if http_request.client else "unknown").split(",")[0]
            request.user_id = f"guest_{config.get_client_fingerprint(user_agent, ip)}"
            print(f"🆔 Assigned fallback guest user_id: {request.user_id}")
        
        # Check free limits if enabled and user is guest/anonymous
        if config.ENABLE_FREE_LIMITS and (request.user_id == "anonymous-user" or request.user_id.startswith("guest_") or request.user_id.startswith("guest-")):
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
        # Persist user message for history/sidebar (guests included)
        log_conversation_message(request.user_id, conversation_id, "user", request.message)
        
        # Initialize sources list (must be before conditional blocks)
        sources = []
        
        # Build sports/auto-search signals early (needed for cache bypass)
        sports_context = await get_sports_context(request.message)
        auto_search = should_trigger_web_search(request.message)

        # Check cache first ONLY when no fresh data is requested
        cached_response = None
        if not request.include_web_search and not auto_search and not sports_context:
            cached_response = get_cached_response(request.user_id, request.message)

        if cached_response:
            response_text = cached_response
            tokens_used = 0
        else:
            # Build context
            rag_context = await build_rag_context(request.user_id, request.message)
            
            # Decide if we really need web search: prefer memory first
            search_needed = request.include_web_search or sports_context or (auto_search and not rag_context)

            # Check web search rate limits before allowing search
            can_use_web_search = False
            if search_needed:
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
            # Domain detection for structured CTA/schema
            msg_lower = request.message.lower()
            domain_type = None
            if is_sports_query or any(k in msg_lower for k in ['probable 11', 'probable xi', 'playing 11', 'win probability', 'forecast']):
                domain_type = "prediction"
            elif any(k in msg_lower for k in ['explain', 'class', 'lesson', 'homework', 'notes', 'animation', 'diagram', 'study', 'learn']):
                domain_type = "education"
            elif any(k in msg_lower for k in ['news', 'headline', 'top stories', 'breaking']):
                domain_type = "news"
            elif any(k in msg_lower for k in ['horoscope', 'zodiac', 'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']):
                domain_type = "horoscope"
            elif any(k in msg_lower for k in ['note this', 'save this', 'todo', 'task list', 'reminder']):
                domain_type = "notes"
            
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
                tasks.append(get_web_search_context(request.message, is_sports_query, request.user_id))
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
            elif search_needed and not web_search_context:
                context += "\n[No live web data fetched; rely on memory/known info only. Do NOT fabricate fresh facts.]\n"
            
            # Prepare messages for LLM
            system_prompt = await get_personalized_system_prompt(request.user_id)
            # Inject current date to reduce hallucinated dates
            system_prompt += f"\n\nToday's date: {datetime.now().strftime('%B %d, %Y')} ({datetime.now().strftime('%A')}). Always use this date when referencing 'today'."
            system_prompt += "\n\nUse conversation memory first. Only rely on web evidence when it adds new or more recent info; if you cite web, use [n] tied to sources."
            
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
                system_prompt += "- Cite only when using web evidence; use [1], [2], [3] linked to provided sources.\n"
                system_prompt += "- Place citations immediately after the fact.\n"
                system_prompt += "- If a claim is from memory/RAG, do NOT attach a web citation.\n"
                system_prompt += "- Don't list sources separately; weave them inline.\n"
            elif search_needed and not web_search_context:
                system_prompt += "\nIf no web evidence is available, clearly say live data could not be fetched right now and avoid making up details."

            # Domain-specific structured format
            if domain_type:
                system_prompt += "\n\n" + build_domain_prompt(domain_type)
            
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
        # Persist assistant message for history/sidebar
        log_conversation_message(request.user_id, conversation_id, "assistant", response_text)
        
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
        _ensure_conv_table()
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT conversation_id,
                   MIN(created_at) AS created_at,
                   MAX(created_at) AS updated_at,
                   COUNT(*) AS message_count,
                   MIN(content) FILTER (WHERE role = 'user') AS first_user_msg
            FROM conversation_messages
            WHERE user_id = %s
            GROUP BY conversation_id
            ORDER BY MAX(created_at) DESC
            LIMIT 50
        """, (user_id,))
        rows = cur.fetchall()

        user_convos = []
        for row in rows:
            preview = (row.get('first_user_msg') or '').replace("User said: ", "").replace("User asked: ", "")
            preview = preview[:120] if preview else "Conversation"
            user_convos.append({
                "id": row['conversation_id'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None,
                "message_count": row['message_count'],
                "preview": preview,
            })

        cur.close()
        conn.close()
        # If no DB rows for guest, fall back to in-memory
        if not user_convos and user_id.startswith("guest_"):
            user_convos = []
            for conv in conversations.values():
                if conv.user_id == user_id:
                    user_convos.append({
                        "id": conv.conversation_id,
                        "created_at": conv.created_at,
                        "updated_at": conv.updated_at,
                        "message_count": len(conv.messages),
                        "preview": conv.messages[0].content[:120] if conv.messages else "Conversation",
                    })
            user_convos = sorted(user_convos, key=lambda c: c["updated_at"], reverse=True)

        return {"conversations": user_convos}
    
    except Exception as e:
        # Fallback: for guests, try in-memory conversations so UI still works without DB
        if user_id.startswith("guest_"):
            user_convos = []
            for conv in conversations.values():
                if conv.user_id == user_id:
                    user_convos.append({
                        "id": conv.conversation_id,
                        "created_at": conv.created_at,
                        "updated_at": conv.updated_at,
                        "message_count": len(conv.messages),
                        "preview": conv.messages[0].content[:120] if conv.messages else "Conversation",
                    })
            return {"conversations": sorted(user_convos, key=lambda c: c["updated_at"], reverse=True)}
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation - from vector DB."""
    try:
        _ensure_conv_table()
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT role, content, created_at
            FROM conversation_messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
        """, (conversation_id,))
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = []
        created_at = rows[0]['created_at'] if rows else None
        updated_at = rows[-1]['created_at'] if rows else None

        for row in rows:
            messages.append({"role": row['role'], "content": row['content']})

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
        # Fallback to in-memory conversations if available
        if conversation_id in conversations:
            conv = conversations[conversation_id]
            return {
                "conversation_id": conv.conversation_id,
                "user_id": conv.user_id,
                "messages": [{"role": m.role, "content": m.content} for m in conv.messages],
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
            }
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations")
async def delete_conversations(user_id: str, confirm: bool = False):
    """Delete all conversations for a user (chat history + vector memories)."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to delete all conversations.")
    deleted_conv = 0
    deleted_vectors = 0
    try:
        _ensure_conv_table()
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("DELETE FROM conversation_messages WHERE user_id = %s", (user_id,))
        deleted_conv = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error deleting conversation_messages: {e}")
    try:
        # Also clear vector DB entries for this user to keep state aligned
        vector_store.delete_user_data(user_id)
    except Exception as e:
        print(f"⚠️ Error deleting user data from vector store: {e}")
    return {"deleted_conversation_messages": deleted_conv, "deleted_vectors": deleted_vectors}

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    try:
        _ensure_conv_table()
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("DELETE FROM conversation_messages WHERE conversation_id = %s", (conversation_id,))
        deleted_conv = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error deleting conversation_messages: {e}")
        deleted_conv = 0
    try:
        if hasattr(vector_store, "delete_conversation"):
            vector_store.delete_conversation(conversation_id)
    except Exception as e:
        print(f"⚠️ Error deleting conversation from vector store: {e}")
    # Remove from in-memory fallback
    if conversation_id in conversations:
        del conversations[conversation_id]
    return {"deleted_conversation_messages": deleted_conv}


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
