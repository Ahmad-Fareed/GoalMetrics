import os
from dotenv import load_dotenv

# Explicitly load the .env file from the current directory
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration class that extracts variables from environment."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-fallback-key')
    
    # MySQL Database Configs
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    DB_NAME = os.environ.get('DB_NAME', 'goalmetric_db')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Dictionary map to easily toggle environments inside the factory pattern
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}