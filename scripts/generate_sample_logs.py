#!/usr/bin/env python3
"""
Script to generate sample logs for testing
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


def generate_transaction_log():
    """Generate a sample transaction log"""
    transaction_types = ['purchase', 'refund', 'subscription']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'apple_pay']
    statuses = ['completed', 'pending', 'failed', 'declined']
    currencies = ['USD', 'EUR', 'GBP']
    
    return {
        '@timestamp': datetime.utcnow().isoformat(),
        'log_type': 'transaction',
        'transaction_id': f"TXN{random.randint(10000, 99999)}",
        'user_id': f"USER{random.randint(1000, 9999)}",
        'amount': round(random.uniform(10, 5000), 2),
        'currency': random.choice(currencies),
        'payment_method': random.choice(payment_methods),
        'status': random.choice(statuses),
        'transaction_type': random.choice(transaction_types),
        'merchant_id': f"MERCHANT{random.randint(100, 999)}"
    }


def generate_error_log():
    """Generate a sample error log"""
    error_codes = [400, 404, 500, 502, 503]
    error_types = ['ValidationError', 'DatabaseError', 'NetworkError', 'AuthenticationError']
    
    return {
        '@timestamp': datetime.utcnow().isoformat(),
        'log_type': 'error',
        'error_code': random.choice(error_codes),
        'error_type': random.choice(error_types),
        'error_message': 'An error occurred during processing',
        'endpoint': f"/api/{random.choice(['users', 'transactions', 'products'])}",
        'user_id': f"USER{random.randint(1000, 9999)}",
        'stack_trace': 'Error stack trace here...'
    }


def generate_user_behavior_log():
    """Generate a sample user behavior log"""
    actions = ['page_view', 'add_to_cart', 'remove_from_cart', 'checkout', 'cart_abandoned']
    pages = ['/home', '/products', '/cart', '/checkout', '/profile']
    
    return {
        '@timestamp': datetime.utcnow().isoformat(),
        'log_type': 'user_behavior',
        'user_id': f"USER{random.randint(1000, 9999)}",
        'action': random.choice(actions),
        'page': random.choice(pages),
        'session_id': f"SESSION{random.randint(100000, 999999)}",
        'duration_ms': random.randint(100, 30000),
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }


def generate_performance_log():
    """Generate a sample performance log"""
    endpoints = ['/api/users', '/api/products', '/api/transactions', '/api/search']
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    
    return {
        '@timestamp': datetime.utcnow().isoformat(),
        'log_type': 'performance',
        'endpoint': random.choice(endpoints),
        'method': random.choice(methods),
        'response_time': round(random.uniform(10, 2000), 2),
        'status_code': random.choice([200, 201, 400, 404, 500]),
        'db_query_time': round(random.uniform(5, 500), 2),
        'cache_hit': random.choice([True, False])
    }


def generate_fraud_log():
    """Generate a sample fraud detection log"""
    indicators = [
        'high_amount',
        'rapid_transactions',
        'suspicious_location',
        'ip_mismatch',
        'multiple_failed_attempts'
    ]
    
    return {
        '@timestamp': datetime.utcnow().isoformat(),
        'log_type': 'fraud',
        'transaction_id': f"TXN{random.randint(10000, 99999)}",
        'user_id': f"USER{random.randint(1000, 9999)}",
        'fraud_score': random.randint(50, 100),
        'fraud_detected': random.choice([True, False]),
        'fraud_indicators': random.sample(indicators, random.randint(1, 3)),
        'amount': round(random.uniform(1000, 20000), 2),
        'location': random.choice(['US', 'UK', 'XX', 'YY'])
    }


def generate_logs(num_logs=1000, output_file='sample_logs.json'):
    """
    Generate sample logs
    
    Args:
        num_logs: Number of logs to generate
        output_file: Output file path
    """
    log_generators = [
        (generate_transaction_log, 0.4),  # 40% transactions
        (generate_error_log, 0.15),       # 15% errors
        (generate_user_behavior_log, 0.25),  # 25% user behavior
        (generate_performance_log, 0.15),  # 15% performance
        (generate_fraud_log, 0.05)        # 5% fraud
    ]
    
    logs = []
    
    for i in range(num_logs):
        # Select log type based on distribution
        rand = random.random()
        cumulative = 0
        
        for generator, weight in log_generators:
            cumulative += weight
            if rand <= cumulative:
                logs.append(generator())
                break
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{num_logs} logs...")
    
    # Write to file
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w') as f:
        for log in logs:
            f.write(json.dumps(log) + '\n')
    
    print(f"\nGenerated {num_logs} logs to {output_path}")
    
    # Print summary
    log_types = {}
    for log in logs:
        log_type = log.get('log_type', 'unknown')
        log_types[log_type] = log_types.get(log_type, 0) + 1
    
    print("\nLog type distribution:")
    for log_type, count in sorted(log_types.items()):
        percentage = (count / num_logs) * 100
        print(f"  {log_type}: {count} ({percentage:.1f}%)")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample logs for testing')
    parser.add_argument('-n', '--num-logs', type=int, default=1000,
                        help='Number of logs to generate (default: 1000)')
    parser.add_argument('-o', '--output', type=str, default='sample_logs.json',
                        help='Output file name (default: sample_logs.json)')
    
    args = parser.parse_args()
    
    generate_logs(num_logs=args.num_logs, output_file=args.output)
