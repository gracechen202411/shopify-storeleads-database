# Shopify Store Leads Database

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fgracechen202411%2Fshopify-storeleads-database&env=POSTGRES_URL,POSTGRES_PRISMA_URL,POSTGRES_URL_NON_POOLING&envDescription=Neon%20PostgreSQL%20connection%20strings&envLink=https%3A%2F%2Fneon.tech)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8?logo=tailwind-css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Next.js web application to browse and search millions of Shopify stores with detailed business information.

![Shopify Store Leads Database](https://img.shields.io/badge/Stores-2.4M%2B-success)
![Database Size](https://img.shields.io/badge/Database-1.5GB-informational)

## Features

- 🔍 Full-text search across store names, domains, and descriptions
- 🌍 Filter by country, monthly visits, and more
- 📊 Real-time statistics dashboard
- 📱 Responsive design with dark mode support
- ⚡ Fast API with PostgreSQL full-text search
- 🎨 Modern UI with Tailwind CSS

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Database**: Neon PostgreSQL (serverless)
- **Deployment**: Vercel
- **ORM**: Vercel Postgres SDK

## Setup Instructions

### 1. Database Setup (Neon)

1. Create a free account at [Neon](https://neon.tech)
2. Create a new project
3. Copy your connection string
4. Run the schema:
   ```bash
   psql "your-connection-string" -f schema.sql
   ```

### 2. Import Data

1. Install Python dependencies:
   ```bash
   pip install psycopg2-binary
   ```

2. Set your database URL:
   ```bash
   export DATABASE_URL="your-neon-connection-string"
   ```

3. Import the CSV chunks (in the chunks/ directory):
   ```bash
   # Import all chunks sequentially
   for file in ../chunks/shopify-storeleads-part*.csv; do
     python import-to-neon.py "$file"
   done
   ```

   This will import all ~2.4M records. The process may take 1-2 hours depending on your connection.

### 3. Frontend Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Add your Neon database URL to `.env`:
   ```
   POSTGRES_URL="your-neon-connection-string"
   POSTGRES_PRISMA_URL="your-neon-connection-string?pgbouncer=true"
   POSTGRES_URL_NON_POOLING="your-neon-connection-string"
   ```

4. Run development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000)

### 4. Deploy to Vercel

1. Push your code to GitHub

2. Import project on [Vercel](https://vercel.com):
   - Connect your GitHub repository
   - Vercel will auto-detect Next.js

3. Add environment variables in Vercel project settings:
   - `POSTGRES_URL`
   - `POSTGRES_PRISMA_URL`
   - `POSTGRES_URL_NON_POOLING`

4. Deploy! 🚀

## Project Structure

```
shopify-storeleads-app/
├── app/
│   ├── api/
│   │   ├── stores/route.ts      # Store search API
│   │   └── stats/route.ts       # Statistics API
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   └── globals.css              # Global styles
├── components/
│   ├── SearchBar.tsx            # Search input component
│   └── StoreCard.tsx            # Store display card
├── lib/
│   └── db.ts                    # Database queries
├── schema.sql                   # PostgreSQL schema
├── import-to-neon.py           # Data import script
└── README.md
```

## Data Schema

The database contains 44 columns including:

- **Basic Info**: domain, merchant_name, description
- **Location**: country_code, city, state, region
- **Metrics**: estimated_monthly_visits, estimated_yearly_sales, employee_count
- **Social Media**: instagram, facebook, twitter, tiktok, youtube, linkedin
- **Business**: categories, status, plan, rank

## Performance Tips

1. **Database Indexes**: The schema includes indexes on frequently queried columns
2. **Pagination**: Results are paginated (20 per page) for optimal performance
3. **Connection Pooling**: Uses Vercel Postgres with built-in connection pooling
4. **Caching**: Consider adding Redis for frequently accessed queries

## CSV File Information

Original file: 1.5GB, 2.4M records
Split into 4 chunks of ~400MB each:
- shopify-storeleads-part1.csv (478,315 lines)
- shopify-storeleads-part2.csv (586,289 lines)
- shopify-storeleads-part3.csv (774,480 lines)
- shopify-storeleads-part4.csv (552,773 lines)

## API Endpoints

### GET /api/stores
Search and filter stores

**Query Parameters:**
- `query`: Search term
- `country`: Country code (e.g., "US")
- `category`: Category filter
- `minVisits`: Minimum monthly visits
- `maxVisits`: Maximum monthly visits
- `status`: Store status (e.g., "Active")
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 50)

**Response:**
```json
{
  "stores": [...],
  "total": 1234567,
  "page": 1,
  "limit": 50,
  "totalPages": 24692
}
```

### GET /api/stats
Get database statistics

**Response:**
```json
{
  "stats": {
    "total_stores": "2391857",
    "total_countries": "180",
    "total_employees": "1234567",
    "avg_monthly_visits": "123456"
  },
  "countries": [...]
}
```

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
