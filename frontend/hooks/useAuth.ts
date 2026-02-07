import { useState, useEffect } from 'react';
import { setAuthToken, getAuthToken, removeAuthToken, isAuthenticated, getUserIdFromToken } from '../lib/auth';
import { authApi } from '../lib/api';

interface AuthState {
  user: {
    id: string;
    email: string;
  } | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isLoading: true,
    error: null,
    isAuthenticated: false,
  });

  // Check authentication status on mount
  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      try {
        // Decode JWT to get user info
        const payload = JSON.parse(atob(token.split('.')[1]));

        // Check if token is expired
        const currentTime = Math.floor(Date.now() / 1000);
        if (payload.exp < currentTime) {
          // Token is expired, remove it
          removeAuthToken();
          setAuthState({
            user: null,
            token: null,
            isLoading: false,
            error: 'Session expired',
            isAuthenticated: false,
          });
          return;
        }

        setAuthState({
          user: {
            id: payload.userId || payload.user_id || payload.sub,
            email: payload.email || '',
          },
          token,
          isLoading: false,
          error: null,
          isAuthenticated: true,
        });
      } catch (error) {
        console.error('Error decoding token:', error);
        removeAuthToken();
        setAuthState({
          user: null,
          token: null,
          isLoading: false,
          error: 'Invalid token',
          isAuthenticated: false,
        });
      }
    } else {
      setAuthState({
        user: null,
        token: null,
        isLoading: false,
        error: null,
        isAuthenticated: false,
      });
    }
  }, []);

  const login = async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const { data } = await authApi.login(email, password);
      const { token, refresh_token, user_id, email: userEmail } = data;
      const user = { id: user_id, email: userEmail };

      setAuthToken(token, refresh_token);
      setAuthState({
        user,
        token,
        isLoading: false,
        error: null,
        isAuthenticated: true,
      });

      return { success: true, data };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      return { success: false, error: errorMessage };
    }
  };

  const signup = async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const { data } = await authApi.signup(email, password);
      const { token, refresh_token, user_id, email: userEmail } = data;
      const user = { id: user_id, email: userEmail };

      setAuthToken(token, refresh_token);
      setAuthState({
        user,
        token,
        isLoading: false,
        error: null,
        isAuthenticated: true,
      });

      return { success: true, data };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Signup failed';
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    removeAuthToken();
    setAuthState({
      user: null,
      token: null,
      isLoading: false,
      error: null,
      isAuthenticated: false,
    });
  };

  const clearError = () => {
    setAuthState(prev => ({ ...prev, error: null }));
  };

  return {
    ...authState,
    login,
    signup,
    logout,
    clearError,
  };
};