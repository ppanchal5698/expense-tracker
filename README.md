# Expense Management API

A production-grade REST API for expense tracking built with FastAPI, Supabase (PostgreSQL), and SQLAlchemy.

## Features

- **User Management**: Registration, authentication (JWT), profile management
- **Expense Tracking**: Create, read, update, delete expenses with timestamps
- **Categories**: Predefined and custom expense categories per user
- **Analytics**: Monthly spending summaries, category breakdown, trends
- **Filtering**: Query by date range, category, amount range, tags
- **Data Validation**: Strict input validation using Pydantic v2
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes

## Technology Stack

- **Framework**: FastAPI ^0.104.0
- **Database**: Supabase (PostgreSQL)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic ^1.13.0
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Server**: Uvicorn
- **Testing**: pytest + pytest-asyncio

## Prerequisites

- Python 3.10 or higher
- Supabase account (free tier sufficient)
- pip or Poetry for dependency management
- Git for version control

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd expense-tracker
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using Poetry (if installed)
poetry install
```

### 4. Set Up Supabase

1. Create an account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Project Settings → Database
4. Copy the connection string
5. Note: Use connection pooler (port 6543) for production

### 5. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update the following:
   - `DATABASE_URL`: Your Supabase connection string
   - `SECRET_KEY`: Generate a new secret key:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

### 6. Run the Application

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (generate a secure random string)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)
- `API_TITLE`: API title for documentation
- `API_VERSION`: API version
- `ALLOWED_ORIGINS`: CORS allowed origins (JSON array)

## Project Structure

```
expense-tracker/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Configuration and security
│   ├── database/         # Database models and connection
│   ├── schemas/          # Pydantic schemas
│   ├── crud/             # Database operations
│   ├── services/         # Business logic
│   ├── middleware/       # Custom middleware
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── .env                  # Environment variables (git-ignored)
├── .env.example          # Environment variables template
├── pyproject.toml        # Project dependencies
└── requirements.txt      # pip dependencies
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_expenses.py
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current revision
alembic current
```

### Code Quality

```bash
# Format code (Black)
black app/ tests/

# Lint code (Ruff)
ruff check app/ tests/

# Type checking (MyPy)
mypy app/
```

## API Documentation

Once the application is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Health Checks

- **Application Health**: `GET /health`
- **Root Endpoint**: `GET /`

## Common Issues

### Virtual Environment Not Activating

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Dependencies Installation Fails

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Database Connection Fails

- Verify your `DATABASE_URL` in `.env`
- Check Supabase project is active
- Ensure connection string format is correct:
  ```
  postgresql://postgres:[password]@[host]:[port]/postgres
  ```

### Port 8000 Already in Use

```bash
uvicorn app.main:app --port 8001
```

## Next Steps

After completing Sprint 0, proceed to:
- **Sprint 1**: Database Schema & Models
- **Sprint 2**: Core Configuration & Security
- **Sprint 3**: User Management & Authentication

See `markdown/Sprint-Index.md` for complete sprint documentation.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

