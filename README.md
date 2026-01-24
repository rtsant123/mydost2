# MyDost - Multi-Domain AI Chatbot

## 🎯 Product Vision

MyDost is a domain-focused AI chatbot designed for Indian users with **multi-language support** (English, Hinglish, Hindi, Assamese). The product focuses on three core domains:

1. **Sports** - Cricket & Football predictions, stats, player analysis (NOT live scores)
2. **Education** - Multi-language homework help, concept learning, exam preparation  
3. **Horoscope** - Daily predictions, zodiac compatibility, astrology insights

**Key Philosophy:**
- **Predictions, not live data** - Cache predictions for 24 hours, share across all users (cost-efficient)
- **Multi-language first** - Hinglish as default, full support for regional languages
- **Smart caching** - One API call serves all users for same query
- **Premium features** - Extended memory (50 messages vs 20), priority access, full history

---

## 🏗️ Architecture

### Tech Stack
- **Backend:** FastAPI (Python 3.11)
- **Frontend:** Next.js 14, React, TailwindCSS
- **Database:** PostgreSQL + pgvector (conversation memory & caching)
- **LLM:** Claude 3.5 Haiku (Anthropic)
- **Search:** SerpAPI (primary) → DuckDuckGo (free fallback)
- **OCR:** Tesseract.js (client-side, free)
- **Deployment:** Railway (backend) + Vercel (frontend)

### Database Schema

**Main Tables:**
- `users` - User accounts, subscription tiers
- `conversations` - Chat history with timestamps
- `predictions` - Cached sports predictions (24hr TTL)
- `player_stats` - Cached player statistics (7 day TTL)
- `vector_embeddings` - Semantic search for RAG

**Vector Store (pgvector):**
- Personal memories (user-specific notes)
- Conversation history (last 20/50 messages)
- Hinglish dataset (public knowledge)

---

## 📁 Project Structure

```
mydost2/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routers/
│   │   ├── chat.py             # Main chat API, RAG, web search
│   │   ├── auth.py             # User authentication
│   │   ├── autocomplete.py     # Domain-specific suggestions
│   │   ├── admin.py            # Admin endpoints
│   │   └── user.py             # User preferences & subscription
│   ├── services/
│   │   ├── llm_service.py      # Claude API integration
│   │   ├── search_service.py   # SerpAPI → DuckDuckGo fallback
│   │   ├── duckduckgo_search.py # Free search API
│   │   ├── embedding_service.py # Text embeddings for RAG
│   │   └── vector_store.py     # pgvector operations
│   ├── models/
│   │   ├── user.py             # User database model
│   │   ├── sports_data.py      # Sports caching model
│   │   └── predictions_db.py   # Predictions caching (NEW)
│   ├── utils/
│   │   ├── config.py           # Environment variables
│   │   ├── cache.py            # Redis/in-memory cache
│   │   └── language_detect.py  # Language detection
│   └── scripts/
│       ├── init_predictions_db.py # Initialize predictions tables
│       └── load_hinglish_dataset.py # Load knowledge base
├── frontend/
│   ├── pages/
│   │   ├── index.js            # Homepage (chat interface)
│   │   ├── sports.js           # Sports predictions page (NEW)
│   │   ├── education.js        # Education help page (NEW)
│   │   ├── horoscope.js        # Horoscope page (NEW)
│   │   └── tools/
│   │       ├── pdf.js          # PDF upload & chat
│   │       ├── ocr.js          # Image text extraction
│   │       └── test-search.js  # Web search testing
│   ├── components/
│   │   ├── ChatWindow.jsx      # Main chat UI
│   │   ├── InputBar.jsx        # Message input with autocomplete
│   │   ├── SportsModal.jsx     # Sports query form
│   │   ├── EducationModal.jsx  # Education query form
│   │   └── MoreDomainsModal.jsx # Domain navigation
│   └── utils/
│       └── apiClient.js        # API client
└── README.md                   # This file
```

---

## ✅ Completed Features (v1.0)

### 1. **Sports Domain** ✅
**Location:** `/frontend/pages/sports.js`, `/backend/models/predictions_db.py`

**What's Built:**
- ✅ Cricket & Football ONLY
- ✅ 6 query types:
  - 🔮 Match Prediction (win probability)
  - 📊 Player Stats (performance, records)
  - ⚔️ Player Comparison (head-to-head)
  - 🎯 Team Analysis (form, strengths)
  - 📅 Upcoming Matches (schedule with predictions)
  - 🏆 Head-to-Head Records

**Database Caching:**
- Table: `predictions` (match details, prediction data, expires_at)
- Table: `player_stats` (player name, stats data)
- Cache: 24 hours
- Shared across all users
- View count tracking

---

### 2. **Education Domain** ✅
**Location:** `/frontend/pages/education.js`

**What's Built:**
- ✅ 4 Languages: English, Hinglish, Hindi, Assamese
- ✅ Age-appropriate (Class 1-5 gets simple explanations)
- ✅ 4 help types: Homework, Concept Learning, Exam Prep, Doubt Solving
- ✅ All boards: CBSE, ICSE, State Board

---

### 3. **Horoscope Domain** ✅
**Location:** `/frontend/pages/horoscope.js`

**What's Built:**
- ✅ 12 Zodiac Signs
- ✅ Daily/Weekly/Monthly predictions
- ✅ Love & relationships
- ✅ Compatibility matching

---

### 4. **Web Search** ✅
**Priority:** Cache → SerpAPI → DuckDuckGo (free fallback)

---

### 5. **Smart Autocomplete** ✅
Domain-specific suggestions for sports, education, horoscope

---

### 6. **RAG System** ✅
**Memory:**
- Free: 20 messages + 3 personal memories
- Premium: 50 messages + 5 personal memories

---

## 🚧 TODO / Remaining Work

### 🔴 HIGH PRIORITY - Work Until Satisfied

#### 1. **Personal Notes/Memory Management** 🚨
**Status:** Backend exists, UI missing

**What's Missing:**
- ❌ UI to view all saved memories
- ❌ Add new note with category
- ❌ Edit existing note
- ❌ Delete note
- ❌ Search through notes
- ❌ Export notes

**Implementation Needed:**
```javascript
// Create: frontend/pages/notes.js
- List all memories with search
- Add/Edit/Delete functionality
- Categories: Education, Sports, Personal, etc.
- Export as text/PDF
```

**API Endpoints to Create:**
```python
GET    /api/user/memories        # List all
POST   /api/user/memories        # Add new
PUT    /api/user/memories/{id}   # Update
DELETE /api/user/memories/{id}   # Delete
GET    /api/user/memories/search?q=  # Search
```

---

#### 2. **Chat Management** 🚨  
**Status:** Basic storage, no UI

**What's Missing:**
- ❌ View all conversations (list with preview)
- ❌ Delete specific conversation
- ❌ Delete all conversations (with confirmation)
- ❌ User control: Keep last X messages (10/20/50/100)
- ❌ Export chat as text/PDF
- ❌ Archive old chats

**Implementation Needed:**
```javascript
// Create: frontend/pages/chats.js
- List all conversations with title & date
- Click to open conversation
- Delete button per chat
- "Delete All" with confirmation
- Settings: Message retention (dropdown: 10/20/50/100/unlimited)
```

**API Endpoints to Create:**
```python
GET    /api/user/conversations           # List all
GET    /api/user/conversations/{id}      # Get specific
DELETE /api/user/conversations/{id}      # Delete one
DELETE /api/user/conversations           # Delete all
PUT    /api/user/settings/retention      # Set limit
GET    /api/user/conversations/{id}/export  # Export
```

**Database Schema to Add:**
```sql
CREATE TABLE conversation_metadata (
    conversation_id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    title VARCHAR,           -- Auto from first message
    message_count INTEGER,
    created_at TIMESTAMP,
    last_message_at TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE
);
```

---

#### 3. **Message Retention Control** 🚨
**Status:** Hardcoded (20 for free, 50 for premium)

**What's Needed:**
- User preference UI: "Keep last X messages"
- Options: 10, 20, 50, 100, Unlimited (premium only)
- Auto-delete old messages
- Warning before deletion
- Option to export before delete

**Implementation:**
```python
# backend/models/user.py
class UserSettings:
    message_retention: int = 20      # User choice
    auto_delete_after_days: int = 30 # Auto cleanup
    export_before_delete: bool = True
```

```javascript
// frontend/pages/settings.js
<select name="retention">
  <option value="10">Last 10 messages</option>
  <option value="20">Last 20 messages</option>
  <option value="50">Last 50 messages (Premium)</option>
  <option value="100">Last 100 messages (Premium)</option>
  <option value="-1">Unlimited (Premium)</option>
</select>
```

---

### 🟡 MEDIUM PRIORITY

#### 4. **Horoscope API Integration** 📅
**Status:** AI-generated only

**What's Needed:**
- Real horoscope API
- Cache daily horoscopes (24hrs)
- Store horoscope history

---

#### 5. **Sports Stats Database** 📅
**Status:** Web search only

**What's Needed:**
- Permanent player stats storage
- Weekly updates
- Match schedules database

---

#### 6. **Premium Features Enhancement** 📅
**Additional Features:**
- Export all chats as PDF
- API access
- Custom AI personality
- No rate limits

---

### 🟢 LOW PRIORITY

#### 7. **Photo Editor Tool** 📅
Canvas-based image editing (client-side)

#### 8. **Summarize Tool** 📅
Text/URL summarization

#### 9. **Teer Results Integration** 📅
Real API + predictions

---

## 🛠️ Development Setup

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# .env file
ANTHROPIC_API_KEY=your_key
DATABASE_URL=postgresql://...
SERPAPI_KEY=your_serpapi_key
SEARCH_PROVIDER=serpapi

# Initialize
python scripts/init_predictions_db.py

# Run
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install

# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Run
npm run dev
```

---

## 📡 Key API Endpoints

```http
# Chat
POST /api/chat
{
  "user_id": "user123",
  "message": "Predict India vs Australia",
  "conversation_id": "conv123",
  "web_search": true
}

# Autocomplete
GET /api/autocomplete?q=cricket

# Admin
POST /api/admin/init-predictions-db?password=mydost2024
GET  /api/admin/predictions/stats

# Authentication
POST /api/auth/register
POST /api/auth/login

# User Settings (TO CREATE)
GET    /api/user/settings
PUT    /api/user/settings/retention
GET    /api/user/memories
POST   /api/user/memories
DELETE /api/user/memories/{id}
GET    /api/user/conversations
DELETE /api/user/conversations/{id}
```

---

## 🚀 Deployment

**Backend (Railway):**
- Auto-deploy from GitHub
- Set environment variables in dashboard
- PostgreSQL + Redis auto-provisioned

**Frontend (Vercel):**
- Auto-deploy from GitHub
- Set NEXT_PUBLIC_API_URL

**Production URLs:**
- Frontend: https://mydost.in
- Backend: https://mydost-backend.railway.app
- Admin: https://mydost.in/admin

---

## 🔍 Testing Checklist

### Manual Tests
- [ ] Sports: Navigate to `/sports`, predict match, verify caching
- [ ] Education: Select Assamese, verify simple language for Class 5
- [ ] Horoscope: Select Aries, get daily prediction
- [ ] Autocomplete: Type "cr" → See "cricket match prediction"
- [ ] Web Search: Ask about IPL → Verify SerpAPI used
- [ ] Notes: (After UI built) Add/edit/delete memory
- [ ] Chats: (After UI built) Delete conversation, set retention

---

## 📊 Performance Metrics

**Targets:**
- Response time: < 3s (with web search)
- Cache hit rate: > 70%
- Cost per user: < ₹1/day

**Current:**
- Web search cache: 1 hour
- Predictions cache: 24 hours
- Player stats cache: 7 days
- Savings: ~80-90% on API costs

---

## 🐛 Known Issues

1. Redis local fallback → Uses in-memory
2. DuckDuckGo sometimes empty → Paid API works
3. Message retention hardcoded → **Needs UI**
4. No chat management UI → **High priority**
5. No notes management UI → **High priority**

---

## 📝 For AI Agents Working on This

### Priority Order:
1. **Chat Management UI** - pages/chats.js + API endpoints
2. **Notes Management UI** - pages/notes.js + API endpoints  
3. **Message Retention Settings** - User control over storage
4. **Horoscope API** - Real astrology data
5. **Sports Database** - Permanent stats storage

### Code Guidelines:
- Python: Type hints, async/await
- React: Functional components, hooks
- Database: Parameterized queries only
- API: RESTful, proper status codes
- Test locally before pushing

### Git Workflow:
```bash
git checkout -b feature/chat-management
# Make changes
git add .
git commit -m "Add chat management UI with delete functionality"
git push origin feature/chat-management
```

### Testing:
- Test SerpAPI key works
- Verify cache logs
- Test all 4 languages
- Test free vs premium flows
- Check Railway logs after deploy

---

## 🤝 Contributing

**Current Sprint Focus:**
1. Build chat management UI (high priority)
2. Build notes management UI (high priority)
3. Add message retention controls (high priority)
4. Test everything thoroughly

**What's Working:**
- ✅ Sports predictions page
- ✅ Education multi-language page
- ✅ Horoscope page
- ✅ Web search with caching
- ✅ Autocomplete suggestions
- ✅ RAG with memory

**What Needs Work:**
- 🚨 Chat management (delete, view history)
- 🚨 Notes management (CRUD operations)
- 🚨 Message retention settings
- 📅 Horoscope API integration
- 📅 Sports database

---

## 📞 Support

**URLs:**
- Production: https://mydost.in
- Backend: https://mydost-backend.railway.app
- Admin: /admin (password: mydost2024)

**Debugging:**
- Backend errors: Railway logs
- Frontend errors: Browser console
- API test: Postman/curl
- Database: Railway PostgreSQL dashboard

---

**Last Updated:** January 24, 2026  
**Version:** 1.0.0  
**Status:** Production with pending features

**Work until satisfied:** Chat Management + Notes Management + Message Retention
