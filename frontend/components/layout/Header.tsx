'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../../hooks/useAuth';

export const Header: React.FC = () => {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
  };

  if (isLoading) {
    return (
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="animate-pulse rounded-md bg-gray-200 h-8 w-24"></div>
            </div>
            <div className="flex items-center">
              <div className="animate-pulse rounded-md bg-gray-200 h-8 w-24"></div>
            </div>
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold text-blue-600">TodoApp</span>
            </Link>
            <nav className="ml-6 hidden md:flex md:space-x-8">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/tasks"
                    className="text-gray-900 hover:text-blue-600 px-1 pt-1 font-medium"
                  >
                    My Tasks
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-gray-900 hover:text-blue-600 px-1 pt-1 font-medium"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/signup"
                    className="text-gray-900 hover:text-blue-600 px-1 pt-1 font-medium"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </nav>
          </div>
          <div className="flex items-center">
            {isAuthenticated ? (
              <div className="flex items-center">
                <span className="hidden md:block text-sm text-gray-700 mr-4">
                  Welcome, {user?.email || user?.id}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-blue-600 font-medium text-sm"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="text-gray-700 hover:text-blue-600 font-medium text-sm"
              >
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 focus:outline-none"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <svg
                className={`${isMenuOpen ? 'hidden' : 'block'} h-6 w-6`}
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg
                className={`${isMenuOpen ? 'block' : 'hidden'} h-6 w-6`}
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="pt-2 pb-3 space-y-1 px-2">
            {isAuthenticated ? (
              <>
                <Link
                  href="/tasks"
                  className="text-gray-900 hover:text-blue-600 block pl-3 pr-4 py-2 border-l-4 border-blue-500 text-base font-medium"
                >
                  My Tasks
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-blue-600 block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium w-full text-left"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-gray-900 hover:text-blue-600 block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium"
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="text-gray-900 hover:text-blue-600 block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;