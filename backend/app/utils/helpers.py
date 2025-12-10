"""
Helpers module
General helper functions
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List


def generate_id(prefix: str = ""):
    """
    Generate unique ID
    
    Args:
        prefix: Optional prefix
    
    Returns:
        str: Unique ID
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def generate_hash(data: str):
    """
    Generate SHA256 hash
    
    Args:
        data: Data to hash
    
    Returns:
        str: Hash
    """
    return hashlib.sha256(data.encode()).hexdigest()


def parse_time_range(time_range: str):
    """
    Parse time range string (e.g., '7d', '24h', '30m')
    
    Args:
        time_range: Time range string
    
    Returns:
        timedelta: Time delta
    """
    units = {
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks'
    }
    
    if not time_range:
        return timedelta(days=7)  # Default
    
    try:
        value = int(time_range[:-1])
        unit = time_range[-1].lower()
        
        if unit in units:
            return timedelta(**{units[unit]: value})
    except (ValueError, KeyError):
        pass
    
    return timedelta(days=7)  # Default fallback


def calculate_date_range(time_range: str):
    """
    Calculate start and end dates from time range
    
    Args:
        time_range: Time range string
    
    Returns:
        tuple: (start_date, end_date)
    """
    delta = parse_time_range(time_range)
    end_date = datetime.utcnow()
    start_date = end_date - delta
    
    return start_date, end_date


def chunk_list(lst: List[Any], chunk_size: int):
    """
    Split list into chunks
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        generator: Chunks
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.'):
    """
    Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator
    
    Returns:
        dict: Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def safe_get(dictionary: Dict, *keys, default=None):
    """
    Safely get nested dictionary value
    
    Args:
        dictionary: Dictionary
        *keys: Keys to traverse
        default: Default value if not found
    
    Returns:
        Any: Value or default
    """
    result = dictionary
    
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    
    return result if result is not None else default


def merge_dicts(*dicts):
    """
    Merge multiple dictionaries
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        dict: Merged dictionary
    """
    result = {}
    
    for d in dicts:
        if d:
            result.update(d)
    
    return result


def calculate_percentage_change(old_value: float, new_value: float):
    """
    Calculate percentage change
    
    Args:
        old_value: Old value
        new_value: New value
    
    Returns:
        float: Percentage change
    """
    if old_value == 0:
        return 0.0 if new_value == 0 else 100.0
    
    return ((new_value - old_value) / old_value) * 100


def is_weekend(date: datetime = None):
    """
    Check if date is weekend
    
    Args:
        date: Date to check (defaults to today)
    
    Returns:
        bool: True if weekend
    """
    if date is None:
        date = datetime.utcnow()
    
    return date.weekday() >= 5  # Saturday = 5, Sunday = 6


def get_time_of_day(hour: int):
    """
    Get time of day classification
    
    Args:
        hour: Hour (0-23)
    
    Returns:
        str: Time of day (morning, afternoon, evening, night)
    """
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"
