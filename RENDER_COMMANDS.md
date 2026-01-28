# Render Deployment Commands

## Quick Start Commands

### 1. Deploy to Render (Automatic)

```bash
# Push your code to GitHub with render.yaml
git add .
git commit -m "Add Render deployment configuration"
git push origin main

# Then in Render Dashboard:
# 1. New → Web Service
# 2. Connect your GitHub repository
# 3. Render will auto-detect render.yaml
```

### 2. Manual Build & Deploy Commands

```bash
# Build frontend and prepare for deployment
npm run install:all
cd frontend && npm run build

# Copy frontend to backend static folder
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

# Start the server (for testing)
cd backend && python main.py
```

### 3. Render Web Service Configuration

**Build Command:**
```bash
pip install -r backend/requirements.txt && cd frontend && npm install && npm run build && mkdir -p ../backend/static && cp -r dist/* ../backend/static/
```

**Start Command:**
```bash
cd backend && python main.py
```

**Environment Variables:**
```bash
GEMINI_API_KEY=your_gemini_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
FIREBASE_ADMIN_SDK_PATH=./firebase-admin-sdk.json
PYTHON_VERSION=3.11
NODE_VERSION=18
```

### 4. Local Testing Commands

```bash
# Test the full deployment process locally
chmod +x deploy.sh
./deploy.sh

# Or step by step:
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build
cd .. && mkdir -p backend/static
cp -r frontend/dist/* backend/static/
cd backend && python main.py
```

### 5. Verification Commands

```bash
# Check API health
curl https://your-app.onrender.com/

# Check frontend is served
curl https://your-app.onrender.com/app

# Check API endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-app.onrender.com/api/tasks
```

## Deployment Architecture

```
┌─────────────────────────────────────┐
│           Render Web Service        │
├─────────────────────────────────────┤
│  FastAPI Server (Port 8000)         │
│  ├── API Routes (/api/*)           │
│  ├── Static Files (/static/*)      │
│  └── SPA Route (/app)               │
├─────────────────────────────────────┤
│  Built Frontend (React/Vite)       │
│  ├── Static HTML/JS/CSS             │
│  └── Assets                         │
└─────────────────────────────────────┘
```

## URL Structure After Deployment

- **Main App**: `https://your-app.onrender.com/app`
- **API Endpoints**: `https://your-app.onrender.com/api/*`
- **Health Check**: `https://your-app.onrender.com/`
- **Static Assets**: `https://your-app.onrender.com/static/*`

## Key Files Created/Modified

1. **`render.yaml`** - Render service configuration
2. **`deploy.sh`** - Manual deployment script
3. **`DEPLOYMENT.md`** - Comprehensive deployment guide
4. **`frontend/vite.config.js`** - Production build configuration
5. **`frontend/.env.production`** - Production environment variables
6. **`backend/main.py`** - Added static file serving

## Next Steps

1. Set up your Render account
2. Add environment variables in Render dashboard
3. Push code with `render.yaml` to GitHub
4. Create web service in Render
5. Test deployment at your Render URL

The deployment is configured to run both frontend and backend in a single web service, optimizing for Render's free tier while maintaining full functionality.
