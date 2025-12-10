"""
Search service module
Provides search functionality across logs
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching logs"""
    
    def __init__(self, es_service, redis_service):
        """
        Initialize search service
        
        Args:
            es_service: Elasticsearch service instance
            redis_service: Redis service instance
        """
        self.es_service = es_service
        self.redis_service = redis_service
    
    def search(self, query, log_type=None, start_date=None, end_date=None, size=100):
        """
        Search logs using Elasticsearch
        
        Args:
            query: Search query string
            log_type: Filter by log type
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            size: Number of results
        
        Returns:
            dict: Search results
        """
        try:
            # Build Elasticsearch query
            es_query = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": []
                    }
                },
                "sort": [
                    {"@timestamp": {"order": "desc"}}
                ],
                "highlight": {
                    "fields": {
                        "message": {},
                        "error_message": {}
                    }
                }
            }
            
            # Add text search
            if query:
                es_query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query,
                        "fields": ["message", "error_message", "user_id", "transaction_id"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            else:
                es_query["query"]["bool"]["must"].append({
                    "match_all": {}
                })
            
            # Add log type filter
            if log_type:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"log_type": log_type}
                })
            
            # Add date range filter
            if start_date or end_date:
                date_range = {}
                if start_date:
                    date_range["gte"] = start_date
                if end_date:
                    date_range["lte"] = end_date
                
                es_query["query"]["bool"]["filter"].append({
                    "range": {"@timestamp": date_range}
                })
            
            # Execute search
            result = self.es_service.search('logs', es_query, size=size)
            
            # Extract results
            hits = result.get('hits', {}).get('hits', [])
            total = result.get('hits', {}).get('total', {}).get('value', 0)
            
            search_results = {
                'total': total,
                'results': [
                    {
                        'id': hit['_id'],
                        'score': hit['_score'],
                        'source': hit['_source'],
                        'highlight': hit.get('highlight', {})
                    }
                    for hit in hits
                ],
                'query': query,
                'filters': {
                    'log_type': log_type,
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching logs: {str(e)}")
            raise
    
    def get_autocomplete_suggestions(self, query):
        """
        Get autocomplete suggestions
        
        Args:
            query: Partial query string
        
        Returns:
            list: Autocomplete suggestions
        """
        try:
            if not query or len(query) < 2:
                return []
            
            # Cache key
            cache_key = f"autocomplete:{query.lower()}"
            cached = self.redis_service.get(cache_key)
            if cached:
                return cached
            
            # Build suggestion query
            es_query = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["message", "error_message", "user_id", "transaction_id"],
                        "type": "phrase_prefix"
                    }
                },
                "aggs": {
                    "suggestions": {
                        "terms": {
                            "field": "message.keyword",
                            "size": 10
                        }
                    }
                }
            }
            
            result = self.es_service.search('logs', es_query, size=0)
            
            # Extract suggestions
            suggestions = [
                bucket['key']
                for bucket in result.get('aggregations', {}).get('suggestions', {}).get('buckets', [])
            ]
            
            # Cache suggestions
            self.redis_service.set(cache_key, suggestions, ttl=3600)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting autocomplete suggestions: {str(e)}")
            return []
