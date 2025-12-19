'use client';

import { Store } from '@/lib/db';
import { useRouter } from 'next/navigation';
import FavoriteButton from './FavoriteButton';

interface StoreCardProps {
  store: Store;
  viewMode?: 'grid' | 'list';
}

// Social Media Icons as SVG components
const InstagramIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
);

const FacebookIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
);

const TwitterIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
);

const TikTokIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>
);

const YouTubeIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
);

const LinkedInIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
);

const PinterestIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"/></svg>
);

export default function StoreCard({ store, viewMode = 'grid' }: StoreCardProps) {
  const router = useRouter();

  const formatNumber = (num: number) => {
    if (!num) return 'N/A';
    return new Intl.NumberFormat().format(num);
  };

  const handleCardClick = (e: React.MouseEvent) => {
    // Don't navigate if clicking on a link
    if ((e.target as HTMLElement).closest('a')) {
      return;
    }
    router.push(`/store/${store.id}`);
  };

  if (viewMode === 'list') {
    return (
      <div
        onClick={handleCardClick}
        className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow bg-white dark:bg-gray-800 flex items-center gap-4 cursor-pointer">
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate">
                {store.merchant_name || store.domain}
              </h3>
              <a
                href={store.domain_url || `https://${store.domain}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                {store.domain}
              </a>
            </div>
            <div className="flex gap-2 ml-4">
              {store.instagram && (
                <a href={`https://instagram.com/${store.instagram}`} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-pink-600 transition-colors" title="Instagram">
                  <InstagramIcon />
                </a>
              )}
              {store.facebook && (
                <a href={`https://facebook.com/${store.facebook}`} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-blue-600 transition-colors" title="Facebook">
                  <FacebookIcon />
                </a>
              )}
              {store.twitter && (
                <a href={`https://twitter.com/${store.twitter}`} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-blue-400 transition-colors" title="Twitter">
                  <TwitterIcon />
                </a>
              )}
              {store.tiktok && (
                <a href={`https://tiktok.com/@${store.tiktok}`} target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-black dark:hover:text-white transition-colors" title="TikTok">
                  <TikTokIcon />
                </a>
              )}
            </div>
          </div>
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500 dark:text-gray-400">Location: </span>
              <span className="font-medium">{[store.city, store.country_code].filter(Boolean).join(', ') || 'N/A'}</span>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Visits: </span>
              <span className="font-medium">{formatNumber(store.estimated_monthly_visits)}/mo</span>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Employees: </span>
              <span className="font-medium">{formatNumber(store.employee_count)}</span>
            </div>
            <div className="flex gap-2">
              <span className={`px-2 py-1 rounded text-xs ${store.status === 'Active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-gray-100 text-gray-800'}`}>
                {store.status}
              </span>
              {store.has_google_ads !== undefined && store.has_google_ads !== null && (
                <span className={`px-2 py-1 rounded text-xs ${
                  store.is_new_customer
                    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {store.is_new_customer ? '🔥 New Customer' : '📊 Has Ads'}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      onClick={handleCardClick}
      className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-lg transition-shadow bg-white dark:bg-gray-800 cursor-pointer">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
            {store.merchant_name || store.domain}
          </h3>
          <a
            href={store.domain_url || `https://${store.domain}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline text-sm"
          >
            {store.domain}
          </a>
        </div>
        <div className="flex gap-2 flex-wrap items-center">
          <FavoriteButton storeId={store.id} />
          {store.instagram && (
            <a
              href={`https://instagram.com/${store.instagram}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-pink-600 transition-colors"
              title="Instagram"
            >
              <InstagramIcon />
            </a>
          )}
          {store.facebook && (
            <a
              href={`https://facebook.com/${store.facebook}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-600 transition-colors"
              title="Facebook"
            >
              <FacebookIcon />
            </a>
          )}
          {store.twitter && (
            <a
              href={`https://twitter.com/${store.twitter}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-400 transition-colors"
              title="Twitter"
            >
              <TwitterIcon />
            </a>
          )}
          {store.tiktok && (
            <a
              href={`https://tiktok.com/@${store.tiktok}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-black dark:hover:text-white transition-colors"
              title="TikTok"
            >
              <TikTokIcon />
            </a>
          )}
        </div>
      </div>

      {store.description && (
        <p className="text-gray-700 dark:text-gray-300 text-sm mb-4 line-clamp-2">
          {store.description}
        </p>
      )}

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500 dark:text-gray-400">Location:</span>
          <p className="font-medium">
            {[store.city, store.state, store.country_code].filter(Boolean).join(', ') || 'N/A'}
          </p>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Monthly Visits:</span>
          <p className="font-medium">{formatNumber(store.estimated_monthly_visits)}</p>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Employees:</span>
          <p className="font-medium">{formatNumber(store.employee_count)}</p>
        </div>
        <div>
          <span className="text-gray-500 dark:text-gray-400">Yearly Sales:</span>
          <p className="font-medium">{store.estimated_yearly_sales || 'N/A'}</p>
        </div>
        {store.has_google_ads !== undefined && store.has_google_ads !== null && (
          <>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Google Ads:</span>
              <p className="font-medium">{store.has_google_ads ? `${store.google_ads_count || 0} ads` : 'No ads'}</p>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Customer Type:</span>
              <p className="font-medium">{store.is_new_customer ? '🔥 New' : 'Existing'}</p>
            </div>
          </>
        )}
      </div>

      {store.categories && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-2">
            {store.categories.split(':').slice(0, 3).map((cat, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
              >
                {cat.replace(/^\//, '')}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 flex justify-between items-center text-xs text-gray-500">
        <span>Rank: #{store.rank || 'N/A'}</span>
        <span className={`px-2 py-1 rounded ${
          store.status === 'Active'
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
        }`}>
          {store.status}
        </span>
      </div>
    </div>
  );
}
