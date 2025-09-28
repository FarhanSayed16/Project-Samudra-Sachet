#!/usr/bin/env python3
"""
Project Samudra Sachet - Backend Startup Script
Clean and simple startup for development and production
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Start the FastAPI backend server"""
    
    # Set default environment variables if not already set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./samudra_sachet.db"
    
    if not os.getenv("SECRET_KEY"):
        os.environ["SECRET_KEY"] = "your-secret-key-change-in-production"
    
    if not os.getenv("DEBUG"):
        os.environ["DEBUG"] = "true"
    
    print("🌊 Starting Project Samudra Sachet Backend...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🚀 API Base URL: http://localhost:8000/api/v1")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
