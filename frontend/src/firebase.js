import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, onIdTokenChanged } from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

let app, auth, googleProvider;

// Check if all required config values are present
const isConfigValid = () => {
  return firebaseConfig.apiKey &&
    firebaseConfig.authDomain &&
    firebaseConfig.projectId &&
    firebaseConfig.appId;
};

if (!isConfigValid()) {
  console.error('Firebase configuration is incomplete. Please check your environment variables.');
  console.log('Current config:', firebaseConfig);
}

try {
  if (isConfigValid()) {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();

    // Configure Google Provider
    googleProvider.setCustomParameters({
      prompt: 'select_account'
    });

    console.log('Firebase initialized successfully');
  } else {
    throw new Error('Firebase configuration is incomplete');
  }
} catch (error) {
  console.error('Firebase initialization error:', error);
  // Create dummy auth object to prevent undefined errors
  auth = null;
  googleProvider = null;
}

/**
 * Get the current user's fresh ID token.
 * This always returns a fresh token by forcing a refresh if needed.
 * @param {boolean} forceRefresh - Force token refresh even if not expired
 * @returns {Promise<string|null>} The ID token or null if not authenticated
 */
export const getCurrentToken = async (forceRefresh = false) => {
  if (!auth || !auth.currentUser) {
    return null;
  }
  try {
    const token = await auth.currentUser.getIdToken(forceRefresh);
    // Update localStorage with the fresh token
    localStorage.setItem('authToken', token);
    return token;
  } catch (error) {
    console.error('Error getting ID token:', error);
    return null;
  }
};

// Set up automatic token refresh listener
if (auth) {
  onIdTokenChanged(auth, async (user) => {
    if (user) {
      try {
        const token = await user.getIdToken();
        localStorage.setItem('authToken', token);
        console.log('[Firebase] Token refreshed automatically');
      } catch (error) {
        console.error('[Firebase] Error refreshing token:', error);
      }
    } else {
      localStorage.removeItem('authToken');
    }
  });
}

export { auth, googleProvider };
export default app;
