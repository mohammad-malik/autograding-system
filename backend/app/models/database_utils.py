from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client
# from dotenv import load_dotenv  # redundant

# load_dotenv()  # redundant

from ..config import get_settings

# Create Supabase client
supabase = create_client(
    get_settings().supabase_url,
    get_settings().supabase_key
)

# SQLAlchemy setup
# For local development, you can use SQLite
SQLALCHEMY_DATABASE_URL = get_settings().sqlalchemy_database_url
# In production, you would use the Supabase PostgreSQL connection
# SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database."""
    from .database import Base
    Base.metadata.create_all(bind=engine) 