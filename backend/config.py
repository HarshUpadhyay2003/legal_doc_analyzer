import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-not-for-production')
    
    # JWT config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'another-super-secret-jwt-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'legal_docs.db')
    )
    
    # Model config
    MODEL_CACHE_SIZE = 1000
    MAX_CONTEXT_LENGTH = 1028
    MAX_ANSWER_LENGTH = 256
    
    # CORS config
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging config
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Add production-specific settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 