"""
Dashboard routes module
Provides dashboard data and metrics
"""

import logging
from flask import Blueprint, request, jsonify, current_app, render_template
from app.services.dashboard_service import DashboardService
from config import get_config

logger = logging.getLogger(__name__)

# Create two blueprints: one for HTML views, one for API
bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
dashboard_view_bp = Blueprint('dashboard_view', __name__)


@dashboard_view_bp.route('/kibana', methods=['GET'])
def kibana_view():
    """
    Render Kibana dashboard embedded in iframe (accessible at /kibana)
    
    Returns:
        Rendered Kibana iframe page with security headers
    """
    try:
        # Get Kibana URL from config
        config = get_config()
        kibana_url = config.KIBANA_URL if hasattr(config, 'KIBANA_URL') else 'http://localhost:5601'
        
        # Dashboard ID from the imported dashboard
        dashboard_id = 'ecommerce-logs-dashboard'
        kibana_dashboard_url = f"{kibana_url}/app/dashboards#/view/{dashboard_id}"
        
        # Render template
        response = render_template('kibana.html', kibana_url=kibana_dashboard_url)
        
        # Note: X-Frame-Options headers are intentionally not set here
        # to allow Kibana iframe embedding. Ensure Kibana is configured
        # with server.cors.enabled: true in kibana.yml
        
        return response
        
    except Exception as e:
        logger.error(f"Error rendering Kibana page: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load Kibana dashboard'
        }), 500


@dashboard_view_bp.route('/dashboard', methods=['GET'])
def dashboard_html():
    """
    Render dashboard HTML page (accessible at /dashboard)
    
    Query Parameters:
        range (str): Time range ('24h', '7d', '30d') - default: '24h'
    
    Returns:
        Rendered HTML dashboard
    """
    try:
        # Get time range from query params
        time_range = request.args.get('range', '24h')
        
        # Initialize service
        dashboard_service = DashboardService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        # Fetch KPIs
        kpis = dashboard_service.get_kpis(time_range)
        
        # Get Kibana URL from config
        config = get_config()
        kibana_url = config.KIBANA_URL if hasattr(config, 'KIBANA_URL') else 'http://localhost:5601'
        
        # Prepare context for template
        context = {
            'kpis': kpis,
            'kibana_url': kibana_url,
            'logs_per_hour': kpis.get('logs_per_hour', []),
            'log_levels_distribution': kpis.get('log_levels_distribution', {}),
            'last_update': kpis.get('last_update', '')
        }
        
        return render_template('dashboard.html', **context)
    
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        # Return error template with empty data
        return render_template('dashboard.html',
                             kpis={},
                             kibana_url='http://localhost:5601',
                             logs_per_hour=[],
                             log_levels_distribution={},
                             last_update='Error loading data'), 500


@bp.route('/view', methods=['GET'])
def dashboard_view():
    """
    Alternative route for dashboard view (accessible at /api/dashboard/view)
    
    Query Parameters:
        range (str): Time range ('24h', '7d', '30d') - default: '24h'
    
    Returns:
        Rendered HTML dashboard
    """
    return dashboard_html()


@bp.route('/kpis', methods=['GET'])
def get_dashboard_kpis():
    """
    Get dashboard KPIs as JSON (for AJAX refresh)
    
    Query Parameters:
        range (str): Time range ('24h', '7d', '30d') - default: '24h'
    
    Returns:
        JSON response with all KPI data
    """
    try:
        # Get time range
        time_range = request.args.get('range', '24h')
        
        # Validate
        if time_range not in ['24h', '7d', '30d']:
            return jsonify({
                'success': False,
                'error': 'Invalid time range. Must be 24h, 7d, or 30d'
            }), 400
        
        # Initialize service
        dashboard_service = DashboardService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        # Fetch KPIs
        kpis = dashboard_service.get_kpis(time_range)
        
        return jsonify(kpis), 200
    
    except Exception as e:
        logger.error(f"Error fetching dashboard KPIs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch KPIs',
            'details': str(e)
        }), 500


@bp.route('/health', methods=['GET'])
def get_system_health():
    """
    Check health status of all systems
    
    Returns:
        JSON with health status
    """
    try:
        dashboard_service = DashboardService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        health = dashboard_service.get_system_health()
        
        return jsonify({
            'success': True,
            'health': health
        }), 200
    
    except Exception as e:
        logger.error(f"Error checking system health: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to check health'
        }), 500


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
