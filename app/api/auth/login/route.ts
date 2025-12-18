import { NextResponse } from 'next/server';

// Simple authentication - In production, use proper password hashing and database storage
const USERS = {
  doudou: 'TopSales2025!',
  weiyi: 'GoogleSales2025!',
  grace: 'SuperGrace2025!',
};

export async function POST(request: Request) {
  try {
    const { username, password } = await request.json();

    // Validate credentials
    if (USERS[username as keyof typeof USERS] === password) {
      // Create a simple token (in production, use JWT or proper session management)
      const token = Buffer.from(`${username}:${Date.now()}`).toString('base64');

      return NextResponse.json({
        success: true,
        token,
        username,
      });
    }

    return NextResponse.json(
      { error: 'Invalid username or password' },
      { status: 401 }
    );
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'An error occurred during login' },
      { status: 500 }
    );
  }
}
