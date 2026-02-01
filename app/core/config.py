from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Application configuration settings.
    Reads from .env file in project root.
    """
    
    # ========================================
    # APPLICATION
    # ========================================
    APP_NAME: str = "FastAPI Blog API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # ========================================
    # DATABASE
    # ========================================
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    
    # ========================================
    # SECURITY
    # ========================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ========================================
    # CORS
    # ========================================
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse ALLOWED_ORIGINS from string to list"""
        if isinstance(v, str):
            # JSON string: '["http://localhost:3000","http://localhost:8000"]'
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Comma-separated: 'http://localhost:3000,http://localhost:8000'
                return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("ALLOWED_METHODS", "ALLOWED_HEADERS", mode="before")
    @classmethod
    def parse_list_fields(cls, v):
        """Parse list fields from string"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",")]
        return v
    
    # ========================================
    # REDIS (optional)
    # ========================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_URL: str | None = None
    
    # ========================================
    # EMAIL (optional)
    # ========================================
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_FROM_NAME: str = ""
    
    # ========================================
    # FILE UPLOAD
    # ========================================
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "pdf"]
    UPLOAD_DIR: str = "/app/uploads"
    
    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        """Parse ALLOWED_EXTENSIONS from string to list"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [ext.strip() for ext in v.split(",")]
        return v
    
    # ========================================
    # PAGINATION
    # ========================================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # ========================================
    # RATE LIMITING
    # ========================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ========================================
    # LOGGING
    # ========================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "/app/logs/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # ========================================
    # PYDANTIC SETTINGS CONFIG
    # ========================================
    model_config = SettingsConfigDict(
        env_file=".env",                    # .env fayl
        env_file_encoding="utf-8",          # Encoding
        case_sensitive=True,                # Case sensitive
        extra="ignore"                      # Extra fieldlarni ignore qilish
    )
    
    # ========================================
    # HELPER METHODS
    # ========================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    def get_database_url(self, async_driver: bool = False) -> str:
        """Get database URL with optional async driver"""
        if async_driver:
            return self.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://")
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to create singleton.
    """
    return Settings()


# Global settings instance
settings = get_settings()


# Debugging helper (development only)
if __name__ == "__main__":
    print("=" * 50)
    print("CURRENT SETTINGS:")
    print("=" * 50)
    for field, value in settings.model_dump().items():
        # Don't print sensitive data
        if "PASSWORD" in field or "SECRET" in field or "KEY" in field:
            print(f"{field}: ***HIDDEN***")
        else:
            print(f"{field}: {value}")
    print("=" * 50)