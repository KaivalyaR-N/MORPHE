import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "MORPHE Document Intelligence"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # Support SQLite async by default for simple dev, postgresql+asyncpg for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./morphe.db"
    
    # Security
    JWT_SECRET: str = "morphe-super-secret-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Storage
    STORAGE_DIR: str = "./storage"
    EXPORTS_DIR: str = "./storage/exports"
    
    # AI / LLM
    AI_PROVIDER: str = "auto"  # 'gemini', 'heuristic', 'auto'
    GOOGLE_API_KEY: Optional[str] = None
    
    # GROBID Optional integration
    GROBID_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
