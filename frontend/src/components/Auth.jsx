import React, { useState } from 'react';
import { signInWithPopup, signOut } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';

const Auth = ({ user, onAuthStateChange }) => {
  const [loading, setLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      onAuthStateChange({
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        token
      });
    } catch (error) {
      console.error('Error signing in with Google:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
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
      disabled={loading}
      className="btn-primary"
    >
      {loading ? '...' : 'Sign in with Google'}
    </button>
  );
};

export default Auth;
