# Project Samudra Sachet - Backend

A comprehensive FastAPI backend for crowdsourced ocean hazard reporting and social media analytics.

## Features

- **User Management**: Multi-role authentication (Citizen, Analyst, Authority, Admin)
- **Hazard Reporting**: Crowdsourced coastal hazard reports with geospatial data
- **Social Media Analytics**: Integration with social media platforms for hazard detection
- **Hotspot Detection**: Dynamic clustering of hazard events
- **Media Analysis**: AI-powered analysis of uploaded media
- **Verification System**: Multi-level report verification workflow

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python init_database.py
```

This will:
- Create the database tables
- Create default admin user: `admin@samudra-sachet.com` / `admin123`
- Create demo users for testing

### 3. Start the Server

```bash
python start.py
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base URL**: http://localhost:8000/api/v1

## Default Users

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@samudra-sachet.com | admin123 |
| Authority | authority@samudra-sachet.com | authority123 |
| Analyst | analyst@samudra-sachet.com | analyst123 |
| Citizen | citizen@samudra-sachet.com | citizen123 |

## Database

The application uses SQLite by default (`samudra_sachet.db`). The database will:
- Persist data between restarts
- Only initialize tables once
- Store all user data, reports, and analytics

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user

### Reports
- `GET /api/v1/reports/` - List reports
- `POST /api/v1/reports/` - Create new report
- `GET /api/v1/reports/{id}` - Get report details
- `PUT /api/v1/reports/{id}` - Update report
- `DELETE /api/v1/reports/{id}` - Delete report

### Hotspots
- `GET /api/v1/hotspots/` - List hotspots
- `GET /api/v1/hotspots/{id}` - Get hotspot details

### Social Media
- `GET /api/v1/social-media/` - List social media posts
- `POST /api/v1/social-media/` - Add social media post

### Admin
- `GET /api/v1/admin/users/` - List all users
- `GET /api/v1/admin/reports/` - List all reports
- `GET /api/v1/admin/analytics/` - Get analytics data

## Development

### Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core configuration and security
│   ├── crud/            # Database operations
│   ├── db/              # Database configuration
│   ├── models/          # SQLAlchemy models
│   └── schemas/         # Pydantic schemas
├── alembic/             # Database migrations
├── docs/                # Documentation
├── init_database.py     # Database initialization
├── main.py              # FastAPI application
├── start.py             # Development server
└── requirements.txt     # Dependencies
```

### Environment Variables

Create a `.env` file for custom configuration:

```env
DATABASE_URL=sqlite+aiosqlite:///./samudra_sachet.db
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```

### Database Migrations

For production deployments, use Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Production Deployment

### Using Docker

```bash
# Build image
docker build -t samudra-sachet-backend .

# Run container
docker run -p 8000:8000 samudra-sachet-backend
```

### Using Docker Compose

```bash
docker-compose up -d
```

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- CORS configuration
- Input validation with Pydantic

## Monitoring

- Health check endpoint: `/health`
- Structured logging
- Error handling with proper HTTP status codes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.