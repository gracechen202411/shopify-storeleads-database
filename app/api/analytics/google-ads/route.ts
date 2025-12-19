import { NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function GET() {
  try {
    // Customer type distribution
    const customerTypeResult = await sql.query(`
      SELECT
        CASE
          WHEN has_google_ads = false OR has_google_ads IS NULL THEN 'no_ads'
          WHEN is_new_customer = true THEN 'new_customer'
          ELSE 'existing_customer'
        END as customer_type,
        COUNT(*) as count
      FROM stores
      WHERE ads_last_checked IS NOT NULL
      GROUP BY customer_type
    `);

    // New customers by province (China focus)
    const provincesResult = await sql.query(`
      SELECT
        state,
        COUNT(*) as new_customer_count,
        SUM(estimated_monthly_visits) as total_visits
      FROM stores
      WHERE is_new_customer = true
        AND country_code = 'CN'
        AND state IS NOT NULL
        AND state != ''
      GROUP BY state
      ORDER BY new_customer_count DESC
      LIMIT 15
    `);

    // Ad count distribution
    const adCountResult = await sql.query(`
      SELECT
        CASE
          WHEN google_ads_count = 0 THEN '0'
          WHEN google_ads_count BETWEEN 1 AND 10 THEN '1-10'
          WHEN google_ads_count BETWEEN 11 AND 50 THEN '11-50'
          WHEN google_ads_count BETWEEN 51 AND 100 THEN '51-100'
          ELSE '100+'
        END as ad_range,
        COUNT(*) as store_count
      FROM stores
      WHERE has_google_ads IS NOT NULL
      GROUP BY ad_range
      ORDER BY
        CASE ad_range
          WHEN '0' THEN 1
          WHEN '1-10' THEN 2
          WHEN '11-50' THEN 3
          WHEN '51-100' THEN 4
          ELSE 5
        END
    `);

    // Recent checking activity (last 7 days)
    const activityResult = await sql.query(`
      SELECT
        DATE(ads_last_checked) as check_date,
        COUNT(*) as stores_checked,
        COUNT(CASE WHEN is_new_customer = true THEN 1 END) as new_customers_found
      FROM stores
      WHERE ads_last_checked >= CURRENT_DATE - INTERVAL '7 days'
      GROUP BY DATE(ads_last_checked)
      ORDER BY check_date DESC
    `);

    return NextResponse.json({
      customerTypes: customerTypeResult.rows.map(row => ({
        type: row.customer_type,
        count: parseInt(row.count)
      })),
      provinceDistribution: provincesResult.rows.map(row => ({
        province: row.state,
        count: parseInt(row.new_customer_count),
        totalVisits: parseInt(row.total_visits) || 0
      })),
      adCountDistribution: adCountResult.rows.map(row => ({
        range: row.ad_range,
        count: parseInt(row.store_count)
      })),
      recentActivity: activityResult.rows.map(row => ({
        date: row.check_date,
        checked: parseInt(row.stores_checked),
        newCustomers: parseInt(row.new_customers_found)
      }))
    });
  } catch (error) {
    console.error('Analytics Google Ads error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch Google Ads analytics' },
      { status: 500 }
    );
  }
}
