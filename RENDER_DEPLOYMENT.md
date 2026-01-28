# Render.com Deployment Guide for GrownyAI

## Quick Setup Commands for Render.com

### Service Configuration

When creating a new **Web Service** on Render.com, use the following settings:

---

## 📋 Render.com Dashboard Settings

### General Settings
| Setting | Value |
|---------|-------|
| **Name** | `growny-ai` |
| **Environment** | `Python 3` |
| **Region** | (Choose nearest to your users) |
| **Branch** | `main` (or your default branch) |
| **Root Directory** | `.` (leave empty or use root) |
| **Plan** | Free |

---

## 🔧 Build & Start Commands

### Root Directory
```
.
```
*(Leave empty for root directory)*

### Build Command
```bash
pip install -r backend/requirements.txt && cd frontend && npm install && npm run build && mkdir -p ../backend/static && cp -r dist/* ../backend/static/
```

### Start Command
```bash
cd backend && python main.py
```

---

## 🌍 Environment Variables

Add these environment variables in the Render dashboard:

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.11` |
| `NODE_VERSION` | `18` |
| `GEMINI_API_KEY` | *Your Google Gemini API key* |
| `SUPABASE_URL` | *Your Supabase project URL* |
| `SUPABASE_KEY` | *Your Supabase anon/service key* |
| `FIREBASE_ADMIN_SDK_PATH` | `./firebase-admin-sdk.json` |

---

## 📁 Project Structure Requirements

Ensure your project has this structure:
```
project-root/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env (local only, not deployed)
│   └── firebase-admin-sdk.json
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── package.json (root level - optional)
└── render.yaml (optional - for Blueprint deployment)
```

---

## ⚙️ Step-by-Step Deployment

### 1. Connect Your Repository
- Go to [Render Dashboard](https://dashboard.render.com)
- Click **New** → **Web Service**
- Connect your GitHub/GitLab repository

### 2. Configure Service
Fill in the settings as shown above.

### 3. Add Environment Variables
Go to **Environment** tab and add all required variables.

### 4. Deploy
Click **Create Web Service** and wait for deployment.

---

## 🔍 Health Check Path

Set the health check path to:
```
/
```

This hits the root endpoint which returns:
```json
{"message": "Growny-AI Backend API", "version": "1.0.0"}
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Build fails with npm error**
   - Ensure Node.js version 18 is set: `NODE_VERSION=18`

2. **Python module not found**
   - Check `PYTHON_VERSION=3.11` is set
   - Verify `requirements.txt` exists in `backend/`

3. **Firebase initialization error**
   - Ensure `firebase-admin-sdk.json` exists in `backend/`
   - Set `FIREBASE_ADMIN_SDK_PATH=./firebase-admin-sdk.json`

4. **CORS errors**
   - The backend already allows all origins (`*`)
   - Update `main.py` origins if needed

5. **Static files not serving**
   - The build command creates `backend/static/` directory
   - Check if `vite build` succeeded

---

## 📋 Alternative: Using render.yaml (Blueprint)

If you prefer using a Blueprint, a `render.yaml` is already included in the project root:

```yaml
services:
  - type: web
    name: growny-ai
    env: python
    plan: free
    buildCommand: |
      pip install -r backend/requirements.txt
      cd frontend && npm install
      npm run build
      mkdir -p ../backend/static
      cp -r dist/* ../backend/static/
    startCommand: |
      cd backend && python main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: NODE_VERSION
        value: 18
      - key: GEMINI_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: FIREBASE_ADMIN_SDK_PATH
        value: ./firebase-admin-sdk.json
    healthCheckPath: /
```

---

## ✅ Post-Deployment Verification

After deployment, verify:
1. Visit `https://your-app.onrender.com` → Should load the React app
2. Visit `https://your-app.onrender.com/` → Should return API health check
3. Test login with Google authentication
4. Create a test task to verify full functionality

---

## 📞 Support

If you encounter issues:
1. Check Render logs in the dashboard
2. Verify all environment variables are set
3. Ensure your Firebase and Supabase configurations are correct
