"""
Log model module
Defines log data structures
"""

from datetime import datetime
from typing import Optional, Dict, Any


class LogEntry:
    """Base log entry model"""
    
    def __init__(
        self,
        message: str,
        log_type: str,
        timestamp: Optional[datetime] = None,
        level: str = "INFO",
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize log entry
        
        Args:
            message: Log message
            log_type: Type of log (transaction, error, user_behavior, etc.)
            timestamp: Log timestamp
            level: Log level (INFO, WARNING, ERROR, etc.)
            source: Source of the log
            metadata: Additional metadata
        """
        self.message = message
        self.log_type = log_type
        self.timestamp = timestamp or datetime.utcnow()
        self.level = level
        self.source = source
        self.metadata = metadata or {}
    
    def to_dict(self):
        """Convert log entry to dictionary"""
        return {
            '@timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'log_type': self.log_type,
            'level': self.level,
            'source': self.source,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create log entry from dictionary"""
        return cls(
            message=data.get('message', ''),
            log_type=data.get('log_type', 'unknown'),
            timestamp=datetime.fromisoformat(data.get('@timestamp')) if data.get('@timestamp') else None,
            level=data.get('level', 'INFO'),
            source=data.get('source'),
            metadata=data.get('metadata', {})
        )


class TransactionLog(LogEntry):
    """Transaction log model"""
    
    def __init__(
        self,
        transaction_id: str,
        user_id: str,
        amount: float,
        currency: str,
        payment_method: str,
        status: str,
        **kwargs
    ):
        """
        Initialize transaction log
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID
            amount: Transaction amount
            currency: Currency code
            payment_method: Payment method
            status: Transaction status
        """
        super().__init__(
            message=f"Transaction {transaction_id} - {status}",
            log_type="transaction",
            **kwargs
        )
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.amount = amount
        self.currency = currency
        self.payment_method = payment_method
        self.status = status
    
    def to_dict(self):
        """Convert transaction log to dictionary"""
        data = super().to_dict()
        data.update({
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status
        })
        return data


class ErrorLog(LogEntry):
    """Error log model"""
    
    def __init__(
        self,
        error_code: int,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize error log
        
        Args:
            error_code: HTTP error code or custom error code
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace (if available)
        """
        super().__init__(
            message=error_message,
            log_type="error",
            level="ERROR",
            **kwargs
        )
        self.error_code = error_code
        self.error_type = error_type
        self.error_message = error_message
        self.stack_trace = stack_trace
    
    def to_dict(self):
        """Convert error log to dictionary"""
        data = super().to_dict()
        data.update({
            'error_code': self.error_code,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'stack_trace': self.stack_trace
        })
        return data


class PerformanceLog(LogEntry):
    """Performance log model"""
    
    def __init__(
        self,
        endpoint: str,
        response_time: float,
        method: str,
        status_code: int,
        db_query_time: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize performance log
        
        Args:
            endpoint: API endpoint or page
            response_time: Response time in milliseconds
            method: HTTP method
            status_code: HTTP status code
            db_query_time: Database query time in milliseconds
        """
        super().__init__(
            message=f"{method} {endpoint} - {response_time}ms",
            log_type="performance",
            **kwargs
        )
        self.endpoint = endpoint
        self.response_time = response_time
        self.method = method
        self.status_code = status_code
        self.db_query_time = db_query_time
    
    def to_dict(self):
        """Convert performance log to dictionary"""
        data = super().to_dict()
        data.update({
            'endpoint': self.endpoint,
            'response_time': self.response_time,
            'method': self.method,
            'status_code': self.status_code,
            'db_query_time': self.db_query_time
        })
        return data
