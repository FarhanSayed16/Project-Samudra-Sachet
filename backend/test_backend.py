#!/usr/bin/env python3
"""
Project Samudra Sachet - Backend Test Script
Comprehensive testing of all backend functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_database_connection():
    """Test database connection and initialization"""
    try:
        from app.db.session import init_db, close_db
        await init_db()
        print("✅ Database connection successful")
        await close_db()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_imports():
    """Test all critical imports"""
    try:
        # Core imports
        from app.core.config import settings
        from app.core.security import create_access_token, verify_password
        from app.db.session import get_db
        from app.db.base_class import Base
        
        # Model imports
        from app.models.user import User
        from app.models.report import Report
        from app.models.hotspot import Hotspot
        from app.models.social_media_post import SocialMediaPost
        from app.models.verification_log import VerificationLog
        from app.models.media_analysis import MediaAnalysis
        from app.models.audit_log import AuditLog
        
        # Schema imports
        from app.schemas.user import UserCreate, UserUpdate, UserResponse
        from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse
        from app.schemas.token import Token, TokenPayload
        
        # CRUD imports
        from app.crud.crud_user import get_user_by_email, create_user
        from app.crud.crud_report import create_report, get_report_by_id
        
        # API imports
        from app.api.v1.api import api_router
        from app.api.v1.endpoints.auth import router as auth_router
        from app.api.v1.endpoints.users import router as users_router
        from app.api.v1.endpoints.reports import router as reports_router
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    try:
        from app.core.config import settings
        
        # Check if required settings are available
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'APP_NAME')
        
        print(f"✅ Configuration loaded successfully")
        print(f"   App Name: {settings.APP_NAME}")
        print(f"   Debug Mode: {settings.DEBUG}")
        print(f"   Database URL: {settings.DATABASE_URL[:20]}...")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_security():
    """Test security functions"""
    try:
        from app.core.security import create_access_token, verify_password, get_password_hash
        
        # Test password hashing
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
        
        # Test token creation
        token = create_access_token(data={"sub": "test@example.com"})
        assert isinstance(token, str)
        assert len(token) > 0
        
        print("✅ Security functions working correctly")
        return True
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🌊 Project Samudra Sachet - Backend Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Imports", test_imports),
        ("Security", test_security),
        ("Database Connection", test_database_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready for frontend integration.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Set test environment variables
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
    os.environ["DEBUG"] = "true"
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
