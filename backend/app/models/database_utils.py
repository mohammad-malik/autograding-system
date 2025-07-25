from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client
# from dotenv import load_dotenv  # redundant

# load_dotenv()  # redundant

from ..config import get_settings

# Deprecated SQLAlchemy utilities have been removed; this module now only
# serves to expose the Supabase client instance used throughout the code base.

supabase = create_client(get_settings().supabase_url, get_settings().supabase_key)

# Backward-compatibility shims -------------------------------------------------
# In places where the old code imported `get_db` for dependency injection we
# will gradually migrate, but for now we keep a dummy generator so FastAPI
# doesn’t crash even if a route still depends on it.  It yields the supabase
# client instead of a SQLAlchemy session.


def get_db():
    """Temporary shim that yields the Supabase client object."""
    try:
        yield supabase
    finally:
        pass


# init_db is no longer needed; kept as a no-op for compatibility


def init_db():
    return None 