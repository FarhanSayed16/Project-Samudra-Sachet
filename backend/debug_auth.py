#!/usr/bin/env python3
"""
Debug authentication issue
"""
import asyncio
import requests
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.db.session import AsyncSessionLocal
from app.crud.crud_user import crud_user
import uuid

async def debug_auth():
    """Debug the authentication issue"""
    
    # Get a token first
    login_data = {'email': 'authority@samudra-sachet.com', 'password': 'authority123'}
    response = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json=login_data)
    data = response.json()
    user_info = data['user']
    user_id_str = user_info['id']
    
    print(f"Login user ID from response: {user_id_str}")
    print(f"User ID type: {type(user_id_str)}")
    
    # Try to convert to UUID and query the database
    try:
        user_uuid = uuid.UUID(user_id_str)
        print(f"Converted UUID: {user_uuid}")
        print(f"UUID type: {type(user_uuid)}")
        
        # Query database directly
        async with AsyncSessionLocal() as db:
            user = await crud_user.get_by_id(db, user_id=user_uuid)
            if user:
                print(f"✅ Found user in DB: {user.email}")
                print(f"   User ID in DB: {user.id}")
                print(f"   User ID type in DB: {type(user.id)}")
                print(f"   User active: {user.is_active}")
            else:
                print("❌ User not found in database")
                
                # List all users to debug
                all_users = await crud_user.get_users(db, limit=10)
                print(f"All users in DB:")
                for u in all_users:
                    print(f"  - ID: {u.id} ({type(u.id)}) - Email: {u.email}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_auth())