-- 扩展Schema：添加分析字段
-- 用于存储店铺的深度分析数据

-- 1. Google Ads 分析字段
ALTER TABLE stores ADD COLUMN IF NOT EXISTS has_google_ads BOOLEAN DEFAULT NULL;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS google_ads_detected_date DATE;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS ad_keywords TEXT;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS estimated_ad_budget VARCHAR(100);

-- 2. SEO 分析字段
ALTER TABLE stores ADD COLUMN IF NOT EXISTS alexa_rank INTEGER;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS domain_authority INTEGER;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS backlinks_count INTEGER;

-- 3. 社交媒体分析
ALTER TABLE stores ADD COLUMN IF NOT EXISTS instagram_followers INTEGER;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS facebook_likes INTEGER;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS tiktok_followers INTEGER;

-- 4. 技术栈分析
ALTER TABLE stores ADD COLUMN IF NOT EXISTS uses_shopify_plus BOOLEAN;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS payment_methods TEXT; -- JSON array
ALTER TABLE stores ADD COLUMN IF NOT EXISTS shipping_countries TEXT; -- JSON array
ALTER TABLE stores ADD COLUMN IF NOT EXISTS technologies TEXT; -- JSON array: Klaviyo, Judge.me, etc

-- 5. 产品分析
ALTER TABLE stores ADD COLUMN IF NOT EXISTS product_count INTEGER;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS avg_product_price DECIMAL(10,2);
ALTER TABLE stores ADD COLUMN IF NOT EXISTS price_range VARCHAR(100);

-- 6. 用户体验分析
ALTER TABLE stores ADD COLUMN IF NOT EXISTS has_reviews BOOLEAN;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS avg_review_score DECIMAL(3,2);
ALTER TABLE stores ADD COLUMN IF NOT EXISTS page_load_speed INTEGER; -- milliseconds
ALTER TABLE stores ADD COLUMN IF NOT EXISTS mobile_friendly BOOLEAN;

-- 7. 营销分析
ALTER TABLE stores ADD COLUMN IF NOT EXISTS has_email_popup BOOLEAN;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS has_discount_code BOOLEAN;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS has_live_chat BOOLEAN;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS uses_affiliate_marketing BOOLEAN;

-- 8. 分析元数据
ALTER TABLE stores ADD COLUMN IF NOT EXISTS analysis_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE stores ADD COLUMN IF NOT EXISTS analysis_score INTEGER; -- 综合评分 0-100
ALTER TABLE stores ADD COLUMN IF NOT EXISTS last_analyzed_at TIMESTAMP;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS analysis_notes TEXT;

-- 创建索引以优化查询
CREATE INDEX IF NOT EXISTS idx_stores_analysis_status ON stores(analysis_status);
CREATE INDEX IF NOT EXISTS idx_stores_has_google_ads ON stores(has_google_ads) WHERE has_google_ads = true;
CREATE INDEX IF NOT EXISTS idx_stores_analysis_score ON stores(analysis_score DESC);
CREATE INDEX IF NOT EXISTS idx_stores_domain_authority ON stores(domain_authority DESC);
CREATE INDEX IF NOT EXISTS idx_stores_instagram_followers ON stores(instagram_followers DESC);
CREATE INDEX IF NOT EXISTS idx_stores_product_count ON stores(product_count DESC);
CREATE INDEX IF NOT EXISTS idx_stores_last_analyzed ON stores(last_analyzed_at DESC);

-- 添加字段注释
COMMENT ON COLUMN stores.has_google_ads IS 'Whether store is running Google Ads';
COMMENT ON COLUMN stores.analysis_status IS 'pending, processing, completed, failed';
COMMENT ON COLUMN stores.analysis_score IS 'Overall store quality score (0-100)';
COMMENT ON COLUMN stores.technologies IS 'JSON array of detected technologies/apps';
COMMENT ON COLUMN stores.payment_methods IS 'JSON array of supported payment methods';

-- 创建分析统计视图
CREATE OR REPLACE VIEW store_analysis_stats AS
SELECT
    COUNT(*) as total_analyzed,
    COUNT(*) FILTER (WHERE has_google_ads = true) as stores_with_ads,
    COUNT(*) FILTER (WHERE mobile_friendly = true) as mobile_friendly_stores,
    COUNT(*) FILTER (WHERE has_reviews = true) as stores_with_reviews,
    AVG(analysis_score) as avg_analysis_score,
    AVG(domain_authority) as avg_domain_authority,
    AVG(product_count) as avg_product_count,
    AVG(page_load_speed) as avg_page_load_speed
FROM stores
WHERE analysis_status = 'completed';

-- 创建高质量店铺视图
CREATE OR REPLACE VIEW high_quality_stores AS
SELECT
    domain,
    merchant_name,
    country_code,
    estimated_monthly_visits,
    analysis_score,
    domain_authority,
    has_google_ads,
    instagram_followers,
    product_count,
    avg_review_score
FROM stores
WHERE
    analysis_status = 'completed'
    AND analysis_score >= 70
    AND estimated_monthly_visits > 10000
ORDER BY analysis_score DESC, estimated_monthly_visits DESC;

COMMENT ON VIEW store_analysis_stats IS 'Aggregated statistics from store analysis';
COMMENT ON VIEW high_quality_stores IS 'Stores with high quality scores and significant traffic';
