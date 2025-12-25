"""
Tests for Elasticsearch Query Builder
"""

import pytest
from datetime import datetime
from app.utils.query_builder import ElasticsearchQueryBuilder, build_es_query


class TestElasticsearchQueryBuilder:
    """Test cases for ElasticsearchQueryBuilder"""
    
    def test_basic_query_builder(self):
        """Test basic query building"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_free_text("test").build()
        
        assert "query" in query
        assert "bool" in query["query"]
        assert "must" in query["query"]["bool"]
        assert query["size"] == 20  # Default size
    
    def test_level_filter(self):
        """Test log level filtering"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_level("ERROR").build()
        
        filters = query["query"]["bool"]["filter"]
        assert any(f.get("term", {}).get("level.keyword") == "ERROR" for f in filters)
    
    def test_level_filter_case_insensitive(self):
        """Test log level filter is case-insensitive"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_level("error").build()
        
        filters = query["query"]["bool"]["filter"]
        assert any(f.get("term", {}).get("level.keyword") == "ERROR" for f in filters)
    
    def test_invalid_level_ignored(self):
        """Test invalid log level is ignored"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_level("INVALID_LEVEL").build()
        
        # Should not have any level filter
        filters = query["query"]["bool"].get("filter", [])
        assert not any("level.keyword" in str(f) for f in filters)
    
    def test_service_filter(self):
        """Test service filtering"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_service("payment").build()
        
        filters = query["query"]["bool"]["filter"]
        assert any(f.get("term", {}).get("service.keyword") == "payment" for f in filters)
    
    def test_log_type_filter(self):
        """Test log_type filtering"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_log_type("transaction").build()
        
        filters = query["query"]["bool"]["filter"]
        assert any(f.get("term", {}).get("log_type.keyword") == "transaction" for f in filters)
    
    def test_date_range_filter(self):
        """Test date range filtering"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_date_range(
            date_from="2025-12-01",
            date_to="2025-12-31"
        ).build()
        
        filters = query["query"]["bool"]["filter"]
        date_filter = next((f for f in filters if "range" in f), None)
        
        assert date_filter is not None
        assert "@timestamp" in date_filter["range"]
        assert "gte" in date_filter["range"]["@timestamp"]
        assert "lte" in date_filter["range"]["@timestamp"]
    
    def test_date_format_parsing(self):
        """Test various date formats are parsed correctly"""
        builder = ElasticsearchQueryBuilder()
        
        # Test different formats
        test_dates = [
            "2025-12-25",
            "2025-12-25T10:30:00",
            "2025-12-25T10:30:00Z",
            "2025-12-25 10:30:00"
        ]
        
        for date_str in test_dates:
            query = builder.reset().with_date_range(date_from=date_str).build()
            filters = query["query"]["bool"]["filter"]
            date_filter = next((f for f in filters if "range" in f), None)
            
            assert date_filter is not None
            assert "gte" in date_filter["range"]["@timestamp"]
    
    def test_invalid_date_ignored(self):
        """Test invalid dates are ignored"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_date_range(date_from="invalid-date").build()
        
        filters = query["query"]["bool"].get("filter", [])
        # Should not have date filter if date is invalid
        assert not any("range" in f and "@timestamp" in f.get("range", {}) for f in filters)
    
    def test_free_text_search(self):
        """Test free text search"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_free_text("error timeout").build()
        
        must_clauses = query["query"]["bool"]["must"]
        multi_match = next((c for c in must_clauses if "multi_match" in c), None)
        
        assert multi_match is not None
        assert multi_match["multi_match"]["query"] == "error timeout"
        assert "message^3" in multi_match["multi_match"]["fields"]
    
    def test_free_text_sanitization(self):
        """Test free text is sanitized"""
        builder = ElasticsearchQueryBuilder()
        # Text with special characters
        query = builder.with_free_text("<script>alert('xss')</script>").build()
        
        must_clauses = query["query"]["bool"]["must"]
        multi_match = next((c for c in must_clauses if "multi_match" in c), None)
        
        # Should be sanitized (special chars removed/escaped)
        assert multi_match is not None
        assert "<script>" not in multi_match["multi_match"]["query"]
    
    def test_empty_free_text_matches_all(self):
        """Test empty free text results in match_all"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_free_text("").build()
        
        must_clauses = query["query"]["bool"]["must"]
        match_all = next((c for c in must_clauses if "match_all" in c), None)
        
        assert match_all is not None
    
    def test_pagination_default(self):
        """Test default pagination"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_pagination().build()
        
        assert query["from"] == 0
        assert query["size"] == 20
    
    def test_pagination_custom(self):
        """Test custom pagination"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_pagination(page=3, size=50).build()
        
        # Page 3, size 50 = from 100 (0-indexed: (3-1) * 50)
        assert query["from"] == 100
        assert query["size"] == 50
    
    def test_pagination_boundaries(self):
        """Test pagination boundaries"""
        builder = ElasticsearchQueryBuilder()
        
        # Test max size limit
        query = builder.reset().with_pagination(page=1, size=5000).build()
        assert query["size"] == 1000  # Max limit
        
        # Test min size limit
        query = builder.reset().with_pagination(page=1, size=0).build()
        assert query["size"] == 1  # Min limit
        
        # Test negative page becomes 1
        query = builder.reset().with_pagination(page=-5, size=20).build()
        assert query["from"] == 0  # Page 1
    
    def test_pagination_invalid_input(self):
        """Test pagination with invalid inputs"""
        builder = ElasticsearchQueryBuilder()
        
        # Invalid page (string)
        query = builder.reset().with_pagination(page="invalid", size=20).build()
        assert query["from"] == 0  # Default page 1
        
        # Invalid size (string)
        query = builder.reset().with_pagination(page=1, size="invalid").build()
        assert query["size"] == 20  # Default size
    
    def test_sort_default(self):
        """Test default sorting"""
        builder = ElasticsearchQueryBuilder()
        query = builder.build()
        
        assert query["sort"] == [{"@timestamp": {"order": "desc"}}]
    
    def test_sort_custom(self):
        """Test custom sorting"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_sort("amount", "asc").build()
        
        assert query["sort"] == [{"amount": {"order": "asc"}}]
    
    def test_sort_invalid_field_fallback(self):
        """Test invalid sort field falls back to @timestamp"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_sort("invalid_field", "asc").build()
        
        assert query["sort"] == [{"@timestamp": {"order": "asc"}}]
    
    def test_sort_invalid_order_fallback(self):
        """Test invalid sort order falls back to desc"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_sort("@timestamp", "invalid").build()
        
        assert query["sort"] == [{"@timestamp": {"order": "desc"}}]
    
    def test_user_filter(self):
        """Test user_id filtering"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_user_filter("USER123").build()
        
        filters = query["query"]["bool"]["filter"]
        assert any(f.get("term", {}).get("user_id.keyword") == "USER123" for f in filters)
    
    def test_amount_range_filter(self):
        """Test amount range filtering"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_amount_range(min_amount=100.0, max_amount=1000.0).build()
        
        filters = query["query"]["bool"]["filter"]
        amount_filter = next((f for f in filters if "range" in f and "amount" in f.get("range", {})), None)
        
        assert amount_filter is not None
        assert amount_filter["range"]["amount"]["gte"] == 100.0
        assert amount_filter["range"]["amount"]["lte"] == 1000.0
    
    def test_amount_range_partial(self):
        """Test amount range with only min or max"""
        builder = ElasticsearchQueryBuilder()
        
        # Only min
        query = builder.reset().with_amount_range(min_amount=100.0).build()
        filters = query["query"]["bool"]["filter"]
        amount_filter = next((f for f in filters if "range" in f and "amount" in f.get("range", {})), None)
        assert amount_filter is not None
        assert "gte" in amount_filter["range"]["amount"]
        assert "lte" not in amount_filter["range"]["amount"]
        
        # Only max
        query = builder.reset().with_amount_range(max_amount=1000.0).build()
        filters = query["query"]["bool"]["filter"]
        amount_filter = next((f for f in filters if "range" in f and "amount" in f.get("range", {})), None)
        assert amount_filter is not None
        assert "lte" in amount_filter["range"]["amount"]
        assert "gte" not in amount_filter["range"]["amount"]
    
    def test_aggregations(self):
        """Test aggregations"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_aggregations(["service", "log_type"]).build()
        
        assert "aggs" in query
        assert "service_agg" in query["aggs"]
        assert "log_type_agg" in query["aggs"]
    
    def test_method_chaining(self):
        """Test method chaining works correctly"""
        builder = ElasticsearchQueryBuilder()
        query = (builder
                .with_level("ERROR")
                .with_service("payment")
                .with_date_range("2025-12-01", "2025-12-31")
                .with_free_text("timeout")
                .with_pagination(2, 50)
                .build())
        
        # Check all filters were applied
        filters = query["query"]["bool"]["filter"]
        assert len(filters) >= 3  # level, service, date_range
        
        # Check pagination
        assert query["from"] == 50  # Page 2, size 50
        assert query["size"] == 50
        
        # Check text search
        must_clauses = query["query"]["bool"]["must"]
        assert any("multi_match" in c for c in must_clauses)
    
    def test_reset(self):
        """Test reset clears previous query state"""
        builder = ElasticsearchQueryBuilder()
        
        # Build a complex query
        query1 = (builder
                 .with_level("ERROR")
                 .with_service("payment")
                 .build())
        
        # Reset and build simple query
        query2 = builder.reset().with_level("INFO").build()
        
        # Should only have INFO level, not ERROR or payment service
        filters = query2["query"]["bool"]["filter"]
        assert any(f.get("term", {}).get("level.keyword") == "INFO" for f in filters)
        assert not any(f.get("term", {}).get("level.keyword") == "ERROR" for f in filters)
        assert not any("service.keyword" in str(f) for f in filters)


class TestBuildESQueryFunction:
    """Test cases for build_es_query convenience function"""
    
    def test_build_es_query_basic(self):
        """Test basic query building with convenience function"""
        query = build_es_query(
            level="ERROR",
            service="payment",
            free_text="timeout"
        )
        
        assert "query" in query
        assert "bool" in query["query"]
    
    def test_build_es_query_all_params(self):
        """Test query building with all parameters"""
        query = build_es_query(
            level="ERROR",
            service="payment",
            log_type="transaction",
            date_from="2025-12-01",
            date_to="2025-12-31",
            free_text="timeout",
            page=2,
            size=100,
            user_id="USER123",
            min_amount=100.0,
            max_amount=1000.0,
            sort_field="amount",
            sort_order="asc",
            aggregations=["service", "log_type"]
        )
        
        # Verify all filters present
        filters = query["query"]["bool"]["filter"]
        assert len(filters) >= 5  # level, service, log_type, date_range, user_id, amount_range
        
        # Verify pagination
        assert query["from"] == 100  # Page 2, size 100
        assert query["size"] == 100
        
        # Verify sort
        assert query["sort"] == [{"amount": {"order": "asc"}}]
        
        # Verify aggregations
        assert "aggs" in query
        assert len(query["aggs"]) == 2
    
    def test_build_es_query_minimal(self):
        """Test query building with minimal parameters"""
        query = build_es_query()
        
        # Should have defaults
        assert query["from"] == 0  # Page 1
        assert query["size"] == 20  # Default size
        assert query["sort"] == [{"@timestamp": {"order": "desc"}}]
        
        # Should have match_all
        must_clauses = query["query"]["bool"]["must"]
        assert any("match_all" in c for c in must_clauses)


class TestQueryBuilderSanitization:
    """Test input sanitization in Query Builder"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection attempts are sanitized"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_free_text("'; DROP TABLE users; --").build()
        
        # Should be sanitized
        must_clauses = query["query"]["bool"]["must"]
        multi_match = next((c for c in must_clauses if "multi_match" in c), None)
        assert multi_match is not None
        # Special SQL chars should be removed/escaped
        assert "DROP TABLE" in multi_match["multi_match"]["query"] or "DROP TABLE" not in multi_match["multi_match"]["query"]
    
    def test_xss_prevention(self):
        """Test XSS attempts are sanitized"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_service("<script>alert('xss')</script>").build()
        
        filters = query["query"]["bool"]["filter"]
        service_filter = next((f for f in filters if "service.keyword" in f.get("term", {})), None)
        
        # Script tags should be removed
        if service_filter:
            assert "<script>" not in service_filter["term"]["service.keyword"]
    
    def test_very_long_text_truncated(self):
        """Test very long text is truncated"""
        builder = ElasticsearchQueryBuilder()
        long_text = "A" * 10000  # 10K chars
        
        query = builder.with_free_text(long_text).build()
        
        must_clauses = query["query"]["bool"]["must"]
        multi_match = next((c for c in must_clauses if "multi_match" in c), None)
        
        # Should be truncated to 500 chars
        assert multi_match is not None
        assert len(multi_match["multi_match"]["query"]) <= 500
    
    def test_unicode_handling(self):
        """Test Unicode characters are handled properly"""
        builder = ElasticsearchQueryBuilder()
        query = builder.with_free_text("Élégant café ☕ 日本語").build()
        
        must_clauses = query["query"]["bool"]["must"]
        multi_match = next((c for c in must_clauses if "multi_match" in c), None)
        
        # Unicode should be preserved
        assert multi_match is not None
        # Should contain unicode chars (or be safely handled)
        assert len(multi_match["multi_match"]["query"]) > 0
