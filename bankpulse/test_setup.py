"""Simple test to verify BankPulse setup"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from bankpulse import database, data_loader, analytics, ai_assistant, api
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    try:
        from bankpulse.database import DatabaseManager
        db = DatabaseManager()
        db.init_database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from bankpulse import config
        print(f"  AWS Profile: {config.AWS_PROFILE}")
        print(f"  AWS Region: {config.AWS_REGION}")
        print(f"  Database Path: {config.DATABASE_PATH}")
        print("✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_api():
    """Test API initialization"""
    print("\nTesting API...")
    try:
        from bankpulse.api import app
        print(f"  API Title: {app.title}")
        print(f"  API Version: {app.version}")
        print("✓ API initialized successfully")
        return True
    except Exception as e:
        print(f"✗ API error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("BankPulse Setup Verification")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_api
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 50)
    
    if all(results):
        print("\n✓ All tests passed! BankPulse is ready to use.")
        print("\nNext steps:")
        print("  1. Download data: uv run python main.py download")
        print("  2. Start server: uv run python main.py serve")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
