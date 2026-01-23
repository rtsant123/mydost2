# Multi-Domain Conversational AI Chatbot

> **✅ Railway Deployment Ready!** - Now using Claude AI + PostgreSQL + Redis

A Claude-like conversational AI chatbot with support for multiple domains (education, sports, astrology, etc.), multilingual interaction (Assamese, Hindi, English), RAG capabilities, and an admin panel. Built with Python (FastAPI) backend and Next.js frontend.

## 🚀 Quick Deploy to Railway

**Deploy in 10 minutes** - Follow [RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md)

1. Add PostgreSQL + Redis on Railway
2. Deploy backend from GitHub
3. Deploy frontend from GitHub
4. Done! 🎉

## 🔧 Tech Stack

- **LLM**: Anthropic Claude 3.5 Sonnet
- **Backend**: Python FastAPI
- **Frontend**: Next.js + React + TailwindCSS
- **Database**: PostgreSQL with pgvector
- **Cache**: Redis
- **Deployment**: Railway (1-click)

## Project Structure

```
/backend/               # Python FastAPI backend
  /services/            # LLM, vector store, domain services
  /routers/             # API endpoints
  /utils/               # Config, caching, language detection
/frontend/              # Next.js React frontend
  /pages/               # Chat and admin pages
  /components/          # React components
  /utils/               # API client, storage
```

## Features

- **Multi-Domain Support**: Education, Sports Predictions, Teer Analysis, Astrology, OCR, PDF Processing, News Summarization, Image Editing, Personal Notes
- **Trilingual**: Assamese, Hindi, English with auto-detection
- **RAG Pipeline**: PostgreSQL + pgvector for semantic retrieval and long-term memory
- **Redis Caching**: Fast responses, reduced API costs
- **External APIs**: Web search, news, sports data integration
- **Admin Panel**: Module management, analytics, API key configuration

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)

### With Docker (Recommended)
```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and add your ANTHROPIC_API_KEY

# 3. Start all services
docker-compose up

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

- **[RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md)** - Deploy in 10 minutes
- **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** - Comprehensive deployment guide
- **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - What changed (OpenAI→Claude, Qdrant→PostgreSQL)
- **[SETUP.md](SETUP.md)** - Detailed local development guide
- **[SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)** - Complete system documentation

## 🔑 Get API Keys

1. **Anthropic Claude AI** (Required)
   - https://console.anthropic.com/
   - Free tier: $5 credit
   
2. **Serper** (Optional - Web Search)
   - https://serper.dev
   - Free tier: 2,500 searches/month

3. **NewsAPI** (Optional - News)
   - https://newsapi.org
   - Free tier: 100 requests/day

## 🎯 Features

### Multi-Domain Intelligence
- 📚 **Education**: Q&A, explanations, learning support
- ⚽ **Sports**: Team stats, match predictions
- 🎯 **Teer**: Analysis, predictions, historical data
- ✨ **Astrology**: Daily horoscopes, zodiac info
- 🖼️ **OCR**: Extract text from images (Assamese/Hindi/English)
- 📄 **PDF**: Upload and query documents
- 📰 **News**: Latest headlines and summaries
- 🎨 **Image Editing**: Crop, enhance, annotate
- 📝 **Personal Notes**: Long-term memory

### Advanced Capabilities
- 🧠 **RAG**: Retrieves relevant context from your history
- 🌍 **Multilingual**: Auto-detects and responds in Assamese/Hindi/English
- ⚡ **Redis Caching**: Fast responses, reduced costs
- 🔍 **Web Search**: Real-time information via Serper
- 💬 **Streaming**: Real-time response generation
- 👤 **User Memory**: Remembers past conversations per user

## 🛠️ Admin Panel

Access at `/admin` with your admin password:
- Toggle features on/off
- Edit system prompt
- View usage statistics
- Clear caches
- Manage configurations

## 📊 Architecture

```
User → Next.js Frontend
         ↓
    FastAPI Backend
         ↓
    ┌────┴────┬──────────┬─────────┐
    ↓         ↓          ↓         ↓
Claude AI  PostgreSQL  Redis   External APIs
          (pgvector)         (Search/News)
```

## 🐛 Troubleshooting

### Build Errors Fixed ✅
- ❌ Backend: `"/backend": not found` → ✅ Dockerfile paths fixed
- ❌ Frontend: CSS import error → ✅ Removed duplicate import

### Common Issues

**Database connection failed**
```bash
# Enable pgvector extension
railway connect postgres
CREATE EXTENSION IF NOT EXISTS vector;
```

**Redis not working**
- System falls back to in-memory cache automatically
- Check `REDIS_URL` is set correctly

**Claude API errors**
- Verify `ANTHROPIC_API_KEY` starts with `sk-ant-`
- Check https://console.anthropic.com/ for usage limits

## 💰 Cost Estimate

**Railway Free Tier**: $5/month credit
- PostgreSQL: ~$1-2/month
- Redis: ~$1/month  
- Backend/Frontend: ~$1-2/month

**Claude API** (pay-as-you-go):
- Claude 3.5 Sonnet: $3/$15 per 1M input/output tokens
- Typical chat: ~500 tokens = $0.005

**Total**: ~$5-10/month for moderate use

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test locally with `docker-compose up`
5. Submit pull request

## 📄 License

MIT License - Free to use and modify

## 🙏 Acknowledgments

- **Anthropic** - Claude AI API
- **Railway** - Easy deployment platform
- **pgvector** - PostgreSQL vector similarity
- **Next.js** - React framework
- **FastAPI** - Python web framework

---

**Status**: ✅ Production Ready  
**Version**: 2.0.0  
**Last Updated**: January 2026

🚀 Ready to deploy? Start with [RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md)