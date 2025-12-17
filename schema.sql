-- Shopify Store Leads Database Schema for Neon PostgreSQL

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gin; -- For multi-column indexes

-- Main stores table
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) UNIQUE NOT NULL,
    domain_url TEXT,
    merchant_name VARCHAR(500),
    title TEXT,
    description TEXT,
    meta_description TEXT,

    -- Categories and classification
    categories TEXT,
    platform VARCHAR(50),
    plan VARCHAR(100),
    platform_rank INTEGER,
    rank INTEGER,
    status VARCHAR(50),

    -- Location information
    city VARCHAR(200),
    state VARCHAR(200),
    region VARCHAR(200),
    country_code VARCHAR(10),
    company_location TEXT,
    street_address TEXT,
    zip VARCHAR(50),

    -- Contact information
    about_us_url TEXT,
    contact_page_url TEXT,
    emails TEXT,
    phones TEXT,
    whatsapp_url TEXT,

    -- Social media
    facebook VARCHAR(255),
    facebook_url TEXT,
    instagram VARCHAR(255),
    instagram_url TEXT,
    twitter VARCHAR(255),
    twitter_url TEXT,
    tiktok VARCHAR(255),
    tiktok_url TEXT,
    youtube VARCHAR(255),
    youtube_url TEXT,
    linkedin_account VARCHAR(255),
    linkedin_url TEXT,
    pinterest VARCHAR(255),
    pinterest_url TEXT,

    -- Business metrics
    employee_count INTEGER,
    estimated_monthly_visits INTEGER,
    estimated_yearly_sales VARCHAR(100),

    -- Other
    aliases TEXT,
    language_code VARCHAR(10),
    created DATE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_stores_country ON stores(country_code);
CREATE INDEX IF NOT EXISTS idx_stores_status ON stores(status);
CREATE INDEX IF NOT EXISTS idx_stores_platform_rank ON stores(platform_rank);
CREATE INDEX IF NOT EXISTS idx_stores_rank ON stores(rank);
CREATE INDEX IF NOT EXISTS idx_stores_monthly_visits ON stores(estimated_monthly_visits DESC);
CREATE INDEX IF NOT EXISTS idx_stores_employee_count ON stores(employee_count DESC);
CREATE INDEX IF NOT EXISTS idx_stores_created ON stores(created);
CREATE INDEX IF NOT EXISTS idx_stores_state ON stores(state);
CREATE INDEX IF NOT EXISTS idx_stores_city ON stores(city);

-- GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_stores_merchant_name_trgm ON stores USING gin(merchant_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_stores_description_trgm ON stores USING gin(description gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_stores_categories_trgm ON stores USING gin(categories gin_trgm_ops);

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_stores_updated_at BEFORE UPDATE ON stores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a view for top stores by traffic
CREATE OR REPLACE VIEW top_stores_by_traffic AS
SELECT
    domain,
    merchant_name,
    country_code,
    estimated_monthly_visits,
    estimated_yearly_sales,
    employee_count,
    rank,
    categories
FROM stores
WHERE estimated_monthly_visits IS NOT NULL
ORDER BY estimated_monthly_visits DESC;

-- Create a view for stores by country
CREATE OR REPLACE VIEW stores_by_country AS
SELECT
    country_code,
    COUNT(*) as store_count,
    AVG(estimated_monthly_visits) as avg_monthly_visits,
    SUM(employee_count) as total_employees
FROM stores
WHERE country_code IS NOT NULL
GROUP BY country_code
ORDER BY store_count DESC;

-- Comments for documentation
COMMENT ON TABLE stores IS 'Shopify store leads with comprehensive business information';
COMMENT ON COLUMN stores.estimated_yearly_sales IS 'Stored as text to preserve currency formatting';
COMMENT ON COLUMN stores.platform_rank IS 'Store ranking within platform';
COMMENT ON COLUMN stores.rank IS 'Overall store ranking';
