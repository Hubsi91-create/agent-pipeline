"""
Configuration Management for 11-Agent Music Video Production System
Centralized settings using Pydantic for validation
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic for automatic validation and type conversion.
    """

    # ============================================================
    # APPLICATION SETTINGS
    # ============================================================

    APP_NAME: str = "Music Agents v2 - 11-Agent System"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False

    # ============================================================
    # GOOGLE CLOUD SETTINGS
    # ============================================================

    GOOGLE_PROJECT_ID: str = "music-agents-prod"
    GOOGLE_REGION: str = "global"

    # Google Sheets Database
    GOOGLE_SHEET_ID: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None  # For local testing

    # ============================================================
    # API SETTINGS
    # ============================================================

    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["*"]  # Configure for production
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # ============================================================
    # LOGGING SETTINGS
    # ============================================================

    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # ============================================================
    # AGENT SETTINGS
    # ============================================================

    # Agent 1: Trend Detective
    AGENT1_DEFAULT_TREND_COUNT: int = 5

    # Agent 2: Suno Prompt Generator
    AGENT2_DEFAULT_PROMPTS_PER_TREND: int = 10

    # QC Processor
    QC_APPROVAL_THRESHOLD: int = 7
    QC_FEW_SHOT_EXAMPLE_LIMIT: int = 15

    # ============================================================
    # GEMINI / LLM SETTINGS
    # ============================================================

    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_DEFAULT_TEMPERATURE: float = 0.8
    GEMINI_DEFAULT_MAX_TOKENS: int = 8192

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create singleton instance of Settings.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
