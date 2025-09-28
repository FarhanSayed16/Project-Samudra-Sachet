# 🌊 Project Samudra Sachet - Backend

A comprehensive FastAPI backend for crowdsourced ocean hazard reporting and social media analytics platform.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Installation

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   # For development (SQLite)
   export DATABASE_URL="sqlite+aiosqlite:///./samudra_sachet.db"
   export SECRET_KEY="your-secret-key-change-in-production"
   export DEBUG="true"
   
   # For production (PostgreSQL)
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost/samudra_sachet"
   export SECRET_KEY="your-production-secret-key"
   export DEBUG="false"
   ```

4. **Run the backend:**
   ```bash
   # Development mode
   python start.py
   
   # Production mode
   python start_production.py
   ```

5. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Base URL: http://localhost:8000/api/v1

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_backend.py
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/              # API endpoints
│   │   ├── endpoints/        # Individual endpoint modules
│   │   └── api.py           # Main API router
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration management
│   │   ├── security.py      # Authentication & authorization
│   │   └── file_upload.py   # File upload utilities
│   ├── crud/                # Database operations
│   ├── db/                  # Database configuration
│   │   ├── base_class.py    # Base model class
│   │   ├── session.py       # Database session management
│   │   └── utils.py         # Database utilities
│   ├── models/              # SQLAlchemy models
│   └── schemas/             # Pydantic schemas
├── alembic/                 # Database migrations
├── docs/                    # Documentation
├── main.py                  # FastAPI application
├── start.py                 # Development startup script
├── start_production.py      # Production startup script
├── test_backend.py          # Comprehensive test suite
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker development setup
└── Dockerfile              # Production Docker image
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./samudra_sachet.db` | Yes |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `DEBUG` | Debug mode | `false` | No |
| `APP_NAME` | Application name | `Project Samudra Sachet` | No |
| `APP_VERSION` | Application version | `1.0.0` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | `30` | No |
| `ALGORITHM` | JWT algorithm | `HS256` | No |

### Database Support

- **SQLite** (Development): `sqlite+aiosqlite:///./samudra_sachet.db`
- **PostgreSQL** (Production): `postgresql+asyncpg://user:password@host:port/database`

## 🔐 Authentication & Authorization

### User Roles
- **Citizen**: Submit reports, view public data
- **Analyst**: Verify reports, access analytics
- **Authority**: Manage alerts, access all data
- **Admin**: Full system access

### JWT Tokens
- Access tokens (30 minutes)
- Refresh tokens (7 days)
- Role-based access control

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout

### User Management
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/password` - Change password

### Reports
- `POST /api/v1/reports` - Submit hazard report
- `GET /api/v1/reports` - List reports (with filters)
- `GET /api/v1/reports/{id}` - Get specific report
- `POST /api/v1/reports/{id}/vote` - Vote on report

### Verification
- `POST /api/v1/reports/{id}/verification` - Verify report
- `GET /api/v1/reports/{id}/verifications` - Get verification history

### Social Media Analytics
- `GET /api/v1/social-media` - List social media posts
- `GET /api/v1/social-media/{id}` - Get specific post

### AI Analysis
- `POST /api/v1/analysis/image` - Analyze image
- `POST /api/v1/analysis/text` - Analyze text
- `GET /api/v1/analysis/{id}` - Get analysis results

### Hotspots
- `GET /api/v1/hotspots` - List active hotspots
- `GET /api/v1/hotspots/{id}` - Get specific hotspot

### Admin
- `GET /api/v1/admin/dashboard` - Admin dashboard
- `GET /api/v1/admin/users` - List all users
- `PATCH /api/v1/admin/users/{id}/role` - Update user role

### Alerts
- `POST /api/v1/alerts` - Create alert
- `GET /api/v1/alerts` - List alerts

## 🐳 Docker Support

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker build -t samudra-sachet-backend .
docker run -p 8000:8000 samudra-sachet-backend
```

## 🗄️ Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🔍 Monitoring & Health Checks

- Health endpoint: `GET /health`
- API documentation: `GET /docs`
- OpenAPI schema: `GET /openapi.json`

## 🚀 Deployment

### Production Checklist
- [ ] Set strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set `DEBUG=false`
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup strategy

### Environment-Specific Configs
- **Development**: SQLite, debug enabled, auto-reload
- **Staging**: PostgreSQL, debug disabled, production-like
- **Production**: PostgreSQL, debug disabled, optimized settings

## 📚 Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Development Guide](docs/DEVELOPMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_backend.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the API documentation at `/docs` endpoint

---

**🌊 Project Samudra Sachet** - Protecting coastal communities through technology