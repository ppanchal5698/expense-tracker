# Sprint 0: Project Setup & Infrastructure

## 📋 Sprint Overview

**Duration:** 2-3 days
**Objective:** Establish project foundation, development environment, and basic infrastructure setup.

**Success Criteria:**
- ✅ Project structure created and organized
- ✅ All dependencies installed and verified
- ✅ Virtual environment configured
- ✅ Git repository initialized
- ✅ Basic FastAPI application running
- ✅ Environment variables configured
- ✅ Supabase project created and connection tested

---

## 🎯 Sprint Goals

1. Initialize project structure following best practices
2. Set up Python virtual environment and dependency management
3. Configure Supabase database connection
4. Create basic FastAPI application skeleton
5. Establish development workflow and tooling

---

## 📝 Detailed Tasks

### Task 1: Project Structure Setup

**Estimated Time:** 30 minutes

**Steps:**
1. Create root project directory: `expense-management-api`
2. Initialize Git repository
   ```bash
   git init
   ```
3. Create directory structure:
   ```
   expense-management-api/
   ├── .env.example
   ├── .env
   ├── .gitignore
   ├── pyproject.toml
   ├── requirements.txt
   ├── README.md
   ├── alembic/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── settings.py
   │   ├── dependencies.py
   │   ├── api/
   │   ├── core/
   │   ├── database/
   │   ├── schemas/
   │   ├── crud/
   │   ├── services/
   │   └── middleware/
   ├── tests/
   └── scripts/
   ```
4. Create `.gitignore` file with Python, environment, and IDE exclusions

**Acceptance Criteria:**
- All directories created
- `.gitignore` properly configured
- Git repository initialized

---

### Task 2: Virtual Environment & Dependencies

**Estimated Time:** 45 minutes

**Steps:**
1. Create Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Create `pyproject.toml` with Poetry configuration:
   ```toml
   [tool.poetry]
   name = "expense-management-api"
   version = "1.0.0"
   description = "Expense tracking API with FastAPI, Supabase, and SQLAlchemy"
   authors = ["Your Name <your.email@example.com>"]

   [tool.poetry.dependencies]
   python = "^3.10"
   fastapi = "^0.104.0"
   uvicorn = {version = "^0.24.0", extras = ["standard"]}
   sqlalchemy = "^2.0.0"
   asyncpg = "^0.29.0"
   alembic = "^1.13.0"
   pydantic = "^2.0.0"
   pydantic-settings = "^2.0.0"
   python-jose = {version = "^3.3.0", extras = ["cryptography"]}
   passlib = {version = "^1.7.0", extras = ["bcrypt"]}
   python-dotenv = "^1.0.0"
   pytest = "^7.4.0"
   pytest-asyncio = "^0.21.0"
   httpx = "^0.25.0"

   [build-system]
   requires = ["poetry-core"]
   build-backend = "poetry.core.masonry.api"
   ```

3. Install dependencies:
   ```bash
   poetry install
   # OR using pip:
   pip install -r requirements.txt
   ```

4. Verify installation:
   ```bash
   python -c "import fastapi; print(fastapi.__version__)"
   python -c "import sqlalchemy; print(sqlalchemy.__version__)"
   ```

**Acceptance Criteria:**
- Virtual environment created and activated
- All dependencies installed successfully
- No import errors when verifying packages

---

### Task 3: Supabase Setup

**Estimated Time:** 30 minutes

**Steps:**
1. Create Supabase account at https://supabase.com
2. Create new project:
   - Choose region (e.g., us-east-1)
   - Set strong database password
   - Wait for project initialization
3. Get connection string:
   - Navigate to Project Settings → Database
   - Copy connection string
   - Note: Use connection pooler (port 6543) for production
4. Test connection using DBeaver or psql:
   ```bash
   psql "postgresql://postgres:[password]@[host]:[port]/postgres"
   ```

**Acceptance Criteria:**
- Supabase project created
- Connection string obtained
- Database connection tested successfully

---

### Task 4: Environment Configuration

**Estimated Time:** 30 minutes

**Steps:**
1. Generate SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Create `.env.example` template:
   ```env
   # Environment
   ENV=development
   DEBUG=true

   # Supabase Database
   DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/postgres
   DATABASE_POOL_MIN=1
   DATABASE_POOL_MAX=20
   DATABASE_TIMEOUT=30

   # JWT Security
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # API Configuration
   API_TITLE=Expense Management API
   API_VERSION=1.0.0
   API_DESCRIPTION=Track and analyze personal expenses
   ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

   # Logging
   LOG_LEVEL=INFO
   ```

3. Create `.env` file with actual values (git-ignored)

**Acceptance Criteria:**
- `.env.example` created with all required variables
- `.env` file created with actual credentials
- SECRET_KEY generated and stored securely

---

### Task 5: Basic FastAPI Application

**Estimated Time:** 45 minutes

**Steps:**
1. Create `app/__init__.py` (empty file)

2. Create `app/main.py`:
   ```python
   from fastapi import FastAPI
   from contextlib import asynccontextmanager
   from app.core.config import settings

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Startup
       print("✅ App starting...")
       yield
       # Shutdown
       print("🛑 App shutting down...")

   app = FastAPI(
       title=settings.API_TITLE,
       version=settings.API_VERSION,
       description=settings.API_DESCRIPTION,
       lifespan=lifespan
   )

   @app.get("/")
   async def root():
       return {
           "message": "Expense Management API",
           "version": settings.API_VERSION,
           "status": "running"
       }

   @app.get("/health")
   async def health_check():
       return {"status": "healthy"}

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
   ```

3. Create `app/core/config.py` (basic version):
   ```python
   from pydantic_settings import BaseSettings
   from typing import List

   class Settings(BaseSettings):
       # App
       APP_NAME: str = "Expense Management API"
       APP_VERSION: str = "1.0.0"
       DEBUG: bool = False

       # Database
       DATABASE_URL: str
       DATABASE_POOL_MIN: int = 5
       DATABASE_POOL_MAX: int = 20
       DATABASE_TIMEOUT: int = 30

       # Security
       SECRET_KEY: str
       ALGORITHM: str = "HS256"
       ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
       REFRESH_TOKEN_EXPIRE_DAYS: int = 7

       # CORS
       ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

       class Config:
           env_file = ".env"
           case_sensitive = True

   settings = Settings()
   ```

4. Test the application:
   ```bash
   python app/main.py
   # OR
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Verify:
   - Visit http://localhost:8000
   - Visit http://localhost:8000/docs (Swagger UI)
   - Visit http://localhost:8000/redoc (ReDoc)

**Acceptance Criteria:**
- FastAPI application starts without errors
- Root endpoint returns correct response
- Health check endpoint works
- OpenAPI documentation accessible at `/docs`
- Settings loaded from `.env` file

---

### Task 6: Alembic Initialization

**Estimated Time:** 30 minutes

**Steps:**
1. Initialize Alembic:
   ```bash
   alembic init alembic
   ```

2. Verify `alembic/` directory structure:
   ```
   alembic/
   ├── versions/
   ├── env.py
   └── alembic.ini
   ```

3. Update `alembic.ini` with database URL (temporary, will use env.py later)

4. Test Alembic connection:
   ```bash
   alembic current
   ```

**Acceptance Criteria:**
- Alembic initialized successfully
- Directory structure created
- Alembic can connect to database

---

### Task 7: README Documentation

**Estimated Time:** 30 minutes

**Steps:**
1. Create comprehensive `README.md`:
   - Project description
   - Setup instructions
   - Environment variables
   - Running the application
   - API documentation links
   - Development workflow

**Acceptance Criteria:**
- README.md created with all essential information
- Setup instructions are clear and complete

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] Project structure matches specification
- [ ] Virtual environment activates correctly
- [ ] All dependencies install without errors
- [ ] FastAPI application starts successfully
- [ ] Root endpoint responds correctly
- [ ] Health check endpoint works
- [ ] OpenAPI docs accessible
- [ ] Environment variables load correctly
- [ ] Supabase connection can be established
- [ ] Alembic initialized properly

### Verification Commands

```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | grep -E "fastapi|sqlalchemy|pydantic"

# Test application
curl http://localhost:8000/
curl http://localhost:8000/health

# Check Alembic
alembic current
```

---

## 📦 Deliverables

1. ✅ Complete project directory structure
2. ✅ Virtual environment with all dependencies
3. ✅ `.env` and `.env.example` files
4. ✅ Basic FastAPI application running
5. ✅ Supabase project configured
6. ✅ Alembic initialized
7. ✅ README.md documentation
8. ✅ Git repository initialized

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Virtual environment not activating | Use full path: `.\venv\Scripts\activate` (Windows) |
| Dependencies installation fails | Upgrade pip: `python -m pip install --upgrade pip` |
| FastAPI import error | Verify virtual environment is activated |
| Database connection fails | Check connection string format and credentials |
| Port 8000 already in use | Change port: `uvicorn app.main:app --port 8001` |

---

## 🔄 Next Sprint Preview

**Sprint 1: Database Schema & Models**
- Design database schema
- Create SQLAlchemy models
- Configure Alembic for migrations
- Create initial migration

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Setup Guide](https://supabase.com/docs/guides/getting-started)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

