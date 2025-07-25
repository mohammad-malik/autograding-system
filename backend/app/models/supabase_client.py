from functools import lru_cache
from typing import Any, Dict, List, Optional

from supabase import create_client, Client

from ..config import get_settings


@lru_cache()
def get_client() -> Client:
    """Lazily instantiate and cache the Supabase client."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)


# -----------------------------------------------------------------------------
# Convenience helpers – thin wrappers around supabase-py to keep other modules
# free of SDK-specific code. Only common operations needed by the current code
# base are included; add more as you migrate additional features.
# -----------------------------------------------------------------------------

def table(name: str):
    """Return a query builder for the given table name."""
    return get_client().table(name)


def get_by_id(table_name: str, row_id: str):
    data = (
        table(table_name).select("*").eq("id", row_id).single().execute().data
    )
    return data


def insert(table_name: str, payload: Dict[str, Any]):
    return table(table_name).insert(payload).execute().data[0]


def update_by_id(table_name: str, row_id: str, payload: Dict[str, Any]):
    return (
        table(table_name).update(payload).eq("id", row_id).single().execute().data
    )


def delete_by_id(table_name: str, row_id: str):
    table(table_name).delete().eq("id", row_id).execute() 