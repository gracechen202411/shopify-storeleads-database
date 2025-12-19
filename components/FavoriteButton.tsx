'use client';

import { useState } from 'react';
import { Button } from './ui/button';

interface FavoriteButtonProps {
  storeId: number;
  initialFavorited?: boolean;
  onToggle?: (favorited: boolean) => void;
}

export default function FavoriteButton({
  storeId,
  initialFavorited = false,
  onToggle
}: FavoriteButtonProps) {
  const [favorited, setFavorited] = useState(initialFavorited);
  const [loading, setLoading] = useState(false);

  const handleToggle = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    e.preventDefault();

    setLoading(true);
    try {
      if (favorited) {
        // Remove favorite
        await fetch(`/api/favorites?store_id=${storeId}`, {
          method: 'DELETE',
        });
        setFavorited(false);
        onToggle?.(false);
      } else {
        // Add favorite
        await fetch('/api/favorites', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ store_id: storeId }),
        });
        setFavorited(true);
        onToggle?.(true);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      onClick={handleToggle}
      disabled={loading}
      variant="ghost"
      size="icon"
      className={`transition-all ${
        favorited
          ? 'text-yellow-500 hover:text-yellow-600'
          : 'text-gray-400 hover:text-yellow-500'
      }`}
      title={favorited ? '取消收藏' : '收藏'}
    >
      {loading ? (
        <span className="animate-spin">⭕</span>
      ) : favorited ? (
        <span className="text-xl">⭐</span>
      ) : (
        <span className="text-xl">☆</span>
      )}
    </Button>
  );
}
