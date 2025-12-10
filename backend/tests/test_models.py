"""
Tests for models
"""

import pytest
from datetime import datetime
from app.models.log_model import LogEntry, TransactionLog, ErrorLog, PerformanceLog
from app.models.transaction_model import Transaction
from app.models.fraud_model import FraudDetection


class TestLogModels:
    """Test cases for log models"""
    
    def test_log_entry_creation(self):
        """Test log entry creation"""
        log = LogEntry(
            message="Test message",
            log_type="test",
            level="INFO"
        )
        
        assert log.message == "Test message"
        assert log.log_type == "test"
        assert log.level == "INFO"
        assert log.timestamp is not None
    
    def test_log_entry_to_dict(self):
        """Test log entry to dictionary"""
        log = LogEntry(
            message="Test message",
            log_type="test"
        )
        
        data = log.to_dict()
        assert '@timestamp' in data
        assert data['message'] == "Test message"
        assert data['log_type'] == "test"
    
    def test_transaction_log_creation(self):
        """Test transaction log creation"""
        log = TransactionLog(
            transaction_id="TXN123",
            user_id="USER123",
            amount=100.0,
            currency="USD",
            payment_method="credit_card",
            status="completed"
        )
        
        assert log.transaction_id == "TXN123"
        assert log.amount == 100.0
        assert log.log_type == "transaction"
    
    def test_error_log_creation(self):
        """Test error log creation"""
        log = ErrorLog(
            error_code=500,
            error_type="InternalServerError",
            error_message="Something went wrong"
        )
        
        assert log.error_code == 500
        assert log.error_type == "InternalServerError"
        assert log.level == "ERROR"
    
    def test_performance_log_creation(self):
        """Test performance log creation"""
        log = PerformanceLog(
            endpoint="/api/users",
            response_time=250.5,
            method="GET",
            status_code=200
        )
        
        assert log.endpoint == "/api/users"
        assert log.response_time == 250.5
        assert log.log_type == "performance"


class TestTransactionModel:
    """Test cases for transaction model"""
    
    def test_transaction_creation(self):
        """Test transaction creation"""
        txn = Transaction(
            transaction_id="TXN123",
            user_id="USER123",
            amount=150.0,
            currency="USD",
            payment_method="credit_card",
            status="completed"
        )
        
        assert txn.transaction_id == "TXN123"
        assert txn.amount == 150.0
        assert txn.currency == "USD"
    
    def test_transaction_to_dict(self):
        """Test transaction to dictionary"""
        txn = Transaction(
            transaction_id="TXN123",
            user_id="USER123",
            amount=150.0
        )
        
        data = txn.to_dict()
        assert data['transaction_id'] == "TXN123"
        assert data['amount'] == 150.0
    
    def test_is_high_value(self):
        """Test high value transaction check"""
        txn1 = Transaction(
            transaction_id="TXN1",
            user_id="USER1",
            amount=500.0
        )
        txn2 = Transaction(
            transaction_id="TXN2",
            user_id="USER2",
            amount=1500.0
        )
        
        assert not txn1.is_high_value()
        assert txn2.is_high_value()
    
    def test_transaction_status_checks(self):
        """Test transaction status checks"""
        txn_success = Transaction(
            transaction_id="TXN1",
            user_id="USER1",
            amount=100.0,
            status="completed"
        )
        txn_failed = Transaction(
            transaction_id="TXN2",
            user_id="USER2",
            amount=100.0,
            status="failed"
        )
        
        assert txn_success.is_successful()
        assert not txn_success.is_failed()
        assert txn_failed.is_failed()
        assert not txn_failed.is_successful()


class TestFraudModel:
    """Test cases for fraud model"""
    
    def test_fraud_detection_creation(self):
        """Test fraud detection creation"""
        fraud = FraudDetection(
            transaction_id="TXN123",
            user_id="USER123",
            fraud_score=85.5,
            is_fraud=True,
            indicators=["high_amount", "suspicious_location"]
        )
        
        assert fraud.transaction_id == "TXN123"
        assert fraud.fraud_score == 85.5
        assert fraud.is_fraud is True
        assert len(fraud.indicators) == 2
    
    def test_get_risk_level(self):
        """Test risk level calculation"""
        fraud_high = FraudDetection(
            transaction_id="TXN1",
            user_id="USER1",
            fraud_score=80,
            is_fraud=True,
            indicators=[]
        )
        fraud_medium = FraudDetection(
            transaction_id="TXN2",
            user_id="USER2",
            fraud_score=60,
            is_fraud=False,
            indicators=[]
        )
        fraud_low = FraudDetection(
            transaction_id="TXN3",
            user_id="USER3",
            fraud_score=30,
            is_fraud=False,
            indicators=[]
        )
        
        assert fraud_high.get_risk_level() == "HIGH"
        assert fraud_medium.get_risk_level() == "MEDIUM"
        assert fraud_low.get_risk_level() == "LOW"
    
    def test_requires_review(self):
        """Test requires review check"""
        fraud1 = FraudDetection(
            transaction_id="TXN1",
            user_id="USER1",
            fraud_score=80,
            is_fraud=True,
            indicators=[]
        )
        fraud2 = FraudDetection(
            transaction_id="TXN2",
            user_id="USER2",
            fraud_score=55,
            is_fraud=False,
            indicators=[]
        )
        fraud3 = FraudDetection(
            transaction_id="TXN3",
            user_id="USER3",
            fraud_score=20,
            is_fraud=False,
            indicators=[]
        )
        
        assert fraud1.requires_review()
        assert fraud2.requires_review()
        assert not fraud3.requires_review()
