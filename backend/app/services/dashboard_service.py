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
                "log_levels": {
                    "terms": {"field": "level", "size": 10}
                },
                "errors": {
                    "filter": {
                        "bool": {
                            "should": [
                                {"match": {"level": "ERROR"}},
                                {"match": {"level": "CRITICAL"}}
                            ]
                        }
                    }
                },
                "services": {
                    "terms": {"field": "service.keyword", "size": 10}
                }
            }
            
            result = self.es_service.search('logs', query, size=0)
            aggs = result.get('aggregations', {})
            
            overview = {
                'total_logs_24h': result.get('hits', {}).get('total', {}).get('value', 0),
                'errors_24h': aggs.get('errors', {}).get('doc_count', 0),
                'transactions_24h': 0,  # Not applicable for these logs
                'transaction_amount_24h': 0,  # Not applicable
                'fraud_alerts_24h': 0,  # Not applicable
                'log_levels_distribution': [
                    {'type': b['key'], 'count': b['doc_count']}
                    for b in aggs.get('log_levels', {}).get('buckets', [])
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
                "filter": {
                    "bool": {
                        "should": [
                            {"match": {"level": "ERROR"}},
                            {"match": {"level": "CRITICAL"}}
                        ]
                    }
                }
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
                        {"exists": {"field": "response_time"}}
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
    
    def get_kpis(self, time_range='24h'):
        """
        Get all KPIs for dashboard HTML template
        
        Args:
            time_range: Time range ('24h', '7d', '30d')
        
        Returns:
            dict: All KPI data for dashboard
        """
        try:
            cache_key = f"dashboard:kpis:{time_range}"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            # Calculate time filter
            now = datetime.utcnow()
            if time_range == '7d':
                start_time = now - timedelta(days=7)
            elif time_range == '30d':
                start_time = now - timedelta(days=30)
            else:
                start_time = now - timedelta(hours=24)
            
            time_filter = {
                "range": {
                    "@timestamp": {
                        "gte": start_time.isoformat(),
                        "lte": now.isoformat()
                    }
                }
            }
            
            # Build comprehensive query with aggregations
            query = {
                "query": {
                    "bool": {
                        "must": [time_filter]
                    }
                },
                "size": 0,
                "aggs": {
                    "total_logs": {
                        "value_count": {"field": "@timestamp"}
                    },
                    "error_logs": {
                        "filter": {
                            "bool": {
                                "should": [
                                    {"match": {"level": "ERROR"}},
                                    {"match": {"level": "CRITICAL"}}
                                ]
                            }
                        }
                    },
                    "unique_users": {
                        "cardinality": {"field": "user_id.keyword"}
                    },
                    "avg_response_time": {
                        "avg": {"field": "response_time"}
                    },
                    "logs_over_time": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "calendar_interval": "1h",
                            "format": "HH:mm"
                        },
                        "aggs": {
                            "errors": {
                                "filter": {
                                    "bool": {
                                        "should": [
                                            {"match": {"level": "ERROR"}},
                                            {"match": {"level": "CRITICAL"}}
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    "log_levels": {
                        "terms": {"field": "level", "size": 10}
                    },
                    "top_services": {
                        "terms": {"field": "service", "size": 5}
                    }
                }
            }
            
            result = self.es_service.search('logs', query)
            aggs = result.get('aggregations', {})
            
            total_logs = result.get('hits', {}).get('total', {}).get('value', 0)
            total_errors = aggs.get('error_logs', {}).get('doc_count', 0)
            error_rate = (total_errors / total_logs * 100) if total_logs > 0 else 0
            
            # Format logs per hour
            logs_per_hour = []
            for bucket in aggs.get('logs_over_time', {}).get('buckets', []):
                logs_per_hour.append({
                    'hour': bucket.get('key_as_string', ''),
                    'total': bucket.get('doc_count', 0),
                    'errors': bucket.get('errors', {}).get('doc_count', 0)
                })
            
            # Format log levels distribution
            log_levels_distribution = {}
            for bucket in aggs.get('log_levels', {}).get('buckets', []):
                log_levels_distribution[bucket['key']] = bucket['doc_count']
            
            # Format top services
            top_services = []
            service_buckets = aggs.get('top_services', {}).get('buckets', [])
            total_service_logs = sum(b['doc_count'] for b in service_buckets)
            for bucket in service_buckets:
                top_services.append({
                    'name': bucket['key'],
                    'count': bucket['doc_count'],
                    'percentage': round((bucket['doc_count'] / total_service_logs * 100), 1) if total_service_logs > 0 else 0
                })
            
            # Get recent errors
            recent_errors = self._get_recent_errors_for_kpis()
            
            # Get active users (last 5 minutes)
            active_users = self._get_active_users()
            
            # Get logs indexed today
            logs_today = self._get_logs_today()
            
            # Get total uploaded files count
            uploaded_files = self._get_uploaded_files_count()
            
            kpis = {
                'total_logs': total_logs,
                'logs_today': logs_today,
                'total_errors': total_errors,
                'unique_users': aggs.get('unique_users', {}).get('value', 0) or 0,
                'avg_response_time': round(aggs.get('avg_response_time', {}).get('value') or 0),
                'uploaded_files': uploaded_files,
                'logs_growth': 12.5,  # Mock value - can be calculated by comparing with previous period
                'error_rate': round(error_rate, 2) if error_rate is not None else 0,
                'active_users': active_users,
                'logs_per_hour': logs_per_hour,
                'log_levels_distribution': log_levels_distribution,
                'top_services': top_services,
                'recent_errors': recent_errors,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Cache for 60 seconds
            self.redis_service.set(cache_key, kpis, ttl=60)
            
            return kpis
        
        except Exception as e:
            logger.error(f"Error fetching KPIs: {str(e)}")
            return self._get_empty_kpis()
    
    def _get_recent_errors_for_kpis(self, limit=10):
        """Get recent error logs for KPIs"""
        try:
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"level": "ERROR"}},
                            {"match": {"level": "CRITICAL"}}
                        ]
                    }
                },
                "size": limit,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
            
            result = self.es_service.search('logs', query)
            hits = result.get('hits', {}).get('hits', [])
            
            errors = []
            for hit in hits:
                source = hit.get('_source', {})
                timestamp = source.get('@timestamp', '')
                if 'T' in timestamp:
                    timestamp = timestamp[:19].replace('T', ' ')
                
                errors.append({
                    'timestamp': timestamp,
                    'service': source.get('service', 'unknown'),
                    'message': source.get('message', 'No message')[:100],
                    'level': source.get('level', 'ERROR')
                })
            
            return errors
        
        except Exception as e:
            logger.error(f"Error fetching recent errors: {str(e)}")
            return []
    
    def _get_active_users(self):
        """Get count of active users in last 5 minutes"""
        try:
            five_mins_ago = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
            
            query = {
                "query": {
                    "range": {"@timestamp": {"gte": five_mins_ago}}
                },
                "size": 0,
                "aggs": {
                    "active_users": {
                        "cardinality": {"field": "user_id.keyword"}
                    }
                }
            }
            
            result = self.es_service.search('logs', query)
            return result.get('aggregations', {}).get('active_users', {}).get('value', 0)
        
        except Exception as e:
            logger.error(f"Error fetching active users: {str(e)}")
            return 0
    
    def _get_logs_today(self):
        """Get count of logs indexed today"""
        try:
            now = datetime.utcnow()
            start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
            
            query = {
                "query": {
                    "range": {
                        "@timestamp": {
                            "gte": start_of_day.isoformat(),
                            "lte": now.isoformat()
                        }
                    }
                },
                "size": 0
            }
            
            result = self.es_service.search('logs', query)
            return result.get('hits', {}).get('total', {}).get('value', 0)
        
        except Exception as e:
            logger.error(f"Error fetching logs today: {str(e)}")
            return 0
    
    def _get_uploaded_files_count(self):
        """Get total count of uploaded files from MongoDB"""
        try:
            # Count documents in uploads collection
            count = self.mongo_service.db.uploads.count_documents({})
            return count
        
        except Exception as e:
            logger.error(f"Error fetching uploaded files count: {str(e)}")
            return 0
    
    def _get_empty_kpis(self):
        """Return empty KPIs structure"""
        return {
            'total_logs': 0,
            'logs_today': 0,
            'total_errors': 0,
            'unique_users': 0,
            'avg_response_time': 0,
            'uploaded_files': 0,
            'logs_growth': 0,
            'error_rate': 0,
            'active_users': 0,
            'logs_per_hour': [],
            'log_levels_distribution': {},
            'top_services': [],
            'recent_errors': [],
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_system_health(self):
        """
        Check health status of connected systems
        
        Returns:
            dict: System health statuses
        """
        health = {
            'elasticsearch': 'Disconnected',
            'redis': 'Unknown',
            'mongodb': 'Unknown'
        }
        
        try:
            # Check Elasticsearch
            if self.es_service.client.ping():
                health['elasticsearch'] = 'Connecté'
        except Exception as e:
            logger.error(f"Error checking Elasticsearch: {str(e)}")
        
        try:
            # Check Redis
            if self.redis_service.client.ping():
                health['redis'] = 'Actif'
        except Exception as e:
            logger.error(f"Error checking Redis: {str(e)}")
        
        try:
            # Check MongoDB
            self.mongo_service.db.command('ping')
            health['mongodb'] = 'Connecté'
        except Exception as e:
            logger.error(f"Error checking MongoDB: {str(e)}")
        
        return health
