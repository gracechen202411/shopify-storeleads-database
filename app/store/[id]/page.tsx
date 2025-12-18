'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Store } from '@/lib/db';

// Reuse the same SVG icons from StoreCard
const InstagramIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
);

const FacebookIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
);

const TwitterIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
);

const TikTokIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>
);

const YouTubeIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
);

const LinkedInIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
);

const PinterestIcon = () => (
  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"/></svg>
);

export default function StorePage() {
  const params = useParams();
  const router = useRouter();
  const [store, setStore] = useState<Store | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStore = async () => {
      try {
        const response = await fetch(`/api/store/${params.id}`);
        if (response.ok) {
          const data = await response.json();
          setStore(data.store);
        }
      } catch (error) {
        console.error('Failed to fetch store:', error);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchStore();
    }
  }, [params.id]);

  const formatNumber = (num: number) => {
    if (!num) return 'N/A';
    return new Intl.NumberFormat().format(num);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading store details...</p>
        </div>
      </div>
    );
  }

  if (!store) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Store Not Found</h1>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Results
          </button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {store.merchant_name || store.domain}
              </h1>
              <a
                href={store.domain_url || `https://${store.domain}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-lg"
              >
                {store.domain} →
              </a>
            </div>
            <span className={`px-4 py-2 rounded-lg ${store.status === 'Active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-gray-100 text-gray-800'}`}>
              {store.status}
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Description */}
        {store.description && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-3">About</h2>
            <p className="text-gray-700 dark:text-gray-300">{store.description}</p>
          </div>
        )}

        {/* Business Metrics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Business Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <div className="text-gray-500 dark:text-gray-400 text-sm mb-1">Monthly Visits</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{formatNumber(store.estimated_monthly_visits)}</div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400 text-sm mb-1">Yearly Sales</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{store.estimated_yearly_sales || 'N/A'}</div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400 text-sm mb-1">Employees</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{formatNumber(store.employee_count)}</div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400 text-sm mb-1">Rank</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">#{formatNumber(store.rank)}</div>
            </div>
          </div>
        </div>

        {/* Location & Contact */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">📍 地址信息</h2>
            <div className="space-y-3">
              {store.company_location && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">完整地址</div>
                  <div className="text-gray-900 dark:text-white">{store.company_location}</div>
                </div>
              )}
              {store.street_address && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">街道地址</div>
                  <div className="text-gray-900 dark:text-white">{store.street_address}</div>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                {store.city && (
                  <div>
                    <div className="text-gray-500 dark:text-gray-400 text-sm">City</div>
                    <div className="text-gray-900 dark:text-white">{store.city}</div>
                  </div>
                )}
                {store.state && (
                  <div>
                    <div className="text-gray-500 dark:text-gray-400 text-sm">State</div>
                    <div className="text-gray-900 dark:text-white">{store.state}</div>
                  </div>
                )}
                {store.region && (
                  <div>
                    <div className="text-gray-500 dark:text-gray-400 text-sm">Region</div>
                    <div className="text-gray-900 dark:text-white">{store.region}</div>
                  </div>
                )}
                {store.country_code && (
                  <div>
                    <div className="text-gray-500 dark:text-gray-400 text-sm">Country</div>
                    <div className="text-gray-900 dark:text-white">{store.country_code}</div>
                  </div>
                )}
                {store.zip && (
                  <div>
                    <div className="text-gray-500 dark:text-gray-400 text-sm">ZIP</div>
                    <div className="text-gray-900 dark:text-white">{store.zip}</div>
                  </div>
                )}
                {store.language_code && (
                  <div>
                    <div className="text-gray-500 dark:text-gray-400 text-sm">Language</div>
                    <div className="text-gray-900 dark:text-white">{store.language_code.toUpperCase()}</div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">联系方式 & 店铺信息</h2>
            <div className="space-y-3">
              {store.domain_url && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">🌐 网站</div>
                  <a href={store.domain_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">Visit Store →</a>
                </div>
              )}
              {store.emails && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">📧 邮箱</div>
                  <a href={`mailto:${store.emails.split(':')[0]}`} className="text-blue-600 hover:underline break-all">{store.emails.split(':')[0]}</a>
                </div>
              )}
              {store.phones && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">📞 电话</div>
                  <a href={`tel:${store.phones.split(':')[0]}`} className="text-blue-600 hover:underline">{store.phones.split(':')[0]}</a>
                </div>
              )}
              {store.whatsapp_url && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">💬 WhatsApp</div>
                  <a href={store.whatsapp_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Contact via WhatsApp →</a>
                </div>
              )}
              {store.contact_page_url && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">📝 联系页面</div>
                  <a href={store.contact_page_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">Visit Contact Page →</a>
                </div>
              )}
              {store.about_us_url && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">ℹ️ 关于我们</div>
                  <a href={store.about_us_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">Visit About Page →</a>
                </div>
              )}
              {store.status && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">Status</div>
                  <div className="text-gray-900 dark:text-white">{store.status}</div>
                </div>
              )}
              {store.plan && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">Plan</div>
                  <div className="text-gray-900 dark:text-white">{store.plan}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Social Media */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Social Media</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {store.instagram && (
              <a href={`https://instagram.com/${store.instagram}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <div className="text-pink-600"><InstagramIcon /></div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Instagram</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white truncate">@{store.instagram}</div>
                </div>
              </a>
            )}
            {store.facebook && (
              <a href={`https://facebook.com/${store.facebook}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <div className="text-blue-600"><FacebookIcon /></div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Facebook</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white truncate">{store.facebook}</div>
                </div>
              </a>
            )}
            {store.twitter && (
              <a href={`https://twitter.com/${store.twitter}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <div className="text-blue-400"><TwitterIcon /></div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Twitter</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white truncate">@{store.twitter}</div>
                </div>
              </a>
            )}
            {store.tiktok && (
              <a href={`https://tiktok.com/@${store.tiktok}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <div className="text-black dark:text-white"><TikTokIcon /></div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">TikTok</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white truncate">@{store.tiktok}</div>
                </div>
              </a>
            )}
          </div>
        </div>

        {/* Platform & Categories */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Platform Details</h2>
            <div className="space-y-3">
              {store.plan && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">Plan</div>
                  <div className="text-gray-900 dark:text-white">{store.plan}</div>
                </div>
              )}
              {store.platform_rank && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">Platform Rank</div>
                  <div className="text-gray-900 dark:text-white">#{formatNumber(store.platform_rank)}</div>
                </div>
              )}
              {store.rank && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">Overall Rank</div>
                  <div className="text-gray-900 dark:text-white">#{formatNumber(store.rank)}</div>
                </div>
              )}
              {store.created && (
                <div>
                  <div className="text-gray-500 dark:text-gray-400 text-sm">Created</div>
                  <div className="text-gray-900 dark:text-white">{new Date(store.created).toLocaleDateString()}</div>
                </div>
              )}
            </div>
          </div>

          {store.categories && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Categories</h2>
              <div className="flex flex-wrap gap-2">
                {store.categories.split(':').map((cat, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full"
                  >
                    {cat.replace(/^\//, '')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
