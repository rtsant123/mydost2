# RAG System Architecture - Already Built! ✅

## What is RAG in MyDost?

**RAG = Retrieval-Augmented Generation**

Your app **doesn't need datasets uploaded**. The RAG system builds knowledge dynamically from:

### 1. **User Conversations** (Automatic)
```
User: "I like cricket"
    ↓
Stored in vector DB with user_id
    ↓
Later: "What sports do I like?"
    ↓
RAG retrieves: "I like cricket" from memory
    ↓
AI responds: "You mentioned you like cricket!"
```

### 2. **Web Search Results** (Automatic)
```
User: "Who won IPL 2025?"
    ↓
Backend searches web via Serper API
    ↓
Results cached in Redis + stored in vector DB
    ↓
AI generates answer with citations
    ↓
Next time someone asks, retrieves from cache
```

### 3. **PDF Uploads** (User provides)
```
User uploads research paper PDF
    ↓
Backend extracts text, splits into chunks
    ↓
Each chunk embedded and stored in vector DB
    ↓
User asks: "What did the paper say about X?"
    ↓
RAG retrieves relevant chunks
    ↓
AI answers based on PDF content
```

### 4. **User Notes** (User provides)
```
User saves note: "My dog's name is Bruno"
    ↓
Stored in vector DB
    ↓
Later: "What's my dog's name?"
    ↓
RAG retrieves note
    ↓
AI responds: "Your dog's name is Bruno!"
```

## Where RAG is Implemented

### ✅ `backend/services/vector_store.py`
```python
# Already has these functions:
- add_memory(user_id, text)           # Store conversation
- retrieve_memories(user_id, query)   # RAG search
- add_pdf_content(user_id, chunks)    # Store PDF
- search_pdf_content(user_id, query)  # Search PDFs
```

### ✅ `backend/routers/chat.py`
```python
async def build_rag_context(user_id, query):
    """Retrieve relevant memories from vector DB"""
    memories = vector_store.retrieve_memories(user_id, query, limit=5)
    return formatted_context
```

### ✅ `backend/services/search_service.py`
```python
# Web search results cached and stored for RAG
search_results = await search_service.async_search(query)
cache_web_search_result(query, results)
```

## RAG Flow in Action

**Example: Sports Prediction Query**

```
User: "Will India win tomorrow's match?"
    ↓
1. Check user's past sports conversations (RAG)
2. Search web for "India cricket match tomorrow prediction" (Serper API)
3. Cache search results (Redis)
4. Store results in vector DB (for future RAG)
5. Combine:
   - User's sports preference (from memory)
   - Web search data (Crictracker, Topbookies)
   - Vector DB matches
6. Generate personalized prediction with citations
```

## No Datasets Needed!

❌ **You don't need to:**
- Upload training datasets
- Pre-load knowledge bases
- Import CSV files

✅ **The system learns from:**
- Every user conversation (auto-stored)
- Every web search (auto-cached)
- Every PDF uploaded (auto-indexed)
- Every note saved (auto-embedded)

## Data Storage Locations

### PostgreSQL Tables
```sql
users              -- User profiles, preferences
usage_limits       -- Per-user daily limits
chat_memories      -- Conversation embeddings (pgvector)
document_chunks    -- PDF content embeddings (pgvector)
```

### Redis Cache
```
web_search:{query_hash}  -- TTL: 30 mins
news:{category}          -- TTL: 15 mins
horoscope:{sign}         -- TTL: 24 hours
```

### Vector Database (pgvector)
```
Embeddings stored with:
- user_id (isolation)
- text content
- metadata (type, timestamp, source)
- 384-dimensional vector
```

## Production Ready Checklist

### Backend Requirements
- [x] Vector store implemented (PostgreSQL + pgvector)
- [x] RAG retrieval working
- [x] Web search integration
- [x] Cache layer (Redis)
- [x] Per-user memory isolation
- [x] Usage tracking

### Missing Configuration (Why you get 404s)

#### Railway Backend Service
```env
DATABASE_URL=${{pgvector.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
ANTHROPIC_API_KEY=your-claude-api-key
SEARCH_API_KEY=your-serper-api-key
SEARCH_API_URL=https://google.serper.dev/search
FRONTEND_URL=https://your-frontend.railway.app
```

#### Railway Frontend Service
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app  ⬅️ THIS IS MISSING!
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXTAUTH_URL=https://your-frontend.railway.app
NEXTAUTH_SECRET=your-generated-secret
```

## Fix 404 Errors

**Problem:** Frontend can't find backend API

**Solution:**

1. **Get Backend URL from Railway:**
   - Go to Railway dashboard
   - Click backend service
   - Copy the domain: `https://mydost-backend-abc123.railway.app`

2. **Set in Frontend Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://mydost-backend-abc123.railway.app
   ```

3. **Redeploy Frontend**

## Test RAG System

Once deployed, test these flows:

### Test 1: Memory
```
You: "My favorite color is blue"
AI: "Got it!"

[Later conversation]
You: "What's my favorite color?"
AI: "Your favorite color is blue!" ✅ (Retrieved from RAG)
```

### Test 2: Web Search + Cache
```
You: "Latest cricket news"
AI: [Searches web, shows results with citations] ✅
    "According to [ESPN](link)..."

[5 minutes later, another user asks same]
AI: [Uses cached results, no new API call] ✅
```

### Test 3: PDF Upload
```
Upload: research-paper.pdf
AI: "I've processed your PDF (15 pages, 3,450 words)"

You: "Summarize the methodology section"
AI: [Retrieves relevant chunks via RAG] ✅
    "The methodology involved..."
```

## Summary

**Your RAG system is ALREADY BUILT!** ✅

You just need to:
1. Set `NEXT_PUBLIC_API_URL` in Railway frontend
2. Set all API keys in Railway backend
3. Deploy both services

No datasets, training data, or additional files needed. The system learns as users interact with it!
