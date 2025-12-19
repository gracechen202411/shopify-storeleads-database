'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import StoreCard from '@/components/StoreCard';
import { Store } from '@/lib/db';
import { Button } from '@/components/ui/button';

interface FavoriteStore extends Store {
  favorite_id: number;
  notes?: string;
  priority?: string;
  favorited_at: string;
}

export default function FavoritesPage() {
  const router = useRouter();
  const [favorites, setFavorites] = useState<FavoriteStore[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchFavorites = async () => {
    try {
      const response = await fetch('/api/favorites');
      if (response.ok) {
        const data = await response.json();
        setFavorites(data.favorites || []);
      } else if (response.status === 401) {
        router.push('/login');
      }
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, []);

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">加载收藏...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-gradient-to-r from-yellow-500 via-yellow-600 to-orange-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                onClick={() => router.push('/')}
                variant="ghost"
                className="text-white hover:bg-white/20"
              >
                ← 返回主页
              </Button>
              <div>
                <h1 className="text-3xl font-extrabold">⭐ 我的收藏</h1>
                <p className="text-yellow-100 text-sm mt-1">
                  已收藏 {favorites.length} 家店铺
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              {favorites.length > 0 && (
                <Button
                  onClick={() => window.open('/api/export/favorites', '_blank')}
                  className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
                >
                  📥 导出收藏 ({favorites.length}条)
                </Button>
              )}
              <Button
                variant="secondary"
                onClick={handleLogout}
                className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
              >
                退出登录
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {favorites.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">☆</div>
            <h2 className="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-2">
              还没有收藏任何店铺
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              在主页点击星标按钮收藏感兴趣的店铺
            </p>
            <Button
              onClick={() => router.push('/')}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              去主页看看
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {favorites.map((store) => (
              <div key={store.favorite_id} className="relative">
                <StoreCard store={store} viewMode="grid" />
                {store.notes && (
                  <div className="absolute top-2 right-2 bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded text-xs">
                    📝 {store.notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-yellow-900 via-orange-900 to-red-900 text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-yellow-200">
            ⭐ 收藏功能帮助你快速找到重点关注的店铺
          </p>
        </div>
      </footer>
    </div>
  );
}
