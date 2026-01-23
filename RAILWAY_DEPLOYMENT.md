# Railway Deployment Guide (Claude AI + PostgreSQL + Redis)

## Overview

This guide will walk you through deploying your chatbot on Railway with:
- **Backend**: FastAPI with Rio
- **Frontend**: Next.js  
- **Database**: PostgreSQL with pgvector extension
- **Cache**: Redis

## Prerequisites

1. Railway account (https://railway.app)
2. GitHub account with your code pushed
3. Anthropic API key for Claude AI

## Step-by-Step Deployment

### 1. Create New Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Authorize Railway to access your repository
4. Select your `mydost2` repository

### 2. Add PostgreSQL Database

1. In Railway project dashboard, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a PostgreSQL instance
4. Note: The `DATABASE_URL` environment variable will be automatically available

### 3. Enable pgvector Extension

1. Click on your PostgreSQL service
2. Go to "Connect" tab and copy the connection command
3. Use Railway CLI or connect via psql:
   ```bash
   # Install Railway CLI if needed
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Link to your project
   railway link
   
   # Connect to PostgreSQL
   railway connect postgres
   
   # In psql, run:
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 4. Add Redis Cache

1. Click "+ New" in your project
2. Select "Database" → "Add Redis"  
3. Railway will create a Redis instance
4. Note: The `REDIS_URL` will be automatically available

### 5. Deploy Backend Service

1. Click "+ New" → "GitHub Repo"  
2. Select your repository again (or click "New Service")
3. Configure the service:
   - **Name**: `chatbot-backend`
   - **Root Directory**: `backend`
   - Railway will auto-detect the Dockerfile

4. Add environment variables (click on service → "Variables"):
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   SEARCH_API_KEY=your-serper-key
   NEWS_API_KEY=your-newsapi-key
   ADMIN_PASSWORD=your-strong-password
   FRONTEND_URL=https://your-frontend.railway.app
   ```

   **Note**: `${{Postgres.DATABASE_URL}}` and `${{Redis.REDIS_URL}}` are Railway references that automatically inject the database URLs.

5. Under "Settings" → "Deploy":
   - **Build Command**: (leave empty, uses Dockerfile)
   - **Start Command**: (leave empty, defined in Dockerfile)

6. Click "Deploy"

### 6. Deploy Frontend Service

1. Click "+ New" → "GitHub Repo"
2. Configure:
   - **Name**: `chatbot-frontend`
   - **Root Directory**: `frontend`
   
3. Railway will detect Node.js. Configure:
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=${{chatbot-backend.RAILWAY_PUBLIC_DOMAIN}}
   ```

   Or use the full URL after backend deploys:
   ```
   NEXT_PUBLIC_API_URL=https://chatbot-backend-production-xxxx.up.railway.app
   ```

5. Click "Deploy"

### 7. Configure Custom Domains (Optional)

1. Click on each service
2. Go to "Settings" → "Networking"
3. Click "Generate Domain" or add your custom domain
4. Update `FRONTEND_URL` in backend and `NEXT_PUBLIC_API_URL` in frontend

### 8. Verify Deployment

1. **Check backend health**:
   - Visit: `https://your-backend.railway.app/health`
   - Should return: `{"status": "healthy"}`

2. **Check API docs**:
   - Visit: `https://your-backend.railway.app/docs`

3. **Test frontend**:
   - Visit: `https://your-frontend.railway.app`
   - Try sending a message

## Environment Variables Summary

### Backend Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude AI API key | `sk-ant-...` |
| `DATABASE_URL` | PostgreSQL connection | Auto-provided by Railway |
| `REDIS_URL` | Redis connection | Auto-provided by Railway |
| `SEARCH_API_KEY` | Serper search API | From serper.dev |
| `NEWS_API_KEY` | NewsAPI key | From newsapi.org |
| `ADMIN_PASSWORD` | Admin panel password | Your secure password |
| `FRONTEND_URL` | Frontend domain (CORS) | `https://your-frontend.railway.app` |

### Frontend Variables
| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |

## Getting API Keys

### 1. Anthropic Claude AI (Required)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to "API Keys"
4. Create new key
5. Copy key starting with `sk-ant-`

### 2. Serper API (Optional - for web search)
1. Go to https://serper.dev
2. Sign up
3. Get API key from dashboard

### 3. NewsAPI (Optional - for news)
1. Go to https://newsapi.org
2. Sign up for free tier
3. Copy API key

## Troubleshooting

### Backend Build Fails

**Error**: `"/backend": not found`
- ✅ Fixed: Dockerfile now uses correct paths (`COPY . .` instead of `COPY backend/ .`)

**Error**: Database connection failed
- Check `DATABASE_URL` is properly set
- Verify PostgreSQL service is running in Railway
- Check if pgvector extension is enabled

**Error**: Redis connection failed
- Check `REDIS_URL` is set
- System will fallback to in-memory cache if Redis unavailable

### Frontend Build Fails

**Error**: `Global CSS cannot be imported`
- ✅ Fixed: Removed CSS import from admin.js

**Error**: API connection failed
- Check `NEXT_PUBLIC_API_URL` is correct
- Ensure backend is deployed first
- Check CORS settings in backend

### Claude AI Issues

**Error**: `Invalid API key`
- Verify API key starts with `sk-ant-`
- Check for extra spaces in environment variable
- Regenerate key if needed

**Error**: Rate limit exceeded
- Check your Anthropic usage dashboard
- Upgrade plan if needed

### Database Issues

**Error**: `vector type does not exist`
```bash
# Connect to postgres and run:
railway connect postgres
CREATE EXTENSION IF NOT EXISTS vector;
```

**Error**: `relation "chat_vectors" does not exist`
- Tables are created automatically on first request
- Check backend logs for connection errors

## Monitoring & Logs

### View Logs
1. Click on service in Railway
2. Go to "Logs" tab
3. View real-time logs

### Check Resource Usage
1. Go to "Metrics" tab
2. Monitor:
   - CPU usage
   - Memory
   - Network
   - Disk

## Scaling

### Vertical Scaling (More Resources)
1. Go to service "Settings"
2. Under "Resources", increase:
   - Memory
   - CPU

### Horizontal Scaling (Multiple Instances)
- Available on Pro plan
- Configure under "Settings" → "Instances"

## Cost Optimization

### Free Tier Limits
- $5 free credit per month
- Enough for development/testing

### Reduce Costs
1. **Use Redis caching**: Reduces API calls
2. **Set reasonable TTLs**: Balance freshness vs costs
3. **Monitor API usage**: Track Claude AI token usage
4. **Use smaller models**: Consider `claude-3-haiku-20240307` for simple queries

## Security Checklist

- [x] Strong `ADMIN_PASSWORD` set
- [x] API keys stored as environment variables
- [x] CORS configured with `FRONTEND_URL`
- [x] Railway service is private by default
- [ ] Add custom domain with HTTPS
- [ ] Enable Railway's authentication (optional)
- [ ] Set up monitoring/alerts

## Backup & Recovery

### Database Backups
1. Click on PostgreSQL service
2. Go to "Backups" tab
3. Configure automatic backups

### Manual Backup
```bash
# Connect with Railway CLI
railway connect postgres

# Or export with pg_dump
pg_dump $DATABASE_URL > backup.sql
```

## Updates & Redeployment

### Automatic Deployment
- Push to GitHub `main` branch
- Railway automatically rebuilds and deploys

### Manual Deployment
1. Go to service in Railway
2. Click "Deploy" → "Redeploy"

### Rollback
1. Go to "Deployments" tab
2. Find previous successful deployment
3. Click "..." → "Redeploy"

## Performance Tips

1. **Enable Redis**: Significantly reduces API calls
2. **Use connection pooling**: Already configured in PostgreSQL client
3. **Optimize embeddings**: Cache frequently accessed embeddings
4. **Monitor token usage**: Track Claude API costs
5. **Set appropriate cache TTLs**: Balance freshness and cost

## Support

- **Railway Docs**: https://docs.railway.app
- **Anthropic Docs**: https://docs.anthropic.com
- **PostgreSQL pgvector**: https://github.com/pgvector/pgvector
- **GitHub Issues**: Your repository issues page

## Quick Command Reference

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to project
railway link

# View logs
railway logs

# Connect to PostgreSQL
railway connect postgres

# Connect to Redis
railway connect redis

# Run command in service
railway run <command>

# Set environment variable
railway variables set KEY=value
```

## Next Steps

1. ✅ Deploy backend with PostgreSQL and Redis
2. ✅ Deploy frontend
3. ✅ Test all features
4. Add custom domain
5. Set up monitoring
6. Configure backups
7. Optimize caching strategy
8. Monitor API usage and costs

---

**Last Updated**: January 2026  
**Stack**: FastAPI + Claude AI + PostgreSQL + Redis + Next.js
