import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AccessGuard"
    VERSION: str = "1.5.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Operations
    ENVIRONMENT: str = "development"  # development, demo, production
    DEMO_MODE: bool = True
    ORGANIZATION_NAME: str = "Anurag Technologies"
    ORGANIZATION_DOMAIN: str = "anurag.tech"
    
    # Database
    DATABASE_URL: str = "sqlite:///./accessguard.db"
    
    # Security & Tokens
    SECRET_KEY: str = "super-secret-accessguard-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    COOKIE_SECURE: bool = False  # Set to True in production HTTPS
    
    # CORS Allowlist
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]

    # GitHub App Connector Settings (Phase 5 & 5.1)
    GITHUB_APP_ID: str = ""
    GITHUB_PRIVATE_KEY: str = ""   # PEM private key — environment only, never logged
    GITHUB_API_VERSION: str = "2026-03-10"
    GITHUB_BASE_URL: str = "https://api.github.com"
    CONNECTOR_TIMEOUT_SECONDS: int = 30

    # Gemini AI Security Analyst Settings (Phase 6)
    GEMINI_API_KEY: str = ""        # Environment variable only — never logged or sent to client
    GEMINI_MODEL: str = "gemini-3.6-flash"  # Configurable model ID (gemini-3.6-flash default)
    AI_DAILY_RATE_LIMIT: int = 100
    AI_REQUEST_TIMEOUT_SECONDS: int = 15

    # Continuous Monitoring & Scheduler Settings (Phase 7.1)
    MONITORING_ENABLED: bool = False
    MONITORING_INTERVAL_SECONDS: int = 900


    def validate_production_config(self) -> None:
        """
        Production Mode Fail-Closed Validation.
        Verifies that production environments do not launch with weak secrets or insecure cookies.
        """
        if not self.DEMO_MODE or self.ENVIRONMENT.lower() == "production":
            if self.SECRET_KEY == "super-secret-accessguard-key-change-in-production" or len(self.SECRET_KEY) < 32:
                raise ValueError("INSECURE PRODUCTION CONFIGURATION: SECRET_KEY must be a strong random key (>= 32 chars) in production mode.")
            if not self.COOKIE_SECURE:
                raise ValueError("INSECURE PRODUCTION CONFIGURATION: COOKIE_SECURE must be True in production mode.")

    class Config:
        case_sensitive = True

settings = Settings()
