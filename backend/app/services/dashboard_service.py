"""
Dashboard service module
Provides dashboard data and metrics
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard operations"""
    
    def __init__(self, es_service, mongo_service, redis_service):
        """
        Initialize dashboard service
        
        Args:
            es_service: Elasticsearch service instance
            mongo_service: MongoDB service instance
            redis_service: Redis service instance
        """
        self.es_service = es_service
        self.mongo_service = mongo_service
        self.redis_service = redis_service
    
    def get_overview(self):
        """
        Get dashboard overview
        
        Returns:
            dict: Dashboard overview data
        """
        try:
            cache_key = "dashboard:overview"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            # Get counts for last 24 hours
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            
            query = {
                "query": {
                    "range": {
                        "@timestamp": {"gte": yesterday}
                    }
                }
            }
            
            agg_query = {
                "log_types": {
                    "terms": {"field": "log_type.keyword"}
                },
                "errors": {
                    "filter": {"term": {"log_type": "error"}}
                },
                "transactions": {
                    "filter": {"term": {"log_type": "transaction"}},
                    "aggs": {
                        "total_amount": {"sum": {"field": "amount"}}
                    }
                },
                "fraud_alerts": {
                    "filter": {"term": {"fraud_detected": True}}
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggs = result.get('aggregations', {})
            
            overview = {
                'total_logs_24h': result.get('hits', {}).get('total', {}).get('value', 0),
                'errors_24h': aggs.get('errors', {}).get('doc_count', 0),
                'transactions_24h': aggs.get('transactions', {}).get('doc_count', 0),
                'transaction_amount_24h': aggs.get('transactions', {}).get('total_amount', {}).get('value', 0),
                'fraud_alerts_24h': aggs.get('fraud_alerts', {}).get('doc_count', 0),
                'log_types_distribution': [
                    {'type': b['key'], 'count': b['doc_count']}
                    for b in aggs.get('log_types', {}).get('buckets', [])
                ]
            }
            
            self.redis_service.set(cache_key, overview, ttl=300)
            return overview
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {str(e)}")
            raise
    
    def get_key_metrics(self):
        """
        Get key metrics
        
        Returns:
            dict: Key metrics
        """
        try:
            cache_key = "dashboard:metrics"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            # Get metrics for various time ranges
            now = datetime.utcnow()
            hour_ago = (now - timedelta(hours=1)).isoformat()
            day_ago = (now - timedelta(days=1)).isoformat()
            week_ago = (now - timedelta(days=7)).isoformat()
            
            metrics = {
                'realtime': self._get_count_for_period(hour_ago),
                'last_24h': self._get_count_for_period(day_ago),
                'last_7d': self._get_count_for_period(week_ago),
                'error_rate': self._calculate_error_rate(day_ago),
                'avg_response_time': self._get_avg_response_time(hour_ago)
            }
            
            self.redis_service.set(cache_key, metrics, ttl=300)
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting key metrics: {str(e)}")
            raise
    
    def get_chart_data(self, chart_type):
        """
        Get chart data for visualizations
        
        Args:
            chart_type: Type of chart
        
        Returns:
            dict: Chart data
        """
        try:
            cache_key = f"dashboard:chart:{chart_type}"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            if chart_type == 'transactions':
                data = self._get_transactions_chart_data()
            elif chart_type == 'errors':
                data = self._get_errors_chart_data()
            elif chart_type == 'performance':
                data = self._get_performance_chart_data()
            else:
                data = {'error': 'Unknown chart type'}
            
            self.redis_service.set(cache_key, data, ttl=300)
            return data
            
        except Exception as e:
            logger.error(f"Error getting chart data: {str(e)}")
            raise
    
    def _get_count_for_period(self, start_date):
        """Get log count for a time period"""
        query = {
            "query": {
                "range": {
                    "@timestamp": {"gte": start_date}
                }
            }
        }
        result = self.es_service.search('logs', query, size=0)
        return result.get('hits', {}).get('total', {}).get('value', 0)
    
    def _calculate_error_rate(self, start_date):
        """Calculate error rate"""
        query = {
            "query": {
                "range": {
                    "@timestamp": {"gte": start_date}
                }
            }
        }
        
        agg_query = {
            "errors": {
                "filter": {"term": {"log_type": "error"}}
            }
        }
        
        result = self.es_service.search('logs', query, size=0)
        total = result.get('hits', {}).get('total', {}).get('value', 0)
        errors = result.get('aggregations', {}).get('errors', {}).get('doc_count', 0)
        
        return (errors / total * 100) if total > 0 else 0
    
    def _get_avg_response_time(self, start_date):
        """Get average response time"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": start_date}}},
                        {"term": {"log_type": "performance"}}
                    ]
                }
            }
        }
        
        agg_query = {
            "avg_response": {
                "avg": {"field": "response_time"}
            }
        }
        
        result = self.es_service.search('logs', query, size=0)
        return result.get('aggregations', {}).get('avg_response', {}).get('value', 0)
    
    def _get_transactions_chart_data(self):
        """Get transactions chart data"""
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": yesterday}}},
                        {"term": {"log_type": "transaction"}}
                    ]
                }
            }
        }
        
        agg_query = {
            "over_time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "1h"
                },
                "aggs": {
                    "total_amount": {"sum": {"field": "amount"}}
                }
            }
        }
        
        result = self.es_service.search('logs', query, size=0)
        buckets = result.get('aggregations', {}).get('over_time', {}).get('buckets', [])
        
        return {
            'labels': [b['key_as_string'] for b in buckets],
            'data': [b['doc_count'] for b in buckets],
            'amounts': [b.get('total_amount', {}).get('value', 0) for b in buckets]
        }
    
    def _get_errors_chart_data(self):
        """Get errors chart data"""
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": yesterday}}},
                        {"term": {"log_type": "error"}}
                    ]
                }
            }
        }
        
        agg_query = {
            "by_code": {
                "terms": {"field": "error_code", "size": 10}
            }
        }
        
        result = self.es_service.search('logs', query, size=0)
        buckets = result.get('aggregations', {}).get('by_code', {}).get('buckets', [])
        
        return {
            'labels': [b['key'] for b in buckets],
            'data': [b['doc_count'] for b in buckets]
        }
    
    def _get_performance_chart_data(self):
        """Get performance chart data"""
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": yesterday}}},
                        {"term": {"log_type": "performance"}}
                    ]
                }
            }
        }
        
        agg_query = {
            "over_time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "1h"
                },
                "aggs": {
                    "avg_response": {"avg": {"field": "response_time"}}
                }
            }
        }
        
        result = self.es_service.search('logs', query, size=0)
        buckets = result.get('aggregations', {}).get('over_time', {}).get('buckets', [])
        
        return {
            'labels': [b['key_as_string'] for b in buckets],
            'data': [b.get('avg_response', {}).get('value', 0) for b in buckets]
        }
