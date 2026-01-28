# Firebase Setup Guide

## Quick Setup Instructions

### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" and create a new project
3. Enable Google Sign-In in Authentication → Sign-in method

### 2. Get Firebase Configuration
1. In Firebase Console, go to Project Settings
2. Under "Your apps", click the web app icon (</>)
3. Copy the Firebase configuration object

### 3. Create Environment Variables
Create a `.env.local` file in the `frontend` directory:

```bash
# Replace with your actual Firebase values
VITE_FIREBASE_API_KEY=your_actual_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_actual_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_actual_sender_id
VITE_FIREBASE_APP_ID=your_actual_app_id

# Backend URL
VITE_API_URL=http://localhost:8000
```

### 4. Backend Setup (Optional for full functionality)
For the backend to verify Firebase tokens, you need:
1. Go to Firebase Console → Project Settings → Service accounts
2. Click "Generate new private key"
3. Save the JSON file as `firebase-admin-sdk.json` in the `backend` directory
4. Update the backend `.env` file with:
```bash
FIREBASE_ADMIN_SDK_PATH=./firebase-admin-sdk.json
```

### 5. Start the Application
```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## What's Fixed
✅ **Optimized user data loading** - Tasks load immediately after authentication
✅ **Better error handling** - Clear error messages for common Firebase issues
✅ **Improved logging** - Console logs to track authentication flow
✅ **Enhanced user feedback** - Better loading states and error messages

## Testing
1. Open http://localhost:5173
2. Click "Sign in with Google"
3. Complete the Google authentication flow
4. Your tasks should load automatically

## Troubleshooting
- **"Firebase Not Configured"**: Check your `.env.local` file values
- **"Pop-up was blocked"**: Allow pop-ups for localhost in your browser
- **Backend auth errors**: Ensure Firebase Admin SDK is properly configured
