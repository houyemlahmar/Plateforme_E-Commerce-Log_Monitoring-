"""
Logs routes module
Handles log collection, upload, and management
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.log_service import LogService
from app.utils.validators import validate_log_file, validate_log_data

logger = logging.getLogger(__name__)

bp = Blueprint('logs', __name__, url_prefix='/api/logs')


@bp.route('/upload', methods=['POST'])
def upload_logs():
    """
    Upload log files
    
    Returns:
        JSON response with upload status
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        is_valid, error_message = validate_log_file(file, current_app.config)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Process log file
        log_service = LogService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        result = log_service.process_log_file(file)
        
        return jsonify({
            'message': 'Logs uploaded successfully',
            'records_processed': result['records_processed'],
            'file_id': result['file_id']
        }), 201
        
    except Exception as e:
        logger.error(f"Error uploading logs: {str(e)}")
        return jsonify({'error': 'Failed to upload logs'}), 500


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
