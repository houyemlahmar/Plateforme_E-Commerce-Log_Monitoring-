"""
Analytics service module
Provides analytics and insights from logs
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for log analytics"""
    
    def __init__(self, es_service, mongo_service, redis_service):
        """
        Initialize analytics service
        
        Args:
            es_service: Elasticsearch service instance
            mongo_service: MongoDB service instance
            redis_service: Redis service instance
        """
        self.es_service = es_service
        self.mongo_service = mongo_service
        self.redis_service = redis_service
    
    def get_transaction_analytics(self, start_date=None, end_date=None, granularity='daily'):
        """
        Get transaction analytics
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            granularity: Time granularity (hourly, daily, weekly, monthly)
        
        Returns:
            dict: Transaction analytics
        """
        try:
            cache_key = f"analytics:transactions:{start_date}:{end_date}:{granularity}"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            # Build date range query
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"log_type": "transaction"}}
                        ]
                    }
                }
            }
            
            if start_date or end_date:
                date_range = {}
                if start_date:
                    date_range["gte"] = start_date
                if end_date:
                    date_range["lte"] = end_date
                
                query["query"]["bool"]["must"].append({
                    "range": {"@timestamp": date_range}
                })
            
            # Aggregations
            interval_map = {
                'hourly': '1h',
                'daily': '1d',
                'weekly': '1w',
                'monthly': '1M'
            }
            
            agg_query = {
                "timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": interval_map.get(granularity, '1d')
                    },
                    "aggs": {
                        "total_amount": {"sum": {"field": "amount"}},
                        "avg_amount": {"avg": {"field": "amount"}}
                    }
                },
                "payment_methods": {
                    "terms": {"field": "payment_method.keyword"}
                },
                "transaction_status": {
                    "terms": {"field": "status.keyword"}
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggregations = result.get('aggregations', {})
            
            analytics = {
                'timeline': [
                    {
                        'date': bucket['key_as_string'],
                        'count': bucket['doc_count'],
                        'total_amount': bucket.get('total_amount', {}).get('value', 0),
                        'avg_amount': bucket.get('avg_amount', {}).get('value', 0)
                    }
                    for bucket in aggregations.get('timeline', {}).get('buckets', [])
                ],
                'payment_methods': [
                    {'method': b['key'], 'count': b['doc_count']}
                    for b in aggregations.get('payment_methods', {}).get('buckets', [])
                ],
                'transaction_status': [
                    {'status': b['key'], 'count': b['doc_count']}
                    for b in aggregations.get('transaction_status', {}).get('buckets', [])
                ]
            }
            
            self.redis_service.set(cache_key, analytics, ttl=600)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting transaction analytics: {str(e)}")
            raise
    
    def get_error_analytics(self):
        """
        Get error analytics
        
        Returns:
            dict: Error analytics
        """
        try:
            cache_key = "analytics:errors"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            query = {
                "query": {
                    "term": {"log_type": "error"}
                }
            }
            
            agg_query = {
                "error_codes": {
                    "terms": {"field": "error_code", "size": 20}
                },
                "error_types": {
                    "terms": {"field": "error_type.keyword", "size": 10}
                },
                "timeline": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "1h"
                    }
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggregations = result.get('aggregations', {})
            
            analytics = {
                'error_codes': [
                    {'code': b['key'], 'count': b['doc_count']}
                    for b in aggregations.get('error_codes', {}).get('buckets', [])
                ],
                'error_types': [
                    {'type': b['key'], 'count': b['doc_count']}
                    for b in aggregations.get('error_types', {}).get('buckets', [])
                ],
                'timeline': [
                    {'date': b['key_as_string'], 'count': b['doc_count']}
                    for b in aggregations.get('timeline', {}).get('buckets', [])
                ]
            }
            
            self.redis_service.set(cache_key, analytics, ttl=300)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting error analytics: {str(e)}")
            raise
    
    def get_user_behavior_analytics(self):
        """
        Get user behavior analytics
        
        Returns:
            dict: User behavior analytics
        """
        try:
            cache_key = "analytics:user_behavior"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            query = {
                "query": {
                    "term": {"log_type": "user_behavior"}
                }
            }
            
            agg_query = {
                "actions": {
                    "terms": {"field": "action.keyword", "size": 20}
                },
                "pages": {
                    "terms": {"field": "page.keyword", "size": 20}
                },
                "cart_abandonment": {
                    "filter": {"term": {"action": "cart_abandoned"}}
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggregations = result.get('aggregations', {})
            
            analytics = {
                'actions': [
                    {'action': b['key'], 'count': b['doc_count']}
                    for b in aggregations.get('actions', {}).get('buckets', [])
                ],
                'pages': [
                    {'page': b['key'], 'count': b['doc_count']}
                    for b in aggregations.get('pages', {}).get('buckets', [])
                ],
                'cart_abandonment_count': aggregations.get('cart_abandonment', {}).get('doc_count', 0)
            }
            
            self.redis_service.set(cache_key, analytics, ttl=600)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user behavior analytics: {str(e)}")
            raise
    
    def get_trends(self, time_range='7d'):
        """
        Get trends analysis
        
        Args:
            time_range: Time range (e.g., '7d', '30d')
        
        Returns:
            dict: Trends data
        """
        try:
            # Parse time range
            days = int(time_range.replace('d', ''))
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            query = {
                "query": {
                    "range": {
                        "@timestamp": {"gte": start_date}
                    }
                }
            }
            
            agg_query = {
                "log_types_trend": {
                    "terms": {"field": "log_type.keyword"},
                    "aggs": {
                        "over_time": {
                            "date_histogram": {
                                "field": "@timestamp",
                                "calendar_interval": "1d"
                            }
                        }
                    }
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggregations = result.get('aggregations', {})
            
            trends = {
                'time_range': time_range,
                'log_types': [
                    {
                        'type': bucket['key'],
                        'total_count': bucket['doc_count'],
                        'timeline': [
                            {'date': b['key_as_string'], 'count': b['doc_count']}
                            for b in bucket.get('over_time', {}).get('buckets', [])
                        ]
                    }
                    for bucket in aggregations.get('log_types_trend', {}).get('buckets', [])
                ]
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting trends: {str(e)}")
            raise
