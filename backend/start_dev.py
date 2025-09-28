#!/usr/bin/env python3
"""
Development startup script for Project Samudra Sachet.
Sets environment variables before importing the application.
"""

import os
import sys

# Set environment variables for development
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-development"
os.environ["DEBUG"] = "true"

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🌊 Starting Project Samudra Sachet Backend (Development Mode)")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🚀 API Base URL: http://localhost:8000/api/v1")
    print("==================================================")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )



