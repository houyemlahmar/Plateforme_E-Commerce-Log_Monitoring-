"""
Analytics routes module
Provides analytical endpoints for log data
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@bp.route('/transactions', methods=['GET'])
def get_transaction_analytics():
    """
    Get transaction analytics
    
    Query Parameters:
        - start_date: Start date (ISO format)
        - end_date: End date (ISO format)
        - granularity: hourly, daily, weekly, monthly
    
    Returns:
        JSON response with transaction analytics
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        granularity = request.args.get('granularity', 'daily')
        
        analytics_service = AnalyticsService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        analytics = analytics_service.get_transaction_analytics(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity
        )
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error fetching transaction analytics: {str(e)}")
        return jsonify({'error': 'Failed to fetch transaction analytics'}), 500


@bp.route('/errors', methods=['GET'])
def get_error_analytics():
    """
    Get error analytics
    
    Returns:
        JSON response with error analytics
    """
    try:
        analytics_service = AnalyticsService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        analytics = analytics_service.get_error_analytics()
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error fetching error analytics: {str(e)}")
        return jsonify({'error': 'Failed to fetch error analytics'}), 500


@bp.route('/user-behavior', methods=['GET'])
def get_user_behavior_analytics():
    """
    Get user behavior analytics
    
    Returns:
        JSON response with user behavior analytics
    """
    try:
        analytics_service = AnalyticsService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        analytics = analytics_service.get_user_behavior_analytics()
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error fetching user behavior analytics: {str(e)}")
        return jsonify({'error': 'Failed to fetch user behavior analytics'}), 500


@bp.route('/trends', methods=['GET'])
def get_trends():
    """
    Get trends analysis
    
    Returns:
        JSON response with trends data
    """
    try:
        time_range = request.args.get('time_range', '7d')
        
        analytics_service = AnalyticsService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        trends = analytics_service.get_trends(time_range=time_range)
        
        return jsonify(trends), 200
        
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        return jsonify({'error': 'Failed to fetch trends'}), 500
