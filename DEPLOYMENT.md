# Deployment Guide

## Railway Deployment

### Prerequisites

- GitHub account
- Railway account (https://railway.app)
- Git repository with this project

### Deployment Steps

#### 1. Connect Repository to Railway

1. Go to https://railway.app
2. Click "Create Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository

#### 2. Create Backend Service

1. In Railway Dashboard, click "New"
2. Select "Service" → "Docker"
3. Configure:
   - **Name**: `chatbot-backend`
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `backend/Dockerfile`

#### 3. Create Frontend Service

1. Click "New" → "Service" → "Node.js"
2. Configure:
   - **Name**: `chatbot-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

#### 4. Add Environment Variables

For **Backend Service**:
```
OPENAI_API_KEY=sk-your-key
VECTOR_DB_URL=http://qdrant:6333
VECTOR_DB_API_KEY=
SEARCH_API_KEY=your-serper-key
NEWS_API_KEY=your-newsapi-key
ADMIN_PASSWORD=strong-password
FRONTEND_URL=https://your-frontend.railway.app
```

For **Frontend Service**:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

#### 5. Optional: Add Qdrant Vector Database

1. Create a new service using PostgreSQL plugin
2. Or use Pinecone cloud service instead

#### 6. Deploy

1. Push changes to main branch
2. Railway will automatically build and deploy
3. Monitor deployment in Dashboard

### Production Checklist

- [ ] Set strong `ADMIN_PASSWORD`
- [ ] Configure all API keys
- [ ] Set up vector database (Qdrant or Pinecone)
- [ ] Enable HTTPS on custom domain
- [ ] Configure CORS properly
- [ ] Set up monitoring and logging
- [ ] Test all features in production
- [ ] Configure backups for vector database

### Monitoring

- View logs in Railway Dashboard
- Set up alerts for deployment failures
- Monitor API usage and costs

### Scaling

- Increase memory/CPU resources
- Configure auto-scaling if needed
- Use CDN for frontend assets

### Troubleshooting

If services fail to start:

1. Check logs in Railway Dashboard
2. Verify environment variables are set
3. Ensure all API keys are valid
4. Check file permissions in Docker
5. Verify port configuration

### Local Development with Docker

Build and run locally:

```bash
# Build backend
docker build -t chatbot-backend ./backend

# Run backend
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e ADMIN_PASSWORD=admin123 \
  chatbot-backend

# In another terminal, start frontend
cd frontend
npm install
npm run dev
```

### Updating Production

1. Make changes locally
2. Test thoroughly
3. Commit and push to main branch
4. Railway automatically redeploys

### Rollback

If deployment fails:

1. Go to Railway Dashboard
2. Click "Deployments"
3. Select previous successful deployment
4. Click "Rollback"

### Support

For Railway-specific issues:
- https://railway.app/docs
- https://discord.gg/railway

For application-specific issues:
- Check GitHub Issues
- Review logs in Railway Dashboard
