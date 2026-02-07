'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import Input from '../ui/Input';
import Button from '../ui/Button';

interface LoginFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onError }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { login, error, isLoading } = useAuth();
  const router = useRouter();

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      onError?.('Please fix the errors in the form');
      return;
    }

    const result = await login(email, password);

    if (result.success) {
      onSuccess?.();
      router.push('/tasks'); // Redirect to tasks after successful login
    } else {
      onError?.(result.error || 'Login failed');
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      <Input
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email address"
        label="Email"
        error={errors.email}
        required={true}
      />

      <Input
        id="password"
        name="password"
        type="password"
        autoComplete="current-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        label="Password"
        error={errors.password}
        required={true}
      />

      <div className="flex items-center justify-between">
        <div className="text-sm">
          <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
            Forgot your password?
          </a>
        </div>
      </div>

      <div>
        <Button
          type="submit"
          variant="primary"
          disabled={isLoading}
          className="w-full"
        >
          {isLoading ? 'Signing in...' : 'Sign in'}
        </Button>
      </div>

      <div className="text-sm text-center">
        Don't have an account?{' '}
        <Link href="/signup" className="font-medium text-blue-600 hover:text-blue-500">
          Sign up
        </Link>
      </div>
    </form>
  );
};

export default LoginForm;