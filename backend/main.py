"""
Main entry point for the Flask application
Plateforme de Monitoring et Analyse de Logs E-Commerce
"""

import os
import logging
from flask import Flask
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Create and run the Flask application"""
    try:
        # Create Flask app
        app = create_app()
        
        # Get configuration from environment
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Starting Flask application on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # Run the application (use_reloader=False to fix Windows socket issue)
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
