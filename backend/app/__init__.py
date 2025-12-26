"""
Application factory module
Creates and configures the Flask application
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config

logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """
    Application factory function
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Enable CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information"""
        return jsonify({
            'service': 'E-Commerce Logs Platform',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'logs': '/api/logs',
                'analytics': '/api/analytics',
                'dashboard': '/api/dashboard',
                'fraud': '/api/fraud',
                'performance': '/api/performance',
                'search': '/api/search'
            },
            'documentation': 'See /docs for API documentation'
        }), 200
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'ecommerce-logs-platform',
            'version': '1.0.0'
        }), 200
    
    logger.info("Flask application created successfully")
    return app


def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes import (
        logs_routes,
        analytics_routes,
        dashboard_routes,
        fraud_routes,
        performance_routes,
        search_routes
    )
    
    app.register_blueprint(logs_routes.bp)
    app.register_blueprint(logs_routes.upload_view_bp)  # Register upload page route
    app.register_blueprint(logs_routes.search_view_bp)  # Register search page route
    app.register_blueprint(analytics_routes.bp)
    app.register_blueprint(dashboard_routes.bp)
    app.register_blueprint(dashboard_routes.dashboard_view_bp)  # Register HTML dashboard route
    app.register_blueprint(fraud_routes.bp)
    app.register_blueprint(performance_routes.bp)
    app.register_blueprint(search_routes.bp)
    
    logger.info("Blueprints registered successfully")


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    logger.info("Error handlers registered successfully")


def initialize_extensions(app):
    """Initialize Flask extensions and database connections"""
    try:
        # Initialize Elasticsearch connection
        from app.services.elasticsearch_service import ElasticsearchService
        es_service = ElasticsearchService(app.config['ELASTICSEARCH_CONFIG'])
        app.es_service = es_service
        
        # Initialize MongoDB connection
        from app.services.mongodb_service import MongoDBService
        mongo_service = MongoDBService(app.config['MONGODB_CONFIG'])
        app.mongo_service = mongo_service
        
        # Initialize Redis connection
        from app.services.redis_service import RedisService
        redis_service = RedisService(app.config['REDIS_CONFIG'])
        app.redis_service = redis_service
        
        logger.info("Extensions initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {str(e)}")
        raise
