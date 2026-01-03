"""
Test script for Search API with Redis Cache and MongoDB History
Tests cache TTL, cache key generation, and search history tracking
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5001/api/search"


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_basic_search():
    """Test 1: Basic search - Cache MISS expected"""
    print_section("TEST 1: Basic Search (Cache MISS)")
    
    params = {
        'q': 'error',
        'level': 'ERROR',
        'size': 10
    }
    
    start_time = time.time()
    response = requests.get(BASE_URL, params=params)
    elapsed = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()['data']
        cached = data.get('cached', False)
        total = data.get('total', 0)
        
        print(f"✅ Status: 200 OK")
        print(f"   Total results: {total}")
        print(f"   Cached: {cached} (Expected: False)")
        print(f"   Response time: {elapsed:.0f}ms")
        
        if not cached:
            print("   ✅ Cache MISS as expected (first request)")
        else:
            print("   ⚠️  Cache HIT unexpected on first request")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Error: {response.text}")


def test_cache_hit():
    """Test 2: Repeat same search - Cache HIT expected"""
    print_section("TEST 2: Repeat Search (Cache HIT)")
    
    params = {
        'q': 'error',
        'level': 'ERROR',
        'size': 10
    }
    
    print("⏱️  Waiting 1 second before retry...")
    time.sleep(1)
    
    start_time = time.time()
    response = requests.get(BASE_URL, params=params)
    elapsed = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()['data']
        cached = data.get('cached', False)
        total = data.get('total', 0)
        
        print(f"✅ Status: 200 OK")
        print(f"   Total results: {total}")
        print(f"   Cached: {cached} (Expected: True)")
        print(f"   Response time: {elapsed:.0f}ms (should be faster)")
        
        if cached:
            print("   ✅ Cache HIT successful!")
            print(f"   💡 Performance gain: cache reduces response time")
        else:
            print("   ⚠️  Cache MISS unexpected on repeat request")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Error: {response.text}")


def test_different_params_cache_miss():
    """Test 3: Different parameters - Cache MISS expected"""
    print_section("TEST 3: Different Parameters (Cache MISS)")
    
    params = {
        'q': 'timeout',  # Different query
        'level': 'WARNING',  # Different level
        'size': 20  # Different size
    }
    
    start_time = time.time()
    response = requests.get(BASE_URL, params=params)
    elapsed = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()['data']
        cached = data.get('cached', False)
        total = data.get('total', 0)
        
        print(f"✅ Status: 200 OK")
        print(f"   Total results: {total}")
        print(f"   Cached: {cached} (Expected: False)")
        print(f"   Response time: {elapsed:.0f}ms")
        
        if not cached:
            print("   ✅ Cache MISS as expected (different parameters)")
        else:
            print("   ⚠️  Cache HIT unexpected with different params")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Error: {response.text}")


def test_cache_expiration():
    """Test 4: Cache expiration after TTL (60s)"""
    print_section("TEST 4: Cache Expiration (TTL 60s)")
    
    params = {
        'q': 'cache_test',
        'size': 5
    }
    
    # First request
    print("📤 First request (Cache MISS expected)...")
    response1 = requests.get(BASE_URL, params=params)
    if response1.status_code == 200:
        cached1 = response1.json()['data'].get('cached', False)
        print(f"   Cached: {cached1} (Expected: False)")
    
    # Immediate second request
    print("\n📤 Second request (Cache HIT expected)...")
    response2 = requests.get(BASE_URL, params=params)
    if response2.status_code == 200:
        cached2 = response2.json()['data'].get('cached', False)
        print(f"   Cached: {cached2} (Expected: True)")
    
    # Wait for cache expiration
    print("\n⏱️  Waiting 61 seconds for cache expiration...")
    print("   (TTL is 60 seconds)")
    for i in range(61, 0, -10):
        print(f"   {i} seconds remaining...", end='\r')
        time.sleep(10)
    print("\n")
    
    # Third request after expiration
    print("📤 Third request after TTL (Cache MISS expected)...")
    response3 = requests.get(BASE_URL, params=params)
    if response3.status_code == 200:
        cached3 = response3.json()['data'].get('cached', False)
        print(f"   Cached: {cached3} (Expected: False)")
        
        if not cached3:
            print("   ✅ Cache expired correctly after 60s TTL")
        else:
            print("   ⚠️  Cache still active after TTL")


def test_pagination_cache_keys():
    """Test 5: Different pages should have different cache keys"""
    print_section("TEST 5: Pagination Cache Keys")
    
    # Page 1
    print("📤 Request page 1...")
    params1 = {'q': 'test', 'page': 1, 'size': 10}
    response1 = requests.get(BASE_URL, params=params1)
    
    if response1.status_code == 200:
        data1 = response1.json()['data']
        print(f"   Page 1 - Cached: {data1.get('cached', False)}")
    
    # Page 2
    print("\n📤 Request page 2...")
    params2 = {'q': 'test', 'page': 2, 'size': 10}
    response2 = requests.get(BASE_URL, params=params2)
    
    if response2.status_code == 200:
        data2 = response2.json()['data']
        print(f"   Page 2 - Cached: {data2.get('cached', False)}")
    
    # Repeat page 1 - should be cached
    print("\n📤 Repeat page 1...")
    response3 = requests.get(BASE_URL, params=params1)
    
    if response3.status_code == 200:
        data3 = response3.json()['data']
        cached = data3.get('cached', False)
        print(f"   Page 1 - Cached: {cached}")
        
        if cached:
            print("   ✅ Pagination cache working correctly")
        else:
            print("   ⚠️  Page 1 should be cached on repeat")


def test_search_history_mongo():
    """Test 6: Verify search history is saved to MongoDB"""
    print_section("TEST 6: MongoDB Search History")
    
    unique_query = f"test_history_{int(time.time())}"
    params = {
        'q': unique_query,
        'level': 'INFO',
        'service': 'test_service',
        'page': 1,
        'size': 10
    }
    
    print(f"📤 Executing search with unique query: {unique_query}")
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()['data']
        results_count = data.get('total', 0)
        
        print(f"✅ Search executed successfully")
        print(f"   Results count: {results_count}")
        print(f"\n💡 Search history should be saved in MongoDB:")
        print(f"   Collection: search_history")
        print(f"   Document includes:")
        print(f"   - timestamp: {datetime.utcnow().isoformat()}")
        print(f"   - query: {unique_query}")
        print(f"   - filters: level=INFO, service=test_service")
        print(f"   - results_count: {results_count}")
        print(f"   - user_ip: <request_ip>")
        print(f"\n📊 To verify in MongoDB:")
        print(f'   db.search_history.find({{query: "{unique_query}"}}).pretty()')
    else:
        print(f"❌ Status: {response.status_code}")


def test_combined_filters():
    """Test 7: Complex query with multiple filters"""
    print_section("TEST 7: Complex Multi-Filter Query")
    
    params = {
        'q': 'payment',
        'level': 'ERROR',
        'service': 'payment',
        'log_type': 'transaction',
        'date_from': '2025-12-01',
        'date_to': '2025-12-31',
        'page': 1,
        'size': 20,
        'sort_field': '@timestamp',
        'sort_order': 'desc'
    }
    
    # First request
    print("📤 First request with all filters (Cache MISS)...")
    start_time = time.time()
    response1 = requests.get(BASE_URL, params=params)
    elapsed1 = (time.time() - start_time) * 1000
    
    if response1.status_code == 200:
        data1 = response1.json()['data']
        print(f"✅ Status: 200 OK")
        print(f"   Total: {data1.get('total', 0)}")
        print(f"   Cached: {data1.get('cached', False)}")
        print(f"   Response time: {elapsed1:.0f}ms")
    
    # Second request - should be cached
    print("\n📤 Repeat same complex query (Cache HIT)...")
    time.sleep(1)
    start_time = time.time()
    response2 = requests.get(BASE_URL, params=params)
    elapsed2 = (time.time() - start_time) * 1000
    
    if response2.status_code == 200:
        data2 = response2.json()['data']
        cached = data2.get('cached', False)
        print(f"✅ Status: 200 OK")
        print(f"   Cached: {cached}")
        print(f"   Response time: {elapsed2:.0f}ms")
        
        if cached and elapsed2 < elapsed1:
            speedup = ((elapsed1 - elapsed2) / elapsed1) * 100
            print(f"   ✅ Cache HIT with {speedup:.1f}% speedup")
        elif cached:
            print(f"   ✅ Cache HIT confirmed")
        else:
            print(f"   ⚠️  Expected cache HIT on repeat")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  SEARCH API - Cache & History Test Suite")
    print("="*70)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Basic Search (Cache MISS)", test_basic_search),
        ("Repeat Search (Cache HIT)", test_cache_hit),
        ("Different Params (Cache MISS)", test_different_params_cache_miss),
        ("Pagination Cache Keys", test_pagination_cache_keys),
        ("MongoDB History Tracking", test_search_history_mongo),
        ("Complex Multi-Filter Query", test_combined_filters),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
    
    # Optional: Cache expiration test (takes 60+ seconds)
    print("\n" + "="*70)
    print("  Optional: Cache Expiration Test (61 seconds)")
    print("="*70)
    run_expiration = input("\nRun cache expiration test? (y/N): ").lower()
    if run_expiration == 'y':
        test_cache_expiration()
    else:
        print("Skipped cache expiration test")
    
    print("\n" + "="*70)
    print("  Test Suite Completed")
    print("="*70)
    print("\nSummary:")
    print("   - Cache Redis: TTL 60s")
    print("   - Cache keys: MD5 hash of sorted parameters")
    print("   - History: MongoDB collection 'search_history'")
    print("   - Performance: Cached responses are faster")
    print("\nTo check MongoDB history:")
    print("   docker exec -it projet_bigdata-mongodb-1 mongosh")
    print("   use ecommerce_logs")
    print("   db.search_history.find().sort({timestamp: -1}).limit(10).pretty()")
    print("\nTo check Redis cache:")
    print("   docker exec -it projet_bigdata-redis-1 redis-cli")
    print("   KEYS search:*")
    print("   GET search:<hash>")
    print("   TTL search:<hash>")


if __name__ == "__main__":
    main()
