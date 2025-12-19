import { NextRequest, NextResponse } from 'next/server';
import { searchStores } from '@/lib/db';
import Papa from 'papaparse';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

    // Get all filters from query params
    const params = {
      query: searchParams.get('query') || '',
      country: searchParams.get('country') || '',
      state: searchParams.get('state') || '',
      city: searchParams.get('city') || '',
      category: searchParams.get('category') || '',
      plan: searchParams.get('plan') || '',
      minVisits: parseInt(searchParams.get('minVisits') || '0'),
      maxVisits: parseInt(searchParams.get('maxVisits') || '999999999'),
      status: searchParams.get('status') || '',
      hasGoogleAds: searchParams.get('hasGoogleAds') || '',
      isNewCustomer: searchParams.get('isNewCustomer') || '',
      page: 1,
      limit: 5000 // Max export limit
    };

    // Fetch data
    const result = await searchStores(params);

    // Transform data for CSV with all database fields
    const csvData = result.stores.map(store => ({
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

    // Generate filename with filters
    const filters: string[] = [];
    if (params.country) filters.push(params.country);
    if (params.state) filters.push(params.state);
    if (params.city) filters.push(params.city);
    if (params.hasGoogleAds === 'true') filters.push('有广告');
    if (params.hasGoogleAds === 'false') filters.push('无广告');
    if (params.isNewCustomer === 'true') filters.push('新客户');

    const filterStr = filters.length > 0 ? `-${filters.join('-')}` : '';
    const date = new Date().toISOString().split('T')[0];
    const filename = `shopify-stores${filterStr}-${date}.csv`;

    // Return CSV file
    return new NextResponse(csvWithBOM, {
      status: 200,
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  } catch (error) {
    console.error('CSV export error:', error);
    return NextResponse.json(
      { error: 'Failed to export CSV' },
      { status: 500 }
    );
  }
}
