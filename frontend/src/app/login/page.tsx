/**
 * Login Page - Officer Dashboard
 */

'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Shield, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    try {
      await login(identifier, password);
      router.push('/officer/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Image src="/logo.png" alt="SahaiSetu Logo" width={80} height={80} className="object-contain mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Officer Dashboard</h1>
          <p className="text-gray-600">Sign in to access the SahaiSetu system</p>
        </div>

        {/* Demo Credentials */}
        <Card className="mb-6 border-amber-200 bg-amber-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-amber-800">
                <p className="font-medium">Demo Credentials</p>
                <p className="mt-1 font-mono text-xs">admin@nhaa.local / admin123</p>
                <p className="font-mono text-xs">counsellor@nhaa.local / counsellor123</p>
                <p className="font-mono text-xs">legal@nhaa.local / legal123</p>
                <p className="font-mono text-xs">officer1@nhaa.local / demo123</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Login Form */}
        <Card>
          <CardHeader className="text-center">
            <CardTitle>Sign In</CardTitle>
            <CardDescription>Enter your credentials to access the dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm" role="alert">
                  {error}
                </div>
              )}
              <Input
                label="Identifier (Email/Username)"
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="Enter your identifier"
                required
                autoComplete="username"
              />
              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
              <Button type="submit" className="w-full" size="lg" isLoading={isSubmitting}>
                Sign In
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="mt-6 text-center text-xs text-gray-400">
          <p>SahaiSetu - Prototype for SIH26093</p>
        </div>
      </div>
    </div>
  );
}
