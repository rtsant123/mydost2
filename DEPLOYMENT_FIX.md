# Railway Deployment Fix - Stop 404 Errors

## Current Problem

❌ **404 errors everywhere** because `NEXT_PUBLIC_API_URL` is not set in Railway frontend

## Quick Fix (5 minutes)

### Step 1: Get Your Backend URL

1. Go to Railway dashboard
2. Click on your **backend service**
3. Go to **Settings** tab
4. Find **Domains** section
5. Copy the URL (looks like: `https://mydost2-backend-production.up.railway.app`)

### Step 2: Set Frontend Environment Variable

1. Go to Railway dashboard
2. Click on your **frontend service**
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://mydost2-backend-production.up.railway.app
   ```
   (Use YOUR actual backend URL)

6. Click **Deploy** or wait for auto-redeploy

### Step 3: Set Backend CORS

1. Go to **backend service** → **Variables**
2. Add/Update:
   ```
   Name: FRONTEND_URL
   Value: https://mydost2-production.up.railway.app
   ```
   (Use YOUR actual frontend URL)

### Step 4: Verify All Required Variables

#### Backend Service Variables:
```env
✅ DATABASE_URL=${{pgvector.DATABASE_URL}}
✅ REDIS_URL=${{Redis.REDIS_URL}}
⚠️ ANTHROPIC_API_KEY=sk-ant-... (YOUR CLAUDE API KEY)
⚠️ SEARCH_API_KEY=your-serper-key (IF YOU HAVE ONE)
⚠️ SEARCH_API_URL=https://google.serper.dev/search
✅ FRONTEND_URL=https://your-frontend.railway.app
```

#### Frontend Service Variables:
```env
⚠️ NEXT_PUBLIC_API_URL=https://your-backend.railway.app (ADD THIS!)
⚠️ GOOGLE_CLIENT_ID=your-google-id
⚠️ GOOGLE_CLIENT_SECRET=your-google-secret
⚠️ NEXTAUTH_URL=https://your-frontend.railway.app
⚠️ NEXTAUTH_SECRET=your-generated-secret
```

## If You Don't Have API Keys Yet

### Required (App won't work without):
- **ANTHROPIC_API_KEY**: Get from https://console.anthropic.com/
  - Create account → API Keys → Create Key
  - Copy key (starts with `sk-ant-`)

### Optional (Features work with web search only):
- **SEARCH_API_KEY**: Get from https://serper.dev/
  - Sign up → Dashboard → API Key
  - Free tier: 2,500 searches/month

- **GOOGLE_CLIENT_ID/SECRET**: For OAuth login
  - Get from https://console.cloud.google.com/
  - Follow `GOOGLE_OAUTH_SETUP.md`

## Test After Deployment

### 1. Check Backend Health
Visit: `https://your-backend.railway.app/health`

Should see:
```json
{"status": "healthy"}
```

### 2. Check Backend API Docs
Visit: `https://your-backend.railway.app/docs`

Should see Swagger UI with all endpoints

### 3. Check Frontend
Visit: `https://your-frontend.railway.app/`

Should redirect to sign-in page (not 404)

## Common Issues

### Issue: "Cannot connect to backend"
**Fix:** Set `NEXT_PUBLIC_API_URL` in frontend variables

### Issue: "CORS error"
**Fix:** Set `FRONTEND_URL` in backend variables with correct frontend domain

### Issue: "Database connection failed"
**Fix:** Set `DATABASE_URL=${{pgvector.DATABASE_URL}}` in backend

### Issue: "Anthropic API error"
**Fix:** Set valid `ANTHROPIC_API_KEY` in backend

### Issue: "Google sign-in fails"
**Fix:** 
1. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
2. Add frontend URL to Google Console authorized redirect URIs:
   `https://your-frontend.railway.app/api/auth/callback/google`

## Railway Service Structure

You should have **4 services**:

1. **pgvector** (Database)
   - Template from Railway marketplace
   - No configuration needed
   - Provides `DATABASE_URL`

2. **Redis** (Cache)
   - Add from Railway marketplace
   - No configuration needed
   - Provides `REDIS_URL`

3. **Backend** (Python FastAPI)
   - Connected to GitHub
   - Root directory: `/backend`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Frontend** (Next.js)
   - Connected to GitHub
   - Root directory: `/frontend`
   - Build: `npm run build`
   - Start: `npm run start`

## Quick Commands to Check

### Check backend logs:
```bash
# In Railway backend service
Click "View Logs"
Look for:
✅ "User database tables initialized successfully"
✅ "Vector store initialized successfully"
✅ "Application startup complete"
```

### Check frontend logs:
```bash
# In Railway frontend service
Click "View Logs"
Look for:
✅ "Compiled successfully"
✅ "Ready on http://0.0.0.0:3000"
```

## Priority Order

1. **MUST HAVE** (App won't run):
   - ✅ DATABASE_URL
   - ✅ ANTHROPIC_API_KEY
   - ✅ NEXT_PUBLIC_API_URL
   - ✅ NEXTAUTH_SECRET

2. **SHOULD HAVE** (For Google login):
   - GOOGLE_CLIENT_ID
   - GOOGLE_CLIENT_SECRET
   - NEXTAUTH_URL

3. **NICE TO HAVE** (For enhanced features):
   - REDIS_URL
   - SEARCH_API_KEY
   - FRONTEND_URL

## After Everything is Set

1. Both services should show **"Active"** status
2. No errors in logs
3. Frontend accessible
4. Backend /health returns 200
5. Can sign in with Google
6. Chat works with AI responses

**Then you're production ready!** 🚀
