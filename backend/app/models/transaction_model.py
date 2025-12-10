"""
Transaction model module
Defines transaction data structures
"""

from datetime import datetime
from typing import Optional, Dict, Any


class Transaction:
    """Transaction model"""
    
    def __init__(
        self,
        transaction_id: str,
        user_id: str,
        amount: float,
        currency: str = "USD",
        payment_method: str = "credit_card",
        status: str = "pending",
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize transaction
        
        Args:
            transaction_id: Unique transaction ID
            user_id: User ID
            amount: Transaction amount
            currency: Currency code
            payment_method: Payment method
            status: Transaction status
            timestamp: Transaction timestamp
            metadata: Additional metadata
        """
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.amount = amount
        self.currency = currency
        self.payment_method = payment_method
        self.status = status
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create transaction from dictionary"""
        return cls(
            transaction_id=data['transaction_id'],
            user_id=data['user_id'],
            amount=data['amount'],
            currency=data.get('currency', 'USD'),
            payment_method=data.get('payment_method', 'credit_card'),
            status=data.get('status', 'pending'),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            metadata=data.get('metadata', {})
        )
    
    def is_high_value(self, threshold: float = 1000.0):
        """Check if transaction is high value"""
        return self.amount >= threshold
    
    def is_successful(self):
        """Check if transaction is successful"""
        return self.status in ['completed', 'success']
    
    def is_failed(self):
        """Check if transaction failed"""
        return self.status in ['failed', 'error', 'declined']
