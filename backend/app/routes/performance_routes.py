"""
Performance monitoring routes module
Handles performance metrics and monitoring
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from app.services.performance_service import PerformanceService

logger = logging.getLogger(__name__)

bp = Blueprint('performance', __name__, url_prefix='/api/performance')


@bp.route('/metrics', methods=['GET'])
def get_performance_metrics():
    """
    Get performance metrics
    
    Returns:
        JSON response with performance metrics
    """
    try:
        performance_service = PerformanceService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        metrics = performance_service.get_performance_metrics()
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch performance metrics'}), 500


@bp.route('/api-response-times', methods=['GET'])
def get_api_response_times():
    """
    Get API response times analysis
    
    Returns:
        JSON response with API response times
    """
    try:
        performance_service = PerformanceService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        response_times = performance_service.get_api_response_times()
        
        return jsonify(response_times), 200
        
    except Exception as e:
        logger.error(f"Error fetching API response times: {str(e)}")
        return jsonify({'error': 'Failed to fetch API response times'}), 500


@bp.route('/database-latency', methods=['GET'])
def get_database_latency():
    """
    Get database latency metrics
    
    Returns:
        JSON response with database latency
    """
    try:
        performance_service = PerformanceService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        latency = performance_service.get_database_latency()
        
        return jsonify(latency), 200
        
    except Exception as e:
        logger.error(f"Error fetching database latency: {str(e)}")
        return jsonify({'error': 'Failed to fetch database latency'}), 500
