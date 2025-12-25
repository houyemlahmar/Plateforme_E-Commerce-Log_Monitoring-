"""
Redis service module
Handles Redis caching operations
"""

import logging
import json
try:
    import redis  # type: ignore
    from redis.exceptions import RedisError  # type: ignore
except ImportError as e:
    raise ImportError("Redis package not installed. Run: pip install redis") from e

logger = logging.getLogger(__name__)


class RedisService:
    """Service for Redis caching operations"""
    
    def __init__(self, config):
        """
        Initialize Redis service
        
        Args:
            config: Redis configuration dictionary
        """
        self.config = config
        self.cache_ttl = config.get('cache_ttl', 3600)
        
        try:
            self.client = redis.Redis(
                host=config.get('host', 'localhost'),
                port=config.get('port', 6379),
                password=config.get('password') if config.get('password') else None,
                db=config.get('db', 0),
                decode_responses=True
            )
            
            # Test connection
            self.client.ping()
            logger.info("Successfully connected to Redis")
            
        except RedisError as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            raise
    
    def set(self, key, value, ttl=None):
        """
        Set a key-value pair
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        
        Returns:
            bool: Success status
        """
        try:
            if ttl is None:
                ttl = self.cache_ttl
            
            # Serialize complex objects to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            self.client.setex(key, ttl, value)
            return True
            
        except RedisError as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def get(self, key):
        """
        Get value by key
        
        Args:
            key: Cache key
        
        Returns:
            Value or None if not found
        """
        try:
            value = self.client.get(key)
            
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except RedisError as e:
            logger.error(f"Error getting cache: {str(e)}")
            return None
    
    def delete(self, key):
        """
        Delete a key
        
        Args:
            key: Cache key
        
        Returns:
            bool: Success status
        """
        try:
            self.client.delete(key)
            return True
            
        except RedisError as e:
            logger.error(f"Error deleting cache: {str(e)}")
            return False
    
    def exists(self, key):
        """
        Check if key exists
        
        Args:
            key: Cache key
        
        Returns:
            bool: True if key exists
        """
        try:
            return self.client.exists(key) > 0
            
        except RedisError as e:
            logger.error(f"Error checking cache existence: {str(e)}")
            return False
    
    def incr(self, key, amount=1):
        """
        Increment a counter
        
        Args:
            key: Cache key
            amount: Amount to increment
        
        Returns:
            int: New value
        """
        try:
            return self.client.incr(key, amount)
            
        except RedisError as e:
            logger.error(f"Error incrementing counter: {str(e)}")
            return None
    
    def expire(self, key, ttl):
        """
        Set expiration time for key
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
        
        Returns:
            bool: Success status
        """
        try:
            return self.client.expire(key, ttl)
            
        except RedisError as e:
            logger.error(f"Error setting expiration: {str(e)}")
            return False
    
    def lpush(self, key, *values):
        """
        Push values to the left (head) of a list
        
        Args:
            key: List key
            values: Values to push
        
        Returns:
            int: Length of list after push
        """
        try:
            return self.client.lpush(key, *values)
            
        except RedisError as e:
            logger.error(f"Error pushing to list: {str(e)}")
            return None
    
    def rpush(self, key, *values):
        """
        Push values to the right (tail) of a list
        
        Args:
            key: List key
            values: Values to push
        
        Returns:
            int: Length of list after push
        """
        try:
            return self.client.rpush(key, *values)
            
        except RedisError as e:
            logger.error(f"Error pushing to list: {str(e)}")
            return None
    
    def lpop(self, key):
        """
        Pop value from the left (head) of a list
        
        Args:
            key: List key
        
        Returns:
            Value or None if list is empty
        """
        try:
            value = self.client.lpop(key)
            if value:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
            
        except RedisError as e:
            logger.error(f"Error popping from list: {str(e)}")
            return None
    
    def rpop(self, key):
        """
        Pop value from the right (tail) of a list
        
        Args:
            key: List key
        
        Returns:
            Value or None if list is empty
        """
        try:
            value = self.client.rpop(key)
            if value:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
            
        except RedisError as e:
            logger.error(f"Error popping from list: {str(e)}")
            return None
    
    def llen(self, key):
        """
        Get length of a list
        
        Args:
            key: List key
        
        Returns:
            int: Length of list
        """
        try:
            return self.client.llen(key)
            
        except RedisError as e:
            logger.error(f"Error getting list length: {str(e)}")
            return 0
    
    def lrange(self, key, start=0, end=-1):
        """
        Get range of elements from a list
        
        Args:
            key: List key
            start: Start index
            end: End index (-1 for all)
        
        Returns:
            list: List elements
        """
        try:
            values = self.client.lrange(key, start, end)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
            return result
            
        except RedisError as e:
            logger.error(f"Error getting list range: {str(e)}")
            return []
    
    def flush_all(self):
        """
        Flush all keys from current database
        
        Returns:
            bool: Success status
        """
        try:
            self.client.flushdb()
            logger.warning("Flushed all keys from Redis")
            return True
            
        except RedisError as e:
            logger.error(f"Error flushing cache: {str(e)}")
            return False
