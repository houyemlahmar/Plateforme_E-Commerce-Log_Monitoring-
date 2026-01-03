"""
Simple Flask starter - runs without auto-reloader
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("Flask Server Starting...")
    print("Server: http://localhost:5001")
    print("Health: http://localhost:5001/health")
    print("Auth API: http://localhost:5001/api/auth/")
    print("Login: http://localhost:5001/login")
    print("="*60 + "\n")
    
    # Run without reloader to avoid Windows socket issues
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False,
        use_reloader=False,
        threaded=True
    )
