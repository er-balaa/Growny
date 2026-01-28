# Render Deployment Guide - Growny-AI

## Overview
This guide explains how to deploy the Growny-AI application (React frontend + FastAPI backend) as a single web service on Render.

## Architecture
- **Single Web Service**: FastAPI backend serves both API endpoints and static frontend files
- **Frontend**: React/Vite application built to static files
- **Backend**: FastAPI with Python
- **Database**: Supabase (external service)
- **Authentication**: Firebase Auth

## Deployment Files

### 1. `render.yaml`
Configuration file for Render deployment that:
- Installs both Python and Node.js dependencies
- Builds the React frontend
- Copies built files to backend static folder
- Starts the FastAPI server

### 2. `deploy.sh`
Manual deployment script for local testing or alternative deployment methods

## Environment Variables Required

Set these in your Render dashboard under Environment Variables:

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Firebase
FIREBASE_ADMIN_SDK_PATH=./firebase-admin-sdk.json

# Optional: Node and Python versions (usually set by render.yaml)
NODE_VERSION=18
PYTHON_VERSION=3.11
```

## Deployment Steps

### Option 1: Using Render Dashboard (Recommended)

1. **Create a New Web Service**
   - Go to Render Dashboard → New → Web Service
   - Connect your GitHub repository
   - Select the root directory of your project

2. **Configure Build Settings**
   - **Runtime**: Python 3.11
   - **Build Command**: Use the command from `render.yaml`
   - **Start Command**: Use the command from `render.yaml`

3. **Set Environment Variables**
   - Add all required environment variables from the section above

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### Option 2: Using `render.yaml` (Automatic)

1. Push the `render.yaml` file to your repository root
2. Connect your repository to Render
3. Render will automatically detect and use the configuration

### Option 3: Manual Deployment

1. Clone your repository to the server
2. Run the deployment script:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## How It Works

### Build Process
1. **Python Dependencies**: Installs FastAPI and required packages
2. **Node.js Dependencies**: Installs React and frontend packages
3. **Frontend Build**: Creates production build of React app
4. **Static Files**: Copies built frontend to backend `/static` folder

### Runtime Process
1. **FastAPI Server**: Starts on port 8000 (Render's expected port)
2. **API Routes**: Serves `/api/*` endpoints
3. **Static Files**: Serves frontend from `/static/*`
4. **SPA Support**: Root route serves the React application

### URL Structure
- **API Endpoints**: `https://your-app.onrender.com/api/*`
- **Frontend App**: `https://your-app.onrender.com/`
- **Static Assets**: `https://your-app.onrender.com/static/*`

## Local Development

To test the deployment setup locally:

```bash
# Build and run locally
./deploy.sh
```

Or manually:

```bash
# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build

# Copy static files
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

# Run server
cd backend && python main.py
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all environment variables are set
   - Verify `requirements.txt` and `package.json` are correct
   - Check build logs in Render dashboard

2. **Static File Issues**
   - Ensure frontend builds successfully
   - Verify static files are copied to `/static` folder
   - Check file permissions

3. **API Connection Issues**
   - Verify CORS settings in `main.py`
   - Check that frontend API URL is correct (empty for same-origin)
   - Ensure authentication tokens are working

4. **Environment Variable Issues**
   - Double-check variable names in Render dashboard
   - Verify Firebase SDK file is accessible
   - Check Supabase connection details

### Debugging

1. **View Logs**: Check Render dashboard logs for errors
2. **Health Check**: Visit `/` endpoint for API status
3. **Static Files**: Check `/static/` for frontend files
4. **Network Tab**: Use browser dev tools to check API calls

## Production Optimizations

The deployment includes several optimizations:

1. **Static File Serving**: FastAPI efficiently serves built frontend
2. **CORS Configuration**: Properly configured for production
3. **Error Handling**: Comprehensive error responses
4. **Security**: Firebase token verification for all API endpoints

## Scaling

- **Free Tier**: Suitable for development and small projects
- **Paid Tiers**: Better performance and reliability for production
- **Database**: Consider upgrading Supabase plan for higher limits

## Support

For issues:
1. Check Render documentation: https://render.com/docs
2. Review this deployment guide
3. Check application logs in Render dashboard
4. Test locally using the deployment script
