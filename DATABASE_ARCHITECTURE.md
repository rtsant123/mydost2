# Backend Database Architecture

## ✅ What's Stored in PostgreSQL Backend

### 1. **Users Table**
Stores all user information:
- `user_id` (UUID) - Primary key
- `email` - User's email from Google
- `name` - User's display name  
- `image` - Profile picture URL
- `google_id` - Google OAuth ID (unique)
- `preferences` (JSONB) - User preferences object
- `has_preferences` (Boolean) - Whether user completed onboarding
- `created_at` - Account creation timestamp
- `last_login` - Last login timestamp

### 2. **Usage Limits Table**
Tracks per-user daily usage:
- `user_id` (FK to users)
- `date` - Usage date
- `api_calls` - Number of API calls made
- `tokens_used` - Total tokens consumed
- `web_searches` - Web search queries made
- `ocr_requests` - OCR processing requests
- `pdf_uploads` - PDF documents uploaded

**Daily tracking** - Each row represents ONE user's usage for ONE day.

### 3. **Vector Database (pgvector)**
All memories stored with user isolation:
- User conversations (per `user_id`)
- User notes (per `user_id`)
- Uploaded document content (per `user_id`)
- Web search results cached for RAG

**Already implemented** in `vector_store.py` - all functions accept `user_id` parameter.

## ✅ Per-User Limits Enforced

In `models/user.py`:

```python
# Check if user exceeded limit
user_db.check_limit(user_id, "api_calls", max_limit=100)
user_db.check_limit(user_id, "tokens_used", max_limit=50000)
user_db.check_limit(user_id, "web_searches", max_limit=20)
```

Admin can set limits globally, enforced per user.

## ✅ What Frontend Does

**Only handles:**
- UI rendering
- Session management (NextAuth JWT tokens)
- Calling backend APIs

**Does NOT store:**
- User data
- Preferences
- Conversation history
- Usage limits
- Memories

## Data Flow

```
User logs in with Google
    ↓
NextAuth creates JWT session (stored in cookie)
    ↓
Frontend calls: POST /api/auth/google-signin
    ↓
Backend creates/retrieves user from PostgreSQL
    ↓
Returns: user_id, preferences, has_preferences
    ↓
Frontend stores user_id in session (in-memory)
    ↓
All requests include user_id in payload
    ↓
Backend validates user_id and tracks usage
```

## Per-User Examples

### Chat Message Flow:
```
User sends message "Hello" 
    ↓
POST /api/chat { user_id: "uuid-123", message: "Hello" }
    ↓
Backend:
  1. Gets user preferences from DB → personalize prompt
  2. Checks user limits → "api_calls < 100 today?"
  3. Retrieves user memories from vector DB (user_id filter)
  4. Generates response
  5. Stores message in vector DB (with user_id)
  6. Increments usage: user_db.increment_usage(user_id, api_calls=1)
```

### OCR Request Flow:
```
User uploads image
    ↓
POST /api/ocr { user_id: "uuid-123", file: image }
    ↓
Backend:
  1. Checks: user_db.check_limit(user_id, "ocr_requests", 10)
  2. Processes image
  3. Increments: user_db.increment_usage(user_id, ocr_requests=1)
```

## Admin Dashboard View

Admin can see per-user stats:

```python
GET /api/users/{user_id}/stats?days=7

Returns:
{
  "today": {
    "api_calls": 15,
    "tokens_used": 3500,
    "web_searches": 3,
    "ocr_requests": 1,
    "pdf_uploads": 0
  },
  "last_7_days": {
    "total_api_calls": 87,
    "total_tokens": 21450,
    ...
  }
}
```

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    image TEXT,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    preferences JSONB DEFAULT '{}',
    has_preferences BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage tracking table
CREATE TABLE usage_limits (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    api_calls INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    web_searches INTEGER DEFAULT 0,
    ocr_requests INTEGER DEFAULT 0,
    pdf_uploads INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);

-- Index for fast lookups
CREATE INDEX idx_usage_limits_user_date ON usage_limits(user_id, date);
```

## Key Benefits

✅ **Per-User Isolation**: Each user's data completely separate
✅ **Usage Tracking**: Track every action per user per day
✅ **Limit Enforcement**: Prevent abuse, control costs
✅ **Scalable**: Database handles millions of users
✅ **Persistent**: Data survives backend restarts
✅ **Secure**: User can only access their own data

## Files Changed

1. **Created**: `backend/models/user.py` - User database operations
2. **Updated**: `backend/routers/auth.py` - Use database instead of in-memory dict
3. **Updated**: `backend/routers/chat.py` - Track usage, get preferences from DB
4. **Updated**: `backend/routers/ocr.py` - Track OCR usage per user
5. **Updated**: `backend/routers/pdf.py` - Track PDF uploads per user
6. **Frontend**: No changes needed - already sends user_id in requests

## Next Steps

1. Push code to GitHub
2. Railway will auto-create tables on first run
3. Test user signup → preferences → chat → usage tracking
4. Add admin endpoint to view all users and their usage
