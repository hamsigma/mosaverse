#!/usr/bin/env python3
"""
Test Django configuration for MosaVerse
"""

import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Test database configuration
from django.db import connection

def test_database_config():
    """Test database configuration"""
    print("🔍 Testing Django MySQL Configuration")
    print("=" * 40)
    
    db_config = connection.settings_dict
    
    print(f"Database Engine: {db_config['ENGINE']}")
    print(f"Database Name: {db_config['NAME']}")
    print(f"Database User: {db_config['USER']}")
    print(f"Database Host: {db_config['HOST']}")
    print(f"Database Port: {db_config['PORT']}")
    
    # Test environment variables
    print(f"\nEnvironment Variables:")
    print(f"DB_ENGINE: {os.getenv('DB_ENGINE')}")
    print(f"DB_NAME: {os.getenv('DB_NAME')}")
    print(f"DB_USER: {os.getenv('DB_USER')}")
    print(f"DB_HOST: {os.getenv('DB_HOST')}")
    print(f"DB_PORT: {os.getenv('DB_PORT')}")
    
    # Check if using MySQL
    if 'mysql' in db_config['ENGINE']:
        print("\n✅ MySQL configuration detected!")
        
        # Test charset settings
        if 'OPTIONS' in db_config and 'charset' in db_config['OPTIONS']:
            print(f"Charset: {db_config['OPTIONS']['charset']}")
        
        return True
    else:
        print(f"\n⚠️  Warning: Not using MySQL. Current engine: {db_config['ENGINE']}")
        return False

def test_apps_config():
    """Test Django apps configuration"""
    from django.apps import apps
    
    print("\n🔍 Testing Django Apps")
    print("=" * 25)
    
    required_apps = [
        'apps.authentication',
        'apps.designs', 
        'apps.ai',
        'apps.dashboard'
    ]
    
    installed_apps = [app.name for app in apps.get_app_configs()]
    
    for app_name in required_apps:
        if app_name in installed_apps:
            print(f"✅ {app_name}")
        else:
            print(f"❌ {app_name} - Not found")
    
    return all(app in installed_apps for app in required_apps)

def main():
    """Main test function"""
    try:
        db_ok = test_database_config()
        apps_ok = test_apps_config()
        
        print("\n" + "=" * 40)
        if db_ok and apps_ok:
            print("🎉 Configuration test PASSED!")
            print("\nNext steps:")
            print("1. Ensure MySQL server is running")
            print("2. Run: python setup_mysql.py")
            print("3. Run: python setup_project.py")
        else:
            print("❌ Configuration test FAILED!")
            print("Please check your settings and .env file")
            
    except Exception as e:
        print(f"❌ Error during configuration test: {e}")
        return False
        
    return True

if __name__ == "__main__":
    main()