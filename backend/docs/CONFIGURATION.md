# Environment Configuration Guide

## Required Environment Variables

Create a `.env` file in the backend directory with the following variables:

### Database Configuration
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/samudra_sachet
```

### Security Configuration
```env
SECRET_KEY=your-secret-key-change-in-production-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Application Configuration
```env
APP_NAME=Project Samudra Sachet
APP_VERSION=1.0.0
DEBUG=True
```

### CORS Configuration
```env
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

## Optional Environment Variables

### File Upload Configuration
```env
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "image/webp", "video/mp4"]
```

### Social Media API Configuration
```env
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

### AI/ML Configuration
```env
AI_MODEL_ENDPOINT=your_ai_model_endpoint
AI_MODEL_API_KEY=your_ai_model_api_key
```

### Redis Configuration
```env
REDIS_URL=redis://localhost:6379
```

### Email Configuration
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_TLS=True
```

## Setup Instructions

1. Copy the required variables to a `.env` file
2. Update the `DATABASE_URL` with your PostgreSQL credentials
3. Generate a secure `SECRET_KEY` (use a password generator)
4. Set `DEBUG=False` for production
5. Add optional variables as needed for your deployment
