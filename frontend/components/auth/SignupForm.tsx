'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import Input from '../ui/Input';
import Button from '../ui/Button';

interface SignupFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onSuccess, onError }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { signup, error, isLoading } = useAuth();
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
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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

    const result = await signup(email, password);

    if (result.success) {
      onSuccess?.();
      router.push('/tasks'); // Redirect to tasks after successful signup
    } else {
      onError?.(result.error || 'Signup failed');
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
        autoComplete="new-password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        label="Password"
        error={errors.password}
        required={true}
      />

      <Input
        id="confirmPassword"
        name="confirmPassword"
        type="password"
        autoComplete="new-password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Confirm Password"
        label="Confirm Password"
        error={errors.confirmPassword}
        required={true}
      />

      <div>
        <Button
          type="submit"
          variant="primary"
          disabled={isLoading}
          className="w-full"
        >
          {isLoading ? 'Creating account...' : 'Sign up'}
        </Button>
      </div>

      <div className="text-sm text-center">
        Already have an account?{' '}
        <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
          Sign in
        </Link>
      </div>
    </form>
  );
};

export default SignupForm;