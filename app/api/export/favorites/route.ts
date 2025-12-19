import { NextRequest, NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';
import { cookies } from 'next/headers';
import Papa from 'papaparse';

export async function GET(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const userEmail = cookieStore.get('user_email')?.value;

    if (!userEmail) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Fetch all favorites for current user with full store data
    const result = await sql.query(`
      SELECT
        s.*,
        f.notes as favorite_notes,
        f.priority as favorite_priority,
        f.created_at as favorited_at
      FROM favorites f
      JOIN stores s ON f.store_id = s.id
      WHERE f.user_email = $1
      ORDER BY f.created_at DESC
    `, [userEmail]);

    // Transform data for CSV with all database fields
    const csvData = result.rows.map(store => ({
      'ID': store.id || '',
      '店铺名称': store.merchant_name || '',
      '域名': store.domain || '',
      '标题': store.title || '',
      '描述': store.description || '',
      'Meta描述': store.meta_description || '',
      '分类': store.categories || '',

      // Platform info
      '平台': store.platform || '',
      '计划': store.plan || '',
      '平台排名': store.platform_rank || '',
      '排名': store.rank || '',
      '状态': store.status || '',

      // Location
      '国家代码': store.country_code || '',
      '城市': store.city || '',
      '省份/州': store.state || '',
      '地区': store.region || '',
      '公司位置': store.company_location || '',
      '街道地址': store.street_address || '',
      '邮编': store.zip || '',

      // Contact info
      '网站URL': store.domain_url || '',
      '关于我们URL': store.about_us_url || '',
      '联系页面URL': store.contact_page_url || '',
      '邮箱': store.emails || '',
      '电话': store.phones || '',
      'WhatsApp URL': store.whatsapp_url || '',

      // Social media
      'Instagram账号': store.instagram || '',
      'Instagram URL': store.instagram_url || '',
      'Facebook账号': store.facebook || '',
      'Facebook URL': store.facebook_url || '',
      'Twitter账号': store.twitter || '',
      'Twitter URL': store.twitter_url || '',
      'TikTok账号': store.tiktok || '',
      'TikTok URL': store.tiktok_url || '',
      'YouTube账号': store.youtube || '',
      'YouTube URL': store.youtube_url || '',
      'LinkedIn账号': store.linkedin_account || '',
      'LinkedIn URL': store.linkedin_url || '',
      'Pinterest账号': store.pinterest || '',
      'Pinterest URL': store.pinterest_url || '',

      // Business metrics
      '员工数': store.employee_count || 0,
      '预估月访问量': store.estimated_monthly_visits || 0,
      '预估年销售额': store.estimated_yearly_sales || '',

      // Google Ads info
      '有Google广告': store.has_google_ads === true ? '是' : store.has_google_ads === false ? '否' : '未检查',
      'Google广告数量': store.google_ads_count || 0,
      '是否新客户': store.is_new_customer === true ? '是' : store.is_new_customer === false ? '否' : '未知',
      '广告最后检查时间': store.ads_last_checked || '',

      // Favorite info
      '收藏备注': store.favorite_notes || '',
      '收藏优先级': store.favorite_priority || '',
      '收藏时间': store.favorited_at || '',

      // Other
      '别名': store.aliases || '',
      '语言代码': store.language_code || '',
      '创建时间': store.created || '',
    }));

    // Generate CSV
    const csv = Papa.unparse(csvData, {
      header: true
    });

    // Add BOM for Excel UTF-8 support
    const csvWithBOM = '\uFEFF' + csv;

    // Generate filename
    const date = new Date().toISOString().split('T')[0];
    const filename = `我的收藏-${date}.csv`;

    // Return CSV file
    return new NextResponse(csvWithBOM, {
      status: 200,
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  } catch (error) {
    console.error('Favorites CSV export error:', error);
    return NextResponse.json(
      { error: 'Failed to export favorites' },
      { status: 500 }
    );
  }
}
