/**
 * Multi-Database Support for Multiple Neon Free Tier Projects
 * Use this if you want to store all data across multiple Neon databases
 */
import { sql as createSqlClient } from '@vercel/postgres';

// Configure multiple database connections
const databases = [
  process.env.POSTGRES_URL_1,
  process.env.POSTGRES_URL_2,
  process.env.POSTGRES_URL_3,
  process.env.POSTGRES_URL_4,
].filter(Boolean);

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

/**
 * Create SQL client for a specific database
 */
function getSqlClient(connectionString: string) {
  return createSqlClient.bind({ connectionString });
}

/**
 * Execute query on all databases and merge results
 */
async function queryAllDatabases(
  queryFn: (sql: typeof createSqlClient) => Promise<any>
) {
  const results = await Promise.all(
    databases.map(async (connStr) => {
      if (!connStr) return { rows: [] };
      try {
        const client = getSqlClient(connStr);
        return await queryFn(client);
      } catch (error) {
        console.error(`Error querying database ${connStr}:`, error);
        return { rows: [] };
      }
    })
  );

  return results;
}

/**
 * Search stores across all databases
 */
export async function searchStoresMultiDB(params: SearchParams) {
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

  // Build WHERE clause
  if (query) {
    whereConditions.push(`(
      merchant_name ILIKE $${paramCount} OR
      description ILIKE $${paramCount} OR
      domain ILIKE $${paramCount}
    )`);
    queryParams.push(`%${query}%`);
    paramCount++;
  }

  if (country) {
    whereConditions.push(`country_code = $${paramCount}`);
    queryParams.push(country);
    paramCount++;
  }

  if (category) {
    whereConditions.push(`categories ILIKE $${paramCount}`);
    queryParams.push(`%${category}%`);
    paramCount++;
  }

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

  if (status) {
    whereConditions.push(`status = $${paramCount}`);
    queryParams.push(status);
    paramCount++;
  }

  const whereClause = whereConditions.length > 0
    ? `WHERE ${whereConditions.join(' AND ')}`
    : '';

  // Query all databases
  const results = await queryAllDatabases(async (sql) => {
    const dataQuery = `
      SELECT
        id, domain, merchant_name, title, description, categories,
        country_code, city, state, estimated_monthly_visits,
        estimated_yearly_sales, employee_count, rank, platform_rank,
        status, plan, created, domain_url, instagram, facebook, twitter, tiktok
      FROM stores
      ${whereClause}
      ORDER BY estimated_monthly_visits DESC NULLS LAST
    `;

    return await sql.query(dataQuery, queryParams);
  });

  // Merge and sort all results
  const allStores = results
    .flatMap(result => result.rows)
    .sort((a, b) => (b.estimated_monthly_visits || 0) - (a.estimated_monthly_visits || 0));

  const total = allStores.length;
  const stores = allStores.slice(offset, offset + limit);

  return {
    stores: stores as Store[],
    total,
    page,
    limit,
    totalPages: Math.ceil(total / limit)
  };
}

/**
 * Get statistics across all databases
 */
export async function getStatsMultiDB() {
  const results = await queryAllDatabases(async (sql) => {
    return await sql.query(`
      SELECT
        COUNT(*) as total_stores,
        COUNT(DISTINCT country_code) as total_countries,
        SUM(employee_count) as total_employees,
        AVG(estimated_monthly_visits)::bigint as avg_monthly_visits
      FROM stores
    `);
  });

  // Aggregate stats
  const totalStores = results.reduce((sum, r) => sum + parseInt(r.rows[0]?.total_stores || 0), 0);
  const uniqueCountries = new Set(
    results.flatMap(r => r.rows[0]?.countries || [])
  ).size;
  const totalEmployees = results.reduce((sum, r) => sum + parseInt(r.rows[0]?.total_employees || 0), 0);
  const avgVisits = Math.floor(
    results.reduce((sum, r) => sum + parseInt(r.rows[0]?.avg_monthly_visits || 0), 0) / results.length
  );

  return {
    total_stores: totalStores.toString(),
    total_countries: uniqueCountries.toString(),
    total_employees: totalEmployees.toString(),
    avg_monthly_visits: avgVisits.toString()
  };
}

/**
 * Get countries across all databases
 */
export async function getCountriesMultiDB() {
  const results = await queryAllDatabases(async (sql) => {
    return await sql.query(`
      SELECT country_code, COUNT(*) as count
      FROM stores
      WHERE country_code IS NOT NULL AND country_code != ''
      GROUP BY country_code
    `);
  });

  // Merge country counts
  const countryCounts = new Map<string, number>();

  results.forEach(result => {
    result.rows.forEach((row: any) => {
      const current = countryCounts.get(row.country_code) || 0;
      countryCounts.set(row.country_code, current + parseInt(row.count));
    });
  });

  // Convert to array and sort
  return Array.from(countryCounts.entries())
    .map(([country_code, count]) => ({ country_code, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 50);
}
