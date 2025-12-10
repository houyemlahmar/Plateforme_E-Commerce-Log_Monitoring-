"""
Fraud model module
Defines fraud detection data structures
"""

from datetime import datetime
from typing import List, Optional, Dict, Any


class FraudDetection:
    """Fraud detection model"""
    
    def __init__(
        self,
        transaction_id: str,
        user_id: str,
        fraud_score: float,
        is_fraud: bool,
        indicators: List[str],
        timestamp: Optional[datetime] = None,
        transaction_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize fraud detection
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID
            fraud_score: Fraud score (0-100)
            is_fraud: Whether fraud was detected
            indicators: List of fraud indicators
            timestamp: Detection timestamp
            transaction_data: Associated transaction data
        """
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.fraud_score = fraud_score
        self.is_fraud = is_fraud
        self.indicators = indicators
        self.timestamp = timestamp or datetime.utcnow()
        self.transaction_data = transaction_data or {}
    
    def to_dict(self):
        """Convert fraud detection to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'fraud_score': self.fraud_score,
            'is_fraud': self.is_fraud,
            'indicators': self.indicators,
            'timestamp': self.timestamp.isoformat(),
            'transaction_data': self.transaction_data
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create fraud detection from dictionary"""
        return cls(
            transaction_id=data['transaction_id'],
            user_id=data['user_id'],
            fraud_score=data['fraud_score'],
            is_fraud=data['is_fraud'],
            indicators=data.get('indicators', []),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            transaction_data=data.get('transaction_data', {})
        )
    
    def get_risk_level(self):
        """Get risk level based on fraud score"""
        if self.fraud_score >= 75:
            return "HIGH"
        elif self.fraud_score >= 50:
            return "MEDIUM"
        elif self.fraud_score >= 25:
            return "LOW"
        else:
            return "MINIMAL"
    
    def requires_review(self):
        """Check if fraud detection requires manual review"""
        return self.fraud_score >= 50 or self.is_fraud
