"""
Search routes module
Provides search functionality across logs
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)

bp = Blueprint('search', __name__, url_prefix='/api/search')


@bp.route('/', methods=['GET'])
def search_logs():
    """
    Search logs using Elasticsearch
    
    Query Parameters:
        - q: Search query
        - log_type: Filter by log type
        - from: Start date
        - to: End date
        - size: Number of results (default: 100)
    
    Returns:
        JSON response with search results
    """
    try:
        query = request.args.get('q', '')
        log_type = request.args.get('log_type')
        start_date = request.args.get('from')
        end_date = request.args.get('to')
        size = request.args.get('size', 100, type=int)
        
        search_service = SearchService(
            current_app.es_service,
            current_app.redis_service
        )
        
        results = search_service.search(
            query=query,
            log_type=log_type,
            start_date=start_date,
            end_date=end_date,
            size=size
        )
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error searching logs: {str(e)}")
        return jsonify({'error': 'Failed to search logs'}), 500


@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    Get autocomplete suggestions
    
    Query Parameters:
        - q: Partial query
    
    Returns:
        JSON response with autocomplete suggestions
    """
    try:
        query = request.args.get('q', '')
        
        search_service = SearchService(
            current_app.es_service,
            current_app.redis_service
        )
        
        suggestions = search_service.get_autocomplete_suggestions(query)
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        logger.error(f"Error getting autocomplete suggestions: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions'}), 500
