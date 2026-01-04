import { NextRequest, NextResponse } from 'next/server';
import { searchStores } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;

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
      customerType: searchParams.get('customerType') || '',
      page: parseInt(searchParams.get('page') || '1'),
      limit: parseInt(searchParams.get('limit') || '50')
    };

    const result = await searchStores(params);

    return NextResponse.json(result);
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stores' },
      { status: 500 }
    );
  }
}
