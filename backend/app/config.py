from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_env: str = ""
    pinecone_index: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    mistralocr_api_key: str = ""
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
