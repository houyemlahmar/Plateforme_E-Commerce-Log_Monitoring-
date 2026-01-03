"""
Test script for POST /api/logs/upload endpoint
"""

import requests
import json
from io import BytesIO

# Flask API URL
BASE_URL = "http://localhost:5001"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/logs/upload"

def test_upload_json():
    """Test uploading a JSON file"""
    print("\n=== Test 1: Upload JSON file ===")
    
    # Create sample JSON content
    json_content = """{"timestamp":"2025-12-25T10:00:00Z","log_type":"transaction","user_id":"USER123","order_id":5001,"amount":99.99,"ip":"8.8.8.8"}
{"timestamp":"2025-12-25T10:01:00Z","log_type":"error","error_code":500,"endpoint":"/api/payment","user_id":"USER456"}
{"timestamp":"2025-12-25T10:02:00Z","log_type":"fraud","transaction_id":"TXN789","fraud_score":85,"amount":5000.00}
{"timestamp":"2025-12-25T10:03:00Z","log_type":"transaction","user_id":"USER789","order_id":5002,"amount":149.50,"ip":"1.1.1.1"}
{"timestamp":"2025-12-25T10:04:00Z","log_type":"performance","endpoint":"/api/products","response_time":250}
{"timestamp":"2025-12-25T10:05:00Z","log_type":"user_behavior","user_id":"USER321","action":"add_to_cart","product_id":"PROD456"}
{"timestamp":"2025-12-25T10:06:00Z","log_type":"transaction","user_id":"USER654","order_id":5003,"amount":299.99,"ip":"2.2.2.2"}
{"timestamp":"2025-12-25T10:07:00Z","log_type":"error","error_code":404,"endpoint":"/api/product/999","user_id":"USER987"}
{"timestamp":"2025-12-25T10:08:00Z","log_type":"transaction","user_id":"USER111","order_id":5004,"amount":49.99,"ip":"3.3.3.3"}
{"timestamp":"2025-12-25T10:09:00Z","log_type":"fraud","transaction_id":"TXN999","fraud_score":90,"amount":10000.00}
{"timestamp":"2025-12-25T10:10:00Z","log_type":"transaction","user_id":"USER222","order_id":5005,"amount":199.99,"ip":"4.4.4.4"}
{"timestamp":"2025-12-25T10:11:00Z","log_type":"performance","endpoint":"/api/checkout","response_time":500}"""
    
    # Create file object
    files = {
        'file': ('test_logs.json', BytesIO(json_content.encode('utf-8')), 'application/json')
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ JSON upload successful!")
            data = response.json()['data']
            print(f"   - File ID: {data['file_id']}")
            print(f"   - Job ID: {data['job_id']}")
            print(f"   - Preview lines: {data['preview_lines']}")
            print(f"   - Total lines: {data['total_lines']}")
        else:
            print("❌ JSON upload failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_upload_csv():
    """Test uploading a CSV file"""
    print("\n=== Test 2: Upload CSV file ===")
    
    # Create sample CSV content
    csv_content = """timestamp,level,service,user_id,order_id,amount,ip
2025-12-25T10:00:00Z,INFO,payment,1001,5001,149.99,203.0.113.10
2025-12-25T10:01:00Z,ERROR,checkout,1002,5002,299.50,198.51.100.20
2025-12-25T10:02:00Z,WARNING,inventory,1003,5003,99.99,192.0.2.30
2025-12-25T10:03:00Z,INFO,payment,1004,5004,499.00,198.51.100.40
2025-12-25T10:04:00Z,ERROR,shipping,1005,5005,199.99,203.0.113.50
2025-12-25T10:05:00Z,INFO,payment,1006,5006,79.99,192.0.2.60
2025-12-25T10:06:00Z,WARNING,fraud_detection,1007,5007,5000.00,198.51.100.70
2025-12-25T10:07:00Z,INFO,checkout,1008,5008,349.50,203.0.113.80
2025-12-25T10:08:00Z,ERROR,payment,1009,5009,599.99,192.0.2.90
2025-12-25T10:09:00Z,INFO,payment,1010,5010,899.00,198.51.100.100
2025-12-25T10:10:00Z,WARNING,inventory,1011,5011,49.99,203.0.113.110"""
    
    # Create file object
    files = {
        'file': ('test_logs.csv', BytesIO(csv_content.encode('utf-8')), 'text/csv')
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ CSV upload successful!")
            data = response.json()['data']
            print(f"   - File ID: {data['file_id']}")
            print(f"   - Job ID: {data['job_id']}")
            print(f"   - Preview lines: {data['preview_lines']}")
            print(f"   - Total lines: {data['total_lines']}")
        else:
            print("❌ CSV upload failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_upload_invalid_extension():
    """Test uploading a file with invalid extension"""
    print("\n=== Test 3: Upload file with invalid extension (.txt) ===")
    
    # Create file with .txt extension
    files = {
        'file': ('test_logs.txt', BytesIO(b'some log data'), 'text/plain')
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✅ Invalid extension correctly rejected!")
        else:
            print("❌ Should have rejected .txt extension!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_upload_empty_file():
    """Test uploading an empty file"""
    print("\n=== Test 4: Upload empty file ===")
    
    files = {
        'file': ('empty.json', BytesIO(b''), 'application/json')
    }
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✅ Empty file correctly rejected!")
        else:
            print("❌ Should have rejected empty file!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_upload_no_file():
    """Test uploading without file"""
    print("\n=== Test 5: Upload without file ===")
    
    try:
        response = requests.post(UPLOAD_ENDPOINT, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✅ No file correctly rejected!")
        else:
            print("❌ Should have rejected request without file!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing POST /api/logs/upload endpoint")
    print("=" * 60)
    
    # Test API availability
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ API is reachable at {BASE_URL}")
    except Exception as e:
        print(f"❌ Cannot reach API at {BASE_URL}")
        print(f"   Make sure Flask is running: docker-compose ps")
        return
    
    # Run tests
    test_upload_json()
    test_upload_csv()
    test_upload_invalid_extension()
    test_upload_empty_file()
    test_upload_no_file()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
