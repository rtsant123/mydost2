# Setup and Development Guide

## System Requirements

- Python 3.11+
- Node.js 18+
- npm or yarn
- Git

### Optional Services

- Qdrant (for vector database) or Pinecone cloud
- Docker (for containerization)
- Railway account (for deployment)

## Local Development Setup

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <repo-url>
cd mydost2

# Copy environment files
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local

# Edit .env with your API keys
nano .env
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload

# Backend runs at http://localhost:8000
```

### 3. Frontend Setup (in new terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup Tailwind CSS
npx tailwindcss init -p

# Run development server
npm run dev

# Frontend runs at http://localhost:3000
```

### 4. Access Application

- **Chat**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Keys and Configuration

### Required API Keys

1. **OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys
   - Set in: `.env` file as `OPENAI_API_KEY`

2. **Web Search API (Serper)**
   - Get from: https://serper.dev
   - Set in: `.env` as `SEARCH_API_KEY`

3. **News API**
   - Get from: https://newsapi.org
   - Set in: `.env` as `NEWS_API_KEY`

4. **Vector Database (Qdrant)**
   - Option A: Run locally with Docker:
     ```bash
     docker run -p 6333:6333 qdrant/qdrant
     ```
   - Option B: Use Qdrant Cloud: https://qdrant.tech/cloud

### Optional API Keys

- **Sports API**: https://www.thesportsdb.com
- **Astrology API**: Various providers available
- **Admin Password**: Set your own strong password

## Project Structure

```
mydost2/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Docker configuration
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic services
│   ├── utils/              # Utility functions
│   └── data/               # Static data files
│
├── frontend/               # Next.js React frontend
│   ├── pages/              # Next.js pages
│   ├── components/         # React components
│   ├── utils/              # Frontend utilities
│   ├── styles/             # CSS styles
│   ├── package.json        # Node dependencies
│   └── next.config.js      # Next.js configuration
│
├── README.md              # Project overview
├── DEPLOYMENT.md          # Deployment instructions
├── .env.example           # Environment template
└── .gitignore            # Git ignore rules
```

## Development Workflow

### Adding a New Feature

1. **Backend**: Create service in `backend/services/`
2. **Backend**: Add router in `backend/routers/`
3. **Frontend**: Create component in `frontend/components/`
4. **Frontend**: Add page or update existing
5. **Test**: Both locally and with Docker

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Linting
npm run lint
```

### Code Organization

**Backend Services**:
- `llm_service.py` - LLM interactions
- `embedding_service.py` - Text embeddings
- `vector_store.py` - Vector database operations
- `search_service.py` - Web search
- `ocr_service.py` - Image text extraction
- `pdf_service.py` - PDF processing
- And more...

**Frontend Components**:
- `ChatWindow.jsx` - Message display
- `InputBar.jsx` - Message input
- `MessageBubble.jsx` - Individual messages
- `Sidebar.jsx` - Navigation sidebar

## Features Guide

### 1. Chat
- Multilingual support (Assamese, Hindi, English)
- Automatic language detection
- Conversation history
- Web search integration

### 2. OCR
- Image text extraction
- Multilingual support
- Supported formats: JPEG, PNG, TIFF, WebP

### 3. PDF Processing
- PDF upload and text extraction
- Semantic chunking
- RAG for Q&A

### 4. Image Editing
- Crop, resize, enhance
- Brightness/contrast adjustment
- Text annotation

### 5. Admin Panel
- Module toggles
- System prompt editing
- Usage statistics
- Cache management

## Troubleshooting

### Backend Issues

**Import errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Port already in use**:
```bash
# Use different port
uvicorn main:app --port 8001
```

**Missing API keys**:
- Check `.env` file exists and has all keys
- Verify keys are correct
- Check API key limits/usage

### Frontend Issues

**Dependencies not installing**:
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Port already in use**:
```bash
# Use different port
npm run dev -- -p 3001
```

### Connection Issues

**Frontend can't reach backend**:
- Check backend is running
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS configuration
- Check firewall/network

## Performance Optimization

### Backend
- Use async/await for concurrent operations
- Implement caching for repeated queries
- Optimize vector DB queries
- Use pagination for large datasets

### Frontend
- Lazy load components
- Implement virtualization for long lists
- Use React memo for optimization
- Optimize images

## Security Best Practices

1. **Never commit API keys** - Use `.env` files
2. **Validate all inputs** - Both frontend and backend
3. **Use HTTPS** - In production
4. **Secure admin panel** - Strong password
5. **Rate limiting** - Implement on backend
6. **CORS configuration** - Set proper origins

## Database

### Vector Database Setup

**Qdrant Local**:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Qdrant Cloud**:
1. Sign up: https://qdrant.tech/cloud
2. Get API key
3. Set `VECTOR_DB_URL` and `VECTOR_DB_API_KEY`

## Monitoring and Logging

- Backend logs go to console
- Frontend errors visible in browser console
- Enable debug mode: `DEBUG=true` in `.env`

## Next Steps

1. Set up all API keys
2. Start local development
3. Test each feature
4. Deploy to Railway
5. Monitor production

## Getting Help

- Check GitHub Issues
- Review API documentation in `/docs`
- Check service logs
- Test endpoints manually with curl/Postman

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

MIT - See LICENSE file
