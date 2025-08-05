import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # API Configuration
    API_TITLE = 'YouTube Analytics API'
    API_VERSION = '1.0.0'
    API_DESCRIPTION = 'Backend API for YouTube Analytics Dashboard'
    
    # CORS Configuration
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174'
    ]
    
    # YouTube API Configuration (for future integration)
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    YOUTUBE_CHANNEL_ID = os.environ.get('YOUTUBE_CHANNEL_ID')
    
    # Database Configuration (for future use)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Analytics Configuration
    DEFAULT_ANALYTICS_PERIOD = 7  # days
    MAX_ANALYTICS_PERIOD = 90     # days
    REFRESH_INTERVAL = 300        # seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 