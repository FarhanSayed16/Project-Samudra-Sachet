#!/usr/bin/env python3
"""
Project Samudra Sachet - Production Startup Script
Optimized for production deployment
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Start the FastAPI backend server in production mode"""
    
    # Production environment variables (should be set by deployment system)
    required_env_vars = ["DATABASE_URL", "SECRET_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("🌊 Starting Project Samudra Sachet Backend (Production)...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🚀 API Base URL: http://localhost:8000/api/v1")
    print("=" * 50)
    
    # Start the server in production mode
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 1)),
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
