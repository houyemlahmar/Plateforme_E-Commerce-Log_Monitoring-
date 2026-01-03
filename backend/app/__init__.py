"""
Application factory module
Creates and configures the Flask application
"""

import logging
from flask import Flask, jsonify, render_template, redirect
from flask_cors import CORS
from flasgger import Swagger
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
    
    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "E-Commerce Logs Platform API",
            "description": "API sécurisée avec JWT pour la gestion et l'analyse de logs e-commerce. Plateforme complète de monitoring avec Elasticsearch, MongoDB et Redis.",
            "version": "2.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@ecommerce-logs.com"
            }
        },
        "host": "localhost:5001",
        "basePath": "/",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "security": [
            {"Bearer": []}
        ],
        "tags": [
            {
                "name": "Authentication",
                "description": "Endpoints d'authentification JWT (login, register, refresh)"
            },
            {
                "name": "Logs",
                "description": "Endpoints de gestion des logs (upload, search, retrieve)"
            },
            {
                "name": "Analytics",
                "description": "Endpoints d'analytics et métriques"
            },
            {
                "name": "Dashboard",
                "description": "Endpoints pour dashboard et visualisations"
            }
        ]
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
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
    
    # Root endpoint - redirect to login
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint - redirect to login"""
        return redirect('/login')
    
    # Login page
    @app.route('/login', methods=['GET'])
    def login_page():
        """Render login page"""
        return render_template('login.html')
    
    # Profile page
    @app.route('/profile', methods=['GET'])
    def profile_page():
        """Render profile page"""
        return render_template('profile.html')
    
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
        search_routes,
        auth_routes
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
    app.register_blueprint(auth_routes.bp)
    
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
    # Initialize Elasticsearch connection (optional)
    try:
        from app.services.elasticsearch_service import ElasticsearchService
        es_service = ElasticsearchService(app.config['ELASTICSEARCH_CONFIG'])
        app.es_service = es_service
    except Exception as e:
        logger.warning(f"Elasticsearch not available: {str(e)}")
        app.es_service = None
    
    # Initialize MongoDB connection (required for auth)
    try:
        from app.services.mongodb_service import MongoDBService
        mongo_service = MongoDBService(app.config['MONGODB_CONFIG'])
        if mongo_service.client is None:
            logger.warning("MongoDB not connected - authentication features will not work")
        app.mongo_service = mongo_service
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB: {str(e)}")
        app.mongo_service = None
    
    # Initialize Redis connection (optional)
    try:
        from app.services.redis_service import RedisService
        redis_service = RedisService(app.config['REDIS_CONFIG'])
        app.redis_service = redis_service
    except Exception as e:
        logger.warning(f"Redis not available: {str(e)}")
        app.redis_service = None
    
    logger.info("Extensions initialized successfully")
