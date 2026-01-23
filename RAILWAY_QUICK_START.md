# Quick Railway Setup Guide

## 🚀 Deploy to Railway in 10 Minutes

### What You Need
1. Railway account (sign up at https://railway.app)
2. Anthropic Claude AI API key (get from https://console.anthropic.com/)
3. This code pushed to GitHub

---

## Step 1: Add Database Services (2 min)

1. **Go to Railway** → Click "New Project"
2. **Add PostgreSQL**:
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Wait for it to deploy
   
3. **Enable pgvector extension**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and link to project
   railway login
   railway link
   
   # Connect to PostgreSQL
   railway connect postgres
   
   # Run this command in psql:
   CREATE EXTENSION IF NOT EXISTS vector;
   
   # Exit with: \q
   ```

4. **Add Redis**:
   - Click "+ New"
   - Select "Database" → "Redis"
   - Wait for it to deploy

---

## Step 2: Deploy Backend (3 min)

1. **Click "+ New"** → "GitHub Repo"
2. **Select your repository**
3. **Configure Service**:
   - Click on the new service
   - Go to "Settings" → Set **Root Directory**: `backend`
   
4. **Add Environment Variables** (click "Variables" tab):
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ADMIN_PASSWORD=your-secure-password
   FRONTEND_URL=https://your-frontend-url.railway.app
   ```
   
   For optional features, add:
   ```
   SEARCH_API_KEY=your-serper-key
   NEWS_API_KEY=your-newsapi-key
   ```

5. **Generate Domain**:
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - Copy the URL (you'll need it for frontend)

---

## Step 3: Deploy Frontend (3 min)

1. **Click "+ New"** → "GitHub Repo"
2. **Select your repository again**
3. **Configure Service**:
   - Set **Root Directory**: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`

4. **Add Environment Variable**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
   (Use the backend URL from Step 2)

5. **Generate Domain**:
   - Go to "Settings" → "Networking"  
   - Click "Generate Domain"
   - This is your app URL!

---

## Step 4: Update Backend CORS (1 min)

1. Go back to **Backend service**
2. Click "Variables"
3. **Update** `FRONTEND_URL` with your actual frontend URL from Step 3
4. Service will automatically redeploy

---

## Step 5: Test Your App (1 min)

1. **Visit your frontend URL**
2. **Try sending a message** like "Hello!"
3. **Test admin panel**: Go to `/admin`, login with your password
4. **Check health**: Visit `your-backend-url/health`

---

## Common Issues & Fixes

### ❌ Backend build fails with "backend not found"
✅ **Fixed in latest code** - Dockerfile paths corrected

### ❌ Frontend build fails with CSS import error  
✅ **Fixed in latest code** - Removed duplicate CSS import

### ❌ "Invalid API key" error
- Double-check your `ANTHROPIC_API_KEY` starts with `sk-ant-`
- Make sure there are no extra spaces
- Get a new key from https://console.anthropic.com/

### ❌ Database connection error
- Verify PostgreSQL service is running
- Check that pgvector extension is enabled
- Ensure `DATABASE_URL=${{Postgres.DATABASE_URL}}` is set correctly

### ❌ API not connecting to frontend
- Check `NEXT_PUBLIC_API_URL` matches your backend domain
- Verify `FRONTEND_URL` is set in backend
- Both services must be deployed

---

## Environment Variables Reference

### Required for Backend
| Variable | Get it from |
|----------|-------------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| `DATABASE_URL` | Automatically from Railway Postgres |
| `REDIS_URL` | Automatically from Railway Redis |
| `ADMIN_PASSWORD` | Choose a strong password |
| `FRONTEND_URL` | Your frontend Railway domain |

### Optional for Backend
| Variable | Get it from | Feature |
|----------|-------------|---------|
| `SEARCH_API_KEY` | https://serper.dev | Web search |
| `NEWS_API_KEY` | https://newsapi.org | News summaries |

### Required for Frontend
| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Your backend Railway domain |

---

## Verify Everything Works

### ✅ Backend Checklist
- [ ] Health endpoint works: `GET /health`
- [ ] API docs accessible: `GET /docs`
- [ ] Database connected (check logs)
- [ ] Redis connected (check logs)

### ✅ Frontend Checklist
- [ ] Page loads without errors
- [ ] Can send messages
- [ ] Admin panel accessible at `/admin`
- [ ] File upload works

---

## Get API Keys

### 1. Anthropic Claude AI (Required)
```
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Click "API Keys"
4. Create new key
5. Copy the key (starts with sk-ant-)
```

### 2. Serper (Optional - Web Search)
```
1. Go to: https://serper.dev
2. Sign up
3. Get free API key from dashboard
```

### 3. NewsAPI (Optional - News)
```
1. Go to: https://newsapi.org
2. Sign up for free
3. Copy API key from account
```

---

## Monitoring

View logs in real-time:
1. Click on service in Railway
2. Go to "Logs" tab
3. See all requests and errors

---

## Cost

- **Free tier**: $5/month credit
- **Typical usage**: $2-5/month for small projects
- **What uses resources**:
  - Claude AI API calls (billed by Anthropic)
  - Database storage
  - Bandwidth

---

## Next Steps

1. ✅ Basic deployment working
2. Add custom domain (optional)
3. Set up monitoring
4. Configure backups
5. Optimize caching

---

## Support

- **Railway Issues**: Check Railway logs first
- **Claude AI Issues**: https://docs.anthropic.com
- **App Issues**: Check GitHub repository

---

**Total Time**: ~10 minutes  
**Difficulty**: Beginner-friendly  
**Cost**: Free tier (first month)
