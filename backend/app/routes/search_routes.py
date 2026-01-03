"""
Search routes module
Provides search functionality across logs
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from app.services.search_service import SearchService
from app.utils.jwt_utils import token_required, role_hierarchy_required

logger = logging.getLogger(__name__)

bp = Blueprint('search', __name__, url_prefix='/api/search')


@bp.route('/', methods=['GET'])
@token_required
@role_hierarchy_required('viewer')
def search_logs():
    """
    Search logs using Elasticsearch Query Builder - Requires viewer role or higher
    
    Query Parameters:
        - q: Search query (free text)
        - log_type: Filter by log type (transaction, error, fraud, performance, user_behavior)
        - level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - service: Filter by service name
        - date_from: Start date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        - date_to: End date (ISO 8601)
        - user_id: Filter by user ID
        - min_amount: Minimum amount filter (for transactions)
        - max_amount: Maximum amount filter (for transactions)
        - page: Page number (default: 1)
        - size: Number of results per page (default: 20, max: 1000)
        - sort_field: Field to sort by (default: @timestamp)
        - sort_order: Sort order - asc or desc (default: desc)
    
    Returns:
        JSON response with search results and pagination metadata
        
    Example:
        GET /api/search?q=timeout&level=ERROR&service=payment&date_from=2025-12-01&page=2&size=50
    """
    try:
        # Extract query parameters with defaults
        query = request.args.get('q', '')
        log_type = request.args.get('log_type')
        level = request.args.get('level')
        service = request.args.get('service')
        date_from = request.args.get('date_from') or request.args.get('from')  # Support both
        date_to = request.args.get('date_to') or request.args.get('to')  # Support both
        user_id = request.args.get('user_id')
        
        # Amount filters (with validation)
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        
        # Sorting
        sort_field = request.args.get('sort_field', '@timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Create search service
        search_service = SearchService(
            current_app.es_service,
            current_app.redis_service,
            current_app.mongo_service if hasattr(current_app, 'mongo_service') else None
        )
        
        # Get user IP for history tracking
        user_ip = request.remote_addr
        
        # Execute search
        results = search_service.search(
            query=query,
            log_type=log_type,
            level=level,
            service=service,
            start_date=date_from,
            end_date=date_to,
            user_id=user_id,
            min_amount=min_amount,
            max_amount=max_amount,
            page=page,
            size=size,
            sort_field=sort_field,
            sort_order=sort_order,
            user_ip=user_ip
        )
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to search logs',
            'message': str(e)
        }), 500


@bp.route('/autocomplete', methods=['GET'])
@token_required
@role_hierarchy_required('viewer')
def autocomplete():
    """
    Get autocomplete suggestions - Requires viewer role or higher
    
    Query Parameters:
        - q: Partial query
    
    Returns:
        JSON response with autocomplete suggestions
    """
    try:
        query = request.args.get('q', '')
        
        search_service = SearchService(
            current_app.es_service,
            current_app.redis_service,
            current_app.mongo_service if hasattr(current_app, 'mongo_service') else None
        )
        
        suggestions = search_service.get_autocomplete_suggestions(query)
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        logger.error(f"Error getting autocomplete suggestions: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions'}), 500
