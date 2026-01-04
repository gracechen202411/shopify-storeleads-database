import { sql } from '@vercel/postgres';

export interface Store {
  id: number;
  domain: string;
  merchant_name: string;
  title: string;
  description: string;
  meta_description?: string;
  categories: string;

  // Platform info
  platform?: string;
  plan: string;
  platform_rank: number;
  rank: number;
  status: string;

  // Location
  country_code: string;
  city: string;
  state: string;
  region?: string;
  company_location?: string;
  street_address?: string;
  zip?: string;

  // Contact info
  domain_url: string;
  about_us_url?: string;
  contact_page_url?: string;
  emails?: string;
  phones?: string;
  whatsapp_url?: string;

  // Social media
  instagram: string;
  instagram_url?: string;
  facebook: string;
  facebook_url?: string;
  twitter: string;
  twitter_url?: string;
  tiktok: string;
  tiktok_url?: string;
  youtube?: string;
  youtube_url?: string;
  linkedin_account?: string;
  linkedin_url?: string;
  pinterest?: string;
  pinterest_url?: string;

  // Business metrics
  employee_count: number;
  estimated_monthly_visits: number;
  estimated_yearly_sales: string;

  // Google Ads info
  has_google_ads?: boolean;
  google_ads_count?: number;
  is_new_customer?: boolean;
  customer_type?: string; // 'never_advertised' | 'new_advertiser_30d' | 'old_advertiser' | 'has_ads' | 'needs_manual_review'
  ads_check_level?: number; // 1 = fast check, 2 = date check
  ads_last_checked?: string;

  // Other
  aliases?: string;
  language_code?: string;
  created: string;
}

export interface SearchParams {
  query?: string;
  country?: string;
  state?: string;
  city?: string;
  category?: string;
  plan?: string;
  minVisits?: number;
  maxVisits?: number;
  status?: string;
  hasGoogleAds?: string;
  customerType?: string; // 'never_advertised' | 'new_advertiser_30d' | 'old_advertiser'
  page?: number;
  limit?: number;
}

export async function searchStores(params: SearchParams) {
  const {
    query = '',
    country = '',
    state = '',
    city = '',
    category = '',
    plan = '',
    minVisits = 0,
    maxVisits = 999999999,
    status = '',
    hasGoogleAds = '',
    customerType = '',
    page = 1,
    limit = 50
  } = params;

  const offset = (page - 1) * limit;

  let whereConditions: string[] = [];
  let queryParams: any[] = [];
  let paramCount = 1;

  // Search query
  if (query) {
    whereConditions.push(`(
      merchant_name ILIKE $${paramCount} OR
      description ILIKE $${paramCount} OR
      domain ILIKE $${paramCount}
    )`);
    queryParams.push(`%${query}%`);
    paramCount++;
  }

  // Country filter
  if (country) {
    whereConditions.push(`country_code = $${paramCount}`);
    queryParams.push(country);
    paramCount++;
  }

  // State filter
  if (state) {
    whereConditions.push(`state ILIKE $${paramCount}`);
    queryParams.push(`%${state}%`);
    paramCount++;
  }

  // City filter
  if (city) {
    whereConditions.push(`city ILIKE $${paramCount}`);
    queryParams.push(`%${city}%`);
    paramCount++;
  }

  // Category filter
  if (category) {
    whereConditions.push(`categories ILIKE $${paramCount}`);
    queryParams.push(`%${category}%`);
    paramCount++;
  }

  // Plan filter
  if (plan) {
    whereConditions.push(`plan ILIKE $${paramCount}`);
    queryParams.push(`%${plan}%`);
    paramCount++;
  }

  // Monthly visits range
  if (minVisits > 0) {
    whereConditions.push(`estimated_monthly_visits >= $${paramCount}`);
    queryParams.push(minVisits);
    paramCount++;
  }

  if (maxVisits < 999999999) {
    whereConditions.push(`estimated_monthly_visits <= $${paramCount}`);
    queryParams.push(maxVisits);
    paramCount++;
  }

  // Status filter
  if (status) {
    whereConditions.push(`status = $${paramCount}`);
    queryParams.push(status);
    paramCount++;
  }

  // Google Ads filter
  if (hasGoogleAds === 'true') {
    whereConditions.push(`has_google_ads = true`);
  } else if (hasGoogleAds === 'false') {
    whereConditions.push(`has_google_ads = false`);
  }

  // Customer type filter (new preferred method)
  if (customerType) {
    whereConditions.push(`customer_type = $${paramCount}`);
    queryParams.push(customerType);
    paramCount++;
  }

  const whereClause = whereConditions.length > 0
    ? `WHERE ${whereConditions.join(' AND ')}`
    : '';

  // Get total count
  const countQuery = `
    SELECT COUNT(*) as total
    FROM stores
    ${whereClause}
  `;

  const dataQuery = `
    SELECT
      id, domain, merchant_name, title, description, categories,
      country_code, city, state, estimated_monthly_visits,
      estimated_yearly_sales, employee_count, rank, platform_rank,
      status, plan, created, domain_url, instagram, facebook, twitter, tiktok,
      has_google_ads, google_ads_count, is_new_customer, customer_type, ads_check_level, ads_last_checked
    FROM stores
    ${whereClause}
    ORDER BY estimated_monthly_visits DESC NULLS LAST
    LIMIT $${paramCount} OFFSET $${paramCount + 1}
  `;

  try {
    const [countResult, dataResult] = await Promise.all([
      sql.query(countQuery, queryParams),
      sql.query(dataQuery, [...queryParams, limit, offset])
    ]);

    return {
      stores: dataResult.rows as Store[],
      total: parseInt(countResult.rows[0].total),
      page,
      limit,
      totalPages: Math.ceil(parseInt(countResult.rows[0].total) / limit)
    };
  } catch (error) {
    console.error('Database query error:', error);
    throw error;
  }
}

export async function getStoreById(id: number) {
  try {
    const result = await sql.query(
      'SELECT * FROM stores WHERE id = $1',
      [id]
    );
    return result.rows[0] as Store;
  } catch (error) {
    console.error('Database query error:', error);
    throw error;
  }
}

export async function getCountries() {
  try {
    const result = await sql.query(`
      SELECT country_code, COUNT(*) as count
      FROM stores
      WHERE country_code IS NOT NULL AND country_code != ''
      GROUP BY country_code
      ORDER BY count DESC
      LIMIT 50
    `);
    return result.rows;
  } catch (error) {
    console.error('Database query error:', error);
    throw error;
  }
}

export async function getStats() {
  try {
    const result = await sql.query(`
      SELECT
        COUNT(*) as total_stores,
        COUNT(DISTINCT country_code) as total_countries,
        SUM(employee_count) as total_employees,
        AVG(estimated_monthly_visits)::bigint as avg_monthly_visits
      FROM stores
    `);
    return result.rows[0];
  } catch (error) {
    console.error('Database query error:', error);
    throw error;
  }
}
