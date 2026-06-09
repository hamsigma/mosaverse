#!/usr/bin/env python3
"""
MosaVerse Project Setup Script
This script sets up the complete Django project with MySQL database.
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def create_superuser():
    """Create superuser interactively"""
    print("\n👤 Creating superuser account...")
    print("You'll be prompted to create an admin account for the Django admin interface.")
    
    try:
        from django.contrib.auth.models import User
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superuser already exists, skipping creation.")
            return True
            
        # Interactive superuser creation
        execute_from_command_line(['manage.py', 'createsuperuser'])
        return True
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False

def seed_sample_data():
    """Create sample categories and designs"""
    print("\n🌱 Creating sample data...")
    
    try:
        from apps.designs.models import Category, Design
        from django.contrib.auth.models import User
        
        # Create sample categories
        categories_data = [
            {'name': 'Casual Wear', 'description': 'Pakaian kasual untuk sehari-hari'},
            {'name': 'Formal Wear', 'description': 'Pakaian formal untuk acara resmi'},
            {'name': 'Streetwear', 'description': 'Fashion jalanan yang trendy'},
            {'name': 'Vintage', 'description': 'Desain dengan sentuhan klasik'},
            {'name': 'Minimalist', 'description': 'Desain simpel dan elegan'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                print(f"✅ Created category: {category.name}")
        
        # Note: Sample designs would need actual image files
        # For now, just create the categories
        
        print(f"✅ Sample data created!")
        print(f"Categories: {Category.objects.count()}")
        print(f"Designs: {Design.objects.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 MosaVerse Project Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Step 1: Check Python dependencies
    print("\n📋 Checking Python dependencies...")
    required_packages = ['django', 'djangorestframework', 'mysqlclient', 'python-dotenv']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            print(f"Please install it with: pip install {package}")
            sys.exit(1)
    
    # Step 2: Check environment file
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please create it from .env.example")
        sys.exit(1)
    
    # Step 3: Setup Django
    setup_django()
    
    # Step 4: Run migrations
    if not run_command("python manage.py makemigrations", "Creating new migrations"):
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Applying database migrations"):
        sys.exit(1)
    
    # Step 5: Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠️  Warning: Static files collection failed, but continuing...")
    
    # Step 6: Create superuser
    create_superuser()
    
    # Step 7: Create sample data
    seed_sample_data()
    
    # Step 8: Final checks
    print("\n🔍 Running system checks...")
    if run_command("python manage.py check", "Django system check"):
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the development server: python manage.py runserver")
        print("2. Access admin interface: http://127.0.0.1:8000/admin/")
        print("3. Access API documentation: http://127.0.0.1:8000/api/")
        print("4. Frontend files are in ../frontend/ directory")
        
        # Show created admin info
        try:
            from django.contrib.auth.models import User
            admin_users = User.objects.filter(is_superuser=True)
            if admin_users.exists():
                print(f"\n👤 Admin users created: {list(admin_users.values_list('username', flat=True))}")
        except:
            pass
            
    else:
        print("\n❌ Setup completed with warnings. Please check the errors above.")

if __name__ == "__main__":
    main()