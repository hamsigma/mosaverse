#!/usr/bin/env python3
"""
Debug dan fix script untuk MosaVerse
Otomatis detect dan fix common issues
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def run_command(command, description, check=True, capture_output=True):
    """Run command dengan error handling"""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check,
            capture_output=capture_output, 
            text=True,
            cwd=os.getcwd()
        )
        if result.stdout and capture_output:
            print(result.stdout)
        return result.returncode == 0, result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False, e

def check_and_fix_directories():
    """Check dan fix missing directories"""
    print("\n📁 Checking directories...")
    
    required_dirs = [
        'static',
        'media',
        'media/designs',
        'templates'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"Creating missing directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
        else:
            print(f"✅ {dir_path} exists")

def check_database_connection():
    """Check database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        from django.db import connection
        from django.core.management.color import no_style
        
        # Test database connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result:
            print("✅ Database connection successful")
            print(f"Engine: {connection.settings_dict['ENGINE']}")
            print(f"Name: {connection.settings_dict['NAME']}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Recommendation: Use SQLite for now, setup MySQL later")
        return False

def fix_env_file():
    """Fix .env file issues"""
    print("\n⚙️  Checking .env configuration...")
    
    if not os.path.exists('.env'):
        print("Creating .env file from .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
        else:
            # Create basic .env
            env_content = """# MosaVerse Backend Environment Variables
SECRET_KEY=django-insecure-mosaverse-dev-key-please-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database - SQLite (default, safe)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# DeepSeek API
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/v1
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Created basic .env file with SQLite config")
    else:
        print("✅ .env file exists")

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'django',
        'djangorestframework', 
        'django-cors-headers',
        'python-dotenv',
        'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalling missing packages: {missing_packages}")
        packages_str = ' '.join(missing_packages)
        success, _ = run_command(f"pip install {packages_str}", "Installing missing dependencies")
        return success
    
    return True

def setup_database():
    """Setup database dan migrations"""
    print("\n🗄️  Setting up database...")
    
    # Makemigrations
    success, _ = run_command("python manage.py makemigrations", "Creating migrations")
    if not success:
        return False
    
    # Migrate
    success, _ = run_command("python manage.py migrate", "Applying migrations") 
    if not success:
        return False
        
    # Check if superuser exists
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        from django.contrib.auth.models import User
        
        if not User.objects.filter(is_superuser=True).exists():
            print("Creating default superuser (admin/admin123)...")
            User.objects.create_superuser('admin', 'admin@mosaverse.com', 'admin123')
            print("✅ Superuser created: admin / admin123")
        else:
            print("✅ Superuser already exists")
            
    except Exception as e:
        print(f"⚠️  Could not create superuser: {e}")
    
    return True

def test_server():
    """Test Django server startup"""
    print("\n🚀 Testing server startup...")
    
    success, _ = run_command("python manage.py check", "Django system check")
    if success:
        print("✅ Django system check passed")
        print("\nTo start server, run: python manage.py runserver")
        print("Admin login: http://127.0.0.1:8000/admin/")
        print("Username: admin | Password: admin123")
        return True
    else:
        print("❌ Django system check failed")
        return False

def create_sample_data():
    """Create sample categories"""
    print("\n🌱 Creating sample data...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        from apps.designs.models import Category
        
        categories = [
            {'name': 'Casual Wear', 'description': 'Pakaian kasual sehari-hari'},
            {'name': 'Formal Wear', 'description': 'Pakaian formal untuk acara resmi'},
            {'name': 'Streetwear', 'description': 'Fashion jalanan yang trendy'},
            {'name': 'Vintage', 'description': 'Desain dengan sentuhan klasik'},
            {'name': 'Minimalist', 'description': 'Desain simpel dan elegan'},
        ]
        
        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                created_count += 1
                
        print(f"✅ Sample categories ready ({created_count} new, {len(categories)} total)")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main debug dan fix function"""
    print("🔧 MosaVerse Debug & Fix Tool")
    print("=" * 40)
    
    # Check working directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Run this from backend/ directory")
        sys.exit(1)
    
    steps = [
        ("Fix environment file", fix_env_file),
        ("Check dependencies", check_dependencies), 
        ("Check and fix directories", check_and_fix_directories),
        ("Test database connection", check_database_connection),
        ("Setup database", setup_database),
        ("Create sample data", create_sample_data),
        ("Test server", test_server),
    ]
    
    results = []
    for description, func in steps:
        try:
            print(f"\n{'='*50}")
            result = func()
            results.append((description, result))
        except Exception as e:
            print(f"❌ Error in {description}: {e}")
            results.append((description, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("🎯 SUMMARY")
    print("=" * 20)
    
    success_count = 0
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
        if success:
            success_count += 1
    
    if success_count == len(results):
        print(f"\n🎉 ALL CHECKS PASSED! ({success_count}/{len(results)})")
        print("\n🚀 Ready to start development:")
        print("   python manage.py runserver")
        print("   http://127.0.0.1:8000/admin/")
    else:
        print(f"\n⚠️  {success_count}/{len(results)} checks passed")
        print("Some issues need manual attention. Check error messages above.")

if __name__ == "__main__":
    main()