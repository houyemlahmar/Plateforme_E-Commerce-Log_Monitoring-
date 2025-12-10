"""
Formatters module
Data formatting utilities
"""

from datetime import datetime
from typing import Any, Dict, List


def format_timestamp(timestamp: datetime, format_string: str = "%Y-%m-%d %H:%M:%S"):
    """
    Format timestamp
    
    Args:
        timestamp: Datetime object
        format_string: Format string
    
    Returns:
        str: Formatted timestamp
    """
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    return timestamp.strftime(format_string)


def format_currency(amount: float, currency: str = "USD"):
    """
    Format currency amount
    
    Args:
        amount: Amount
        currency: Currency code
    
    Returns:
        str: Formatted currency
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$'
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_file_size(size_bytes: int):
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        str: Formatted file size
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_duration(milliseconds: float):
    """
    Format duration in human-readable format
    
    Args:
        milliseconds: Duration in milliseconds
    
    Returns:
        str: Formatted duration
    """
    if milliseconds < 1000:
        return f"{milliseconds:.2f}ms"
    
    seconds = milliseconds / 1000
    if seconds < 60:
        return f"{seconds:.2f}s"
    
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.2f}m"
    
    hours = minutes / 60
    return f"{hours:.2f}h"


def format_percentage(value: float, total: float, decimals: int = 2):
    """
    Format percentage
    
    Args:
        value: Value
        total: Total
        decimals: Number of decimal places
    
    Returns:
        str: Formatted percentage
    """
    if total == 0:
        return "0.00%"
    
    percentage = (value / total) * 100
    return f"{percentage:.{decimals}f}%"


def format_log_entry(log: Dict[str, Any]):
    """
    Format log entry for display
    
    Args:
        log: Log entry dictionary
    
    Returns:
        dict: Formatted log entry
    """
    formatted = log.copy()
    
    # Format timestamp
    if '@timestamp' in formatted:
        formatted['formatted_timestamp'] = format_timestamp(formatted['@timestamp'])
    
    # Format amount if present
    if 'amount' in formatted and 'currency' in formatted:
        formatted['formatted_amount'] = format_currency(
            formatted['amount'],
            formatted['currency']
        )
    
    # Format response time if present
    if 'response_time' in formatted:
        formatted['formatted_response_time'] = format_duration(formatted['response_time'])
    
    return formatted


def format_table_data(data: List[Dict[str, Any]], columns: List[str] = None):
    """
    Format data for table display
    
    Args:
        data: List of data dictionaries
        columns: List of columns to include (None for all)
    
    Returns:
        dict: Formatted table data
    """
    if not data:
        return {'headers': [], 'rows': []}
    
    # Determine columns
    if columns is None:
        columns = list(data[0].keys())
    
    # Format rows
    rows = []
    for item in data:
        row = []
        for col in columns:
            value = item.get(col, '')
            
            # Format special types
            if isinstance(value, datetime):
                value = format_timestamp(value)
            elif isinstance(value, float):
                value = f"{value:.2f}"
            
            row.append(str(value))
        
        rows.append(row)
    
    return {
        'headers': columns,
        'rows': rows
    }


def truncate_text(text: str, max_length: int = 100, suffix: str = "..."):
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
    
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
