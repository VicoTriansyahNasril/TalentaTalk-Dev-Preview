# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator, AsyncGenerator
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration with environment variables for security
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Check if DATABASE_URL is provided directly (for Docker/production)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # URL encode password to handle special characters
    encoded_password = quote_plus(DB_PASSWORD)
    # Construct database URL
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # If using asyncpg in env, convert to psycopg2 for sync operations
    if "asyncpg" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

print(f"Using DATABASE_URL: {DATABASE_URL}")

# Create engine with connection pooling and better error handling
try:
    engine = create_engine(
        DATABASE_URL,
        # Connection pool settings
        pool_size=10,                    # Number of connections to maintain in pool
        max_overflow=20,                 # Additional connections beyond pool_size
        pool_timeout=30,                 # Timeout for getting connection from pool
        pool_recycle=3600,              # Recycle connections every hour
        pool_pre_ping=True,             # Validate connections before use
        # Echo SQL queries for debugging (set to False in production)
        echo=os.getenv("DB_ECHO", "False").lower() == "true"
    )
except Exception as e:
    print(f"Error creating database engine: {e}")
    raise

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Create declarative base for models (fixed deprecation warning)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    This function yields a database session and ensures it's properly closed.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        raise e
    finally:
        # Always close the session
        db.close()

async def get_db_async() -> AsyncGenerator[Session, None]:
    """
    Async version of get_db for async endpoints.
    Note: This is still using sync SQLAlchemy, but provides async-compatible interface.
    For true async database operations, consider using asyncpg with SQLAlchemy async.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Alias for backward compatibility
get_async_db = get_db_async

def create_tables():
    """
    Create all tables defined in models.
    Call this function to initialize the database schema.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise e

def check_connection():
    """
    Test database connection.
    Useful for health checks and debugging.
    """
    try:
        with engine.connect() as connection:
            # Fixed: Use text() wrapper for SQL queries
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_engine():
    """
    Get the SQLAlchemy engine instance.
    Useful for direct database operations or migrations.
    """
    return engine

# Database health check function
def database_health_check() -> dict:
    """
    Comprehensive database health check.
    Returns status and connection info.
    """
    try:
        with engine.connect() as connection:
            # Test basic query (fixed with text())
            result = connection.execute(text("SELECT 1"))
            version = result.fetchone()[0]
            
            # Get connection pool info
            pool = engine.pool
            
            return {
                "status": "healthy",
                "database_version": version,
                "pool_size": pool.size(),
                "checked_in_connections": pool.checkedin(),
                "checked_out_connections": pool.checkedout(),
                "overflow_connections": pool.overflow(),
                "invalid_connections": pool.invalid()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Context manager for manual database operations
class DatabaseSession:
    """
    Context manager for database sessions.
    Usage:
        with DatabaseSession() as db:
            # perform database operations
            pass
    """
    def __init__(self):
        self.db = None
    
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()

# Environment configuration checker
def check_environment():
    """
    Check if all required environment variables are set.
    """
    required_vars = ["SECRET_KEY", "GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {missing_vars}")
        return False
    return True

# Test database connection with better error reporting
def test_database_connection():
    """
    Comprehensive database connection test
    """
    print("=" * 50)
    print("DATABASE CONNECTION TEST")
    print("=" * 50)
    
    # Print configuration (without password)
    print(f"DB_HOST: {DB_HOST}")
    print(f"DB_PORT: {DB_PORT}")
    print(f"DB_NAME: {DB_NAME}")
    print(f"DB_USER: {DB_USER}")
    print(f"DATABASE_URL: {DATABASE_URL[:30]}...")
    
    # Test connection
    try:
        print("\nTesting connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            db_version = result.fetchone()[0]
            print(f"✓ Connection successful!")
            print(f"✓ Database version: {db_version[:50]}...")
            
            # Test basic query
            result = connection.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            print(f"✓ Connected to database: {db_info[0]}")
            print(f"✓ Connected as user: {db_info[1]}")
            
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print(f"✗ Error type: {type(e).__name__}")
        
        # Common troubleshooting
        print("\nTroubleshooting tips:")
        print("1. Check if PostgreSQL server is running")
        print("2. Verify database credentials")
        print("3. Check network connectivity")
        print("4. Ensure database exists")
        
        return False

# Initialize on import
if __name__ == "__main__":
    # Load environment variables
    print("Loading environment variables...")
    load_dotenv()
    
    # Test connection
    test_database_connection()
    
    print("\n" + "=" * 50)
    print("ENVIRONMENT VARIABLES CHECK")
    print("=" * 50)
    
    if check_environment():
        print("✓ All required environment variables are set!")
    else:
        print("✗ Some environment variables are missing!")
        
    # Show loaded env vars (safely)
    print(f"SECRET_KEY: {'Set' if os.getenv('SECRET_KEY') else 'Missing'}")
    print(f"GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'Missing'}")
    print(f"DATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Missing'}")