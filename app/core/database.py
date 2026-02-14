from sqlalchemy import create_engine,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

# Settings'dan database URL olish
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,  # Connection health check
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ========================================
# ASYNC ENGINE (YANGI!)
# ========================================
# MySQL URL ni async ga o'zgartirish
async_database_url = settings.DATABASE_URL.replace(
    "mysql+pymysql://",
    "mysql+aiomysql://"
)

async_engine = create_async_engine(
    async_database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


# Helper function - database connection test
def test_database_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    
    # ========================================
# ASYNC TEST (YANGI!)
# ========================================
async def test_async_database_connection():
    """Test async database connection"""
    try:
        async with async_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Async database connection failed: {e}")
        return False


# ========================================
# INFO
# ========================================
if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE CONFIGURATION")
    print("=" * 60)
    print(f"Sync URL:  {settings.DATABASE_URL}")
    print(f"Async URL: {async_database_url}")
    print(f"Pool size: {settings.DB_POOL_SIZE}")
    print("=" * 60)