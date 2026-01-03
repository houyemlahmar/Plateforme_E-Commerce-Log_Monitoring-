"""
Elasticsearch Query Builder Utility
Builds safe, sanitized Elasticsearch DSL queries from user inputs
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.utils.validators import sanitize_string

logger = logging.getLogger(__name__)


class ElasticsearchQueryBuilder:
    """
    Builds Elasticsearch DSL queries with input sanitization and safe fallbacks
    """
    
    # Default values
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 1000
    MIN_PAGE_SIZE = 1
    
    # Allowed fields for sorting and searching
    SEARCHABLE_FIELDS = [
        'message', 'error_message', 'user_id', 'transaction_id',
        'order_id', 'endpoint', 'service', 'action', 'product_id'
    ]
    
    SORTABLE_FIELDS = ['@timestamp', 'amount', 'response_time', 'fraud_score']
    
    # Valid log levels
    VALID_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def __init__(self):
        """Initialize the query builder"""
        self.reset()
    
    def reset(self):
        """Reset the query builder to initial state"""
        self.query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "from": 0,
            "size": self.DEFAULT_PAGE_SIZE
        }
        return self
    
    def with_level(self, level: Optional[str]) -> 'ElasticsearchQueryBuilder':
        """
        Add log level filter
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            self for chaining
        """
        if not level:
            return self
        
        # Sanitize and validate level
        level_clean = self._sanitize_level(level)
        if level_clean:
            self.query["query"]["bool"]["filter"].append({
                "term": {"level.keyword": level_clean}
            })
            logger.debug(f"Added level filter: {level_clean}")
        
        return self
    
    def with_service(self, service: Optional[str]) -> 'ElasticsearchQueryBuilder':
        """
        Add service filter
        
        Args:
            service: Service name
        
        Returns:
            self for chaining
        """
        if not service:
            return self
        
        # Sanitize service name (remove HTML tags)
        service_clean = self._sanitize_search_text(service)
        if service_clean:
            self.query["query"]["bool"]["filter"].append({
                "term": {"service.keyword": service_clean}
            })
            logger.debug(f"Added service filter: {service_clean}")
        
        return self
    
    def with_log_type(self, log_type: Optional[str]) -> 'ElasticsearchQueryBuilder':
        """
        Add log_type filter
        
        Args:
            log_type: Log type (transaction, error, fraud, performance, user_behavior)
        
        Returns:
            self for chaining
        """
        if not log_type:
            return self
        
        # Sanitize log type (remove HTML tags)
        log_type_clean = self._sanitize_search_text(log_type)
        if log_type_clean:
            self.query["query"]["bool"]["filter"].append({
                "term": {"log_type.keyword": log_type_clean}
            })
            logger.debug(f"Added log_type filter: {log_type_clean}")
        
        return self
    
    def with_date_range(
        self, 
        date_from: Optional[str] = None, 
        date_to: Optional[str] = None
    ) -> 'ElasticsearchQueryBuilder':
        """
        Add date range filter
        
        Args:
            date_from: Start date (ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            date_to: End date (ISO 8601 format)
        
        Returns:
            self for chaining
        """
        if not date_from and not date_to:
            return self
        
        date_range = {}
        
        # Parse and validate date_from
        if date_from:
            parsed_from = self._parse_date(date_from)
            if parsed_from:
                date_range["gte"] = parsed_from
                logger.debug(f"Added date_from filter: {parsed_from}")
        
        # Parse and validate date_to
        if date_to:
            parsed_to = self._parse_date(date_to)
            if parsed_to:
                date_range["lte"] = parsed_to
                logger.debug(f"Added date_to filter: {parsed_to}")
        
        if date_range:
            self.query["query"]["bool"]["filter"].append({
                "range": {"@timestamp": date_range}
            })
        
        return self
    
    def with_free_text(self, text: Optional[str]) -> 'ElasticsearchQueryBuilder':
        """
        Add free text search across multiple fields
        
        Args:
            text: Search text
        
        Returns:
            self for chaining
        """
        if not text or not text.strip():
            # If no text, match all
            self.query["query"]["bool"]["must"].append({"match_all": {}})
            return self
        
        # Sanitize text
        text_clean = self._sanitize_search_text(text)
        
        if text_clean:
            # Multi-field search with boosting (only text fields)
            self.query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": text_clean,
                    "fields": [
                        "message^3",           # Boost message field
                        "error_message^2",     # Boost error messages
                        "endpoint",
                        "service",
                        "action",
                        "product_id"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO",       # Auto fuzzy matching
                    "operator": "or",
                    "minimum_should_match": "75%"
                }
            })
            
            # Add highlighting for matched terms
            self.query["highlight"] = {
                "fields": {
                    "message": {},
                    "error_message": {}
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            }
            
            logger.debug(f"Added free text search: {text_clean[:50]}...")
        else:
            # Fallback to match_all if sanitization removes everything
            self.query["query"]["bool"]["must"].append({"match_all": {}})
        
        return self
    
    def with_pagination(
        self, 
        page: Optional[int] = None, 
        size: Optional[int] = None
    ) -> 'ElasticsearchQueryBuilder':
        """
        Add pagination
        
        Args:
            page: Page number (1-indexed)
            size: Page size (number of results per page)
        
        Returns:
            self for chaining
        """
        # Sanitize and validate page
        page_clean = self._sanitize_page(page)
        size_clean = self._sanitize_page_size(size)
        
        # Calculate 'from' offset (Elasticsearch uses 0-indexed)
        from_offset = (page_clean - 1) * size_clean
        
        self.query["from"] = from_offset
        self.query["size"] = size_clean
        
        logger.debug(f"Added pagination: page={page_clean}, size={size_clean}, from={from_offset}")
        
        return self
    
    def with_sort(
        self, 
        field: Optional[str] = None, 
        order: Optional[str] = 'desc'
    ) -> 'ElasticsearchQueryBuilder':
        """
        Add sorting
        
        Args:
            field: Field to sort by (default: @timestamp)
            order: Sort order ('asc' or 'desc', default: 'desc')
        
        Returns:
            self for chaining
        """
        # Validate and sanitize field
        field_clean = field if field in self.SORTABLE_FIELDS else '@timestamp'
        
        # Validate order
        order_clean = 'desc' if order not in ['asc', 'desc'] else order
        
        self.query["sort"] = [{field_clean: {"order": order_clean}}]
        
        logger.debug(f"Added sort: {field_clean} {order_clean}")
        
        return self
    
    def with_aggregations(self, agg_fields: Optional[List[str]] = None) -> 'ElasticsearchQueryBuilder':
        """
        Add aggregations for analytics
        
        Args:
            agg_fields: List of fields to aggregate on
        
        Returns:
            self for chaining
        """
        if not agg_fields:
            return self
        
        self.query["aggs"] = {}
        
        for field in agg_fields:
            # Sanitize field name
            field_clean = sanitize_string(field, max_length=50)
            if field_clean:
                self.query["aggs"][f"{field_clean}_agg"] = {
                    "terms": {
                        "field": f"{field_clean}.keyword",
                        "size": 10
                    }
                }
        
        logger.debug(f"Added aggregations: {agg_fields}")
        
        return self
    
    def with_user_filter(self, user_id: Optional[str]) -> 'ElasticsearchQueryBuilder':
        """
        Add user_id filter
        
        Args:
            user_id: User ID
        
        Returns:
            self for chaining
        """
        if not user_id:
            return self
        
        user_id_clean = sanitize_string(user_id, max_length=100)
        if user_id_clean:
            # Try to convert to int if it's numeric (user_id might be long type)
            try:
                user_id_value = int(user_id_clean)
                self.query["query"]["bool"]["filter"].append({
                    "term": {"user_id": user_id_value}
                })
            except ValueError:
                # If not numeric, treat as keyword field
                self.query["query"]["bool"]["filter"].append({
                    "term": {"user_id.keyword": user_id_clean}
                })
            logger.debug(f"Added user_id filter: {user_id_clean}")
        
        return self
    
    def with_amount_range(
        self, 
        min_amount: Optional[float] = None, 
        max_amount: Optional[float] = None
    ) -> 'ElasticsearchQueryBuilder':
        """
        Add amount range filter (for transactions)
        
        Args:
            min_amount: Minimum amount
            max_amount: Maximum amount
        
        Returns:
            self for chaining
        """
        if min_amount is None and max_amount is None:
            return self
        
        amount_range = {}
        
        if min_amount is not None and min_amount >= 0:
            amount_range["gte"] = min_amount
        
        if max_amount is not None and max_amount >= 0:
            amount_range["lte"] = max_amount
        
        if amount_range:
            self.query["query"]["bool"]["filter"].append({
                "range": {"amount": amount_range}
            })
            logger.debug(f"Added amount range filter: {amount_range}")
        
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build and return the final Elasticsearch query
        
        Returns:
            dict: Complete Elasticsearch DSL query
        """
        # Ensure at least one must clause exists
        if not self.query["query"]["bool"]["must"]:
            self.query["query"]["bool"]["must"].append({"match_all": {}})
        
        # Remove empty bool clauses
        for clause in ["must", "filter", "should", "must_not"]:
            if not self.query["query"]["bool"][clause]:
                del self.query["query"]["bool"][clause]
        
        logger.info(f"Built query with {self.query['size']} results from offset {self.query['from']}")
        
        return self.query
    
    # Private helper methods
    
    def _sanitize_level(self, level: str) -> Optional[str]:
        """
        Sanitize and validate log level
        
        Args:
            level: Raw level string
        
        Returns:
            Sanitized level or None
        """
        if not level:
            return None
        
        level_upper = level.strip().upper()
        
        if level_upper in self.VALID_LEVELS:
            return level_upper
        
        logger.warning(f"Invalid log level: {level}. Allowed: {self.VALID_LEVELS}")
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse and validate date string
        
        Args:
            date_str: Date string in ISO 8601 format
        
        Returns:
            Validated ISO date string or None
        """
        if not date_str:
            return None
        
        # Try various date formats
        date_formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # Return in ISO 8601 format with Z
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
        
        logger.warning(f"Invalid date format: {date_str}")
        return None
    
    def _sanitize_search_text(self, text: str) -> str:
        """
        Sanitize search text for safe querying
        
        Args:
            text: Raw search text
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove potentially dangerous characters for Elasticsearch
        # Keep alphanumeric, spaces, and common punctuation
        text_clean = re.sub(r'[^\w\s\-_@.+\'"]+', ' ', text)
        
        # Remove multiple spaces
        text_clean = re.sub(r'\s+', ' ', text_clean).strip()
        
        # Limit length
        text_clean = sanitize_string(text_clean, max_length=500)
        
        return text_clean
    
    def _sanitize_page(self, page: Optional[int]) -> int:
        """
        Sanitize and validate page number
        
        Args:
            page: Raw page number
        
        Returns:
            Validated page number (1-indexed)
        """
        if page is None:
            return self.DEFAULT_PAGE
        
        try:
            page_int = int(page)
            # Ensure page is at least 1
            return max(1, page_int)
        except (ValueError, TypeError):
            logger.warning(f"Invalid page number: {page}, using default: {self.DEFAULT_PAGE}")
            return self.DEFAULT_PAGE
    
    def _sanitize_page_size(self, size: Optional[int]) -> int:
        """
        Sanitize and validate page size
        
        Args:
            size: Raw page size
        
        Returns:
            Validated page size
        """
        if size is None:
            return self.DEFAULT_PAGE_SIZE
        
        try:
            size_int = int(size)
            # Clamp between MIN and MAX
            return max(self.MIN_PAGE_SIZE, min(size_int, self.MAX_PAGE_SIZE))
        except (ValueError, TypeError):
            logger.warning(f"Invalid page size: {size}, using default: {self.DEFAULT_PAGE_SIZE}")
            return self.DEFAULT_PAGE_SIZE


# Convenience function for quick query building
def build_es_query(
    level: Optional[str] = None,
    service: Optional[str] = None,
    log_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    free_text: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    user_id: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    sort_field: str = '@timestamp',
    sort_order: str = 'desc',
    aggregations: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to build an Elasticsearch query in one call
    
    Args:
        level: Log level filter
        service: Service name filter
        log_type: Log type filter
        date_from: Start date
        date_to: End date
        free_text: Free text search
        page: Page number (1-indexed)
        size: Page size
        user_id: User ID filter
        min_amount: Minimum amount filter
        max_amount: Maximum amount filter
        sort_field: Field to sort by
        sort_order: Sort order (asc/desc)
        aggregations: Fields to aggregate on
    
    Returns:
        dict: Complete Elasticsearch DSL query
    
    Example:
        >>> query = build_es_query(
        ...     level='ERROR',
        ...     service='payment',
        ...     date_from='2025-12-01',
        ...     date_to='2025-12-31',
        ...     free_text='timeout',
        ...     page=1,
        ...     size=50
        ... )
    """
    builder = ElasticsearchQueryBuilder()
    
    return (builder
            .with_level(level)
            .with_service(service)
            .with_log_type(log_type)
            .with_date_range(date_from, date_to)
            .with_free_text(free_text)
            .with_user_filter(user_id)
            .with_amount_range(min_amount, max_amount)
            .with_sort(sort_field, sort_order)
            .with_pagination(page, size)
            .with_aggregations(aggregations)
            .build())
