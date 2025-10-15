import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Test connection
try:
    with engine.connect() as conn:
        print("✅ Connected to Supabase PostgreSQL successfully!")
except Exception as e:
    print("❌ Connection failed:", e)
