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

    // Transform data for CSV
    const csvData = result.stores.map(store => ({
      '店铺名称': store.merchant_name || '',
      '域名': store.domain || '',
      '国家': store.country_code || '',
      '省份': store.state || '',
      '城市': store.city || '',
      '月访问量': store.estimated_monthly_visits || 0,
      '员工数': store.employee_count || 0,
      '年销售额': store.estimated_yearly_sales || '',
      'Instagram': store.instagram || '',
      'Facebook': store.facebook || '',
      'TikTok': store.tiktok || '',
      'YouTube': store.youtube || '',
      '有Google广告': store.has_google_ads === true ? '是' : store.has_google_ads === false ? '否' : '未检查',
      '广告数量': store.google_ads_count || 0,
      '是否新客户': store.is_new_customer === true ? '是' : store.is_new_customer === false ? '否' : '未知',
      '最后检查时间': store.ads_last_checked || '',
      '状态': store.status || '',
      '排名': store.rank || '',
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
