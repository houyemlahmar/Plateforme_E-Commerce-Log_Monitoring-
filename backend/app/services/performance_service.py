"""
Performance monitoring service module
Handles performance metrics and monitoring
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceService:
    """Service for performance monitoring"""
    
    def __init__(self, es_service, mongo_service, redis_service):
        """
        Initialize performance service
        
        Args:
            es_service: Elasticsearch service instance
            mongo_service: MongoDB service instance
            redis_service: Redis service instance
        """
        self.es_service = es_service
        self.mongo_service = mongo_service
        self.redis_service = redis_service
    
    def get_performance_metrics(self):
        """
        Get performance metrics
        
        Returns:
            dict: Performance metrics
        """
        try:
            cache_key = "performance:metrics"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
            
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"@timestamp": {"gte": hour_ago}}},
                            {"term": {"log_type": "performance"}}
                        ]
                    }
                }
            }
            
            agg_query = {
                "avg_response_time": {
                    "avg": {"field": "response_time"}
                },
                "max_response_time": {
                    "max": {"field": "response_time"}
                },
                "min_response_time": {
                    "min": {"field": "response_time"}
                },
                "percentiles": {
                    "percentiles": {
                        "field": "response_time",
                        "percents": [50, 90, 95, 99]
                    }
                },
                "by_endpoint": {
                    "terms": {"field": "endpoint.keyword", "size": 20},
                    "aggs": {
                        "avg_response": {"avg": {"field": "response_time"}}
                    }
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggs = result.get('aggregations', {})
            
            metrics = {
                'avg_response_time': aggs.get('avg_response_time', {}).get('value', 0),
                'max_response_time': aggs.get('max_response_time', {}).get('value', 0),
                'min_response_time': aggs.get('min_response_time', {}).get('value', 0),
                'percentiles': aggs.get('percentiles', {}).get('values', {}),
                'by_endpoint': [
                    {
                        'endpoint': b['key'],
                        'count': b['doc_count'],
                        'avg_response_time': b.get('avg_response', {}).get('value', 0)
                    }
                    for b in aggs.get('by_endpoint', {}).get('buckets', [])
                ]
            }
            
            self.redis_service.set(cache_key, metrics, ttl=300)
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            raise
    
    def get_api_response_times(self):
        """
        Get API response times analysis
        
        Returns:
            dict: API response times
        """
        try:
            cache_key = "performance:api_response_times"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"@timestamp": {"gte": yesterday}}},
                            {"term": {"log_type": "performance"}},
                            {"exists": {"field": "api_endpoint"}}
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
                        "avg_response": {"avg": {"field": "response_time"}},
                        "max_response": {"max": {"field": "response_time"}}
                    }
                },
                "by_api": {
                    "terms": {"field": "api_endpoint.keyword", "size": 20},
                    "aggs": {
                        "avg_response": {"avg": {"field": "response_time"}},
                        "slow_requests": {
                            "filter": {"range": {"response_time": {"gte": 1000}}}
                        }
                    }
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggs = result.get('aggregations', {})
            
            response_times = {
                'timeline': [
                    {
                        'timestamp': b['key_as_string'],
                        'avg_response_time': b.get('avg_response', {}).get('value', 0),
                        'max_response_time': b.get('max_response', {}).get('value', 0)
                    }
                    for b in aggs.get('over_time', {}).get('buckets', [])
                ],
                'by_api': [
                    {
                        'api': b['key'],
                        'total_requests': b['doc_count'],
                        'avg_response_time': b.get('avg_response', {}).get('value', 0),
                        'slow_requests_count': b.get('slow_requests', {}).get('doc_count', 0)
                    }
                    for b in aggs.get('by_api', {}).get('buckets', [])
                ]
            }
            
            self.redis_service.set(cache_key, response_times, ttl=600)
            return response_times
            
        except Exception as e:
            logger.error(f"Error getting API response times: {str(e)}")
            raise
    
    def get_database_latency(self):
        """
        Get database latency metrics
        
        Returns:
            dict: Database latency metrics
        """
        try:
            cache_key = "performance:db_latency"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
            
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"@timestamp": {"gte": hour_ago}}},
                            {"term": {"log_type": "performance"}},
                            {"exists": {"field": "db_query_time"}}
                        ]
                    }
                }
            }
            
            agg_query = {
                "avg_db_latency": {
                    "avg": {"field": "db_query_time"}
                },
                "max_db_latency": {
                    "max": {"field": "db_query_time"}
                },
                "by_query_type": {
                    "terms": {"field": "query_type.keyword", "size": 10},
                    "aggs": {
                        "avg_latency": {"avg": {"field": "db_query_time"}}
                    }
                },
                "slow_queries": {
                    "filter": {"range": {"db_query_time": {"gte": 500}}}
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggs = result.get('aggregations', {})
            
            latency = {
                'avg_db_latency': aggs.get('avg_db_latency', {}).get('value', 0),
                'max_db_latency': aggs.get('max_db_latency', {}).get('value', 0),
                'slow_queries_count': aggs.get('slow_queries', {}).get('doc_count', 0),
                'by_query_type': [
                    {
                        'query_type': b['key'],
                        'count': b['doc_count'],
                        'avg_latency': b.get('avg_latency', {}).get('value', 0)
                    }
                    for b in aggs.get('by_query_type', {}).get('buckets', [])
                ]
            }
            
            self.redis_service.set(cache_key, latency, ttl=300)
            return latency
            
        except Exception as e:
            logger.error(f"Error getting database latency: {str(e)}")
            raise
