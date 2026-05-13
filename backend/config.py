# =============================================================================
# File: config.py
# Project: Grocery Intelligence Platform
# Author: Anita Woodford
# Created Date: 2024-06-01
# Description: Configuration management
# authentication , OCR thresholds, rebate point conversion, and other settings.
# Usage: backend modules should call get_settings() instead of reading env
# variables directly.
# security Note: real secrete values are hidden
# =============================================================================

"""Centralized configuration for the grocery intelligence platform for the
backend. This module loads settings from environment variables and provides"""
# import caching so the setting object is created once and reused
from functools import lru_cache
from pathlib import Path
from pydantic import Field, SecretStr, field_validator 
from pydantic_settings import BaseSettings, SettingsConfigDict # imports upport for env variable loading and settings management
# store the backend directory that contains ths config.py files
BASE_DIR = Path(__file__).resolve().parent
# build an explicit path to backend .env 
ENV_FILE = BASE_DIR / ".env"

# Define one typed configuration object for the backend.
class Settings(BaseSettings):
    """Application settings loaded from environment variables. 
    This includes database connection info, security keys, OCR thresholds, and
    other configurable parameters. 
    """
    # database settings
    mongo_uri: str = Field(alias="MONGO_URI")
    mongo_db: str = Field(alias="MONGO_DB") # main mongo database name
    test_mongo_db: str = Field(alias="TEST_MONGO_DB") # test database name
    redis_url: str = Field(alias="REDIS_URL") # loads the Redis connection URL from REDIS_URL
    # security settings
    # load application secret key, masking it in logs and repr output
    secret_key: SecretStr = Field(alias="SECRET_KEY") 
    # load the encryption key for credentials, also masked
    credential_encryption_key: SecretStr = Field(alias="CREDENTIAL_ENCRYPTION_KEY")
    # OCR confidence thresholds for review and auto-acceptance
    ocr_confidence_threshold_review: float = Field(0.70,alias="OCR_CONFIDENCE_THRESHOLD_REVIEW")
    ocr_confidence_threshold_accept: float = Field(0.85,alias="OCR_CONFIDENCE_THRESHOLD_ACCEPT")
    # rebate point conversion rate
    fetch_points_per_dollar: int = Field(1000, alias="FETCH_POINTS_PER_DOLLAR")
    # swagbucks awarded per fetch    swagbucks: int = Field(100, alias="SWAGBUCKS")
    swagbucks_points_per_dollar: int = Field(100, alias="SWAGBUCKS_POINTS_PER_DOLLAR")
    
    # validate raw values to ensure they are in the expected format and range
    @field_validator("secret_key",mode="before")
    @classmethod # marks validator as a class leve vaidation method
    
    # define validation rule length for the secret_key
    def validate_length_secret_key(cls, value: str) -> str:
        # requires key to be long enough for local development and future production use
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for security.")
        return value
    
    # validate the credential encryption key to ensure it is a valid Fernet key
    @field_validator("credential_encryption_key",mode="before")
    @classmethod # marks validator as a class leve vaidation method
    
    # define the validation rule length for credential_encryption_key
    def validate_length_credential_encryption_key(cls, value: str) -> str:
        # requires key to be long enough for local development and future production use
        if len(value) < 32:
            raise ValueError("CREDENTIAL_ENCRYPTION_KEY must be at least 32 characters long for security.")
        return value
    
    # define the validation rule for the OCR confidence thresholds to ensure they are between 0 and 1
    @field_validator("ocr_confidence_threshold_review", "ocr_confidence_threshold_accept")
    @classmethod # marks validator as a class leve vaidation method
    def validate_ocr_confidence_thresholds(cls, value: float) -> float:
        # requires thresholds to be between 0 and 1
        if not (0 <= value <= 1.0):
            raise ValueError("OCR confidence thresholds must be between 0 and 1.")
        return value
    
    # Configures how Pydantic Settings should load values.
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, # specifies the path to the .env file to load environment variables from
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True, # allows loading env variables by field name or alias
    )
    
# Use caching to ensure the settings object is created once and reused across the app
@lru_cache(maxsize=1) # cache the result of this function, maxsize=1 means only one instance will be stored
# defines the public settings getter used by backend
def get_settings() -> Settings:
    """Returns a cached instance of the Settings object. 
    This function should be used by all backend modules to access configuration
    values, ensuring that settings are loaded once and reused.
    """
    return Settings()