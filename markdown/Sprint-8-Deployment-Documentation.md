# Sprint 8: Deployment & Documentation

## 📋 Sprint Overview

**Duration:** 3-4 days
**Objective:** Prepare application for production deployment, complete API documentation, and set up monitoring.

**Success Criteria:**
- ✅ Production configuration complete
- ✅ Application deployed to production
- ✅ API documentation complete
- ✅ Deployment checklist verified
- ✅ Monitoring and logging configured
- ✅ Environment variables documented

---

## 🎯 Sprint Goals

1. Configure production settings
2. Set up deployment infrastructure
3. Complete API documentation
4. Configure monitoring and logging
5. Create deployment guide
6. Perform final security review

---

## 📝 Detailed Tasks

### Task 1: Production Configuration

**Estimated Time:** 2 hours

**Steps:**
1. Create production `.env.example`:
   ```env
   # Environment
   ENV=production
   DEBUG=false

   # Supabase Database (Production)
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   DATABASE_POOL_MIN=10
   DATABASE_POOL_MAX=50
   DATABASE_TIMEOUT=30

   # JWT Security (Generate new secret for production)
   SECRET_KEY=your-production-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # API Configuration
   API_TITLE=Expense Management API
   API_VERSION=1.0.0
   API_DESCRIPTION=Track and analyze personal expenses

   # CORS (Update with production frontend URL)
   ALLOWED_ORIGINS=["https://yourdomain.com"]

   # Logging
   LOG_LEVEL=INFO
   ```

2. Update `app/core/config.py` for production:
   ```python
   class Settings(BaseSettings):
       # ... existing fields

       # Add production-specific settings
       LOG_LEVEL: str = "INFO"
       SENTRY_DSN: Optional[str] = None  # Optional error tracking

       @validator("SECRET_KEY")
       def validate_secret_key(cls, v):
           if len(v) < 32:
               raise ValueError("SECRET_KEY must be at least 32 characters")
           return v

       @validator("ALLOWED_ORIGINS", pre=True)
       def parse_cors_origins(cls, v):
           if isinstance(v, str):
               import json
               return json.loads(v)
           return v
   ```

3. Create production startup script `scripts/start_production.sh`:
   ```bash
   #!/bin/bash
   export ENV=production
   export DEBUG=false

   # Run migrations
   alembic upgrade head

   # Start application
   uvicorn app.main:app \
     --host 0.0.0.0 \
     --port 8000 \
     --workers 4 \
     --log-level info
   ```

**Acceptance Criteria:**
- Production configuration complete
- Environment variables validated
- Security settings hardened

---

### Task 2: Logging Configuration

**Estimated Time:** 1.5 hours

**Steps:**
1. Create `app/core/logging_config.py`:
   ```python
   import logging
   import sys
   from app.core.config import settings

   def setup_logging():
       """Configure application logging"""
       log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

       logging.basicConfig(
           level=log_level,
           format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
           datefmt="%Y-%m-%d %H:%M:%S",
           handlers=[
               logging.StreamHandler(sys.stdout)
           ]
       )

       # Set specific loggers
       logging.getLogger("uvicorn").setLevel(log_level)
       logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
   ```

2. Update `app/main.py`:
   ```python
   from app.core.logging_config import setup_logging

   # Setup logging before creating app
   setup_logging()

   app = FastAPI(...)
   ```

3. Add structured logging to endpoints:
   ```python
   import logging

   logger = logging.getLogger(__name__)

   @router.post("/expenses")
   async def create_expense(...):
       logger.info(f"Creating expense for user {current_user.id}")
       # ... rest of code
   ```

**Acceptance Criteria:**
- Logging configured
- Log levels appropriate
- Structured logging in place

---

### Task 3: API Documentation Enhancement

**Estimated Time:** 2 hours

**Steps:**
1. Update `app/main.py` with enhanced OpenAPI config:
   ```python
   app = FastAPI(
       title=settings.API_TITLE,
       version=settings.API_VERSION,
       description=settings.API_DESCRIPTION,
       docs_url="/docs",
       redoc_url="/redoc",
       openapi_url="/openapi.json",
       openapi_tags=[
           {
               "name": "Authentication",
               "description": "User authentication and token management"
           },
           {
               "name": "Users",
               "description": "User profile management"
           },
           {
               "name": "Categories",
               "description": "Expense category management"
           },
           {
               "name": "Expenses",
               "description": "Expense tracking and management"
           },
           {
               "name": "Analytics",
               "description": "Expense analytics and reporting"
           }
       ]
   )
   ```

2. Add detailed docstrings to all endpoints:
   ```python
   @router.post(
       "/expenses",
       response_model=ExpenseResponse,
       status_code=status.HTTP_201_CREATED,
       summary="Create a new expense",
       description="""
       Create a new expense record with the following information:
       - Amount (must be greater than 0)
       - Date of expense
       - Category (must belong to the authenticated user)
       - Optional: description, payment method, tags, notes

       The expense will be associated with the authenticated user.
       """
   )
   async def create_expense(...):
       """Create a new expense record"""
       ...
   ```

3. Add response examples:
   ```python
   from fastapi.responses import JSONResponse

   @router.get(
       "/expenses",
       responses={
           200: {
               "description": "List of expenses",
               "content": {
                   "application/json": {
                       "example": {
                           "total": 100,
                           "items": [...],
                           "page": 1,
                           "per_page": 10,
                           "total_pages": 10
                       }
                   }
               }
           }
       }
   )
   ```

**Acceptance Criteria:**
- OpenAPI documentation complete
- All endpoints documented
- Examples provided
- Tags organized

---

### Task 4: Docker Configuration

**Estimated Time:** 2 hours

**Steps:**
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       postgresql-client \
       && rm -rf /var/lib/apt/lists/*

   # Copy dependency files
   COPY pyproject.toml ./
   COPY requirements.txt ./

   # Install Python dependencies
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Create non-root user
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser

   # Expose port
   EXPOSE 8000

   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
     CMD python -c "import requests; requests.get('http://localhost:8000/health')"

   # Run application
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Create `.dockerignore`:
   ```
   __pycache__
   *.pyc
   *.pyo
   *.pyd
   .env
   .venv
   venv/
   .git
   .gitignore
   tests/
   *.md
   .pytest_cache
   htmlcov/
   .coverage
   ```

3. Create `docker-compose.yml` (for local testing):
   ```yaml
   version: '3.8'

   services:
     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://user:pass@db:5432/expense_db
         - SECRET_KEY=${SECRET_KEY}
       depends_on:
         - db
       volumes:
         - ./app:/app/app

     db:
       image: postgres:15
       environment:
         - POSTGRES_USER=user
         - POSTGRES_PASSWORD=pass
         - POSTGRES_DB=expense_db
       volumes:
         - postgres_data:/var/lib/postgresql/data

   volumes:
     postgres_data:
   ```

**Acceptance Criteria:**
- Dockerfile created
- Docker image builds successfully
- Docker Compose works for local testing

---

### Task 5: Deployment Platform Setup

**Estimated Time:** 3 hours

**Steps:**
1. **Option A: Railway Deployment**
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli

   # Login
   railway login

   # Initialize project
   railway init

   # Add environment variables
   railway variables set DATABASE_URL=$DATABASE_URL
   railway variables set SECRET_KEY=$SECRET_KEY

   # Deploy
   railway up
   ```

2. **Option B: Render Deployment**
   - Create `render.yaml`:
   ```yaml
   services:
     - type: web
       name: expense-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: DATABASE_URL
           sync: false
         - key: SECRET_KEY
           generateValue: true
   ```

3. **Option C: AWS EC2 Deployment**
   ```bash
   # On EC2 instance
   sudo apt update
   sudo apt install python3-pip postgresql-client

   # Clone repository
   git clone <repo-url>
   cd expense-management-api

   # Install dependencies
   pip3 install -r requirements.txt

   # Run with Gunicorn
   pip3 install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

4. **Option D: Docker Deployment**
   ```bash
   # Build image
   docker build -t expense-api .

   # Run container
   docker run -d \
     -p 8000:8000 \
     -e DATABASE_URL=$DATABASE_URL \
     -e SECRET_KEY=$SECRET_KEY \
     expense-api
   ```

**Acceptance Criteria:**
- Deployment platform chosen
- Application deployed
- Environment variables configured
- Application accessible

---

### Task 6: Database Migration in Production

**Estimated Time:** 1 hour

**Steps:**
1. Create migration script `scripts/deploy_migrations.sh`:
   ```bash
   #!/bin/bash
   set -e

   echo "Running database migrations..."
   alembic upgrade head

   echo "Migrations completed successfully"
   ```

2. Verify migration strategy:
   - Backup database before migration
   - Test migrations on staging first
   - Rollback plan in place

3. Add migration health check:
   ```python
   @app.get("/health/db")
   async def health_check_db(db: AsyncSession = Depends(get_db)):
       """Check database connectivity"""
       try:
           await db.execute("SELECT 1")
           return {"status": "healthy", "database": "connected"}
       except Exception as e:
           return {"status": "unhealthy", "error": str(e)}
   ```

**Acceptance Criteria:**
- Migration script created
- Database migrations tested
- Health check endpoint works

---

### Task 7: Security Hardening

**Estimated Time:** 2 hours

**Steps:**
1. Review security checklist:
   - [ ] SECRET_KEY is strong and unique
   - [ ] Database credentials secure
   - [ ] CORS properly configured
   - [ ] No sensitive data in logs
   - [ ] HTTPS enabled in production
   - [ ] Rate limiting configured (optional)
   - [ ] Input validation on all endpoints
   - [ ] SQL injection prevention (using ORM)
   - [ ] XSS prevention (API only, no HTML)

2. Add rate limiting (optional):
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded

   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

   @router.post("/auth/login")
   @limiter.limit("5/minute")
   async def login(...):
       ...
   ```

3. Add security headers middleware:
   ```python
   from fastapi.middleware.trustedhost import TrustedHostMiddleware

   app.add_middleware(
       TrustedHostMiddleware,
       allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
   )
   ```

**Acceptance Criteria:**
- Security checklist completed
- Rate limiting configured (if needed)
- Security headers added
- No security vulnerabilities

---

### Task 8: Monitoring Setup

**Estimated Time:** 2 hours

**Steps:**
1. Add application metrics endpoint:
   ```python
   @app.get("/metrics")
   async def metrics():
       """Application metrics (for monitoring)"""
       return {
           "version": settings.API_VERSION,
           "status": "running",
           "timestamp": datetime.utcnow().isoformat()
       }
   ```

2. Set up error tracking (optional - Sentry):
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.fastapi import FastApiIntegration
   from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

   if settings.SENTRY_DSN:
       sentry_sdk.init(
           dsn=settings.SENTRY_DSN,
           integrations=[
               FastApiIntegration(),
               SqlalchemyIntegration()
           ],
           traces_sample_rate=0.1,
           environment=settings.ENV
       )
   ```

3. Add request logging middleware:
   ```python
   @app.middleware("http")
   async def log_requests(request: Request, call_next):
       start_time = time.time()
       response = await call_next(request)
       process_time = time.time() - start_time

       logger.info(
           f"{request.method} {request.url.path} - "
           f"Status: {response.status_code} - "
           f"Time: {process_time:.3f}s"
       )
       return response
   ```

**Acceptance Criteria:**
- Monitoring endpoints created
- Error tracking configured (if used)
- Request logging works
- Metrics available

---

### Task 9: Deployment Documentation

**Estimated Time:** 2 hours

**Steps:**
1. Create `DEPLOYMENT.md`:
   ```markdown
   # Deployment Guide

   ## Prerequisites
   - Python 3.10+
   - PostgreSQL database (Supabase)
   - Environment variables configured

   ## Deployment Steps

   1. Clone repository
   2. Install dependencies
   3. Configure environment variables
   4. Run database migrations
   5. Start application

   ## Environment Variables
   [List all required variables]

   ## Health Checks
   - `/health` - Application health
   - `/health/db` - Database connectivity

   ## Rollback Procedure
   [Steps to rollback if needed]
   ```

2. Update `README.md` with deployment section:
   - Quick start guide
   - API documentation links
   - Environment setup
   - Testing instructions
   - Deployment options

3. Create `CHANGELOG.md`:
   ```markdown
   # Changelog

   ## [1.0.0] - 2024-01-01
   - Initial release
   - User authentication
   - Expense management
   - Category management
   - Analytics and reporting
   ```

**Acceptance Criteria:**
- Deployment guide complete
- README updated
- Changelog created
- Documentation clear

---

### Task 10: Final Verification

**Estimated Time:** 2 hours

**Steps:**
1. Run deployment checklist:
   - [ ] All tests passing
   - [ ] No hardcoded secrets
   - [ ] Environment variables documented
   - [ ] Database migrations tested
   - [ ] API documentation complete
   - [ ] Error handling comprehensive
   - [ ] CORS properly configured
   - [ ] Logging configured
   - [ ] Health checks working
   - [ ] Security review completed

2. Perform smoke tests:
   - Test all endpoints
   - Verify authentication
   - Check error responses
   - Verify logging

3. Load testing (optional):
   ```bash
   # Using Apache Bench
   ab -n 1000 -c 10 http://your-api.com/api/v1/expenses
   ```

**Acceptance Criteria:**
- All checklist items verified
- Smoke tests pass
- Application ready for production

---

## 🧪 Testing & Verification

### Pre-Deployment Checklist

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Code coverage > 80%
- [ ] No security vulnerabilities
- [ ] Environment variables set
- [ ] Database migrations tested
- [ ] API documentation complete
- [ ] Logging configured
- [ ] Health checks working
- [ ] CORS configured correctly

### Post-Deployment Verification

- [ ] Application accessible
- [ ] Health endpoint responds
- [ ] Database connection works
- [ ] Authentication works
- [ ] All endpoints functional
- [ ] Logging working
- [ ] Error handling works
- [ ] Performance acceptable

---

## 📦 Deliverables

1. ✅ Production configuration
2. ✅ Logging setup
3. ✅ Enhanced API documentation
4. ✅ Docker configuration
5. ✅ Deployment platform setup
6. ✅ Database migration strategy
7. ✅ Security hardening
8. ✅ Monitoring setup
9. ✅ Deployment documentation
10. ✅ Final verification complete

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Database connection fails | Check connection string and credentials |
| Environment variables not loading | Verify .env file or platform variables |
| CORS errors | Update ALLOWED_ORIGINS with correct domain |
| Migration fails | Test migrations on staging first |
| Performance issues | Check database indexes, connection pooling |
| Logs not appearing | Verify log level and handlers |

---

## 📚 Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Railway Deployment](https://docs.railway.app/)
- [Render Deployment](https://render.com/docs)
- [AWS EC2 Setup](https://aws.amazon.com/ec2/)

---

## 🎉 Project Completion

Congratulations! You have successfully completed the Expense Management API project. The application is now:

- ✅ Fully functional with all features
- ✅ Tested with comprehensive test suite
- ✅ Documented with OpenAPI/Swagger
- ✅ Deployed to production
- ✅ Monitored and logged
- ✅ Secure and optimized

**Next Steps:**
- Monitor application performance
- Gather user feedback
- Plan feature enhancements
- Scale infrastructure as needed

