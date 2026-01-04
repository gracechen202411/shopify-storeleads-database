
import os
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get database URL
db_url = os.getenv("POSTGRES_URL")

if not db_url:
    print("❌ POSTGRES_URL is not set in .env")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    print("✅ Successfully connected to database using .env credentials")
    conn.close()
except Exception as e:
    print(f"❌ Failed to connect using .env credentials: {e}")
    exit(1)
