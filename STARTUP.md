# 🚀 Growny-AI Startup Guide

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuration Required

### Firebase Setup
1. Go to Firebase Console
2. Create a new project or use existing "growny-co"
3. Enable Google Sign-In in Authentication
4. Download Firebase Admin SDK JSON and place in `backend/`
5. Update frontend `.env` with your Firebase config

### Supabase Setup
1. Create a Supabase project
2. Create a `tasks` table with columns:
   - `id` (uuid, primary key)
   - `content` (text)
   - `raw_text` (text)
   - `category` (text)
   - `priority` (text)
   - `due_date` (date, nullable)
   - `embedding` (vector, 768 dimensions)
   - `user_id` (text)
   - `created_at` (timestamp)
3. Create the `match_tasks` function for vector search
4. Update backend `.env` with Supabase credentials

### Gemini API
1. Get API key from Google AI Studio
2. Update `GEMINI_API_KEY` in backend `.env`

## 🎯 Features
- ✅ Google Firebase Authentication
- ✅ AI-powered task analysis (Gemini 2.0 Flash)
- ✅ Vector-based semantic search
- ✅ Modern responsive UI with TailwindCSS
- ✅ Real-time task management
- ✅ Professional icons and animations

## 📱 Usage
1. Sign in with Google
2. Add tasks, reminders, or notes
3. AI automatically categorizes and prioritizes
4. Search using natural language
5. Manage your intelligent task list

## 🔍 API Endpoints
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - Get all user tasks
- `POST /api/search` - Search tasks
- `DELETE /api/tasks/{id}` - Delete task
