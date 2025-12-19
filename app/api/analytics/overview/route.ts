import { NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function GET() {
  try {
    // Get overall statistics
    const statsResult = await sql.query(`
      SELECT
        COUNT(*) as total_stores,
        COUNT(DISTINCT country_code) as total_countries,
        SUM(estimated_monthly_visits) as total_visits,
        COUNT(CASE WHEN has_google_ads = true THEN 1 END) as stores_with_ads,
        COUNT(CASE WHEN is_new_customer = true THEN 1 END) as new_customers,
        COUNT(CASE WHEN ads_last_checked IS NOT NULL THEN 1 END) as checked_stores
      FROM stores
    `);

    // Get today's and yesterday's checked count for comparison
    const dailyResult = await sql.query(`
      SELECT
        COUNT(CASE WHEN ads_last_checked >= CURRENT_DATE THEN 1 END) as today_checked,
        COUNT(CASE WHEN ads_last_checked >= CURRENT_DATE - INTERVAL '1 day'
                    AND ads_last_checked < CURRENT_DATE THEN 1 END) as yesterday_checked
      FROM stores
    `);

    const stats = statsResult.rows[0];
    const daily = dailyResult.rows[0];

    return NextResponse.json({
      overview: {
        total_stores: parseInt(stats.total_stores),
        total_countries: parseInt(stats.total_countries),
        total_visits: parseInt(stats.total_visits) || 0,
        stores_with_ads: parseInt(stats.stores_with_ads),
        new_customers: parseInt(stats.new_customers),
        checked_stores: parseInt(stats.checked_stores),
        today_checked: parseInt(daily.today_checked),
        yesterday_checked: parseInt(daily.yesterday_checked),
        growth_rate: daily.yesterday_checked > 0
          ? ((daily.today_checked - daily.yesterday_checked) / daily.yesterday_checked * 100).toFixed(1)
          : '0'
      }
    });
  } catch (error) {
    console.error('Analytics overview error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analytics overview' },
      { status: 500 }
    );
  }
}
