"""Flask configuration classes loaded from environment variables."""

import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base configuration — shared across all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "default-fallback-key")

    # MySQL connection parameters
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "root")
    DB_NAME = os.environ.get("DB_NAME", "goalmetric_db")


class DevelopmentConfig(Config):
    """Development-specific overrides."""

    DEBUG = True


class TestingConfig(Config):
    """Testing-specific overrides."""

    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production-specific overrides."""

    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}