#!/usr/bin/env python3
"""
Test script to debug authentication issues
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import AsyncSessionLocal
from app.crud.crud_user import crud_user
from app.core.security import create_access_token, verify_token
from app.models.user import UserRole
import json

async def test_auth():
    """Test authentication flow"""
    print("Testing Authentication Flow")
    print("=" * 50)
    
    async with AsyncSessionLocal() as db:
        # Test 1: Check if citizen user exists
        print("\n1. Checking citizen user...")
        user = await crud_user.get_by_email(db, "citizen@samudra-sachet.com")
        if user:
            print(f"SUCCESS: User found: {user.email}")
            print(f"   Role: {user.user_role}")
            print(f"   Active: {user.is_active}")
            print(f"   ID: {user.id}")
        else:
            print("ERROR: User not found!")
            return
        
        # Test 2: Create a test token
        print("\n2. Creating test token...")
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "user_role": user.user_role.value
        }
        
        access_token = create_access_token(data=token_data)
        print(f"SUCCESS: Token created: {access_token[:50]}...")
        
        # Test 3: Verify the token
        print("\n3. Verifying token...")
        try:
            verified_data = verify_token(access_token, "access")
            print(f"SUCCESS: Token verified successfully!")
            print(f"   User ID: {verified_data.user_id}")
            print(f"   Email: {verified_data.email}")
            print(f"   Role: {verified_data.user_role}")
        except Exception as e:
            print(f"ERROR: Token verification failed: {e}")
            return
        
        # Test 4: Test user lookup by ID
        print("\n4. Testing user lookup by ID...")
        try:
            found_user = await crud_user.get_by_id(db, user_id=verified_data.user_id)
            if found_user:
                print(f"SUCCESS: User lookup successful: {found_user.email}")
            else:
                print("ERROR: User lookup failed!")
        except Exception as e:
            print(f"ERROR: User lookup error: {e}")
        
        # Test 5: Test role check
        print("\n5. Testing role check...")
        if user.user_role == UserRole.CITIZEN:
            print("SUCCESS: User has CITIZEN role - should be able to create reports")
        else:
            print(f"ERROR: User has {user.user_role} role - may not be able to create reports")
        
        print("\n" + "=" * 50)
        print("Authentication test completed!")

if __name__ == "__main__":
    asyncio.run(test_auth())
