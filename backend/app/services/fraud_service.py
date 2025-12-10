"""
Fraud detection service module
Handles fraud detection and suspicious activity monitoring
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """Service for fraud detection"""
    
    def __init__(self, es_service, mongo_service, redis_service):
        """
        Initialize fraud detection service
        
        Args:
            es_service: Elasticsearch service instance
            mongo_service: MongoDB service instance
            redis_service: Redis service instance
        """
        self.es_service = es_service
        self.mongo_service = mongo_service
        self.redis_service = redis_service
        self.fraud_threshold = 75
    
    def detect_fraud(self, transaction_data):
        """
        Detect fraud in transaction data
        
        Args:
            transaction_data: Transaction data to analyze
        
        Returns:
            dict: Fraud detection result
        """
        try:
            fraud_score = 0
            fraud_indicators = []
            
            # Check for unusual amount
            if transaction_data.get('amount', 0) > 10000:
                fraud_score += 20
                fraud_indicators.append('high_amount')
            
            # Check for rapid successive transactions
            user_id = transaction_data.get('user_id')
            if user_id and self._check_rapid_transactions(user_id):
                fraud_score += 25
                fraud_indicators.append('rapid_transactions')
            
            # Check for suspicious location
            if self._check_suspicious_location(transaction_data.get('location')):
                fraud_score += 15
                fraud_indicators.append('suspicious_location')
            
            # Check for mismatched IP
            if self._check_ip_mismatch(transaction_data):
                fraud_score += 30
                fraud_indicators.append('ip_mismatch')
            
            # Check failed attempts
            if user_id and self._check_failed_attempts(user_id):
                fraud_score += 20
                fraud_indicators.append('multiple_failed_attempts')
            
            is_fraud = fraud_score >= self.fraud_threshold
            
            # Log fraud detection
            if is_fraud:
                self._log_fraud_detection(transaction_data, fraud_score, fraud_indicators)
            
            return {
                'is_fraud': is_fraud,
                'fraud_score': fraud_score,
                'indicators': fraud_indicators,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting fraud: {str(e)}")
            raise
    
    def get_suspicious_activities(self, limit=100):
        """
        Get list of suspicious activities
        
        Args:
            limit: Maximum number of activities to return
        
        Returns:
            list: Suspicious activities
        """
        try:
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"fraud_detected": True}},
                            {"range": {"fraud_score": {"gte": 50}}}
                        ]
                    }
                },
                "sort": [
                    {"fraud_score": {"order": "desc"}},
                    {"@timestamp": {"order": "desc"}}
                ]
            }
            
            result = self.es_service.search('logs', query, size=limit)
            activities = [hit['_source'] for hit in result.get('hits', {}).get('hits', [])]
            
            return activities
            
        except Exception as e:
            logger.error(f"Error getting suspicious activities: {str(e)}")
            raise
    
    def get_fraud_statistics(self):
        """
        Get fraud detection statistics
        
        Returns:
            dict: Fraud statistics
        """
        try:
            cache_key = "fraud:stats"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            
            query = {
                "query": {
                    "range": {
                        "@timestamp": {"gte": yesterday}
                    }
                }
            }
            
            agg_query = {
                "fraud_detected": {
                    "filter": {"term": {"fraud_detected": True}}
                },
                "by_indicator": {
                    "terms": {"field": "fraud_indicators.keyword", "size": 10}
                },
                "avg_fraud_score": {
                    "avg": {"field": "fraud_score"}
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggs = result.get('aggregations', {})
            
            stats = {
                'total_fraud_detected_24h': aggs.get('fraud_detected', {}).get('doc_count', 0),
                'avg_fraud_score': aggs.get('avg_fraud_score', {}).get('value', 0),
                'top_indicators': [
                    {'indicator': b['key'], 'count': b['doc_count']}
                    for b in aggs.get('by_indicator', {}).get('buckets', [])
                ]
            }
            
            self.redis_service.set(cache_key, stats, ttl=300)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting fraud statistics: {str(e)}")
            raise
    
    def _check_rapid_transactions(self, user_id):
        """Check for rapid successive transactions"""
        minute_ago = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"user_id": user_id}},
                        {"term": {"log_type": "transaction"}},
                        {"range": {"@timestamp": {"gte": minute_ago}}}
                    ]
                }
            }
        }
        
        result = self.es_service.search('logs', query, size=0)
        count = result.get('hits', {}).get('total', {}).get('value', 0)
        
        return count > 3
    
    def _check_suspicious_location(self, location):
        """Check for suspicious location"""
        if not location:
            return False
        
        # Simple check - can be enhanced with geolocation data
        suspicious_countries = ['XX', 'YY']  # Placeholder
        return location in suspicious_countries
    
    def _check_ip_mismatch(self, transaction_data):
        """Check for IP address mismatch"""
        # Placeholder - implement actual IP validation
        return False
    
    def _check_failed_attempts(self, user_id):
        """Check for multiple failed attempts"""
        hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"user_id": user_id}},
                        {"term": {"status": "failed"}},
                        {"range": {"@timestamp": {"gte": hour_ago}}}
                    ]
                }
            }
        }
        
        result = self.es_service.search('logs', query, size=0)
        count = result.get('hits', {}).get('total', {}).get('value', 0)
        
        return count >= 3
    
    def _log_fraud_detection(self, transaction_data, fraud_score, indicators):
        """Log fraud detection to database"""
        try:
            fraud_log = {
                'transaction_id': transaction_data.get('transaction_id'),
                'user_id': transaction_data.get('user_id'),
                'fraud_score': fraud_score,
                'indicators': indicators,
                'detected_at': datetime.utcnow(),
                'transaction_data': transaction_data
            }
            
            self.mongo_service.insert_one('fraud_detections', fraud_log)
            
            # Also index to Elasticsearch for quick search
            fraud_log['@timestamp'] = fraud_log['detected_at'].isoformat()
            fraud_log['log_type'] = 'fraud'
            fraud_log['fraud_detected'] = True
            fraud_log['fraud_indicators'] = indicators
            
            self.es_service.index_document('logs', fraud_log)
            
        except Exception as e:
            logger.error(f"Error logging fraud detection: {str(e)}")
