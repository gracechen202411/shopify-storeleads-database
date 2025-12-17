import { NextResponse } from 'next/server';
import { getStats, getCountries } from '@/lib/db';

export async function GET() {
  try {
    const [stats, countries] = await Promise.all([
      getStats(),
      getCountries()
    ]);

    return NextResponse.json({
      stats,
      countries
    });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch statistics' },
      { status: 500 }
    );
  }
}
