# Sports Predictions & Memory System - Integration Guide

## ✅ What's Been Implemented

### 1. **CORS & Deployment Fixes**
- ✅ Fixed CORS configuration to properly allow `www.mydost.in` and other production domains
- ✅ Fixed deprecated `apple-mobile-web-app-capable` meta tag
- ✅ Backend now accepts requests from frontend without CORS errors

### 2. **Database Tables Created**

#### `matches` Table
```sql
- match_id (PK)
- match_type: 'IPL', 'Test', 'ODI', 'T20', 'Football', etc.
- team_1, team_2: Team names
- match_date: When the match is scheduled
- venue: Match location
- status: 'scheduled', 'live', 'completed'
- result: {winner, margin, etc.}
- odds: Live betting odds
- external_data: Web search context
```

#### `teer_data` Table
```sql
- teer_id (PK)
- date: Unique daily entry
- first_round, second_round: Lottery numbers
- common_num, patti_num: Analysis
- predictions: AI predictions for future
- historical_patterns: Pattern analysis
```

#### `user_predictions` Table
```sql
- prediction_id (PK)
- user_id: FK to users
- prediction_type: 'match', 'teer', 'astrology'
- prediction_for: Match ID, date, or topic
- prediction_text: User's prediction
- confidence_score: Confidence level
- actual_result: When outcome is known
- was_correct: Boolean accuracy tracking
```

#### `sports_memory` Table
- User-specific predictions and accuracy
- Per-match analysis
- Historical performance

### 3. **Background Scheduler**

**Location**: `backend/services/sports_scheduler.py`

**Scheduled Jobs**:
```
1. Fetch Upcoming Matches (Daily at midnight)
   - Searches for IPL, Cricket, Football matches
   - Stores in database with teams, date, time
   - Maintains 7-day lookahead

2. Fetch Teer Results (Daily at 4 PM)
   - Gets today's lottery results
   - Updates database
   - Calculates patterns

3. Update Match Results (Every 6 hours)
   - Checks if completed matches have results
   - Updates with winner, margin, etc.
   - Helps with accuracy tracking
```

### 4. **Enhanced Services**

#### Sports Service (`backend/services/sports_service.py`)

**New Methods**:
```python
# Get upcoming matches with AI context
get_upcoming_matches_with_context()
  ↓ Returns: List of matches with dates, teams, odds

# Predict with user history
predict_match_with_user_memory(user_id, team_1, team_2)
  ↓ Considers: User's past predictions, accuracy

# Save prediction for tracking
save_match_prediction(user_id, match_id, prediction_text)
  ↓ Stores in DB + Vector DB for memory

# Get user's sports profile
get_user_sports_profile(user_id)
  ↓ Returns: Prediction history, accuracy, trends
```

#### Teer Service (`backend/services/teer_service.py`)

**New Methods**:
```python
# Save teer prediction
save_teer_prediction(user_id, target_date, first_num, second_num)
  ↓ Stores with reasoning in DB

# Get pattern analysis
get_teer_with_pattern_analysis()
  ↓ Returns: Most common numbers, trends, analysis

# User accuracy
get_teer_prediction_accuracy(user_id)
  ↓ Returns: Total predictions, correct, accuracy %
```

### 5. **New API Endpoints**

#### Match Predictions
```
GET  /api/sports/upcoming-matches
     ↓ Get all upcoming matches

POST /api/sports/predict-match
     ↓ Get prediction for specific match
     {
       "user_id": "uuid",
       "team_1": "India",
       "team_2": "Australia"
     }

POST /api/sports/save-prediction
     ↓ Save user's match prediction

GET  /api/sports/profile/{user_id}
     ↓ Get user's sports prediction history & accuracy
```

#### Teer Predictions
```
GET  /api/teer/results
     ↓ Get teer data with pattern analysis

POST /api/teer/predict
     ↓ Save teer prediction
     {
       "user_id": "uuid",
       "target_date": "2025-01-24",
       "predicted_first": "42",
       "predicted_second": "78"
     }

GET  /api/teer/accuracy/{user_id}
     ↓ Get user's teer prediction accuracy
```

#### Combined Profile
```
GET  /api/profile/sports/{user_id}
     ↓ Complete sports profile (matches + teer)
```

---

## 🔄 Data Flow (How It Works)

### User Makes Prediction
```
1. User asks: "Who will win India vs Australia?"
   
2. Backend:
   - Searches database for upcoming matches
   - Finds: "India vs Australia on Jan 25, 2025"
   - Gets from cache: Past odds, team stats
   - Gets from vector DB: User's past predictions about these teams
   
3. LLM receives context:
   - Match details from database
   - Upcoming matches list
   - User's prediction history
   - Historical patterns
   
4. AI generates prediction
   - Takes user preferences into account
   - Cites recent form, odds, expert opinions
   - Expresses confidence level
   
5. Backend saves:
   - User prediction in user_predictions table
   - Prediction text in vector DB (for future retrieval)
   - Confidence score for tracking
   
6. Later when match completes:
   - Scheduler fetches result
   - Updates user_predictions.was_correct
   - Calculates accuracy over time
```

### Memory & Personalization
```
Chat History:
User: "I love cricket"
  ↓ Stored in vector DB with user_id

Later:
User: "Who wins tomorrow's match?"
  ↓ RAG retrieves: "User loves cricket"
  ↓ AI personalizes answer: "Since you love cricket..."
  ↓ Plus: Adds match analysis, odds, predictions
  ↓ User responds to predictions
  ↓ All conversation + prediction history remembered
```

---

## 🚀 Deployment Instructions

### 1. Update Railway Variables
```
ENVIRONMENT=production  # Enables production CORS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
# Includes: apscheduler==3.10.4
```

### 3. Deploy Backend
```bash
git push  # Railway auto-deploys
```

### 4. Verify Scheduler
```
Check backend logs:
✅ "Sports Data Scheduler started"
```

### 5. Access Endpoints
```
https://www.mydost.in/api/sports/upcoming-matches
https://www.mydost.in/api/teer/results
```

---

## 📊 Database Queries for Analytics

### User Prediction Accuracy
```sql
SELECT 
  user_id,
  prediction_type,
  COUNT(*) as total,
  SUM(CASE WHEN was_correct = true THEN 1 ELSE 0 END) as correct,
  ROUND(100.0 * SUM(CASE WHEN was_correct = true THEN 1 ELSE 0 END) / COUNT(*), 2) as accuracy_percent
FROM user_predictions
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY user_id, prediction_type;
```

### Upcoming Matches
```sql
SELECT * FROM matches
WHERE match_date >= NOW() AND match_date <= NOW() + INTERVAL '7 days'
AND status IN ('scheduled', 'live')
ORDER BY match_date ASC;
```

### Teer Patterns (Last 30 Days)
```sql
SELECT 
  date,
  first_round,
  second_round,
  common_num
FROM teer_data
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;
```

---

## 🔧 Customization

### Add More Sports
Edit `backend/services/sports_scheduler.py`:
```python
search_queries = [
    "IPL 2025 schedule...",
    "IPL 2025 schedule...",
    "Football Premier League matches",  # Add this
    "NBA basketball matches",  # Or this
]
```

### Adjust Scheduler Timing
In `backend/services/sports_scheduler.py`:
```python
# Change cron times:
hour=0,  # Change to 6, 12, 18, etc.
minute=0

# Change update frequency:
trigger="cron",
hour="*/6",  # Change to */4 for every 4 hours
```

### Fine-tune Predictions
In `backend/services/sports_service.py`:
```python
# Adjust confidence calculation
confidence = min(abs(home_win_rate - away_win_rate) * 100, 95)
# Change multiplier or cap value
```

---

## ⚠️ Important Notes

1. **Match Data Source**: Web search (Serper API)
   - Results depend on current news availability
   - May not have all upcoming matches

2. **Teer Results**: Web search
   - Unofficial lottery results
   - Not authoritative source
   - For entertainment/analysis only

3. **Prediction Accuracy**: Tracked over time
   - More data = better analysis
   - System learns user preferences
   - Confidence increases with history

4. **Memory Integration**: Automatic
   - All predictions stored in vector DB
   - Retrieved for context in future chats
   - Removed only when user deletes chat

---

## 📝 Testing the System

### Test Match Prediction
```bash
curl -X GET "https://www.mydost.in/api/sports/upcoming-matches"

curl -X POST "https://www.mydost.in/api/sports/predict-match" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "team_1": "India",
    "team_2": "Australia"
  }'
```

### Test Teer
```bash
curl -X GET "https://www.mydost.in/api/teer/results"
```

### Check User Profile
```bash
curl -X GET "https://www.mydost.in/api/profile/sports/{user_id}"
```

---

## 🎯 Next Steps

1. ✅ Test CORS fixes on production
2. ✅ Monitor scheduler logs for 24 hours
3. ✅ Verify match data is being fetched
4. ✅ Test user predictions save/retrieve
5. ✅ Monitor accuracy calculations
6. 📌 Set up alerts for scheduler failures
7. 📌 Add more sports/domains as needed
8. 📌 Implement SMS/email notifications for prediction results

---

**Questions?** Check the routers:
- `/backend/routers/sports.py` - All endpoints
- `/backend/services/sports_service.py` - Logic
- `/backend/models/sports_data.py` - Database operations
