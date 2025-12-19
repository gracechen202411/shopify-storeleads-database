import { NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function GET() {
  try {
    // Top provinces/states by store count
    const provincesResult = await sql.query(`
      SELECT
        COALESCE(state, 'Unknown') as state,
        country_code,
        COUNT(*) as store_count,
        COUNT(CASE WHEN is_new_customer = true THEN 1 END) as new_customer_count,
        SUM(estimated_monthly_visits) as total_visits
      FROM stores
      WHERE state IS NOT NULL AND state != ''
      GROUP BY state, country_code
      ORDER BY store_count DESC
      LIMIT 20
    `);

    // Top cities by store count
    const citiesResult = await sql.query(`
      SELECT
        COALESCE(city, 'Unknown') as city,
        COALESCE(state, '') as state,
        country_code,
        COUNT(*) as store_count,
        COUNT(CASE WHEN is_new_customer = true THEN 1 END) as new_customer_count
      FROM stores
      WHERE city IS NOT NULL AND city != ''
      GROUP BY city, state, country_code
      ORDER BY store_count DESC
      LIMIT 20
    `);

    // Country distribution
    const countriesResult = await sql.query(`
      SELECT
        country_code,
        COUNT(*) as store_count,
        COUNT(CASE WHEN is_new_customer = true THEN 1 END) as new_customer_count
      FROM stores
      WHERE country_code IS NOT NULL AND country_code != ''
      GROUP BY country_code
      ORDER BY store_count DESC
      LIMIT 10
    `);

    return NextResponse.json({
      provinces: provincesResult.rows.map(row => ({
        name: row.state,
        country: row.country_code,
        stores: parseInt(row.store_count),
        newCustomers: parseInt(row.new_customer_count),
        totalVisits: parseInt(row.total_visits) || 0
      })),
      cities: citiesResult.rows.map(row => ({
        name: row.city,
        state: row.state,
        country: row.country_code,
        stores: parseInt(row.store_count),
        newCustomers: parseInt(row.new_customer_count)
      })),
      countries: countriesResult.rows.map(row => ({
        code: row.country_code,
        stores: parseInt(row.store_count),
        newCustomers: parseInt(row.new_customer_count)
      }))
    });
  } catch (error) {
    console.error('Analytics geography error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch geography analytics' },
      { status: 500 }
    );
  }
}
