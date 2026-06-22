from supabase import create_client, Client
from src.utils.config_loader import load_yaml, get_env
from typing import Optional

class SupabaseDB:
    """
    Class that manages Supabase database connections.

    Attributes:
        _client (Optional[Client]): The Supabase client instance.
    """
    
    _client : Optional[Client] = None

    @classmethod
    def init(cls) -> Client:
        if cls._client is None:
            db_config = load_yaml("db.yaml")["supabase"]
            url = get_env(db_config["url_env"])
            key = get_env(db_config["key_env"])

            if not url or not key:
                raise ValueError("Supabase URL or Key not configured")
            cls._client = create_client(url, key)
        return cls._client
    
    
    @classmethod
    def table(cls, table_name: str):
        return cls.init().table(table_name)