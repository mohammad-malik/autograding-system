from functools import lru_cache
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = "AI-Powered Educational System"
    environment: str = "development"
    
    # API keys
    openai_api_key: str
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index: str
    supabase_url: str
    supabase_key: str
    mistralocr_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # CORS
    backend_cors_origins: Union[List[str], List[AnyHttpUrl]] = ["http://localhost:3000", "http://localhost:8000"]

    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email settings
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings() 