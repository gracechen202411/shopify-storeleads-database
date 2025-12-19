import { NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function GET() {
  try {
    // Traffic distribution by ranges
    const trafficRangesResult = await sql.query(`
      SELECT
        CASE
          WHEN estimated_monthly_visits < 10000 THEN '< 1万'
          WHEN estimated_monthly_visits BETWEEN 10000 AND 50000 THEN '1-5万'
          WHEN estimated_monthly_visits BETWEEN 50000 AND 100000 THEN '5-10万'
          WHEN estimated_monthly_visits BETWEEN 100000 AND 500000 THEN '10-50万'
          WHEN estimated_monthly_visits BETWEEN 500000 AND 1000000 THEN '50-100万'
          ELSE '100万+'
        END as traffic_range,
        COUNT(*) as store_count,
        COUNT(CASE WHEN is_new_customer = true THEN 1 END) as new_customer_count
      FROM stores
      WHERE estimated_monthly_visits > 0
      GROUP BY traffic_range
      ORDER BY
        CASE traffic_range
          WHEN '< 1万' THEN 1
          WHEN '1-5万' THEN 2
          WHEN '5-10万' THEN 3
          WHEN '10-50万' THEN 4
          WHEN '50-100万' THEN 5
          ELSE 6
        END
    `);

    // Top 100 stores by traffic
    const topStoresResult = await sql.query(`
      SELECT
        id,
        merchant_name,
        domain,
        country_code,
        state,
        city,
        estimated_monthly_visits,
        has_google_ads,
        is_new_customer,
        google_ads_count
      FROM stores
      WHERE estimated_monthly_visits > 0
      ORDER BY estimated_monthly_visits DESC
      LIMIT 100
    `);

    // New customers with high traffic (priority targets)
    const priorityTargetsResult = await sql.query(`
      SELECT
        id,
        merchant_name,
        domain,
        country_code,
        state,
        city,
        estimated_monthly_visits,
        google_ads_count,
        employee_count
      FROM stores
      WHERE is_new_customer = true
        AND estimated_monthly_visits > 100000
      ORDER BY estimated_monthly_visits DESC
      LIMIT 50
    `);

    return NextResponse.json({
      trafficRanges: trafficRangesResult.rows.map(row => ({
        range: row.traffic_range,
        stores: parseInt(row.store_count),
        newCustomers: parseInt(row.new_customer_count)
      })),
      topStores: topStoresResult.rows.map(row => ({
        id: row.id,
        name: row.merchant_name || row.domain,
        domain: row.domain,
        location: [row.city, row.state, row.country_code].filter(Boolean).join(', '),
        visits: parseInt(row.estimated_monthly_visits),
        hasAds: row.has_google_ads,
        isNewCustomer: row.is_new_customer,
        adCount: parseInt(row.google_ads_count) || 0
      })),
      priorityTargets: priorityTargetsResult.rows.map(row => ({
        id: row.id,
        name: row.merchant_name || row.domain,
        domain: row.domain,
        location: [row.city, row.state, row.country_code].filter(Boolean).join(', '),
        visits: parseInt(row.estimated_monthly_visits),
        adCount: parseInt(row.google_ads_count) || 0,
        employees: parseInt(row.employee_count) || 0
      }))
    });
  } catch (error) {
    console.error('Analytics traffic error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch traffic analytics' },
      { status: 500 }
    );
  }
}
