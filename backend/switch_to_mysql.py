#!/usr/bin/env python3
"""
Switch MosaVerse dari SQLite ke MySQL dengan mudah
"""

import os
import sys
import subprocess
import mysql.connector
from dotenv import load_dotenv
import django
from pathlib import Path

def update_env_to_mysql():
    """Update .env file untuk MySQL"""
    print("🔧 Updating .env file for MySQL...")
    
    mysql_config = """# MosaVerse Backend Environment Variables
SECRET_KEY=django-insecure-mosaverse-dev-key-please-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database - MySQL Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=mosaverse_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# DeepSeek API
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/v1
"""
    
    with open('.env', 'w') as f:
        f.write(mysql_config)
    
    print("✅ .env updated for MySQL")

def test_mysql_connection():
    """Test MySQL connection"""
    print("\n🔍 Testing MySQL connection...")
    
    # Reload environment
    load_dotenv()
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 3306))
    
    # Get password from user
    db_password = input(f"Enter MySQL root password for {db_host} (leave empty if no password): ")
    if db_password == "":
        db_password = None
    
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user='root',
            password=db_password,
            auth_plugin='mysql_native_password'
        )
        
        if connection.is_connected():
            print("✅ MySQL connection successful!")
            connection.close()
            
            # Update password in .env
            if db_password:
                with open('.env', 'r') as f:
                    content = f.read()
                content = content.replace('DB_PASSWORD=', f'DB_PASSWORD={db_password}')
                with open('.env', 'w') as f:
                    f.write(content)
                    
            return True
            
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check your root password")
        print("3. Try: mysql -u root -p")
        return False

def create_mysql_database():
    """Create MySQL database"""
    print("\n🗄️  Creating MySQL database...")
    
    load_dotenv()
    
    db_name = os.getenv('DB_NAME', 'mosaverse_db')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 3306))
    db_password = os.getenv('DB_PASSWORD', '')
    
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user='root',
            password=db_password if db_password else None,
            auth_plugin='mysql_native_password'
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{db_name}' created/verified")
        
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def migrate_to_mysql():
    """Migrate Django to MySQL"""
    print("\n📦 Migrating Django to MySQL...")
    
    try:
        # Reset Django setup
        if hasattr(django, 'setup'):
            django.setup()
        
        # Run migrations
        result = subprocess.run(['python', 'manage.py', 'migrate'], 
                               capture_output=True, text=True, check=True)
        print(result.stdout)
        
        print("✅ Migration to MySQL successful!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_mysql_superuser():
    """Create superuser for MySQL database"""
    print("\n👤 Creating superuser for MySQL...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        from django.contrib.auth.models import User
        
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@mosaverse.com', 'admin123')
            print("✅ Superuser created: admin / admin123")
        else:
            print("✅ Superuser already exists")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

def test_mysql_django():
    """Test Django with MySQL"""
    print("\n🧪 Testing Django with MySQL...")
    
    try:
        result = subprocess.run(['python', 'manage.py', 'check'], 
                               capture_output=True, text=True, check=True)
        print("✅ Django MySQL check passed!")
        
        # Test database query
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL Version: {version[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django MySQL test failed: {e}")
        return False

def backup_sqlite_data():
    """Backup data from SQLite before switching"""
    print("\n💾 Backing up SQLite data...")
    
    if not os.path.exists('db.sqlite3'):
        print("No SQLite database found, skipping backup")
        return True
    
    try:
        # Create fixtures from SQLite
        result = subprocess.run([
            'python', 'manage.py', 'dumpdata', 
            '--format=json', '--indent=2',
            '--exclude=contenttypes', '--exclude=auth.permission',
            '--exclude=sessions', '--exclude=admin.logentry'
        ], capture_output=True, text=True, check=True)
        
        with open('sqlite_backup.json', 'w') as f:
            f.write(result.stdout)
            
        print("✅ SQLite data backed up to sqlite_backup.json")
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def load_data_to_mysql():
    """Load backed up data to MySQL"""
    print("\n📥 Loading data to MySQL...")
    
    if not os.path.exists('sqlite_backup.json'):
        print("No backup file found, skipping data load")
        return True
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'loaddata', 'sqlite_backup.json'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Data loaded to MySQL successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        print("You can manually load data later with: python manage.py loaddata sqlite_backup.json")
        return False

def main():
    """Main function"""
    print("🔄 MySQL Migration Tool for MosaVerse")
    print("=" * 40)
    
    if not os.path.exists('manage.py'):
        print("❌ Error: Run this from backend/ directory")
        sys.exit(1)
    
    print("This will switch your database from SQLite to MySQL.")
    print("Make sure MySQL server is installed and running.")
    confirm = input("\nContinue? (y/N): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled")
        sys.exit(0)
    
    steps = [
        ("Backup SQLite data", backup_sqlite_data),
        ("Update .env for MySQL", update_env_to_mysql),
        ("Test MySQL connection", test_mysql_connection),
        ("Create MySQL database", create_mysql_database),
        ("Migrate to MySQL", migrate_to_mysql),
        ("Create superuser", create_mysql_superuser),
        ("Load backed up data", load_data_to_mysql),
        ("Test Django with MySQL", test_mysql_django),
    ]
    
    results = []
    for description, func in steps:
        print(f"\n{'='*50}")
        try:
            result = func()
            results.append((description, result))
            if not result:
                print(f"Step failed: {description}")
                rollback = input("Continue anyway? (y/N): ")
                if rollback.lower() != 'y':
                    break
        except Exception as e:
            print(f"❌ Error in {description}: {e}")
            results.append((description, False))
            break
    
    # Summary
    print(f"\n{'='*50}")
    print("🎯 MIGRATION SUMMARY")
    print("=" * 25)
    
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
    
    success_count = sum(1 for _, success in results if success)
    
    if success_count == len(steps):
        print(f"\n🎉 MySQL MIGRATION SUCCESSFUL!")
        print("\n🚀 Your MosaVerse now uses MySQL!")
        print("   python manage.py runserver")
        print("   Admin: http://127.0.0.1:8000/admin/")
        print("   Login: admin / admin123")
    else:
        print(f"\n⚠️  Migration partially completed ({success_count}/{len(steps)})")
        print("Check errors above. You can:")
        print("1. Fix issues and run this script again")
        print("2. Continue with SQLite (already working)")

if __name__ == "__main__":
    main()