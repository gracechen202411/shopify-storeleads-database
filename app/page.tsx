'use client';

import { useState, useEffect } from 'react';
import SearchBar from '@/components/SearchBar';
import StoreCard from '@/components/StoreCard';
import { Store } from '@/lib/db';

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
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState({
    country: '',
    minVisits: '',
  });

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
        ...(filters.minVisits && { minVisits: filters.minVisits }),
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
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            🛍️ Shopify Store Leads Database
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Discover and explore millions of Shopify stores worldwide
          </p>
        </div>
      </header>

      {/* Stats Section */}
      {stats && (
        <div className="bg-blue-600 text-white py-8">
          <div className="max-w-7xl mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold">{formatNumber(stats.total_stores)}</div>
                <div className="text-blue-100 text-sm mt-1">Total Stores</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">{formatNumber(stats.total_countries)}</div>
                <div className="text-blue-100 text-sm mt-1">Countries</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">{formatNumber(stats.total_employees)}</div>
                <div className="text-blue-100 text-sm mt-1">Total Employees</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">{formatNumber(stats.avg_monthly_visits)}</div>
                <div className="text-blue-100 text-sm mt-1">Avg Monthly Visits</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Section */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col items-center mb-8">
          <SearchBar onSearch={handleSearch} initialValue={currentQuery} />

          {/* Filters */}
          <div className="flex gap-4 mt-4 w-full max-w-4xl">
            <select
              value={filters.country}
              onChange={(e) => setFilters({ ...filters, country: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            >
              <option value="">All Countries</option>
              <option value="US">United States</option>
              <option value="GB">United Kingdom</option>
              <option value="CA">Canada</option>
              <option value="AU">Australia</option>
              <option value="DE">Germany</option>
            </select>

            <input
              type="number"
              placeholder="Min monthly visits"
              value={filters.minVisits}
              onChange={(e) => setFilters({ ...filters, minVisits: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            />

            <button
              onClick={() => performSearch(currentQuery, 1)}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading stores...</p>
          </div>
        ) : searchResult ? (
          <>
            <div className="mb-6">
              <p className="text-gray-700 dark:text-gray-300">
                Found <span className="font-bold">{formatNumber(searchResult.total)}</span> stores
                {currentQuery && (
                  <span> matching &quot;<span className="font-semibold">{currentQuery}</span>&quot;</span>
                )}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {searchResult.stores.map((store) => (
                <StoreCard key={store.id} store={store} />
              ))}
            </div>

            {/* Pagination */}
            {searchResult.totalPages > 1 && (
              <div className="flex justify-center gap-2 pb-12">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
                >
                  Previous
                </button>

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
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`px-4 py-2 rounded-lg ${
                          currentPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'border border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === searchResult.totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12 text-gray-600 dark:text-gray-400">
            Enter a search query to find stores
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p>Shopify Store Leads Database - {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  );
}
