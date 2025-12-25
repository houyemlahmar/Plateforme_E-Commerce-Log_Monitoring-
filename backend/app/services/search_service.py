"""
Search service module
Provides search functionality across logs
"""

import logging
import hashlib
import json
from datetime import datetime
from app.utils.query_builder import ElasticsearchQueryBuilder

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching logs"""
    
    def __init__(self, es_service, redis_service, mongo_service=None):
        """
        Initialize search service
        
        Args:
            es_service: Elasticsearch service instance
            redis_service: Redis service instance
            mongo_service: MongoDB service instance (optional)
        """
        self.es_service = es_service
        self.redis_service = redis_service
        self.mongo_service = mongo_service
    
    def _generate_cache_key(self, **params):
        """
        Generate cache key from search parameters
        
        Args:
            **params: Search parameters
        
        Returns:
            str: Cache key
        """
        # Sort params to ensure consistent keys
        sorted_params = sorted(params.items())
        # Filter out None values
        filtered_params = [(k, v) for k, v in sorted_params if v is not None]
        # Create hash
        params_str = json.dumps(filtered_params, sort_keys=True)
        hash_obj = hashlib.md5(params_str.encode())
        return f"search:{hash_obj.hexdigest()}"
    
    def _save_search_history(self, query_params, results_count, user_ip=None):
        """
        Save search history to MongoDB
        
        Args:
            query_params: Search parameters
            results_count: Number of results returned
            user_ip: User IP address (optional)
        """
        if not self.mongo_service:
            return
        
        try:
            history_entry = {
                'timestamp': datetime.utcnow(),
                'query': query_params.get('query'),
                'filters': {
                    'log_type': query_params.get('log_type'),
                    'level': query_params.get('level'),
                    'service': query_params.get('service'),
                    'start_date': query_params.get('start_date'),
                    'end_date': query_params.get('end_date'),
                    'user_id': query_params.get('user_id'),
                    'min_amount': query_params.get('min_amount'),
                    'max_amount': query_params.get('max_amount')
                },
                'pagination': {
                    'page': query_params.get('page', 1),
                    'size': query_params.get('size', 20)
                },
                'results_count': results_count,
                'user_ip': user_ip
            }
            
            self.mongo_service.insert_one('search_history', history_entry)
            logger.debug(f"Saved search history: {results_count} results")
            
        except Exception as e:
            logger.error(f"Error saving search history: {str(e)}")
    
    def search(
        self, 
        query=None, 
        log_type=None, 
        level=None,
        service=None,
        start_date=None, 
        end_date=None, 
        user_id=None,
        min_amount=None,
        max_amount=None,
        page=1,
        size=20,
        sort_field='@timestamp',
        sort_order='desc',
        user_ip=None
    ):
        """
        Search logs using Elasticsearch with Query Builder
        Implements Redis caching (TTL 60s) and MongoDB search history
        
        Args:
            query: Search query string (free text)
            log_type: Filter by log type
            level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            service: Filter by service name
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            user_id: Filter by user ID
            min_amount: Minimum amount filter
            max_amount: Maximum amount filter
            page: Page number (1-indexed)
            size: Number of results per page
            sort_field: Field to sort by
            sort_order: Sort order (asc/desc)
            user_ip: User IP address for history tracking
        
        Returns:
            dict: Search results with metadata (cached if available)
        """
        try:
            # Create cache key from parameters
            cache_params = {
                'query': query,
                'log_type': log_type,
                'level': level,
                'service': service,
                'start_date': start_date,
                'end_date': end_date,
                'user_id': user_id,
                'min_amount': min_amount,
                'max_amount': max_amount,
                'page': page,
                'size': size,
                'sort_field': sort_field,
                'sort_order': sort_order
            }
            cache_key = self._generate_cache_key(**cache_params)
            
            # Try to get from cache (TTL 60s)
            cached_result = self.redis_service.get(cache_key)
            if cached_result:
                logger.info(f"Cache HIT for search: {cache_key}")
                cached_result['cached'] = True
                return cached_result
            
            logger.info(f"Cache MISS for search: {cache_key}")
            
            # Build Elasticsearch query using Query Builder
            builder = ElasticsearchQueryBuilder()
            es_query = (builder
                       .with_free_text(query)
                       .with_log_type(log_type)
                       .with_level(level)
                       .with_service(service)
                       .with_date_range(start_date, end_date)
                       .with_user_filter(user_id)
                       .with_amount_range(min_amount, max_amount)
                       .with_sort(sort_field, sort_order)
                       .with_pagination(page, size)
                       .build())
            
            logger.info(f"Executing search: query='{query}', page={page}, size={size}")
            
            # Execute search (size is already in the query via pagination)
            result = self.es_service.search('logs', es_query)
            
            # Extract results
            hits = result.get('hits', {}).get('hits', [])
            total = result.get('hits', {}).get('total', {}).get('value', 0)
            
            # Calculate pagination metadata
            total_pages = (total + size - 1) // size if size > 0 else 0
            
            search_results = {
                'total': total,
                'page': page,
                'page_size': size,
                'total_pages': total_pages,
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
                    'level': level,
                    'service': service,
                    'start_date': start_date,
                    'end_date': end_date,
                    'user_id': user_id,
                    'min_amount': min_amount,
                    'max_amount': max_amount
                },
                'sort': {
                    'field': sort_field,
                    'order': sort_order
                },
                'cached': False
            }
            
            # Cache results with 60 seconds TTL
            self.redis_service.set(cache_key, search_results, ttl=60)
            logger.debug(f"Cached search results: {cache_key}")
            
            # Save search history to MongoDB
            self._save_search_history(cache_params, total, user_ip)
            
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
