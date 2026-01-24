# System Architecture Diagram

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE                               │
│                         Frontend (Next.js)                              │
│                        www.mydost.in:3000                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ChatWindow │ InputBar │ MessageBubble │ Sidebar │ Admin Panel         │
└──────────────────────────────────────────────────────────────────────────┘
                                  ↓↑
                    ✅ CORS FIXED - Can now talk to backend
                                  ↓↑
┌─────────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY / BACKEND                            │
│                   FastAPI Server (Railway)                              │
│          mydost2-backend-production.up.railway.app                     │
├─────────────────────────────────────────────────────────────────────────┤
│  CORS Middleware (Fixed for www.mydost.in)                             │
│    ↓                    ↓                      ↓                        │
│  /api/chat         /api/sports          /api/admin                    │
│  /api/ocr          /api/teer            /api/auth                     │
│  /api/pdf          /api/profile         /api/image                    │
└──────────────────────────────────────────────────────────────────────────┘
                          ↓↑
                    Routes & Services
                          ↓↑
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICES LAYER                                   │
├──────────────────────────┬──────────────────────┬───────────────────────┤
│   LLM Service            │  Sports Service      │  Teer Service         │
│   (Claude API)           │  (Predictions)       │  (Lottery)            │
│                          │                      │                        │
│   • Stream responses     │  • Match prediction  │  • Pattern analysis   │
│   • Token counting       │  • User memory       │  • Number patterns    │
│   • Context building     │  • Accuracy track    │  • Accuracy track     │
├──────────────────────────┼──────────────────────┼───────────────────────┤
│   Search Service         │  Vector Store        │  Cache Service        │
│   (Web Search)           │  (pgvector)          │  (Redis)              │
│                          │                      │                        │
│   • Serper API           │  • Embeddings        │  • Session cache      │
│   • Result parsing       │  • Memory retrieval  │  • Query cache        │
│   • Web context          │  • User isolation    │  • API results        │
└──────────────────────────┴──────────────────────┴───────────────────────┘
                          ↓↑
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKGROUND SCHEDULER                                  │
│                  (APScheduler)                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─ Midnight ──────────┐                                               │
│  │ Fetch Matches       │                                               │
│  │ • Search: "IPL..."  │ ──→ Database: matches table                  │
│  │ • Parse teams/date  │                                               │
│  │ • Store in DB       │                                               │
│  └─────────────────────┘                                               │
│                                                                          │
│  ┌─ 4 PM ──────────────┐                                               │
│  │ Fetch Teer Results  │ ──→ Database: teer_data table                │
│  │ • Search: "teer..." │                                               │
│  │ • Extract numbers   │                                               │
│  │ • Pattern analysis  │                                               │
│  └─────────────────────┘                                               │
│                                                                          │
│  ┌─ Every 6 Hours ─────┐                                               │
│  │ Update Results      │ ──→ Update: matches.result, status           │
│  │ • Check if played   │ ──→ Update: was_correct in predictions      │
│  │ • Fetch result      │ ──→ Recalc: user accuracy                   │
│  │ • Store outcome     │                                               │
│  └─────────────────────┘                                               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                          ↓↑
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA STORAGE LAYER                                │
├──────────────────────────┬──────────────────────┬───────────────────────┤
│   PostgreSQL             │  pgvector (Vector)   │  Redis Cache          │
│   (Primary Database)     │  (Semantic Memory)   │  (Hot Cache)          │
│                          │                      │                        │
│   Tables:                │   • User memories    │   • Session data      │
│   • users                │   • Conversation     │   • Query results     │
│   • matches              │   • Predictions      │   • Match data        │
│   • teer_data            │   • Notes            │   • Teer results      │
│   • user_predictions     │   • Context chunks   │   • Odds data         │
│   • usage_limits         │   (384-dimensional)  │   • TTL: 24h          │
│   • sports_memory        │                      │                        │
└──────────────────────────┴──────────────────────┴───────────────────────┘
```

---

## 🔄 Data Flow Diagram

### User Asks About Sports

```
User Question: "Who wins India vs Australia IPL?"
         │
         ↓
    FastAPI Route (/api/chat)
         │
         ├─→ Language Detection: English
         │
         ├─→ RAG Memory Retrieval
         │   ├─ Vector Store: "User loves cricket"
         │   ├─ User ID: uuid-123
         │   └─ Get: Past India predictions
         │
         ├─→ Feature Detection: Sports Module
         │   └─ Route to: sports_service.py
         │
         ├─→ Get Match Context
         │   ├─ Query: SELECT * FROM matches
         │   │          WHERE team_1='India' AND team_2='Australia'
         │   └─ Get: "India vs Australia - Jan 25, 7 PM, Dubai"
         │
         ├─→ Get User Sports History
         │   ├─ Query: SELECT * FROM user_predictions
         │   │          WHERE user_id='uuid-123' AND prediction_type='match'
         │   └─ Get: User has 15 predictions, 11 correct (73% accuracy)
         │
         ├─→ Web Search (if needed)
         │   ├─ Query Serper: "India vs Australia recent form"
         │   └─ Get: Latest news, stats, odds
         │
         ├─→ Cache Check
         │   ├─ Redis Key: "match_india_australia_odds"
         │   └─ Get: Current betting odds (1.45 vs 2.70)
         │
         ├─→ Build LLM Context
         │   {
         │     "user": {
         │       "interests": ["cricket", "India matches"],
         │       "accuracy": 73%,
         │       "past_predictions": [...]
         │     },
         │     "match": {
         │       "teams": "India vs Australia",
         │       "date": "2025-01-25 19:00",
         │       "venue": "Dubai",
         │       "odds": {"India": 1.45, "Australia": 2.70}
         │     },
         │     "context": {
         │       "india_form": "5 wins in last 6",
         │       "australia_form": "2 wins in last 5",
         │       "head_to_head": "India 7-3"
         │     }
         │   }
         │
         ├─→ Claude AI Generates Response
         │   └─ "Based on your 73% accuracy record and India's
         │      recent form, I predict India wins with 76% confidence..."
         │
         ├─→ Save Prediction
         │   ├─ INSERT INTO user_predictions VALUES (
         │   │    user_id='uuid-123',
         │   │    prediction_type='match',
         │   │    prediction_text='...',
         │   │    confidence_score=76,
         │   │    was_correct=NULL  /* pending */
         │   │  )
         │   └─ Vector Store: Add memory "User predicted India wins..."
         │
         └─→ Return Response to User
              └─ "India with 76% confidence. 
                  You've been right 73% of the time on such predictions."
```

---

## 🎯 When Match Happens

```
Scheduler @ 6 AM Check (or when match is in past)
         │
         ├─→ Query: SELECT * FROM matches
         │          WHERE status='scheduled' AND match_date < NOW()
         │
         ├─→ For Each Completed Match:
         │   │
         │   ├─→ Web Search: "India vs Australia result"
         │   │
         │   ├─→ Parse Result: India won by 23 runs
         │   │
         │   ├─→ Update Matches Table
         │   │   UPDATE matches SET
         │   │   result={'winner': 'India', 'margin': '23 runs'},
         │   │   status='completed'
         │   │
         │   └─→ Find User Predictions for this match
         │       │
         │       ├─→ Query: SELECT * FROM user_predictions
         │       │          WHERE prediction_for='India vs Australia'
         │       │          AND prediction_type='match'
         │       │
         │       └─→ For Each User Prediction:
         │           │
         │           ├─→ Check: Did user predict correctly?
         │           │   If prediction was "India wins" → was_correct=true
         │           │
         │           ├─→ Update Prediction
         │           │   UPDATE user_predictions SET
         │           │   was_correct=true,
         │           │   actual_result='India by 23 runs'
         │           │
         │           ├─→ Recalculate User Accuracy
         │           │   SELECT COUNT(*) as total,
         │           │          SUM(was_correct) as correct,
         │           │          correct/total*100 as accuracy
         │           │
         │           └─→ User Profile Updates
         │               "You now have 73% accuracy (12/16 correct)"
         │
         └─→ Future Query: User asks about predictions
             └─ AI says: "You were right! India won as you predicted"
```

---

## 📊 Memory Retrieval Architecture

```
User Query → Language Detection → Feature Detection
                                       ↓
                            Is it sports-related? YES
                                       ↓
                            ┌──────────────────────┐
                            │  Semantic Search     │
                            │  (pgvector)          │
                            └──────────────────────┘
                                       ↓
                    Query Vector Store with user_id
                                       ↓
         ┌─────────────────────────────┬────────────────────────────────┐
         ↓                             ↓                                ↓
    "Cricket" memory          "India matches" memory          "Past 73% accuracy"
    (Embeddings match)        (Embeddings match)              (Embeddings match)
         │                             │                                │
         └─────────────────────────────┴────────────────────────────────┘
                                       ↓
                    Combine Top 5 Relevant Memories
                                       ↓
                    Add to LLM System Prompt
                                       ↓
                    "User loves cricket, India matches,
                     and has been right 73% of the time..."
                                       ↓
                    AI generates more personalized response
```

---

## 🔐 User Isolation & Privacy

```
User A (ID: uuid-111)              User B (ID: uuid-222)
        │                                  │
        ├─→ Database:                     ├─→ Database:
        │   • Matches (shared)            │   • Matches (shared)
        │   • Predictions (user=111)      │   • Predictions (user=222)
        │   • Memory (user=111)           │   • Memory (user=222)
        │   • Usage (user=111)            │   • Usage (user=222)
        │                                 │
        └─ Cannot see User B data ─ ✅ ─ Cannot see User A data

All queries include: WHERE user_id = 'current_user_id'
All memory retrieval: Filtered by user_id
All predictions: Stored with user_id FK relationship
```

---

## ⚡ Performance Optimization

```
Request comes in:
         │
         ├─→ Check Redis Cache (0-10ms)
         │   ├─ "Did we search this query recently?"
         │   └─ "Is match data fresh?"
         │
         ├─→ If Cache Hit: Return cached response (FAST)
         │
         └─→ If Cache Miss:
             │
             ├─→ Check PostgreSQL (10-50ms)
             │   ├─ Fetch matches
             │   ├─ Fetch user predictions
             │   └─ Fetch usage limits
             │
             ├─→ Check Vector Store (50-100ms)
             │   └─ Semantic search on memories
             │
             ├─→ Optional: Web Search (500-2000ms)
             │   └─ Get latest data
             │
             ├─→ Store in Redis (1-5ms)
             │   └─ Cache for next 24h
             │
             └─→ Return combined response
```

---

## 🎛️ Configuration Management

```
Environment Variables
         │
         ├─→ DATABASE_URL (PostgreSQL)
         │   └─ Connection string
         │
         ├─→ REDIS_URL (Redis Cache)
         │   └─ Connection string
         │
         ├─→ ANTHROPIC_API_KEY (Claude)
         │   └─ LLM API key
         │
         ├─→ SERPER_API_KEY (Web Search)
         │   └─ Search API key
         │
         ├─→ ENVIRONMENT (production/development)
         │   └─ Controls CORS & logging
         │
         └─→ NEXT_PUBLIC_API_URL (Frontend)
             └─ Backend URL
```

---

## 🔄 Complete Request Lifecycle

```
1. Frontend sends message
   └─ POST /api/chat {user_id, message}

2. CORS check ✅ (Fixed)
   └─ Allow from www.mydost.in

3. Route to handler
   └─ routers/chat.py

4. User validation
   └─ Get user from database

5. Language detection
   └─ Detect: English/Hindi/Assamese

6. Feature detection
   └─ Is it sports? → sports_service

7. Memory retrieval
   └─ Vector DB + user_id

8. Web search (if needed)
   └─ Serper API + cache

9. LLM prompt building
   └─ Combine all context

10. Claude API call
    └─ Generate response

11. Save interaction
    └─ Store in vector DB

12. Track usage
    └─ Update usage_limits table

13. Return response
    └─ Stream to frontend

14. Background:
    └─ Cache in Redis
    └─ Update timestamps
    └─ Scheduler jobs run
```

---

## 🚀 Deployment Architecture

```
GitHub Repository
    │
    └─→ Push trigger
        │
        └─→ Railway CI/CD
            │
            ├─→ Build Docker image
            ├─→ Install dependencies (pip install -r requirements.txt)
            ├─→ Start backend (uvicorn main:app)
            ├─→ Initialize PostgreSQL tables
            ├─→ Start Scheduler (APScheduler)
            │
            └─→ Production Running
                │
                ├─→ Backend serves /api/chat, /api/sports, etc.
                ├─→ Scheduler runs jobs automatically
                ├─→ Frontend communicates with CORS ✅
                └─→ Users get predictions with memory ✅
```

---

This architecture ensures:
- ✅ Fast responses (caching)
- ✅ User privacy (isolation)
- ✅ Accurate data (database)
- ✅ Personal recommendations (memory)
- ✅ Automatic updates (scheduler)
- ✅ Scalability (stateless API)
- ✅ Production-ready (Railway deployment)
