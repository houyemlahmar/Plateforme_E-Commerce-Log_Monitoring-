"""
Logs routes module
Handles log collection, upload, and management
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
from app.services.log_service import LogService
from app.utils.validators import validate_log_file, validate_log_data

logger = logging.getLogger(__name__)

bp = Blueprint('logs', __name__, url_prefix='/api/logs')
upload_view_bp = Blueprint('upload_view', __name__)
search_view_bp = Blueprint('search_view', __name__)


@upload_view_bp.route('/upload', methods=['GET'])
def upload_page():
    """
    Render upload HTML page (accessible at /upload without /api prefix)
    
    Returns:
        Rendered upload.html template
    """
    try:
        return render_template('upload.html')
    except Exception as e:
        logger.error(f"Error rendering upload page: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load upload page'
        }), 500


@bp.route('/upload/view', methods=['GET'])
def upload_view():
    """
    Render upload HTML page
    
    Returns:
        Rendered upload.html template
    """
    try:
        return render_template('upload.html')
    except Exception as e:
        logger.error(f"Error rendering upload page: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load upload page'
        }), 500


@bp.route('/upload', methods=['POST'])
def upload_logs():
    """
    Upload log files (CSV or JSON)
    - File validation (size, extension csv/json)
    - Save file to /uploads
    - Extract first 10 lines for preview
    - Insert metadata into MongoDB collection "uploads"
    - Push job ID into Redis queue "ingest_jobs"
    
    Returns:
        JSON response with upload status, preview, and job ID
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'message': 'Please upload a file'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Validate file (size and extension csv/json only)
        is_valid, error_message = validate_log_file(file, current_app.config, allowed_extensions=['csv', 'json'])
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message,
                'message': 'File validation failed'
            }), 400
        
        # Process log file with preview and queue job
        log_service = LogService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        result = log_service.process_upload_with_preview(file)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'data': {
                'file_id': result['file_id'],
                'job_id': result['job_id'],
                'filename': result['filename'],
                'file_size': result['file_size'],
                'file_type': result['file_type'],
                'preview': result['preview'],
                'preview_lines': len(result['preview']),
                'total_lines': result['total_lines'],
                'uploaded_at': result['uploaded_at']
            }
        }), 201
        
    except ValueError as e:
        logger.error(f"Validation error uploading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Invalid file data'
        }), 400
    except IOError as e:
        logger.error(f"IO error uploading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'File system error',
            'message': 'Unable to save file'
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error uploading logs: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'Failed to upload logs'
        }), 500


@bp.route('/ingest', methods=['POST'])
def ingest_logs():
    """
    Ingest logs via JSON payload
    
    Returns:
        JSON response with ingestion status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate log data
        is_valid, error_message = validate_log_data(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Process logs
        log_service = LogService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        result = log_service.ingest_logs(data)
        
        return jsonify({
            'message': 'Logs ingested successfully',
            'records_processed': result['records_processed']
        }), 201
        
    except Exception as e:
        logger.error(f"Error ingesting logs: {str(e)}")
        return jsonify({'error': 'Failed to ingest logs'}), 500


@bp.route('/types', methods=['GET'])
def get_log_types():
    """
    Get available log types
    
    Returns:
        JSON response with log types
    """
    try:
        log_types = [
            {
                'id': 'transaction',
                'name': 'Transaction Logs',
                'description': 'Payment, order, and refund logs'
            },
            {
                'id': 'error',
                'name': 'Error Logs',
                'description': 'Application errors, 404, 500, timeouts'
            },
            {
                'id': 'user_behavior',
                'name': 'User Behavior Logs',
                'description': 'Navigation, cart actions, abandonment'
            },
            {
                'id': 'performance',
                'name': 'Performance Logs',
                'description': 'API response times, database latency'
            },
            {
                'id': 'fraud',
                'name': 'Fraud Detection Logs',
                'description': 'Suspicious payment attempts, bot detection'
            }
        ]
        
        return jsonify({'log_types': log_types}), 200
        
    except Exception as e:
        logger.error(f"Error fetching log types: {str(e)}")
        return jsonify({'error': 'Failed to fetch log types'}), 500


@bp.route('/uploads/recent', methods=['GET'])
def get_recent_uploads():
    """
    Get recent file uploads from MongoDB
    
    Query Parameters:
        limit (int): Number of uploads to return (default: 10)
    
    Returns:
        JSON response with recent uploads
        
    Example:
        GET /api/logs/uploads/recent?limit=10
        
        Response:
        {
            "success": true,
            "uploads": [
                {
                    "job_id": "abc123",
                    "filename": "logs.json",
                    "status": "completed",
                    "uploaded_at": "2025-12-25T10:30:00"
                }
            ],
            "count": 10
        }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get recent uploads from MongoDB uploads collection
        uploads = list(current_app.mongo_service.db.uploads
            .find({}, {
                'job_id': 1,
                'filename': 1,
                'status': 1,
                'uploaded_at': 1,
                '_id': 0
            })
            .sort('uploaded_at', -1)
            .limit(limit))
        
        # Convert datetime to string for JSON serialization
        for upload in uploads:
            if 'uploaded_at' in upload:
                upload['uploaded_at'] = upload['uploaded_at'].isoformat() if hasattr(upload['uploaded_at'], 'isoformat') else str(upload['uploaded_at'])
        
        return jsonify({
            'success': True,
            'uploads': uploads,
            'count': len(uploads)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching recent uploads: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch recent uploads',
            'details': str(e)
        }), 500


@bp.route('/recent', methods=['GET'])
def get_recent_logs():
    """
    Get recent logs
    
    Query Parameters:
        - limit: Number of logs to return (default: 100)
        - log_type: Filter by log type
    
    Returns:
        JSON response with recent logs
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        log_type = request.args.get('log_type', None)
        
        log_service = LogService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        logs = log_service.get_recent_logs(limit=limit, log_type=log_type)
        
        return jsonify({
            'logs': logs,
            'count': len(logs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching recent logs: {str(e)}")
        return jsonify({'error': 'Failed to fetch recent logs'}), 500


@bp.route('/stats', methods=['GET'])
def get_logs_stats():
    """
    Get logs statistics
    
    Returns:
        JSON response with logs statistics
    """
    try:
        log_service = LogService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        stats = log_service.get_logs_statistics()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error fetching logs stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch logs statistics'}), 500


# ============================================
# SEARCH ROUTES
# ============================================

@search_view_bp.route('/search', methods=['GET'])
def search_page():
    """
    Render search HTML page
    
    Returns:
        Rendered search.html template
    """
    try:
        return render_template('search.html')
    except Exception as e:
        logger.error(f"Error rendering search page: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load search page'
        }), 500


@search_view_bp.route('/results', methods=['GET'])
def results_page():
    """
    Render results HTML page
    
    Returns:
        Rendered results.html template
    """
    try:
        return render_template('results.html')
    except Exception as e:
        logger.error(f"Error rendering results page: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load results page'
        }), 500


@bp.route('/search', methods=['POST'])
def search_logs():
    """
    Search logs with filters
    
    Request Body:
        {
            "query": "search text",
            "level": "ERROR",
            "service": "payment",
            "date_from": "2025-12-25 00:00",
            "date_to": "2025-12-25 23:59",
            "size": 100
        }
    
    Returns:
        JSON response with search results
    """
    try:
        filters = request.get_json()
        
        # Build Elasticsearch query
        query = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "size": filters.get('size', 100),
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        # Add text search if provided
        if filters.get('query'):
            query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": filters['query'],
                    "fields": ["message", "service", "event.original"],
                    "type": "best_fields"
                }
            })
        
        # Add level filter
        if filters.get('level'):
            query["query"]["bool"]["must"].append({
                "match": {"level": filters['level']}
            })
        
        # Add service filter
        if filters.get('service'):
            query["query"]["bool"]["must"].append({
                "match": {"service": filters['service']}
            })
        
        # Add date range filter
        if filters.get('date_from') or filters.get('date_to'):
            date_range = {}
            if filters.get('date_from'):
                # Convert to ISO format: "2025-12-24 22:03" -> "2025-12-24T22:03:00"
                date_from = filters['date_from'].replace(' ', 'T')
                if len(date_from) == 16:  # Format: "2025-12-24T22:03"
                    date_from += ":00"
                date_range['gte'] = date_from
            if filters.get('date_to'):
                # Convert to ISO format: "2025-12-24 22:03" -> "2025-12-24T22:03:59"
                date_to = filters['date_to'].replace(' ', 'T')
                if len(date_to) == 16:  # Format: "2025-12-24T22:03"
                    date_to += ":59"
                date_range['lte'] = date_to
            
            query["query"]["bool"]["must"].append({
                "range": {"@timestamp": date_range}
            })
        
        # If no filters, match all
        if not query["query"]["bool"]["must"]:
            query["query"] = {"match_all": {}}
        
        # Execute search
        result = current_app.es_service.search('logs', query)
        
        # Extract results
        hits = result.get('hits', {}).get('hits', [])
        results = [hit['_source'] for hit in hits]
        
        return jsonify({
            'success': True,
            'results': results,
            'total': result.get('hits', {}).get('total', {}).get('value', 0),
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching logs: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'details': str(e)
        }), 500


@bp.route('/search/services', methods=['GET'])
def get_services():
    """
    Get list of available services
    
    Returns:
        JSON response with services list
    """
    try:
        # Get unique services from Elasticsearch
        query = {
            "size": 0,
            "aggs": {
                "services": {
                    "terms": {
                        "field": "service",
                        "size": 100
                    }
                }
            }
        }
        
        result = current_app.es_service.search('logs', query)
        buckets = result.get('aggregations', {}).get('services', {}).get('buckets', [])
        services = [bucket['key'] for bucket in buckets]
        
        return jsonify({
            'success': True,
            'services': services
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching services: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch services'
        }), 500


@bp.route('/search/save', methods=['POST'])
def save_search():
    """
    Save a search query to MongoDB
    
    Request Body:
        {
            "name": "My Search",
            "filters": {...}
        }
    
    Returns:
        JSON response with save status
    """
    try:
        data = request.get_json()
        name = data.get('name', '')
        filters = data.get('filters', {})
        
        # Create search document
        search_doc = {
            'name': name,
            'filters': filters,
            'created_at': datetime.utcnow(),
            'user': 'default'  # Can be replaced with actual user auth
        }
        
        # Save to MongoDB
        result = current_app.mongo_service.insert_one('saved_searches', search_doc)
        
        return jsonify({
            'success': True,
            'search_id': str(result),
            'message': 'Search saved successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error saving search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to save search'
        }), 500


@bp.route('/search/recent', methods=['GET'])
def get_recent_searches():
    """
    Get recent saved searches
    
    Query Parameters:
        - limit: Number of searches to return (default: 10)
    
    Returns:
        JSON response with recent searches
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get recent searches from MongoDB
        searches = list(current_app.mongo_service.db.saved_searches
            .find({}, {'_id': 0})
            .sort('created_at', -1)
            .limit(limit))
        
        # Convert datetime to string
        for search in searches:
            if 'created_at' in search:
                search['created_at'] = search['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'searches': searches,
            'count': len(searches)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching recent searches: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch recent searches'
        }), 500
