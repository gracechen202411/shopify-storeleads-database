import { NextRequest, NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';
import { cookies } from 'next/headers';

// GET: Fetch all favorites for current user
export async function GET(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const userEmail = cookieStore.get('user_email')?.value;

    if (!userEmail) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const result = await sql.query(`
      SELECT
        f.id as favorite_id,
        f.notes,
        f.priority,
        f.created_at as favorited_at,
        s.*
      FROM favorites f
      JOIN stores s ON f.store_id = s.id
      WHERE f.user_email = $1
      ORDER BY f.created_at DESC
    `, [userEmail]);

    return NextResponse.json({ favorites: result.rows });
  } catch (error) {
    console.error('Favorites GET error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch favorites' },
      { status: 500 }
    );
  }
}

// POST: Add a favorite
export async function POST(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const userEmail = cookieStore.get('user_email')?.value;

    if (!userEmail) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { store_id, notes, priority } = body;

    if (!store_id) {
      return NextResponse.json({ error: 'store_id is required' }, { status: 400 });
    }

    const result = await sql.query(`
      INSERT INTO favorites (user_email, store_id, notes, priority)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (user_email, store_id)
      DO UPDATE SET
        notes = COALESCE($3, favorites.notes),
        priority = COALESCE($4, favorites.priority),
        updated_at = NOW()
      RETURNING *
    `, [userEmail, store_id, notes || null, priority || 'medium']);

    return NextResponse.json({ favorite: result.rows[0] });
  } catch (error) {
    console.error('Favorites POST error:', error);
    return NextResponse.json(
      { error: 'Failed to add favorite' },
      { status: 500 }
    );
  }
}

// DELETE: Remove a favorite
export async function DELETE(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const userEmail = cookieStore.get('user_email')?.value;

    if (!userEmail) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const searchParams = request.nextUrl.searchParams;
    const storeId = searchParams.get('store_id');

    if (!storeId) {
      return NextResponse.json({ error: 'store_id is required' }, { status: 400 });
    }

    await sql.query(`
      DELETE FROM favorites
      WHERE user_email = $1 AND store_id = $2
    `, [userEmail, parseInt(storeId)]);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Favorites DELETE error:', error);
    return NextResponse.json(
      { error: 'Failed to remove favorite' },
      { status: 500 }
    );
  }
}
