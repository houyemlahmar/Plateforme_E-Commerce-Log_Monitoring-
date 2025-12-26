"""
Configuration module for the application
Loads environment variables and provides configuration classes
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.getenv('FLASK_APP', 'main.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Elasticsearch Configuration
    ELASTICSEARCH_CONFIG = {
        'host': os.getenv('ELASTICSEARCH_HOST', 'localhost'),
        'port': int(os.getenv('ELASTICSEARCH_PORT', 9200)),
        'user': os.getenv('ELASTICSEARCH_USER', 'elastic'),
        'password': os.getenv('ELASTICSEARCH_PASSWORD', 'changeme'),
        'index_prefix': os.getenv('ELASTICSEARCH_INDEX_PREFIX', 'logs-ecom')
    }
    
    # Logstash Configuration
    LOGSTASH_CONFIG = {
        'host': os.getenv('LOGSTASH_HOST', 'localhost'),
        'port': int(os.getenv('LOGSTASH_PORT', 5000)),
        'beats_port': int(os.getenv('LOGSTASH_BEATS_PORT', 5044))
    }
    
    # Kibana Configuration
    KIBANA_CONFIG = {
        'host': os.getenv('KIBANA_HOST', 'localhost'),
        'port': int(os.getenv('KIBANA_PORT', 5601))
    }
    
    # MongoDB Configuration
    MONGODB_CONFIG = {
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', 27017)),
        'database': os.getenv('MONGODB_DATABASE', 'ecommerce_logs'),
        'user': os.getenv('MONGODB_USER', 'admin'),
        'password': os.getenv('MONGODB_PASSWORD', 'changeme'),
        'uri': os.getenv('MONGODB_URI')
    }
    
    # Redis Configuration
    REDIS_CONFIG = {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'password': os.getenv('REDIS_PASSWORD', ''),
        'db': int(os.getenv('REDIS_DB', 0)),
        'cache_ttl': int(os.getenv('REDIS_CACHE_TTL', 3600))
    }
    
    # Application Configuration
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 104857600))  # 100MB
    ALLOWED_LOG_EXTENSIONS = os.getenv('ALLOWED_LOG_EXTENSIONS', 'log,txt,json,csv').split(',')
    LOGS_RETENTION_DAYS = int(os.getenv('LOGS_RETENTION_DAYS', 90))
    
    # Security Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    
    # Performance Configuration
    WORKER_PROCESSES = int(os.getenv('WORKER_PROCESSES', 4))
    WORKER_THREADS = int(os.getenv('WORKER_THREADS', 2))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 300))
    
    # Monitoring Configuration
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Fraud Detection Configuration
    FRAUD_DETECTION_CONFIG = {
        'enabled': os.getenv('FRAUD_DETECTION_ENABLED', 'True').lower() == 'true',
        'score_threshold': int(os.getenv('FRAUD_SCORE_THRESHOLD', 75)),
        'max_failed_attempts': int(os.getenv('MAX_FAILED_ATTEMPTS', 5))
    }
    
    # Email Notification Configuration
    EMAIL_CONFIG = {
        'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'smtp_user': os.getenv('SMTP_USER', ''),
        'smtp_password': os.getenv('SMTP_PASSWORD', ''),
        'alert_email_to': os.getenv('ALERT_EMAIL_TO', '')
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGODB_CONFIG = {
        **Config.MONGODB_CONFIG,
        'database': 'ecommerce_logs_test'
    }


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration object based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(config_name, DevelopmentConfig)
