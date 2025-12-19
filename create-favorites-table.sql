-- Create favorites table for storing user bookmarks
CREATE TABLE IF NOT EXISTS favorites (
  id SERIAL PRIMARY KEY,
  user_email VARCHAR(255) NOT NULL,
  store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
  notes TEXT,
  priority VARCHAR(20) DEFAULT 'medium',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_email, store_id)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_favorites_user_email ON favorites(user_email);
CREATE INDEX IF NOT EXISTS idx_favorites_store_id ON favorites(store_id);
CREATE INDEX IF NOT EXISTS idx_favorites_created_at ON favorites(created_at DESC);

-- Add comment
COMMENT ON TABLE favorites IS '用户收藏的店铺';
COMMENT ON COLUMN favorites.user_email IS '用户邮箱';
COMMENT ON COLUMN favorites.store_id IS '店铺ID';
COMMENT ON COLUMN favorites.notes IS '备注';
COMMENT ON COLUMN favorites.priority IS '优先级: high, medium, low';
