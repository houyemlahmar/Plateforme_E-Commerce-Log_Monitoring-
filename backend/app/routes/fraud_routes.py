"""
Fraud detection routes module
Handles fraud detection and suspicious activity monitoring
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from app.services.fraud_service import FraudDetectionService

logger = logging.getLogger(__name__)

bp = Blueprint('fraud', __name__, url_prefix='/api/fraud')


@bp.route('/detect', methods=['POST'])
def detect_fraud():
    """
    Detect fraud in transaction data
    
    Returns:
        JSON response with fraud detection results
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        fraud_service = FraudDetectionService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        result = fraud_service.detect_fraud(data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error detecting fraud: {str(e)}")
        return jsonify({'error': 'Failed to detect fraud'}), 500


@bp.route('/suspicious-activities', methods=['GET'])
def get_suspicious_activities():
    """
    Get list of suspicious activities
    
    Returns:
        JSON response with suspicious activities
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        
        fraud_service = FraudDetectionService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        activities = fraud_service.get_suspicious_activities(limit=limit)
        
        return jsonify({
            'activities': activities,
            'count': len(activities)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching suspicious activities: {str(e)}")
        return jsonify({'error': 'Failed to fetch suspicious activities'}), 500


@bp.route('/stats', methods=['GET'])
def get_fraud_stats():
    """
    Get fraud detection statistics
    
    Returns:
        JSON response with fraud statistics
    """
    try:
        fraud_service = FraudDetectionService(
            current_app.es_service,
            current_app.mongo_service,
            current_app.redis_service
        )
        
        stats = fraud_service.get_fraud_statistics()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error fetching fraud stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch fraud statistics'}), 500
