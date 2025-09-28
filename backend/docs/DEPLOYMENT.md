# Deployment Guide - Project Samudra Sachet

## 🚀 Production Deployment

This guide covers deploying the Project Samudra Sachet backend to production environments.

## 📋 Prerequisites

- Docker and Docker Compose
- PostgreSQL 12+ with PostGIS extension
- Redis (optional, for caching)
- SSL certificates (for HTTPS)
- Domain name and DNS configuration

## 🐳 Docker Deployment

### 1. **Build and Run with Docker Compose**

```bash
# Clone the repository
git clone <repository-url>
cd Project-Samudra-Sachet/backend

# Copy environment configuration
cp .env.example .env
# Edit .env with production values

# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 2. **Manual Docker Build**

```bash
# Build the image
docker build -t samudra-sachet-backend .

# Run the container
docker run -d \
  --name samudra-sachet-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  samudra-sachet-backend
```

## 🗄️ Database Setup

### 1. **PostgreSQL with PostGIS**

```sql
-- Create database
CREATE DATABASE samudra_sachet;

-- Connect to database
\c samudra_sachet;

-- Enable PostGIS extension
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Create user (optional)
CREATE USER samudra_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE samudra_sachet TO samudra_user;
```

### 2. **Run Database Migrations**

```bash
# Inside the container or local environment
alembic upgrade head
```

## ⚙️ Environment Configuration

### **Production Environment Variables**

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/samudra_sachet

# Security
SECRET_KEY=your-very-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=Project Samudra Sachet
APP_VERSION=1.0.0
DEBUG=False

# CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "image/webp", "video/mp4"]

# Redis (optional)
REDIS_URL=redis://redis-host:6379

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=True

# Social Media APIs (optional)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# AI/ML Services (optional)
AI_MODEL_ENDPOINT=https://your-ai-service.com/api
AI_MODEL_API_KEY=your_ai_api_key
```

## 🔒 Security Configuration

### 1. **SSL/TLS Setup**

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. **Security Headers**

```python
# Add to main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Monitoring and Logging

### 1. **Health Checks**

```bash
# Check API health
curl https://yourdomain.com/health

# Check database connection
curl https://yourdomain.com/api/v1/admin/system/health
```

### 2. **Log Management**

```python
# Add to main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("logs/app.log", maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

## 🔄 Background Services

### 1. **Hotspot Generation Service**

```bash
# Create cron job for hotspot generation
# Run every 10 minutes
*/10 * * * * /usr/local/bin/python /app/services/hotspot_generator.py
```

### 2. **Social Media Ingestor**

```bash
# Create cron job for social media ingestion
# Run every 5 minutes
*/5 * * * * /usr/local/bin/python /app/services/social_media_ingestor.py
```

### 3. **AI Processing Service**

```bash
# Create cron job for AI processing
# Run every 15 minutes
*/15 * * * * /usr/local/bin/python /app/services/ai_processor.py
```

## 📈 Performance Optimization

### 1. **Database Optimization**

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_reports_location ON reports USING GIST (location);
CREATE INDEX CONCURRENTLY idx_reports_created_at ON reports (created_at);
CREATE INDEX CONCURRENTLY idx_hotspots_location ON hotspots USING GIST (location);
CREATE INDEX CONCURRENTLY idx_social_media_location ON social_media_posts USING GIST (location);
```

### 2. **Caching Strategy**

```python
# Add Redis caching
import redis
from functools import wraps

redis_client = redis.from_url(settings.REDIS_URL)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached_result = redis_client.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        
        return wrapper
    return decorator
```

## 🚨 Backup and Recovery

### 1. **Database Backup**

```bash
# Create backup script
#!/bin/bash
pg_dump -h localhost -U postgres -d samudra_sachet > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated daily backups
0 2 * * * /path/to/backup_script.sh
```

### 2. **File Backup**

```bash
# Backup uploaded files
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz /app/uploads/
```

## 🔧 Maintenance

### 1. **Regular Maintenance Tasks**

```bash
# Clean up old audit logs
python -c "from app.crud.crud_audit_log import crud_audit_log; crud_audit_log.cleanup_old_logs(db, days=90)"

# Clean up expired hotspots
python -c "from app.crud.crud_hotspot import crud_hotspot; crud_hotspot.cleanup_expired_hotspots(db)"

# Update AI models
curl -X POST https://yourdomain.com/api/v1/analysis/models/retrain
```

### 2. **Monitoring Commands**

```bash
# Check container health
docker-compose ps

# View resource usage
docker stats

# Check logs
docker-compose logs --tail=100 backend

# Database connection test
docker-compose exec backend python -c "from app.db.session import get_db; print('DB OK')"
```

## 🚀 Scaling

### 1. **Horizontal Scaling**

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/samudra_sachet
```

### 2. **Load Balancing**

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

## 📞 Troubleshooting

### **Common Issues**

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   docker-compose exec backend python -c "import asyncpg; print('DB OK')"
   ```

2. **File Upload Issues**
   ```bash
   # Check upload directory permissions
   ls -la /app/uploads/
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   ```

4. **Performance Issues**
   ```bash
   # Check slow queries
   docker-compose exec postgres psql -U postgres -d samudra_sachet -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
   ```

## 📚 Additional Resources

- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)

---

**Deployment Status**: ✅ Production Ready  
**Security**: ✅ Hardened Configuration  
**Monitoring**: ✅ Health Checks & Logging  
**Scaling**: ✅ Horizontal Scaling Support
