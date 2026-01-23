# Google OAuth Setup Guide

## 1. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add authorized JavaScript origins:
     - `http://localhost:3000` (local)
     - `https://your-frontend-domain.railway.app` (production)
   - Add authorized redirect URIs:
     - `http://localhost:3000/api/auth/callback/google` (local)
     - `https://your-frontend-domain.railway.app/api/auth/callback/google` (production)
   - Click "Create"
   - Copy the Client ID and Client Secret

## 2. Frontend Environment Variables

Create `.env.local` in the frontend folder:

```bash
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=run-this-command-openssl-rand-base64-32
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Generate NEXTAUTH_SECRET:
```bash
openssl rand -base64 32
```

## 3. Railway Environment Variables

### Frontend Service:
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXTAUTH_URL=https://your-frontend-domain.railway.app
NEXTAUTH_SECRET=your-generated-secret
NEXT_PUBLIC_API_URL=https://your-backend-domain.railway.app
```

### Backend Service:
```
ANTHROPIC_API_KEY=your-claude-api-key
DATABASE_URL=postgresql://postgres:password@host:port/railway
REDIS_URL=redis://default:password@host:port
SEARCH_API_KEY=your-serper-api-key
SEARCH_API_URL=https://google.serper.dev/search
FRONTEND_URL=https://your-frontend-domain.railway.app
```

## 4. Install Dependencies

### Frontend:
```bash
cd frontend
npm install next-auth
```

### Backend (already included):
No additional dependencies needed

## 5. Test Locally

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit http://localhost:3000 and click "Sign in with Google"

## Features Implemented

✅ **Google OAuth Sign-In** - One-click login with Google account
✅ **User Preferences on Signup** - Collect user preferences during first login:
  - Preferred Language (English, Hindi, Assamese)
  - Conversation Tone (Friendly, Professional, Supportive)
  - Interests (Education, Sports, Teer, Astrology, News, etc.)
  - Response Style (Concise, Balanced, Detailed)

✅ **Personalized AI Responses** - AI adapts based on user preferences:
  - Responds in user's preferred language
  - Adjusts tone (friendly/professional/supportive)
  - Provides responses matching desired detail level
  - Considers user interests when relevant

## User Flow

1. User visits site → Redirected to Google Sign-In
2. Signs in with Google → Backend creates user account
3. First-time users → Redirected to preferences page
4. User sets preferences → Saved to backend
5. Chat interface loads → AI uses personalized system prompt
6. Every response tailored to user's preferences

## Updating Preferences

Users can update preferences anytime from settings (you can add a settings page later).
