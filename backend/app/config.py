
from typing import Optional
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()