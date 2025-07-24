import os
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = "AI-Powered Educational System"
    environment: str = "development"
    
    # API keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY")
    
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT")
    pinecone_index: str = os.getenv("PINECONE_INDEX")
    
    mistralocr_api_key: str = os.getenv("MISTRALOCR_API_KEY")
    sqlalchemy_database_url: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    
    supabase_url: str = os.getenv("SUPABASE_URL")
    supabase_key: str = os.getenv("SUPABASE_KEY")
    bucket_textbooks: str = os.getenv("BUCKET_TEXTBOOKS")
    bucket_quizzes: str = os.getenv("BUCKET_QUIZZES")
    bucket_submissions: str = os.getenv("BUCKET_SUBMISSIONS")
    bucket_reports: str = os.getenv("BUCKET_REPORTS")
    bucket_slides: str = os.getenv("BUCKET_SLIDES")
    
    # Authentication
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # CORS
    backend_cors_origins: Union[List[str], List[AnyHttpUrl]] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("backend_cors_origins", mode='before')
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="",
        extra="allow"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings() 