"""Direct test of authentication without server"""
import sys
sys.path.insert(0, '.')

from app import create_app
from flask import Flask
import json

# Create app
app = create_app()

def test_token_decorator():
    """Test if the token_required decorator works"""
    with app.app_context():
        with app.test_client() as client:
            # Login first
            print("1. Testing login...")
            login_response = client.post(
                '/api/auth/login',
                data=json.dumps({'username': 'admin', 'password': 'admin12345'}),
                content_type='application/json'
            )
            print(f"   Login status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                data = json.loads(login_response.data)
                token = data.get('access_token')
                print(f"   Token: {token[:20]}...")
                
                # Test dashboard
                print("\n2. Testing dashboard with token...")
                try:
                    dash_response = client.get(
                        '/api/dashboard/kpis',
                        headers={'Authorization': f'Bearer {token}'}
                    )
                    print(f"   Dashboard status: {dash_response.status_code}")
                    if dash_response.status_code != 200:
                        print(f"   Response: {dash_response.data}")
                except Exception as e:
                    print(f"   Error: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"   Login failed: {login_response.data}")

if __name__ == '__main__':
    test_token_decorator()
