'use client';

import { Store } from '@/lib/db';

interface StoreCardProps {
  store: Store;
}

export default function StoreCard({ store }: StoreCardProps) {
  const formatNumber = (num: number) => {
    if (!num) return 'N/A';
    return new Intl.NumberFormat().format(num);
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-lg transition-shadow bg-white dark:bg-gray-800">
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
        <div className="flex gap-2">
          {store.instagram && (
            <a
              href={`https://instagram.com/${store.instagram}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-pink-600"
              title="Instagram"
            >
              📷
            </a>
          )}
          {store.facebook && (
            <a
              href={`https://facebook.com/${store.facebook}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-600"
              title="Facebook"
            >
              📘
            </a>
          )}
          {store.twitter && (
            <a
              href={`https://twitter.com/${store.twitter}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-400"
              title="Twitter"
            >
              🐦
            </a>
          )}
          {store.tiktok && (
            <a
              href={`https://tiktok.com/@${store.tiktok}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-black dark:hover:text-white"
              title="TikTok"
            >
              🎵
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
