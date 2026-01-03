"""
Comprehensive Authentication Test
Tests all protected routes with JWT tokens
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_complete_auth_flow():
    print("\n" + "="*60)
    print("  JWT AUTHENTICATION TEST SUITE")
    print("="*60 + "\n")
    
    # Test 1: Login
    print("1. Testing Login...")
    login_data = {"username": "admin", "password": "admin12345"}
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"   ✓ Token obtained: {token[:30]}...")
        else:
            print(f"   ✗ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return
    
    # Test 2: Dashboard
    print("\n2. Testing Dashboard (requires viewer+)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/dashboard/kpis",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Dashboard accessible")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 3: Search
    print("\n3. Testing Search (requires viewer+)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/search?q=test&size=5",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Search accessible")
        else:
            print(f"   ✗ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 4: Analytics
    print("\n4. Testing Analytics (requires analyst+)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/analytics/transactions",
            params={"start_date": "2024-01-01", "end_date": "2024-12-31"},
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Analytics accessible")
        else:
            print(f"   ✗ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test 5: No token
    print("\n5. Testing without token (should fail)...")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/kpis")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print(f"   ✓ Correctly rejected")
        else:
            print(f"   ✗ Should have been rejected: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("  TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_complete_auth_flow()
