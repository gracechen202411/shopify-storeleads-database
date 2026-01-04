'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import SearchBar from '@/components/SearchBar';
import StoreCard from '@/components/StoreCard';
import { Store } from '@/lib/db';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface SearchResult {
  stores: Store[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

interface Stats {
  total_stores: string;
  total_countries: string;
  total_employees: string;
  avg_monthly_visits: string;
}

export default function Home() {
  const router = useRouter();
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filters, setFilters] = useState({
    country: '',
    state: '',
    city: '',
    category: '',
    plan: '',
    minVisits: '',
    maxVisits: '',
    minEmployees: '',
    hasSocial: '',
    hasGoogleAds: '',
  });

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    router.push('/login');
  };

  useEffect(() => {
    fetchStats();
    performSearch('', 1); // Load initial data
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();
      setStats(data.stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const performSearch = async (query: string, page: number = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        query,
        page: page.toString(),
        limit: '20',
        ...(filters.country && { country: filters.country }),
        ...(filters.state && { state: filters.state }),
        ...(filters.city && { city: filters.city }),
        ...(filters.category && { category: filters.category }),
        ...(filters.plan && { plan: filters.plan }),
        ...(filters.minVisits && { minVisits: filters.minVisits }),
        ...(filters.maxVisits && { maxVisits: filters.maxVisits }),
        ...(filters.minEmployees && { minEmployees: filters.minEmployees }),
        ...(filters.hasSocial && { hasSocial: filters.hasSocial }),
        ...(filters.hasGoogleAds && { hasGoogleAds: filters.hasGoogleAds }),
      });

      const response = await fetch(`/api/stores?${params}`);
      const data = await response.json();
      setSearchResult(data);
      setCurrentQuery(query);
      setCurrentPage(page);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    performSearch(query, 1);
  };

  const handlePageChange = (newPage: number) => {
    performSearch(currentQuery, newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const formatNumber = (num: string | number) => {
    if (!num) return 'N/A';
    return new Intl.NumberFormat().format(Number(num));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-5xl">🚀</span>
                <div>
                  <h1 className="text-4xl font-extrabold mb-1 bg-clip-text text-transparent bg-gradient-to-r from-yellow-200 to-yellow-400">
                    豆豆 & 唯一专属数据库
                  </h1>
                  <div className="flex items-center gap-2">
                    <Badge className="bg-yellow-400 text-purple-900 hover:bg-yellow-300 font-bold">
                      🎯 Top Sales Dream Team
                    </Badge>
                    <Badge className="bg-white/20 backdrop-blur-sm border-white/40">
                      励志成为谷歌 Top Sales
                    </Badge>
                  </div>
                </div>
              </div>
              <p className="text-purple-100 text-lg font-medium ml-16">
                ✨ 豆豆 & 唯一的销售宝库 · 挖掘全球 Shopify 店铺，冲向销售巅峰！
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={() => router.push('/favorites')}
                className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
              >
                ⭐ 我的收藏
              </Button>
              <Button
                variant="secondary"
                onClick={() => router.push('/analytics')}
                className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
              >
                📊 数据分析
              </Button>
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

      {/* Stats Section */}
      {stats && (
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white py-10">
          <div className="max-w-7xl mx-auto px-4">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold mb-2">📊 数据概览</h2>
              <p className="text-purple-100">豆豆 & 唯一的销售宝库，满满的商机！</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <Card className="bg-white/15 backdrop-blur-md border-white/30 hover:bg-white/20 transition-all hover:scale-105 cursor-pointer">
                <CardContent className="text-center pt-6">
                  <div className="text-4xl mb-2">🏪</div>
                  <div className="text-4xl font-bold text-white">{formatNumber(stats.total_stores)}</div>
                  <div className="text-purple-100 text-sm mt-2 font-medium">精选店铺</div>
                </CardContent>
              </Card>
              <Card className="bg-white/15 backdrop-blur-md border-white/30 hover:bg-white/20 transition-all hover:scale-105 cursor-pointer">
                <CardContent className="text-center pt-6">
                  <div className="text-4xl mb-2">🌍</div>
                  <div className="text-4xl font-bold text-white">{formatNumber(stats.total_countries)}</div>
                  <div className="text-purple-100 text-sm mt-2 font-medium">覆盖国家</div>
                </CardContent>
              </Card>
              <Card className="bg-white/15 backdrop-blur-md border-white/30 hover:bg-white/20 transition-all hover:scale-105 cursor-pointer">
                <CardContent className="text-center pt-6">
                  <div className="text-4xl mb-2">👥</div>
                  <div className="text-4xl font-bold text-white">{formatNumber(stats.total_employees)}</div>
                  <div className="text-purple-100 text-sm mt-2 font-medium">员工总数</div>
                </CardContent>
              </Card>
              <Card className="bg-white/15 backdrop-blur-md border-white/30 hover:bg-white/20 transition-all hover:scale-105 cursor-pointer">
                <CardContent className="text-center pt-6">
                  <div className="text-4xl mb-2">📈</div>
                  <div className="text-4xl font-bold text-white">{formatNumber(stats.avg_monthly_visits)}</div>
                  <div className="text-purple-100 text-sm mt-2 font-medium">月均访问</div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* Search Section */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col items-center mb-8">
          <SearchBar onSearch={handleSearch} initialValue={currentQuery} />

          {/* View Mode Toggle */}
          <div className="flex gap-2 mt-4 justify-end w-full max-w-4xl">
            <Button
              onClick={() => setViewMode('grid')}
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="icon"
              title="Grid View"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </Button>
            <Button
              onClick={() => setViewMode('list')}
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="icon"
              title="List View"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </Button>
          </div>

          {/* Filters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-full px-4 mt-6"
          >
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-bold mb-4 text-gray-800 dark:text-white flex items-center gap-2">
                🔍 高级筛选
              </h3>

              {/* Row 1: Location Filters */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">国家/地区</label>
                  <select
                    value={filters.country}
                    onChange={(e) => setFilters({ ...filters, country: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  >
                    <option value="">全部国家</option>
                    <option value="US">🇺🇸 United States</option>
                    <option value="CN">🇨🇳 China</option>
                    <option value="HK">🇭🇰 Hong Kong</option>
                    <option value="GB">🇬🇧 United Kingdom</option>
                    <option value="CA">🇨🇦 Canada</option>
                    <option value="AU">🇦🇺 Australia</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">省份/州</label>
                  <input
                    type="text"
                    placeholder="输入省份或州"
                    value={filters.state}
                    onChange={(e) => setFilters({ ...filters, state: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">城市</label>
                  <input
                    type="text"
                    placeholder="输入城市名称"
                    value={filters.city}
                    onChange={(e) => setFilters({ ...filters, city: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">类目</label>
                  <input
                    type="text"
                    placeholder="如: Fashion, Beauty"
                    value={filters.category}
                    onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {/* Row 2: Business Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">计划类型</label>
                  <select
                    value={filters.plan}
                    onChange={(e) => setFilters({ ...filters, plan: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  >
                    <option value="">全部计划</option>
                    <option value="basic">Basic</option>
                    <option value="shopify">Shopify</option>
                    <option value="advanced">Advanced</option>
                    <option value="plus">Shopify Plus</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">最小月访问量</label>
                  <input
                    type="number"
                    placeholder="例: 10000"
                    value={filters.minVisits}
                    onChange={(e) => setFilters({ ...filters, minVisits: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">最大月访问量</label>
                  <input
                    type="number"
                    placeholder="例: 1000000"
                    value={filters.maxVisits}
                    onChange={(e) => setFilters({ ...filters, maxVisits: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">最小员工数</label>
                  <input
                    type="number"
                    placeholder="例: 10"
                    value={filters.minEmployees}
                    onChange={(e) => setFilters({ ...filters, minEmployees: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {/* Row 3: Social & Ads */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">社交媒体</label>
                  <select
                    value={filters.hasSocial}
                    onChange={(e) => setFilters({ ...filters, hasSocial: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  >
                    <option value="">全部</option>
                    <option value="instagram">📷 Has Instagram</option>
                    <option value="facebook">📘 Has Facebook</option>
                    <option value="tiktok">🎵 Has TikTok</option>
                    <option value="youtube">📹 Has YouTube</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Google 广告</label>
                  <select
                    value={filters.hasGoogleAds}
                    onChange={(e) => setFilters({ ...filters, hasGoogleAds: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  >
                    <option value="">全部</option>
                    <option value="true">📊 有广告</option>
                    <option value="false">⭕ 无广告 (潜在客户)</option>
                  </select>
                </div>
              </div>
            </div>
          </motion.div>

          <div className="flex gap-4 mt-4 w-full max-w-6xl justify-center">
            <Button
              onClick={() => performSearch(currentQuery, 1)}
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 font-semibold"
            >
              🔍 应用筛选
            </Button>
            <Button
              onClick={() => {
                setFilters({
                  country: '',
                  state: '',
                  city: '',
                  category: '',
                  plan: '',
                  minVisits: '',
                  maxVisits: '',
                  minEmployees: '',
                  hasSocial: '',
                  hasGoogleAds: '',
                });
                performSearch('', 1);
              }}
              variant="outline"
              size="lg"
              className="font-semibold"
            >
              🔄 重置筛选
            </Button>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400 font-medium">🔎 正在搜索店铺数据...</p>
          </div>
        ) : searchResult ? (
          <>
            <div className="mb-6 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-between">
                <p className="text-gray-700 dark:text-gray-300 text-lg">
                  🎯 找到 <span className="font-bold text-purple-600 dark:text-purple-400 text-xl">{formatNumber(searchResult.total)}</span> 家店铺
                  {currentQuery && (
                    <span> 匹配关键词 &quot;<span className="font-semibold text-pink-600 dark:text-pink-400">{currentQuery}</span>&quot;</span>
                  )}
                </p>
                <Button
                  onClick={() => {
                    const params = new URLSearchParams({
                      query: currentQuery,
                      ...(filters.country && { country: filters.country }),
                      ...(filters.state && { state: filters.state }),
                      ...(filters.city && { city: filters.city }),
                      ...(filters.category && { category: filters.category }),
                      ...(filters.plan && { plan: filters.plan }),
                      ...(filters.minVisits && { minVisits: filters.minVisits }),
                      ...(filters.maxVisits && { maxVisits: filters.maxVisits }),
                      ...(filters.minEmployees && { minEmployees: filters.minEmployees }),
                      ...(filters.hasSocial && { hasSocial: filters.hasSocial }),
                      ...(filters.hasGoogleAds && { hasGoogleAds: filters.hasGoogleAds }),
                    });
                    window.open(`/api/export/csv?${params}`, '_blank');
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white font-semibold"
                >
                  📥 导出CSV {searchResult.total > 5000 && `(最多5000条)`}
                </Button>
              </div>
            </div>

            <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 gap-6 mb-8' : 'flex flex-col gap-4 mb-8'}>
              {searchResult.stores.map((store) => (
                <StoreCard key={store.id} store={store} viewMode={viewMode} />
              ))}
            </div>

            {/* Pagination */}
            {searchResult.totalPages > 1 && (
              <div className="flex justify-center gap-2 pb-12">
                <Button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  variant="outline"
                  className="font-medium"
                >
                  ← 上一页
                </Button>

                <div className="flex items-center gap-2">
                  {Array.from({ length: Math.min(5, searchResult.totalPages) }, (_, i) => {
                    let pageNum;
                    if (searchResult.totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= searchResult.totalPages - 2) {
                      pageNum = searchResult.totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }

                    return (
                      <Button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        variant={currentPage === pageNum ? 'default' : 'outline'}
                        className="min-w-[40px]"
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                </div>

                <Button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === searchResult.totalPages}
                  variant="outline"
                  className="font-medium"
                >
                  下一页 →
                </Button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-xl text-gray-600 dark:text-gray-400 font-medium">
              输入关键词开始搜索店铺
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              试试搜索店铺名称、域名或描述
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-purple-900 via-pink-900 to-red-900 text-white py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center space-y-3">
            <div className="flex items-center justify-center gap-2 mb-4">
              <span className="text-3xl">🚀</span>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-yellow-200 to-yellow-400 bg-clip-text text-transparent">
                豆豆 & 唯一专属数据库
              </h3>
            </div>
            <p className="text-purple-200 text-lg font-medium">
              💪 励志成为谷歌 Top Sales · 每一步都在向目标迈进
            </p>
            <div className="pt-4 border-t border-white/20 mt-4">
              <p className="text-purple-300 text-sm">
                © {new Date().getFullYear()} 豆豆 & 唯一的销售帝国 · Made with 💖 and ☕
              </p>
              <p className="text-purple-200 text-xs mt-2 font-semibold">
                Powered by 超级无敌Grace ⚡
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
