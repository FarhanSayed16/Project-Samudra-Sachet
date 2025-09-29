#!/usr/bin/env python3
"""
Test script to verify the login fix works correctly
"""
import asyncio
import json
import aiohttp

async def test_login():
    """Test the login endpoint with authority credentials"""
    
    # Test data
    login_data = {
        "email": "authority@samudra-sachet.com",
        "password": "authority123"
    }
    
    url = "http://127.0.0.1:8000/api/v1/auth/login"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Make login request
            async with session.post(
                url, 
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                status = response.status
                data = await response.json()
                
                print(f"🔐 Login Test Results")
                print(f"{'='*50}")
                print(f"Status Code: {status}")
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if status == 200:
                    print(f"\n✅ LOGIN SUCCESS!")
                    
                    # Verify all required fields are present
                    required_fields = ['access_token', 'refresh_token', 'token_type', 'expires_in', 'user']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print(f"✅ All required fields present")
                        
                        # Verify user object structure
                        user = data['user']
                        user_fields = ['id', 'email', 'full_name', 'user_role', 'is_active', 'is_verified']
                        missing_user_fields = [field for field in user_fields if field not in user]
                        
                        if not missing_user_fields:
                            print(f"✅ User object structure correct")
                            print(f"   - User ID: {user['id']}")
                            print(f"   - Email: {user['email']}")
                            print(f"   - Role: {user['user_role']}")
                            print(f"   - Active: {user['is_active']}")
                        else:
                            print(f"❌ Missing user fields: {missing_user_fields}")
                    else:
                        print(f"❌ Missing fields: {missing_fields}")
                        
                else:
                    print(f"❌ LOGIN FAILED!")
                    print(f"Error: {data.get('detail', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Connection Error: {str(e)}")

async def test_other_users():
    """Test login for other user roles"""
    
    test_users = [
        {"email": "admin@samudra-sachet.com", "password": "admin123", "role": "admin"},
        {"email": "analyst@samudra-sachet.com", "password": "analyst123", "role": "analyst"},
        {"email": "citizen@samudra-sachet.com", "password": "citizen123", "role": "citizen"}
    ]
    
    url = "http://127.0.0.1:8000/api/v1/auth/login"
    
    print(f"\n🧪 Testing Other User Roles")
    print(f"{'='*50}")
    
    async with aiohttp.ClientSession() as session:
        for user_data in test_users:
            try:
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                
                async with session.post(url, json=login_data) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        user_role = data['user']['user_role']
                        print(f"✅ {user_data['role'].upper()}: Login successful (role: {user_role})")
                    else:
                        print(f"❌ {user_data['role'].upper()}: Login failed - {data.get('detail', 'Unknown error')}")
                        
            except Exception as e:
                print(f"❌ {user_data['role'].upper()}: Connection error - {str(e)}")

async def main():
    """Run all tests"""
    print(f"🌊 Project Samudra Sachet - Login Fix Test")
    print(f"{'='*60}")
    
    # Test main login
    await test_login()
    
    # Test other users
    await test_other_users()
    
    print(f"\n🎯 Test Summary")
    print(f"{'='*60}")
    print(f"✅ Backend API: http://127.0.0.1:8000")
    print(f"✅ Frontend UI: http://localhost:5173")
    print(f"✅ API Docs: http://127.0.0.1:8000/docs")
    print(f"\n🔑 Demo Credentials:")
    print(f"   - Admin: admin@samudra-sachet.com / admin123")
    print(f"   - Authority: authority@samudra-sachet.com / authority123")
    print(f"   - Analyst: analyst@samudra-sachet.com / analyst123")
    print(f"   - Citizen: citizen@samudra-sachet.com / citizen123")

if __name__ == "__main__":
    asyncio.run(main())