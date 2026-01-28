import React, { useState } from 'react';
import { signInWithPopup, signOut } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';

const Auth = ({ user, onAuthStateChange }) => {
  const [loading, setLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    // Check if Firebase is properly initialized
    if (!auth || !googleProvider) {
      alert('Firebase is not properly configured. Please check your environment variables.');
      return;
    }

    setLoading(true);
    try {
      console.log('Starting Google sign-in...');
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      
      console.log('Google sign-in successful, user:', result.user.displayName);
      
      // Immediately update auth state
      onAuthStateChange({
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        token
      });
    } catch (error) {
      console.error('Error signing in with Google:', error);
      const errorMessage = error.code === 'auth/popup-closed-by-user' 
        ? 'Sign-in was cancelled. Please try again.'
        : error.code === 'auth/popup-blocked'
        ? 'Pop-up was blocked by your browser. Please allow pop-ups and try again.'
        : `Sign in error: ${error.message}`;
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    if (!auth) {
      onAuthStateChange(null);
      return;
    }

    setLoading(true);
    try {
      await signOut(auth);
      onAuthStateChange(null);
    } catch (error) {
      console.error('Error signing out:', error);
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return (
      <button
        onClick={handleSignOut}
        disabled={loading}
        className="btn-secondary"
      >
        {loading ? '...' : 'Sign Out'}
      </button>
    );
  }

  return (
    <button
      onClick={handleGoogleSignIn}
      disabled={loading || !auth || !googleProvider}
      className="btn-primary"
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          Signing in...
        </span>
      ) : !auth || !googleProvider ? (
        'Firebase Not Configured'
      ) : (
        'Sign in with Google'
      )}
    </button>
  );
};

export default Auth;
