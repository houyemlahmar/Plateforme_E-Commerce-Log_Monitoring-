"""
Dashboard routes module
Provides dashboard data and metrics
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@bp.route('/overview', methods=['GET'])
def get_dashboard_overview():
    """
    Get dashboard overview data
    
    Returns:
        JSON response with dashboard overview
    """
    try:
        dashboard_service = DashboardService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        overview = dashboard_service.get_overview()
        
        return jsonify(overview), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard overview'}), 500


@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get key metrics
    
    Returns:
        JSON response with key metrics
    """
    try:
        dashboard_service = DashboardService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        metrics = dashboard_service.get_key_metrics()
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500


@bp.route('/charts', methods=['GET'])
def get_chart_data():
    """
    Get chart data for visualizations
    
    Query Parameters:
        - chart_type: Type of chart (transactions, errors, performance, etc.)
    
    Returns:
        JSON response with chart data
    """
    try:
        chart_type = request.args.get('chart_type', 'transactions')
        
        dashboard_service = DashboardService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        chart_data = dashboard_service.get_chart_data(chart_type)
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching chart data: {str(e)}")
        return jsonify({'error': 'Failed to fetch chart data'}), 500
