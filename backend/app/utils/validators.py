"""
Validators module
Input validation functions
"""

import re
import os
from werkzeug.datastructures import FileStorage


def validate_log_file(file: FileStorage, config):
    """
    Validate uploaded log file
    
    Args:
        file: Uploaded file
        config: Application config
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check file size
    max_size = config.get('MAX_UPLOAD_SIZE', 104857600)  # 100MB default
    
    # Check file extension
    allowed_extensions = config.get('ALLOWED_LOG_EXTENSIONS', ['log', 'txt', 'json'])
    
    filename = file.filename
    if not filename:
        return False, "No filename provided"
    
    # Check extension
    if '.' not in filename:
        return False, "File must have an extension"
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File extension '{extension}' not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    # Try to read first few bytes to check if file is readable
    try:
        file.stream.seek(0, os.SEEK_END)
        size = file.stream.tell()
        file.stream.seek(0)
        
        if size > max_size:
            return False, f"File size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        
        if size == 0:
            return False, "File is empty"
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"
    
    return True, None


def validate_log_data(data):
    """
    Validate log data from JSON payload
    
    Args:
        data: Log data (dict or list)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"
    
    # Ensure data is dict or list
    if not isinstance(data, (dict, list)):
        return False, "Data must be a dictionary or list"
    
    # If list, check each item
    if isinstance(data, list):
        if len(data) == 0:
            return False, "Empty list provided"
        
        for item in data:
            if not isinstance(item, dict):
                return False, "All list items must be dictionaries"
    
    # Validate required fields if single log entry
    if isinstance(data, dict):
        if 'message' not in data and 'log_type' not in data:
            return False, "Log entry must contain at least 'message' or 'log_type' field"
    
    return True, None


def validate_email(email: str):
    """
    Validate email address
    
    Args:
        email: Email address
    
    Returns:
        bool: True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_date_format(date_string: str):
    """
    Validate ISO date format
    
    Args:
        date_string: Date string
    
    Returns:
        bool: True if valid
    """
    try:
        from datetime import datetime
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def validate_transaction_data(data: dict):
    """
    Validate transaction data
    
    Args:
        data: Transaction data
    
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['transaction_id', 'user_id', 'amount', 'currency', 'payment_method']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount < 0:
            return False, "Amount must be positive"
    except (ValueError, TypeError):
        return False, "Invalid amount value"
    
    # Validate currency
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
    if data['currency'] not in valid_currencies:
        return False, f"Invalid currency. Allowed: {', '.join(valid_currencies)}"
    
    return True, None


def sanitize_string(text: str, max_length: int = 1000):
    """
    Sanitize string input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters
    text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()
