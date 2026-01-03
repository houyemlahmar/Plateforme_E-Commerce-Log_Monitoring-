"""
Test script for JWT authentication on protected routes
Tests that routes properly require authentication and respect role hierarchy
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'


def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_section(message):
    print(f"\n{Colors.YELLOW}{'=' * 60}")
    print(f"{message}")
    print(f"{'=' * 60}{Colors.END}\n")


def login(username, password):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data['access_token']
    return None


def test_route_without_auth(route, method='GET'):
    """Test that a route rejects requests without authentication"""
    print_info(f"Testing {method} {route} without auth...")
    
    if method == 'GET':
        response = requests.get(f"{BASE_URL}{route}")
    elif method == 'POST':
        response = requests.post(f"{BASE_URL}{route}", json={})
    
    if response.status_code == 401:
        print_success(f"Correctly rejected unauthenticated request")
        return True
    else:
        print_error(f"Should reject but got status {response.status_code}")
        return False


def test_route_with_auth(route, token, expected_status=200, method='GET'):
    """Test that a route accepts requests with valid authentication"""
    print_info(f"Testing {method} {route} with auth...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if method == 'GET':
        response = requests.get(f"{BASE_URL}{route}", headers=headers)
    elif method == 'POST':
        response = requests.post(f"{BASE_URL}{route}", headers=headers, json={})
    
    if response.status_code == expected_status:
        print_success(f"Got expected status {expected_status}")
        return True
    else:
        print_error(f"Expected {expected_status} but got {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return False


def test_route_with_insufficient_role(route, token, method='GET'):
    """Test that a route rejects requests with insufficient role"""
    print_info(f"Testing {method} {route} with insufficient role...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if method == 'GET':
        response = requests.get(f"{BASE_URL}{route}", headers=headers)
    elif method == 'POST':
        response = requests.post(f"{BASE_URL}{route}", headers=headers, json={})
    
    if response.status_code == 403:
        print_success(f"Correctly rejected request with insufficient role")
        return True
    else:
        print_error(f"Should reject with 403 but got {response.status_code}")
        return False


def main():
    print_section("JWT Authentication Test - Protected Routes")
    
    # Login with different roles
    print_info("Logging in with different user roles...")
    admin_token = login("admin", "admin12345")
    analyst_token = login("analyst_demo", "analyst123")
    viewer_token = login("viewer_demo", "viewer123")
    
    if not admin_token:
        print_error("Failed to login as admin")
        return
    if not analyst_token:
        print_error("Failed to login as analyst")
        return
    if not viewer_token:
        print_error("Failed to login as viewer")
        return
    
    print_success("Successfully logged in with all roles")
    
    results = {
        'passed': 0,
        'failed': 0
    }
    
    # Test 1: Dashboard routes (require viewer+)
    print_section("Test 1: Dashboard Routes (Require Viewer Role)")
    
    dashboard_routes = [
        '/dashboard',
        '/api/dashboard/kpis',
        '/api/dashboard/overview',
        '/api/dashboard/metrics'
    ]
    
    for route in dashboard_routes:
        # Test without auth
        if test_route_without_auth(route):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Test with viewer (should work)
        if test_route_with_auth(route, viewer_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Test with analyst (should work - higher role)
        if test_route_with_auth(route, analyst_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 2: Analytics routes (require analyst+)
    print_section("Test 2: Analytics Routes (Require Analyst Role)")
    
    analytics_routes = [
        '/api/analytics/transactions',
        '/api/analytics/errors',
        '/api/analytics/user-behavior'
    ]
    
    for route in analytics_routes:
        # Test without auth
        if test_route_without_auth(route):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Test with viewer (should fail)
        if test_route_with_insufficient_role(route, viewer_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Test with analyst (should work)
        if test_route_with_auth(route, analyst_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 3: Search routes (require viewer+)
    print_section("Test 3: Search Routes (Require Viewer Role)")
    
    search_routes = [
        '/api/search',
        '/api/search/autocomplete?q=test'
    ]
    
    for route in search_routes:
        # Test without auth
        if test_route_without_auth(route):
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Test with viewer (should work)
        if test_route_with_auth(route, viewer_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Test 4: Log upload (require analyst+)
    print_section("Test 4: Log Upload (Requires Analyst Role)")
    
    # Test without auth
    if test_route_without_auth('/api/logs/upload', 'POST'):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test with viewer (should fail)
    if test_route_with_insufficient_role('/api/logs/upload', viewer_token, 'POST'):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test with analyst (should work - though might fail for other reasons like missing file)
    print_info("Testing POST /api/logs/upload with analyst auth...")
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = requests.post(f"{BASE_URL}/api/logs/upload", headers=headers)
    # Should not be 401 or 403 (auth passed), might be 400 (missing file)
    if response.status_code not in [401, 403]:
        print_success(f"Authentication passed (got {response.status_code} for missing file)")
        results['passed'] += 1
    else:
        print_error(f"Authentication failed with {response.status_code}")
        results['failed'] += 1
    
    # Summary
    print_section("Test Summary")
    print(f"Total Passed: {Colors.GREEN}{results['passed']}{Colors.END}")
    print(f"Total Failed: {Colors.RED}{results['failed']}{Colors.END}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}🎉 All authentication tests passed!{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}⚠ Some tests failed{Colors.END}\n")


if __name__ == '__main__':
    main()
