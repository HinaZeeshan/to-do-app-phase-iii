// Authentication helper functions

// Store JWT token in localStorage
export const setAuthToken = (token: string, refreshToken?: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('jwtToken', token);
    if (refreshToken) {
      localStorage.setItem('refreshToken', refreshToken);
    }
  }
};

// Retrieve JWT token from localStorage
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('jwtToken');
  }
  return null;
};

// Retrieve Refresh token from localStorage
export const getRefreshToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('refreshToken');
  }
  return null;
};

// Remove JWT token from localStorage
export const removeAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('jwtToken');
    localStorage.removeItem('refreshToken');
  }
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  if (!token) {
    return false;
  }

  // Decode JWT token to check expiration
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp > currentTime;
  } catch (error) {
    console.error('Error decoding token:', error);
    return false;
  }
};

// Check if token is about to expire (within 5 minutes)
export const isTokenExpiringSoon = (): boolean => {
  const token = getAuthToken();
  if (!token) {
    return false;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    const fiveMinutes = 5 * 60; // 5 minutes in seconds
    return payload.exp - currentTime < fiveMinutes;
  } catch (error) {
    console.error('Error decoding token:', error);
    return true; // If we can't decode, assume token is bad
  }
};

// Get user ID from token
export const getUserIdFromToken = (): string | null => {
  const token = getAuthToken();
  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.userId || payload.user_id || payload.sub;
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};