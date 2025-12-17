import { sql } from '@vercel/postgres';

export interface Store {
  id: number;
  domain: string;
  merchant_name: string;
  title: string;
  description: string;
  categories: string;
  country_code: string;
  city: string;
  state: string;
  estimated_monthly_visits: number;
  estimated_yearly_sales: string;
  employee_count: number;
  rank: number;
  platform_rank: number;
  status: string;
  plan: string;
  created: string;
  domain_url: string;
  instagram: string;
  facebook: string;
  twitter: string;
  tiktok: string;
}

export interface SearchParams {
  query?: string;
  country?: string;
  category?: string;
  minVisits?: number;
  maxVisits?: number;
  status?: string;
  page?: number;
  limit?: number;
}

export async function searchStores(params: SearchParams) {
  const {
    query = '',
    country = '',
    category = '',
    minVisits = 0,
    maxVisits = 999999999,
    status = '',
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

  // Category filter
  if (category) {
    whereConditions.push(`categories ILIKE $${paramCount}`);
    queryParams.push(`%${category}%`);
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
      status, plan, created, domain_url, instagram, facebook, twitter, tiktok
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
