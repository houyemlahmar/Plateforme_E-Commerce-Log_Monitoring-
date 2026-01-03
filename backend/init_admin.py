"""
Initialize admin user
Creates the first admin user for the application
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.auth_service import AuthService


def create_admin():
    """Create the initial admin user"""
    print("=" * 60)
    print("Create Admin User")
    print("=" * 60)
    
    auth_service = AuthService()
    
    # Default admin credentials (change in production!)
    username = input("\nEnter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email (default: admin@example.com): ").strip() or "admin@example.com"
    password = input("Enter admin password (default: admin12345): ").strip() or "admin12345"
    
    try:
        # Check if admin already exists
        existing_user = auth_service.get_user_by_username(username)
        
        if existing_user:
            print(f"\n⚠ User '{username}' already exists!")
            print(f"User details:")
            print(f"  - Username: {existing_user.username}")
            print(f"  - Email: {existing_user.email}")
            print(f"  - Role: {existing_user.role}")
            print(f"  - Active: {existing_user.is_active}")
            
            update = input("\nDo you want to update this user to admin role? (y/N): ").strip().lower()
            
            if update == 'y':
                if existing_user.role != 'admin':
                    auth_service.update_user_role(existing_user._id, 'admin')
                    print(f"\n✓ User '{username}' updated to admin role!")
                else:
                    print(f"\n✓ User '{username}' is already an admin!")
                
                if not existing_user.is_active:
                    auth_service.activate_user(existing_user._id)
                    print(f"✓ User '{username}' has been activated!")
            
            return
        
        # Create new admin user
        user = auth_service.register_user(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
        
        print("\n✓ Admin user created successfully!")
        print(f"\nAdmin credentials:")
        print(f"  - Username: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - Role: {user.role}")
        print(f"\n⚠ IMPORTANT: Change the default password after first login!")
        
    except ValueError as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        print(f"  Make sure MongoDB is running and accessible")
        sys.exit(1)


def create_sample_users():
    """Create sample users for testing"""
    print("\n" + "=" * 60)
    print("Create Sample Users")
    print("=" * 60)
    
    create_samples = input("\nDo you want to create sample users for testing? (y/N): ").strip().lower()
    
    if create_samples != 'y':
        return
    
    auth_service = AuthService()
    
    sample_users = [
        {
            "username": "analyst_demo",
            "email": "analyst@demo.com",
            "password": "analyst123",
            "role": "analyst"
        },
        {
            "username": "moderator_demo",
            "email": "moderator@demo.com",
            "password": "moderator123",
            "role": "moderator"
        },
        {
            "username": "viewer_demo",
            "email": "viewer@demo.com",
            "password": "viewer123",
            "role": "viewer"
        }
    ]
    
    print("\nCreating sample users...")
    
    for user_data in sample_users:
        try:
            existing = auth_service.get_user_by_username(user_data['username'])
            
            if existing:
                print(f"  ⚠ {user_data['username']} already exists (skipped)")
                continue
            
            user = auth_service.register_user(**user_data)
            print(f"  ✓ Created {user_data['username']} (role: {user_data['role']})")
        
        except Exception as e:
            print(f"  ✗ Failed to create {user_data['username']}: {str(e)}")
    
    print("\n✓ Sample users creation completed!")
    print("\nSample credentials:")
    for user_data in sample_users:
        print(f"  - {user_data['username']} / {user_data['password']} ({user_data['role']})")


def main():
    """Main function"""
    try:
        create_admin()
        create_sample_users()
        
        print("\n" + "=" * 60)
        print("Setup completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Start the Flask application: python main.py")
        print("  2. Test authentication: python test_auth.py")
        print("  3. Read documentation: JWT_AUTHENTICATION.md")
        print()
    
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
