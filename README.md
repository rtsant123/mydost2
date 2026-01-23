# Multi-Domain Conversational AI Chatbot

A Claude-like conversational AI chatbot with support for multiple domains (education, sports, astrology, etc.), multilingual interaction (Assamese, Hindi, English), RAG capabilities, and an admin panel. Built with Python (FastAPI) backend and Next.js frontend.

## Project Structure

```
/backend/               # Python FastAPI backend
/frontend/              # Next.js React frontend
```

## Features

- **Multi-Domain Support**: Education, Sports Predictions, Teer Analysis, Astrology, OCR, PDF Processing, News Summarization, Image Editing, Personal Notes
- **Trilingual**: Assamese, Hindi, English with auto-detection
- **RAG Pipeline**: Vector database integration for semantic retrieval and long-term memory
- **External APIs**: Web search, news, sports data integration
- **Admin Panel**: Module management, analytics, API key configuration

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```