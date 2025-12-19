'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store the session token and user email
        document.cookie = `auth-token=${data.token}; path=/; max-age=86400`; // 24 hours
        document.cookie = `user_email=${username}@topsales.com; path=/; max-age=86400`; // 24 hours
        router.push('/');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-pink-600 to-red-600 px-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="space-y-3 text-center pb-6">
          <div className="flex justify-center mb-2">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-4xl shadow-lg">
              🚀
            </div>
          </div>
          <CardTitle className="text-3xl font-extrabold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            豆豆 & 唯一专属数据库
          </CardTitle>
          <CardDescription className="text-base">
            🎯 开启你们的 Top Sales 之旅
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-sm font-semibold">用户名</Label>
              <Input
                id="username"
                type="text"
                placeholder="输入你的用户名"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
                className="h-11"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-semibold">密码</Label>
              <Input
                id="password"
                type="password"
                placeholder="输入你的密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                className="h-11"
              />
            </div>
            {error && (
              <div className="text-red-600 text-sm text-center bg-red-50 dark:bg-red-900/20 p-3 rounded-lg font-medium">
                {error}
              </div>
            )}
            <Button
              type="submit"
              className="w-full h-11 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold text-base"
              disabled={loading}
            >
              {loading ? '登录中...' : '🚀 立即登录'}
            </Button>
          </form>
          <div className="mt-6 text-center space-y-2">
            <div className="inline-block bg-gradient-to-r from-purple-100 to-pink-100 px-4 py-3 rounded-lg">
              <p className="text-sm text-gray-700 font-medium mb-2">
                💡 可用账号：
              </p>
              <div className="space-y-1 text-xs">
                <p><span className="font-bold text-purple-600">doudou</span> / <span className="font-bold text-pink-600">TopSales2025!</span></p>
                <p><span className="font-bold text-purple-600">weiyi</span> / <span className="font-bold text-pink-600">GoogleSales2025!</span></p>
                <p><span className="font-bold text-purple-600">grace</span> / <span className="font-bold text-pink-600">SuperGrace2025!</span></p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
