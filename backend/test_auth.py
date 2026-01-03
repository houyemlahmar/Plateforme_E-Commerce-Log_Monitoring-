"""
Test script for JWT authentication endpoints
Demonstrates registration, login, token usage, and role-based access
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api/auth"

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


def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_response(response, title="Response"):
    """Print formatted response"""
    print(f"\n{Colors.BLUE}--- {title} ---{Colors.END}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")
    print()


def test_register():
    """Test user registration"""
    print_info("Testing user registration...")
    
    # Test cases
    test_users = [
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "admin12345",
            "role": "admin"
        },
        {
            "username": "analyst_user",
            "email": "analyst@example.com",
            "password": "analyst12345",
            "role": "analyst"
        },
        {
            "username": "viewer_user",
            "email": "viewer@example.com",
            "password": "viewer12345",
            "role": "viewer"
        }
    ]
    
    for user in test_users:
        response = requests.post(f"{BASE_URL}/register", json=user)
        
        if response.status_code == 201:
            print_success(f"Registered user: {user['username']} (role: {user['role']})")
        elif response.status_code == 400 and "already exists" in response.text:
            print_warning(f"User already exists: {user['username']}")
        else:
            print_error(f"Failed to register {user['username']}")
            print_response(response, f"Registration Failed - {user['username']}")
    
    return True


def test_login():
    """Test user login and token generation"""
    print_info("\nTesting user login...")
    
    credentials = {
        "username": "admin",
        "password": "admin12345"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=credentials)
    print_response(response, "Login Response")
    
    if response.status_code == 200:
        data = response.json()
        print_success("Login successful!")
        print_info(f"Access Token: {data['access_token'][:50]}...")
        print_info(f"Refresh Token: {data['refresh_token'][:50]}...")
        return data['access_token'], data['refresh_token']
    else:
        print_error("Login failed!")
        return None, None


def test_get_current_user(access_token):
    """Test getting current user profile"""
    print_info("\nTesting get current user...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print_response(response, "Current User")
    
    if response.status_code == 200:
        print_success("Successfully retrieved current user profile")
        return True
    else:
        print_error("Failed to get current user")
        return False


def test_refresh_token(refresh_token):
    """Test token refresh"""
    print_info("\nTesting token refresh...")
    
    response = requests.post(
        f"{BASE_URL}/refresh",
        json={"refresh_token": refresh_token}
    )
    print_response(response, "Token Refresh")
    
    if response.status_code == 200:
        data = response.json()
        print_success("Token refreshed successfully!")
        print_info(f"New Access Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print_error("Token refresh failed!")
        return None


def test_change_password(access_token):
    """Test password change"""
    print_info("\nTesting password change...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    data = {
        "old_password": "admin12345",
        "new_password": "newpassword123"
    }
    
    response = requests.put(f"{BASE_URL}/me/password", json=data, headers=headers)
    print_response(response, "Change Password")
    
    if response.status_code == 200:
        print_success("Password changed successfully!")
        
        # Change it back
        data_back = {
            "old_password": "newpassword123",
            "new_password": "admin12345"
        }
        requests.put(f"{BASE_URL}/me/password", json=data_back, headers=headers)
        print_info("Password reverted back for testing purposes")
        return True
    else:
        print_error("Password change failed!")
        return False


def test_role_based_access(access_token):
    """Test role-based access control"""
    print_info("\nTesting role-based access...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test admin-only route
    response = requests.get(f"{BASE_URL}/admin-only", headers=headers)
    print_response(response, "Admin-Only Route")
    
    if response.status_code == 200:
        print_success("Admin access granted!")
    elif response.status_code == 403:
        print_warning("Admin access denied (insufficient permissions)")
    else:
        print_error("Unexpected response from admin route")
    
    # Test analyst area route
    response = requests.get(f"{BASE_URL}/analyst-area", headers=headers)
    print_response(response, "Analyst Area Route")
    
    if response.status_code == 200:
        print_success("Analyst area access granted!")
    elif response.status_code == 403:
        print_warning("Analyst area access denied (insufficient permissions)")
    
    # Test public/private route without token
    response = requests.get(f"{BASE_URL}/public-or-private")
    print_response(response, "Public Route (No Token)")
    
    # Test public/private route with token
    response = requests.get(f"{BASE_URL}/public-or-private", headers=headers)
    print_response(response, "Public Route (With Token)")


def test_list_users(access_token):
    """Test listing users (moderator/admin only)"""
    print_info("\nTesting list users...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    print_response(response, "List Users")
    
    if response.status_code == 200:
        print_success("Successfully retrieved user list")
        return True
    elif response.status_code == 403:
        print_warning("Access denied (insufficient permissions)")
        return False
    else:
        print_error("Failed to list users")
        return False


def test_invalid_token():
    """Test with invalid token"""
    print_info("\nTesting invalid token...")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print_response(response, "Invalid Token Test")
    
    if response.status_code == 401:
        print_success("Invalid token correctly rejected!")
        return True
    else:
        print_error("Invalid token was not properly rejected")
        return False


def test_no_token():
    """Test protected route without token"""
    print_info("\nTesting protected route without token...")
    
    response = requests.get(f"{BASE_URL}/me")
    print_response(response, "No Token Test")
    
    if response.status_code == 401:
        print_success("Request without token correctly rejected!")
        return True
    else:
        print_error("Request without token was not properly rejected")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}JWT Authentication Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    try:
        # Test registration
        test_register()
        
        # Test login
        access_token, refresh_token = test_login()
        
        if not access_token:
            print_error("Cannot continue tests without access token")
            return
        
        # Test protected routes
        test_get_current_user(access_token)
        test_change_password(access_token)
        test_role_based_access(access_token)
        test_list_users(access_token)
        
        # Test token refresh
        test_refresh_token(refresh_token)
        
        # Test error cases
        test_invalid_token()
        test_no_token()
        
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}All tests completed!{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        
    except requests.exceptions.ConnectionError:
        print_error("\nCould not connect to the API server!")
        print_info("Make sure the Flask application is running on http://localhost:5000")
    except Exception as e:
        print_error(f"\nAn error occurred: {str(e)}")


if __name__ == "__main__":
    main()
