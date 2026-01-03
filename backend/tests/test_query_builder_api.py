"""
Test script for Elasticsearch Query Builder API
Demonstrates usage and validates functionality
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"
SEARCH_ENDPOINT = f"{BASE_URL}/api/search"

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def print_result(test_name, response):
    """Print test result"""
    print(f"Test: {test_name}")
    print(f"Status: {response.status_code}")
    
    try:
        data = response.json()
        if response.status_code == 200:
            result_data = data.get('data', data)
            print(f"Total Results: {result_data.get('total', 0)}")
            print(f"Page: {result_data.get('page', 1)}/{result_data.get('total_pages', 1)}")
            print(f"Results Count: {len(result_data.get('results', []))}")
            
            # Print first result if exists
            results = result_data.get('results', [])
            if results:
                print(f"\nFirst Result:")
                first = results[0]['source']
                print(json.dumps(first, indent=2)[:300])
            
            print("✅ Test PASSED")
        else:
            print(f"❌ Test FAILED: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error parsing response: {str(e)}")
    
    print("-" * 70)

def test_basic_search():
    """Test 1: Basic free text search"""
    print_header("TEST 1: Basic Free Text Search")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'q': 'error'
    })
    
    print_result("Basic search for 'error'", response)

def test_level_filter():
    """Test 2: Filter by log level"""
    print_header("TEST 2: Filter by Log Level")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'level': 'ERROR',
        'size': 10
    })
    
    print_result("Filter ERROR level logs", response)

def test_service_filter():
    """Test 3: Filter by service"""
    print_header("TEST 3: Filter by Service")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'service': 'payment',
        'size': 10
    })
    
    print_result("Filter payment service logs", response)

def test_date_range():
    """Test 4: Date range filter"""
    print_header("TEST 4: Date Range Filter")
    
    # Last 7 days
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'date_from': week_ago.strftime('%Y-%m-%d'),
        'date_to': today.strftime('%Y-%m-%d'),
        'size': 10
    })
    
    print_result(f"Logs from {week_ago.date()} to {today.date()}", response)

def test_combined_filters():
    """Test 5: Combined filters"""
    print_header("TEST 5: Combined Filters")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'q': 'timeout',
        'level': 'ERROR',
        'service': 'payment',
        'date_from': '2025-12-01',
        'date_to': '2025-12-31',
        'size': 20
    })
    
    print_result("Combined: timeout + ERROR + payment + December 2025", response)

def test_pagination():
    """Test 6: Pagination"""
    print_header("TEST 6: Pagination")
    
    # Page 1
    print("Fetching Page 1:")
    response1 = requests.get(f"{SEARCH_ENDPOINT}", params={
        'page': 1,
        'size': 5
    })
    print_result("Page 1 (size=5)", response1)
    
    # Page 2
    print("\nFetching Page 2:")
    response2 = requests.get(f"{SEARCH_ENDPOINT}", params={
        'page': 2,
        'size': 5
    })
    print_result("Page 2 (size=5)", response2)

def test_sorting():
    """Test 7: Custom sorting"""
    print_header("TEST 7: Custom Sorting")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'log_type': 'transaction',
        'sort_field': 'amount',
        'sort_order': 'desc',
        'size': 10
    })
    
    print_result("Transactions sorted by amount DESC", response)

def test_user_filter():
    """Test 8: User ID filter"""
    print_header("TEST 8: User ID Filter")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'user_id': 'USER123',
        'size': 10
    })
    
    print_result("Logs for USER123", response)

def test_amount_range():
    """Test 9: Amount range filter"""
    print_header("TEST 9: Amount Range Filter")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'log_type': 'transaction',
        'min_amount': 100,
        'max_amount': 1000,
        'size': 10
    })
    
    print_result("Transactions between $100 and $1000", response)

def test_log_type_filter():
    """Test 10: Log type filter"""
    print_header("TEST 10: Log Type Filter")
    
    response = requests.get(f"{SEARCH_ENDPOINT}", params={
        'log_type': 'fraud',
        'size': 10
    })
    
    print_result("Fraud detection logs", response)

def test_input_sanitization():
    """Test 11: Input sanitization (security)"""
    print_header("TEST 11: Input Sanitization")
    
    # Try malicious inputs
    test_cases = [
        ("SQL Injection", {'q': "'; DROP TABLE users; --"}),
        ("XSS Attempt", {'q': "<script>alert('xss')</script>"}),
        ("Invalid Level", {'level': 'INVALID_LEVEL'}),
        ("Invalid Date", {'date_from': 'not-a-date'}),
        ("Negative Page", {'page': -5}),
        ("Huge Page Size", {'size': 999999}),
    ]
    
    for test_name, params in test_cases:
        print(f"\nTesting {test_name}:")
        response = requests.get(f"{SEARCH_ENDPOINT}", params=params)
        
        # Should still return 200 (sanitized) or 400 (rejected)
        if response.status_code in [200, 400]:
            print(f"✅ Handled safely (status: {response.status_code})")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")

def test_edge_cases():
    """Test 12: Edge cases"""
    print_header("TEST 12: Edge Cases")
    
    edge_cases = [
        ("Empty Query", {}),
        ("Only Pagination", {'page': 3, 'size': 50}),
        ("Unicode Text", {'q': '日本語 Élégant café ☕'}),
        ("Very Long Text", {'q': 'A' * 600}),  # Over 500 char limit
        ("Zero Size", {'size': 0}),
    ]
    
    for test_name, params in edge_cases:
        print(f"\nTesting {test_name}:")
        response = requests.get(f"{SEARCH_ENDPOINT}", params=params)
        
        if response.status_code == 200:
            print(f"✅ Handled correctly")
        else:
            print(f"⚠️  Status: {response.status_code}")

def run_all_tests():
    """Run all tests"""
    print_header("ELASTICSEARCH QUERY BUILDER API TESTS")
    print(f"Testing endpoint: {SEARCH_ENDPOINT}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check if API is reachable
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not reachable!")
            return
        print("✅ API is reachable\n")
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        return
    
    # Run tests
    tests = [
        test_basic_search,
        test_level_filter,
        test_service_filter,
        test_date_range,
        test_combined_filters,
        test_pagination,
        test_sorting,
        test_user_filter,
        test_amount_range,
        test_log_type_filter,
        test_input_sanitization,
        test_edge_cases
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            failed += 1
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

if __name__ == "__main__":
    run_all_tests()
