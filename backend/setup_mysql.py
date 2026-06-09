#!/usr/bin/env python3
"""
MySQL Database Setup Script for MosaVerse
This script creates the MySQL database and user for MosaVerse project.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create MySQL database and user for MosaVerse"""
    
    # Database configuration from .env
    db_name = os.getenv('DB_NAME', 'mosaverse_db')
    db_user = os.getenv('DB_USER', 'mosaverse_user')
    db_password = os.getenv('DB_PASSWORD', 'mosaverse123')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 3306))
    
    # Root credentials for initial setup
    print(f"\nTrying to connect to MySQL server...")
    print(f"Host: {db_host}:{db_port}")
    root_password = input("Enter MySQL root password (leave empty if no password): ")
    if root_password == "":
        root_password = None
    
    try:
        # Connect to MySQL server as root
        print("Connecting to MySQL...")
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user='root',
            password=root_password,
            auth_plugin='mysql_native_password'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            print(f"Creating database: {db_name}")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # Create user (only if not root)
            if db_user != 'root':
                print(f"Creating user: {db_user}")
                cursor.execute(f"CREATE USER IF NOT EXISTS '{db_user}'@'{db_host}' IDENTIFIED BY '{db_password}'")
                
                # Grant privileges
                print(f"Granting privileges to {db_user}")
                cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'{db_host}'")
                cursor.execute("FLUSH PRIVILEGES")
            
            print(f"\n✅ MySQL setup completed successfully!")
            print(f"Database: {db_name}")
            print(f"User: {db_user}")
            print(f"Host: {db_host}:{db_port}")
            
            # Test connection with new credentials
            print("\n🔍 Testing connection with new credentials...")
            test_connection = mysql.connector.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password if db_user != 'root' else root_password,
                database=db_name
            )
            
            if test_connection.is_connected():
                print("✅ Connection test successful!")
                test_connection.close()
            
    except Error as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            
    return True

def main():
    """Main function"""
    print("🚀 MosaVerse MySQL Setup")
    print("=" * 30)
    
    # Check if MySQL is running
    try:
        import mysql.connector
    except ImportError:
        print("❌ Error: mysqlclient not installed. Run 'pip install mysqlclient'")
        sys.exit(1)
    
    if create_database():
        print("\n🎉 Setup completed! You can now run Django migrations:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
        print("   python manage.py createsuperuser")
    else:
        print("\n❌ Setup failed. Please check your MySQL installation and credentials.")
        sys.exit(1)

if __name__ == "__main__":
    main()