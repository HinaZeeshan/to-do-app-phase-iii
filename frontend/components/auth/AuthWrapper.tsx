'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import LoadingSpinner from '../ui/LoadingSpinner';

interface AuthWrapperProps {
  children: React.ReactNode;
  requireAuth?: boolean; // If true, redirects to login if not authenticated
  redirectTo?: string; // Where to redirect if not authenticated (default: '/login')
}

export const AuthWrapper: React.FC<AuthWrapperProps> = ({
  children,
  requireAuth = true,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (requireAuth && !isAuthenticated) {
        router.push(redirectTo);
      } else if (!requireAuth && isAuthenticated) {
        // If auth is not required but user is logged in, maybe redirect to dashboard
        // This is optional behavior - you can customize as needed
      }
    }
  }, [isAuthenticated, isLoading, requireAuth, redirectTo, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // If auth is required and user is not authenticated, don't render children
  if (requireAuth && !isAuthenticated) {
    return null; // The redirect happens in the useEffect
  }

  return <>{children}</>;
};

export default AuthWrapper;