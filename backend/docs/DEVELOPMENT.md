# Development Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 12+ with PostGIS extension
- Git

### Quick Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run setup script
python setup.py

# 3. Configure environment
# Edit .env file with your database credentials

# 4. Set up database
psql -U postgres
CREATE DATABASE samudra_sachet;
\c samudra_sachet
CREATE EXTENSION postgis;
\q

# 5. Run migrations
alembic upgrade head

# 6. Start development server
python main.py
```

## 🏗️ Project Architecture

### Layer Structure
```
┌─────────────────┐
│   API Layer     │ ← FastAPI endpoints, request/response handling
├─────────────────┤
│   CRUD Layer    │ ← Business logic, database operations
├─────────────────┤
│   Database      │ ← SQLAlchemy models, PostgreSQL
└─────────────────┘
```

### Directory Structure
- `app/api/` - API endpoints and routing
- `app/crud/` - Business logic and database operations
- `app/models/` - SQLAlchemy ORM models
- `app/schemas/` - Pydantic data validation schemas
- `app/core/` - Configuration and security utilities
- `app/db/` - Database connection and session management

## 🔧 Development Workflow

### Adding New Features

1. **Create Model** (`app/models/`)
   ```python
   from app.db.base_class import BaseModel
   
   class NewModel(BaseModel):
       __tablename__ = "new_table"
       # Define fields
   ```

2. **Create Schema** (`app/schemas/`)
   ```python
   from pydantic import BaseModel
   
   class NewModelBase(BaseModel):
       # Define base fields
   
   class NewModelCreate(NewModelBase):
       # Define creation fields
   
   class NewModel(NewModelBase):
       # Define response fields
   ```

3. **Create CRUD** (`app/crud/`)
   ```python
   class CRUDNewModel:
       @staticmethod
       async def create(db: AsyncSession, obj_in: NewModelCreate):
           # Implementation
   ```

4. **Create API Endpoints** (`app/api/v1/endpoints/`)
   ```python
   from fastapi import APIRouter
   
   router = APIRouter()
   
   @router.post("/", response_model=NewModel)
   async def create_new_model(
       obj_in: NewModelCreate,
       db: AsyncSession = Depends(get_db)
   ):
       # Implementation
   ```

5. **Add to Main Router** (`app/api/v1/api.py`)
   ```python
   api_router.include_router(
       new_model.router,
       prefix="/new-models",
       tags=["New Models"]
   )
   ```

6. **Create Migration**
   ```bash
   alembic revision --autogenerate -m "Add new model"
   alembic upgrade head
   ```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current revision
alembic current
```

### Testing

```bash
# Run API tests
python test_api.py

# Run specific test
python -m pytest tests/test_auth.py

# Run with coverage
python -m pytest --cov=app tests/
```

## 🔐 Security Guidelines

### Authentication
- Use JWT tokens for authentication
- Implement refresh token mechanism
- Hash passwords with bcrypt
- Validate all input data with Pydantic

### Authorization
- Use role-based access control
- Implement dependency injection for auth checks
- Validate user permissions at endpoint level

### Data Validation
- Use Pydantic schemas for all request/response data
- Validate file uploads (type, size)
- Sanitize user input
- Use SQLAlchemy ORM to prevent SQL injection

## 📝 Code Style

### Python Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public functions
- Use async/await for database operations

### API Design
- Use RESTful conventions
- Return consistent error responses
- Implement proper HTTP status codes
- Use pagination for list endpoints

### Database Design
- Use UUIDs for primary keys
- Add proper indexes for performance
- Use foreign key constraints
- Implement soft deletes where appropriate

## 🐛 Debugging

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running
   - Verify database exists

2. **Import Errors**
   - Check Python path
   - Ensure all dependencies installed
   - Verify __init__.py files exist

3. **Authentication Errors**
   - Check SECRET_KEY in .env
   - Verify JWT token format
   - Check user role permissions

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
python main.py
```

### Database Debugging
```python
# Enable SQL query logging
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True  # Enable SQL logging
)
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in environment
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure file storage (S3, etc.)
- [ ] Set up email service
- [ ] Configure Redis for caching

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostGIS Documentation](https://postgis.net/documentation/)
