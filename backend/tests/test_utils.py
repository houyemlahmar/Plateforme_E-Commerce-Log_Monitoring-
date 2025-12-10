"""
Tests for utility functions
"""

import pytest
from datetime import datetime, timedelta
from io import BytesIO
from werkzeug.datastructures import FileStorage

from app.utils.validators import (
    validate_log_file,
    validate_log_data,
    validate_email,
    validate_date_format,
    validate_transaction_data,
    sanitize_string
)
from app.utils.formatters import (
    format_timestamp,
    format_currency,
    format_file_size,
    format_duration,
    format_percentage,
    truncate_text
)
from app.utils.helpers import (
    generate_id,
    generate_hash,
    parse_time_range,
    calculate_date_range,
    flatten_dict,
    safe_get,
    merge_dicts,
    calculate_percentage_change
)


class TestValidators:
    """Test cases for validators"""
    
    def test_validate_email(self):
        """Test email validation"""
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False
        assert validate_email("test@") is False
        assert validate_email("@example.com") is False
    
    def test_validate_date_format(self):
        """Test date format validation"""
        assert validate_date_format("2024-01-01T12:00:00") is True
        assert validate_date_format("2024-01-01T12:00:00Z") is True
        assert validate_date_format("invalid-date") is False
        assert validate_date_format("2024-13-01") is False
    
    def test_validate_log_data(self):
        """Test log data validation"""
        valid_data = {"message": "test", "log_type": "info"}
        is_valid, error = validate_log_data(valid_data)
        assert is_valid is True
        assert error is None
        
        is_valid, error = validate_log_data(None)
        assert is_valid is False
        
        is_valid, error = validate_log_data([])
        assert is_valid is False
    
    def test_validate_transaction_data(self):
        """Test transaction data validation"""
        valid_data = {
            "transaction_id": "TXN123",
            "user_id": "USER123",
            "amount": 100.0,
            "currency": "USD",
            "payment_method": "credit_card"
        }
        is_valid, error = validate_transaction_data(valid_data)
        assert is_valid is True
        
        invalid_data = {"transaction_id": "TXN123"}
        is_valid, error = validate_transaction_data(invalid_data)
        assert is_valid is False
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        text = "  Hello World  "
        assert sanitize_string(text) == "Hello World"
        
        long_text = "a" * 2000
        sanitized = sanitize_string(long_text, max_length=100)
        assert len(sanitized) == 100


class TestFormatters:
    """Test cases for formatters"""
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        formatted = format_timestamp(dt)
        assert "2024-01-01" in formatted
        assert "12:00:00" in formatted
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert format_currency(100.0, "USD") == "$100.00"
        assert format_currency(1000.5, "EUR") == "€1,000.50"
        assert format_currency(50, "GBP") == "£50.00"
    
    def test_format_file_size(self):
        """Test file size formatting"""
        assert "KB" in format_file_size(1024)
        assert "MB" in format_file_size(1024 * 1024)
        assert "GB" in format_file_size(1024 * 1024 * 1024)
    
    def test_format_duration(self):
        """Test duration formatting"""
        assert format_duration(500) == "500.00ms"
        assert "s" in format_duration(2000)
        assert "m" in format_duration(120000)
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        assert format_percentage(50, 100) == "50.00%"
        assert format_percentage(1, 3, decimals=1) == "33.3%"
        assert format_percentage(0, 0) == "0.00%"
    
    def test_truncate_text(self):
        """Test text truncation"""
        text = "This is a very long text that needs to be truncated"
        truncated = truncate_text(text, max_length=20)
        assert len(truncated) <= 20
        assert truncated.endswith("...")


class TestHelpers:
    """Test cases for helper functions"""
    
    def test_generate_id(self):
        """Test ID generation"""
        id1 = generate_id()
        id2 = generate_id()
        assert id1 != id2
        
        id_with_prefix = generate_id("TXN_")
        assert id_with_prefix.startswith("TXN_")
    
    def test_generate_hash(self):
        """Test hash generation"""
        hash1 = generate_hash("test")
        hash2 = generate_hash("test")
        hash3 = generate_hash("different")
        
        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 64  # SHA256 hash length
    
    def test_parse_time_range(self):
        """Test time range parsing"""
        delta = parse_time_range("7d")
        assert delta == timedelta(days=7)
        
        delta = parse_time_range("24h")
        assert delta == timedelta(hours=24)
        
        delta = parse_time_range("30m")
        assert delta == timedelta(minutes=30)
    
    def test_flatten_dict(self):
        """Test dictionary flattening"""
        nested = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3
                }
            }
        }
        
        flat = flatten_dict(nested)
        assert flat["a"] == 1
        assert flat["b.c"] == 2
        assert flat["b.d.e"] == 3
    
    def test_safe_get(self):
        """Test safe dictionary access"""
        data = {
            "a": {
                "b": {
                    "c": 123
                }
            }
        }
        
        assert safe_get(data, "a", "b", "c") == 123
        assert safe_get(data, "a", "x", "y", default=0) == 0
        assert safe_get(data, "z", default="default") == "default"
    
    def test_merge_dicts(self):
        """Test dictionary merging"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        dict3 = {"d": 5}
        
        merged = merge_dicts(dict1, dict2, dict3)
        assert merged["a"] == 1
        assert merged["b"] == 3  # Later dict overwrites
        assert merged["c"] == 4
        assert merged["d"] == 5
    
    def test_calculate_percentage_change(self):
        """Test percentage change calculation"""
        change = calculate_percentage_change(100, 150)
        assert change == 50.0
        
        change = calculate_percentage_change(200, 100)
        assert change == -50.0
        
        change = calculate_percentage_change(0, 100)
        assert change == 100.0
