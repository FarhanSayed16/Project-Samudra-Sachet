#!/usr/bin/env python3
"""
Comprehensive API test to verify all endpoints work properly
"""
import asyncio
import aiohttp
import json

async def test_api_endpoints():
    """Test all the main API endpoints"""
    
    base_url = "http://127.0.0.1:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        print("🌊 Project Samudra Sachet - Comprehensive API Test")
        print("=" * 60)
        
        # 1. Test Login
        print("\n🔐 Testing Authentication...")
        login_data = {
            "email": "authority@samudra-sachet.com",
            "password": "authority123"
        }
        
        try:
            async with session.post(f"{base_url}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data['access_token']
                    user_info = data['user']
                    print(f"✅ Login successful - User: {user_info['email']} ({user_info['user_role']})")
                    
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # 2. Test Get Current User
                    print("\n👤 Testing User Profile...")
                    try:
                        async with session.get(f"{base_url}/users/me", headers=headers) as response:
                            if response.status == 200:
                                user = await response.json()
                                print(f"✅ User profile retrieved: {user.get('full_name', 'N/A')}")
                            else:
                                error_data = await response.json()
                                print(f"❌ User profile failed: {error_data}")
                    except Exception as e:
                        print(f"❌ User profile error: {e}")
                    
                    # 3. Test Reports API
                    print("\n📊 Testing Reports API...")
                    try:
                        async with session.get(f"{base_url}/reports", headers=headers) as response:
                            if response.status == 200:
                                reports = await response.json()
                                print(f"✅ Reports retrieved: {len(reports.get('items', reports))} reports found")
                            else:
                                error_data = await response.json()
                                print(f"❌ Reports failed: {error_data}")
                    except Exception as e:
                        print(f"❌ Reports error: {e}")
                    
                    # 4. Test Hotspots API
                    print("\n🔥 Testing Hotspots API...")
                    try:
                        async with session.get(f"{base_url}/hotspots", headers=headers) as response:
                            if response.status == 200:
                                hotspots = await response.json()
                                print(f"✅ Hotspots retrieved: {len(hotspots.get('items', hotspots))} hotspots found")
                            else:
                                error_data = await response.json()
                                print(f"❌ Hotspots failed: {error_data}")
                    except Exception as e:
                        print(f"❌ Hotspots error: {e}")
                    
                    # 5. Test Social Media API
                    print("\n📱 Testing Social Media API...")
                    try:
                        async with session.get(f"{base_url}/social-media", headers=headers) as response:
                            if response.status == 200:
                                posts = await response.json()
                                print(f"✅ Social media posts retrieved: {len(posts.get('items', posts))} posts found")
                            else:
                                error_data = await response.json()
                                print(f"❌ Social media failed: {error_data}")
                    except Exception as e:
                        print(f"❌ Social media error: {e}")
                    
                    # 6. Test Admin Dashboard (for authority user)
                    print("\n🛠️  Testing Admin API...")
                    try:
                        async with session.get(f"{base_url}/admin/dashboard", headers=headers) as response:
                            if response.status == 200:
                                dashboard = await response.json()
                                print(f"✅ Admin dashboard retrieved")
                            else:
                                error_data = await response.json()
                                print(f"❌ Admin dashboard failed: {error_data}")
                    except Exception as e:
                        print(f"❌ Admin dashboard error: {e}")
                    
                else:
                    error_data = await response.json()
                    print(f"❌ Login failed: {error_data}")
                    return
                    
        except Exception as e:
            print(f"❌ Login error: {e}")
            return
        
        # 7. Test Public Endpoints (no auth required)
        print("\n🌐 Testing Public Endpoints...")
        
        try:
            async with session.get(f"http://127.0.0.1:8000/") as response:
                if response.status == 200:
                    root_data = await response.json()
                    print(f"✅ Root endpoint: {root_data.get('message', 'OK')}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        try:
            async with session.get(f"http://127.0.0.1:8000/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check: {health_data.get('status', 'OK')}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        print(f"\n🎯 API Test Summary")
        print(f"=" * 60)
        print(f"✅ Backend API: http://127.0.0.1:8000")
        print(f"✅ Frontend UI: http://localhost:5173")
        print(f"✅ API Docs: http://127.0.0.1:8000/docs")
        print(f"\n🔑 Test Credentials Used:")
        print(f"   - Email: authority@samudra-sachet.com")
        print(f"   - Password: authority123")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())