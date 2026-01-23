# 🚀 Railway Deployment Checklist

Use this checklist to ensure smooth deployment.

## Pre-Deployment

### Local Testing
- [ ] Code is working locally with `docker-compose up`
- [ ] All tests pass
- [ ] Environment variables are configured
- [ ] `.env` file is NOT committed (use `.env.example`)

### Git Repository
- [ ] All changes committed
- [ ] Code pushed to GitHub `main` branch
- [ ] `.gitignore` includes `.env`, `node_modules`, etc.

### API Keys Ready
- [ ] Anthropic Claude AI key from https://console.anthropic.com/
- [ ] (Optional) Serper API key from https://serper.dev
- [ ] (Optional) NewsAPI key from https://newsapi.org
- [ ] Strong admin password chosen

---

## Railway Setup

### 1. Database Services
- [ ] PostgreSQL database created
- [ ] pgvector extension enabled:
  ```bash
  railway connect postgres
  CREATE EXTENSION IF NOT EXISTS vector;
  \q
  ```
- [ ] Redis cache created
- [ ] Both services show "Active" status

### 2. Backend Deployment
- [ ] New service created from GitHub repo
- [ ] Root directory set to: `backend`
- [ ] Environment variables added:
  - [ ] `ANTHROPIC_API_KEY=sk-ant-...`
  - [ ] `DATABASE_URL=${{Postgres.DATABASE_URL}}`
  - [ ] `REDIS_URL=${{Redis.REDIS_URL}}`
  - [ ] `ADMIN_PASSWORD=your-password`
  - [ ] `FRONTEND_URL=https://...` (update after frontend deployed)
  - [ ] `SEARCH_API_KEY=...` (optional)
  - [ ] `NEWS_API_KEY=...` (optional)
- [ ] Service deployed successfully (green status)
- [ ] Domain generated in Settings → Networking
- [ ] Health check works: `https://your-backend.railway.app/health`

### 3. Frontend Deployment  
- [ ] New service created from GitHub repo
- [ ] Root directory set to: `frontend`
- [ ] Build command: `npm install && npm run build`
- [ ] Start command: `npm start`
- [ ] Environment variable added:
  - [ ] `NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app`
- [ ] Service deployed successfully
- [ ] Domain generated
- [ ] Site loads at: `https://your-frontend.railway.app`

### 4. CORS Configuration
- [ ] Backend `FRONTEND_URL` updated with actual frontend domain
- [ ] Backend redeployed (automatic after variable change)

---

## Testing

### Backend Tests
- [ ] Health endpoint: `GET https://backend-url/health`
  - Expected: `{"status": "healthy"}`
- [ ] API docs: `GET https://backend-url/docs`
  - Should show Swagger UI
- [ ] Check logs for database connection success
- [ ] Check logs for Redis connection (or fallback message)

### Frontend Tests
- [ ] Homepage loads without errors
- [ ] Can send a chat message
- [ ] Claude AI responds correctly
- [ ] Conversation history saves
- [ ] Admin panel accessible: `/admin`
- [ ] Can login with admin password

### Feature Tests
- [ ] **Chat**: Basic conversation works
- [ ] **RAG**: Asks about previous conversation, gets context
- [ ] **File Upload**: Can upload image or PDF
- [ ] **OCR**: Text extracted from image
- [ ] **PDF**: Can query PDF content
- [ ] **Web Search** (if enabled): Gets current information
- [ ] **News** (if enabled): Shows latest headlines
- [ ] **Multilingual**: Try Assamese/Hindi input

### Admin Panel Tests
- [ ] Login works
- [ ] Can view usage statistics
- [ ] Can toggle modules on/off
- [ ] Can edit system prompt
- [ ] Can clear cache
- [ ] Changes persist after refresh

---

## Post-Deployment

### Monitoring
- [ ] Bookmarked Railway dashboard
- [ ] Checked logs for errors
- [ ] Verified all services are "Active"
- [ ] Set up email notifications (Railway settings)

### Optimization
- [ ] Redis caching working (check logs for cache hits)
- [ ] Response times acceptable (<3 seconds)
- [ ] No memory leaks (monitor Metrics tab)
- [ ] Database queries optimized

### Security
- [ ] Admin password is strong (not "admin123")
- [ ] API keys are in environment variables (not code)
- [ ] CORS is configured (not using wildcard `*`)
- [ ] No sensitive data in logs

### Documentation
- [ ] Team members have Railway access
- [ ] API keys documented securely
- [ ] Deployment process documented
- [ ] Monitoring/alerting set up

---

## Troubleshooting Common Issues

### ❌ Backend Build Fails
**Error**: `"/backend": not found`
- ✅ **FIXED**: Dockerfile updated in latest code
- If still fails: Verify you're on latest commit

### ❌ Frontend Build Fails  
**Error**: `Global CSS cannot be imported`
- ✅ **FIXED**: CSS import removed from admin.js
- If still fails: Check for other pages importing CSS

### ❌ Database Connection Error
```
ERROR: database connection failed
```
**Fix**:
1. Check PostgreSQL is active
2. Verify `DATABASE_URL` is set
3. Enable pgvector: `CREATE EXTENSION IF NOT EXISTS vector;`

### ❌ API Key Invalid
```
ERROR: Invalid API key
```
**Fix**:
1. Check key starts with `sk-ant-`
2. Verify no extra spaces
3. Get new key from console.anthropic.com

### ❌ CORS Error
```
Access blocked by CORS policy
```
**Fix**:
1. Set `FRONTEND_URL` in backend to exact frontend domain
2. Include `https://` in URL
3. Redeploy backend after changing

### ❌ Redis Not Working
```
Redis connection failed
```
**Note**: This is OK - system falls back to in-memory cache
**Fix** (optional):
1. Check Redis service is active
2. Verify `REDIS_URL` is set correctly

---

## Performance Checklist

- [ ] Redis hit rate >70% (check logs)
- [ ] Average response time <3 seconds
- [ ] Memory usage stable (not growing)
- [ ] No 5xx errors in logs
- [ ] Database query time reasonable

---

## Cost Management

### Monitor Usage
- [ ] Railway dashboard → Usage tab
- [ ] Anthropic console → Usage stats
- [ ] Set up billing alerts

### Optimize Costs
- [ ] Redis caching enabled (reduces API calls)
- [ ] Appropriate cache TTLs set
- [ ] Not calling APIs unnecessarily
- [ ] Consider using Claude 3 Haiku for simple queries

### Expected Costs (per month)
- Railway Free Tier: $5 credit
- Typical usage: $2-5
- Claude API: ~$2-10 depending on volume

---

## Success Criteria

✅ All green checkmarks above
✅ Users can chat successfully
✅ No errors in logs
✅ Response times acceptable
✅ All features working
✅ Admin panel accessible
✅ Costs within budget

---

## Next Steps After Launch

1. **Monitor**: Check logs daily for first week
2. **Optimize**: Improve caching strategy
3. **Scale**: Increase resources if needed
4. **Secure**: Regular security audits
5. **Backup**: Configure database backups
6. **Domain**: Add custom domain (optional)
7. **Analytics**: Set up user analytics
8. **Feedback**: Collect user feedback

---

## Support Resources

- **Railway Docs**: https://docs.railway.app
- **Anthropic Docs**: https://docs.anthropic.com
- **Your Repo**: Check Issues tab
- **Railway Community**: Discord server

---

## Emergency Contacts

- Railway Status: https://status.railway.app
- Anthropic Status: https://status.anthropic.com

---

**Estimated Time**: 15-20 minutes  
**Difficulty**: ⭐⭐☆☆☆ (Beginner-Intermediate)  
**Prerequisites**: GitHub account, Railway account, Anthropic API key

🎉 Good luck with your deployment!
