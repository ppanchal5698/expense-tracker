# Sprint 7: Testing & Quality Assurance

## 📋 Sprint Overview

**Duration:** 5-6 days
**Objective:** Implement comprehensive test suite with unit tests, integration tests, achieve >80% code coverage, and set up code quality tools.

**Success Criteria:**
- ✅ Unit tests for all services
- ✅ Integration tests for all endpoints
- ✅ Test coverage > 80%
- ✅ Code quality tools configured
- ✅ CI/CD pipeline setup (optional)
- ✅ All tests passing

---

## 🎯 Sprint Goals

1. Set up testing infrastructure
2. Write unit tests for all services
3. Write integration tests for all endpoints
4. Achieve >80% code coverage
5. Configure code quality tools
6. Set up automated testing workflow

---

## 📝 Detailed Tasks

### Task 1: Testing Infrastructure Setup

**Estimated Time:** 2 hours

**Steps:**
1. Create `tests/__init__.py` (empty)

2. Create `tests/conftest.py`:
   ```python
   import pytest
   import asyncio
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from httpx import AsyncClient
   from app.main import app
   from app.database.connection import get_db
   from app.database.models import Base
   from app.core.config import settings
   from uuid import uuid4

   # Test database URL (use separate test database)
   TEST_DATABASE_URL = settings.DATABASE_URL.replace(
       "/postgres", "/test_expense_db"
   )

   @pytest.fixture(scope="session")
   def event_loop():
       """Create event loop for async tests"""
       loop = asyncio.get_event_loop_policy().new_event_loop()
       yield loop
       loop.close()

   @pytest.fixture(scope="session")
   async def test_engine():
       """Create test database engine"""
       engine = create_async_engine(
           TEST_DATABASE_URL,
           echo=False,
           pool_pre_ping=True
       )
       yield engine
       await engine.dispose()

   @pytest.fixture(scope="function")
   async def test_db(test_engine):
       """Create test database session and tables"""
       # Create all tables
       async with test_engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)

       # Create session
       async_session = sessionmaker(
           test_engine, class_=AsyncSession, expire_on_commit=False
       )

       async with async_session() as session:
           yield session
           await session.rollback()

       # Drop all tables after test
       async with test_engine.begin() as conn:
           await conn.run_sync(Base.metadata.drop_all)

   @pytest.fixture
   async def client(test_db):
       """Create test client with database override"""
       async def override_get_db():
           yield test_db

       app.dependency_overrides[get_db] = override_get_db

       async with AsyncClient(app=app, base_url="http://test") as ac:
           yield ac

       app.dependency_overrides.clear()

   @pytest.fixture
   async def test_user(test_db):
       """Create a test user"""
       from app.database.models import User
       from app.core.security import get_password_hash

       user = User(
           id=uuid4(),
           email="test@example.com",
           username="testuser",
           full_name="Test User",
           hashed_password=get_password_hash("testpass123"),
           is_active=True
       )
       test_db.add(user)
       await test_db.commit()
       await test_db.refresh(user)
       return user

   @pytest.fixture
   async def auth_headers(client, test_user):
       """Get authentication headers for test user"""
       from app.core.security import create_access_token

       token_data = {"sub": str(test_user.id), "email": test_user.email}
       token = create_access_token(token_data)

       return {"Authorization": f"Bearer {token}"}
   ```

3. Create `pytest.ini`:
   ```ini
   [pytest]
   asyncio_mode = auto
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   addopts =
       -v
       --strict-markers
       --tb=short
       --cov=app
       --cov-report=term-missing
       --cov-report=html
       --cov-fail-under=80
   markers =
       unit: Unit tests
       integration: Integration tests
       slow: Slow running tests
   ```

4. Update `pyproject.toml` with test dependencies:
   ```toml
   [tool.poetry.dev-dependencies]
   pytest = "^7.4.0"
   pytest-asyncio = "^0.21.0"
   pytest-cov = "^4.1.0"
   httpx = "^0.25.0"
   ```

**Acceptance Criteria:**
- Test infrastructure set up
- Fixtures created
- Test database configured
- Pytest configured

---

### Task 2: Unit Tests for Services

**Estimated Time:** 6 hours

**Steps:**
1. Create `tests/test_auth_service.py`:
   ```python
   import pytest
   from app.services.auth_service import auth_service
   from app.schemas.user import UserCreate, UserLogin
   from app.core.exceptions import ConflictError, UnauthorizedError

   @pytest.mark.asyncio
   @pytest.mark.unit
   class TestAuthService:
       async def test_register_user_success(self, test_db, test_user):
           """Test successful user registration"""
           user_data = UserCreate(
               email="newuser@example.com",
               username="newuser",
               password="password123",
               full_name="New User"
           )

           result = await auth_service.register_user(test_db, user_data)

           assert result.access_token is not None
           assert result.refresh_token is not None
           assert result.token_type == "bearer"

       async def test_register_duplicate_email(self, test_db, test_user):
           """Test registration with duplicate email"""
           user_data = UserCreate(
               email=test_user.email,
               username="different",
               password="password123"
           )

           with pytest.raises(ConflictError):
               await auth_service.register_user(test_db, user_data)

       async def test_login_success(self, test_db, test_user):
           """Test successful login"""
           login_data = UserLogin(
               email=test_user.email,
               password="testpass123"
           )

           result = await auth_service.login_user(test_db, login_data)

           assert result.access_token is not None
           assert result.refresh_token is not None

       async def test_login_wrong_password(self, test_db, test_user):
           """Test login with wrong password"""
           login_data = UserLogin(
               email=test_user.email,
               password="wrongpassword"
           )

           with pytest.raises(UnauthorizedError):
               await auth_service.login_user(test_db, login_data)
   ```

2. Create `tests/test_expense_service.py`:
   ```python
   import pytest
   from app.services.expense_service import expense_service
   from app.schemas.expense import ExpenseCreate
   from app.core.exceptions import NotFoundError
   from decimal import Decimal
   from datetime import date

   @pytest.mark.asyncio
   @pytest.mark.unit
   class TestExpenseService:
       async def test_create_expense_success(self, test_db, test_user):
           """Test successful expense creation"""
           # Create category first
           from app.database.models import Category
           category = Category(
               user_id=test_user.id,
               name="Test Category",
               is_default=False
           )
           test_db.add(category)
           await test_db.commit()

           expense_data = ExpenseCreate(
               amount=Decimal("25.50"),
               date=date.today(),
               category_id=category.id,
               description="Test expense"
           )

           expense = await expense_service.create_expense(
               test_db, test_user.id, expense_data
           )

           assert expense.amount == Decimal("25.50")
           assert expense.user_id == test_user.id
           assert expense.category_id == category.id

       async def test_create_expense_invalid_category(self, test_db, test_user):
           """Test expense creation with invalid category"""
           from uuid import uuid4

           expense_data = ExpenseCreate(
               amount=Decimal("25.50"),
               date=date.today(),
               category_id=uuid4(),
               description="Test expense"
           )

           with pytest.raises(NotFoundError):
               await expense_service.create_expense(
                   test_db, test_user.id, expense_data
               )
   ```

3. Create `tests/test_category_service.py`:
   ```python
   import pytest
   from app.services.category_service import category_service
   from app.schemas.category import CategoryCreate
   from app.core.exceptions import ConflictError, BadRequestError

   @pytest.mark.asyncio
   @pytest.mark.unit
   class TestCategoryService:
       async def test_create_category_success(self, test_db, test_user):
           """Test successful category creation"""
           category_data = CategoryCreate(
               name="Test Category",
               color="#10b981",
               description="Test description"
           )

           category = await category_service.create_category(
               test_db, test_user.id, category_data
           )

           assert category.name == "Test Category"
           assert category.user_id == test_user.id

       async def test_create_duplicate_category(self, test_db, test_user):
           """Test creating duplicate category"""
           category_data = CategoryCreate(name="Duplicate")
           await category_service.create_category(
               test_db, test_user.id, category_data
           )

           with pytest.raises(ConflictError):
               await category_service.create_category(
                   test_db, test_user.id, category_data
               )
   ```

4. Create `tests/test_analytics_service.py`:
   ```python
   import pytest
   from app.services.analytics_service import analytics_service
   from datetime import date

   @pytest.mark.asyncio
   @pytest.mark.unit
   class TestAnalyticsService:
       async def test_get_monthly_summary(self, test_db, test_user):
           """Test monthly summary calculation"""
           # Create test expenses first
           # ... (setup code)

           summary = await analytics_service.get_monthly_summary(
               test_db, test_user.id, 2024, 1
           )

           assert summary.year == 2024
           assert summary.month == 1
           assert summary.total_expenses >= 0
   ```

**Acceptance Criteria:**
- Unit tests for all services
- Edge cases covered
- Error scenarios tested
- Tests pass successfully

---

### Task 3: Integration Tests for Endpoints

**Estimated Time:** 8 hours

**Steps:**
1. Create `tests/test_auth_endpoints.py`:
   ```python
   import pytest
   from httpx import AsyncClient

   @pytest.mark.asyncio
   @pytest.mark.integration
   class TestAuthEndpoints:
       async def test_register_endpoint(self, client: AsyncClient):
           """Test user registration endpoint"""
           response = await client.post(
               "/api/v1/auth/register",
               json={
                   "email": "new@example.com",
                   "username": "newuser",
                   "password": "password123",
                   "full_name": "New User"
               }
           )

           assert response.status_code == 201
           data = response.json()
           assert "access_token" in data
           assert "refresh_token" in data

       async def test_login_endpoint(self, client: AsyncClient, test_user):
           """Test user login endpoint"""
           response = await client.post(
               "/api/v1/auth/login",
               json={
                   "email": test_user.email,
                   "password": "testpass123"
               }
           )

           assert response.status_code == 200
           data = response.json()
           assert "access_token" in data

       async def test_login_invalid_credentials(self, client: AsyncClient, test_user):
           """Test login with invalid credentials"""
           response = await client.post(
               "/api/v1/auth/login",
               json={
                   "email": test_user.email,
                   "password": "wrongpassword"
               }
           )

           assert response.status_code == 401
   ```

2. Create `tests/test_expense_endpoints.py`:
   ```python
   import pytest
   from httpx import AsyncClient
   from decimal import Decimal
   from datetime import date

   @pytest.mark.asyncio
   @pytest.mark.integration
   class TestExpenseEndpoints:
       async def test_create_expense(
           self,
           client: AsyncClient,
           auth_headers,
           test_user
       ):
           """Test expense creation endpoint"""
           # Create category first
           category_response = await client.post(
               "/api/v1/categories",
               headers=auth_headers,
               json={
                   "name": "Test Category",
                   "color": "#10b981"
               }
           )
           category_id = category_response.json()["id"]

           response = await client.post(
               "/api/v1/expenses",
               headers=auth_headers,
               json={
                   "amount": "25.50",
                   "date": str(date.today()),
                   "category_id": category_id,
                   "description": "Test expense"
               }
           )

           assert response.status_code == 201
           data = response.json()
           assert data["amount"] == "25.50"

       async def test_list_expenses(
           self,
           client: AsyncClient,
           auth_headers
       ):
           """Test expense listing endpoint"""
           response = await client.get(
               "/api/v1/expenses",
               headers=auth_headers
           )

           assert response.status_code == 200
           data = response.json()
           assert "items" in data
           assert "total" in data

       async def test_list_expenses_with_filters(
           self,
           client: AsyncClient,
           auth_headers
       ):
           """Test expense listing with filters"""
           response = await client.get(
               "/api/v1/expenses",
               headers=auth_headers,
               params={
                   "start_date": "2024-01-01",
                   "end_date": "2024-01-31",
                   "page": 1,
                   "per_page": 10
               }
           )

           assert response.status_code == 200
   ```

3. Create `tests/test_category_endpoints.py`:
   ```python
   import pytest
   from httpx import AsyncClient

   @pytest.mark.asyncio
   @pytest.mark.integration
   class TestCategoryEndpoints:
       async def test_create_category(
           self,
           client: AsyncClient,
           auth_headers
       ):
           """Test category creation endpoint"""
           response = await client.post(
               "/api/v1/categories",
               headers=auth_headers,
               json={
                   "name": "Test Category",
                   "color": "#10b981",
                   "description": "Test"
               }
           )

           assert response.status_code == 201
           data = response.json()
           assert data["name"] == "Test Category"

       async def test_list_categories(
           self,
           client: AsyncClient,
           auth_headers
       ):
           """Test category listing endpoint"""
           response = await client.get(
               "/api/v1/categories",
               headers=auth_headers
           )

           assert response.status_code == 200
   ```

4. Create `tests/test_analytics_endpoints.py`:
   ```python
   import pytest
   from httpx import AsyncClient

   @pytest.mark.asyncio
   @pytest.mark.integration
   class TestAnalyticsEndpoints:
       async def test_get_monthly_summary(
           self,
           client: AsyncClient,
           auth_headers
       ):
           """Test monthly summary endpoint"""
           response = await client.get(
               "/api/v1/analytics/monthly/2024/1",
               headers=auth_headers
           )

           assert response.status_code == 200
           data = response.json()
           assert "total_expenses" in data
           assert "category_breakdown" in data
   ```

**Acceptance Criteria:**
- Integration tests for all endpoints
- Authentication tested
- Error cases tested
- All tests pass

---

### Task 4: Code Quality Tools

**Estimated Time:** 2 hours

**Steps:**
1. Install code quality tools:
   ```bash
   pip install black ruff mypy
   ```

2. Create `.black` or `pyproject.toml` config:
   ```toml
   [tool.black]
   line-length = 100
   target-version = ['py310']
   include = '\.pyi?$'
   ```

3. Create `ruff.toml`:
   ```toml
   line-length = 100
   target-version = "py310"
   ```

4. Create `mypy.ini`:
   ```ini
   [mypy]
   python_version = 3.10
   warn_return_any = True
   warn_unused_configs = True
   disallow_untyped_defs = False
   ```

5. Create `scripts/lint.sh`:
   ```bash
   #!/bin/bash
   echo "Running Black..."
   black app tests

   echo "Running Ruff..."
   ruff check app tests

   echo "Running MyPy..."
   mypy app
   ```

6. Update `pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   # ... existing config

   [tool.coverage.run]
   source = ["app"]
   omit = ["*/tests/*", "*/migrations/*"]

   [tool.coverage.report]
   exclude_lines = [
       "pragma: no cover",
       "def __repr__",
       "raise AssertionError",
       "raise NotImplementedError",
       "if __name__ == .__main__.:",
       "if TYPE_CHECKING:",
   ]
   ```

**Acceptance Criteria:**
- Code quality tools configured
- Linting rules defined
- Formatting consistent
- Type checking configured

---

### Task 5: Test Coverage Analysis

**Estimated Time:** 1.5 hours

**Steps:**
1. Run tests with coverage:
   ```bash
   pytest --cov=app --cov-report=html --cov-report=term
   ```

2. Review coverage report:
   - Identify uncovered code
   - Add tests for missing coverage
   - Aim for >80% coverage

3. Generate coverage report:
   ```bash
   # HTML report in htmlcov/index.html
   # Terminal report in console
   ```

**Acceptance Criteria:**
- Coverage > 80%
- All critical paths tested
- Coverage report generated

---

### Task 6: Performance Testing

**Estimated Time:** 2 hours

**Steps:**
1. Create `tests/test_performance.py`:
   ```python
   import pytest
   import time
   from httpx import AsyncClient

   @pytest.mark.asyncio
   @pytest.mark.slow
   class TestPerformance:
       async def test_expense_listing_performance(
           self,
           client: AsyncClient,
           auth_headers
       ):
           """Test expense listing performance"""
           start = time.time()
           response = await client.get(
               "/api/v1/expenses",
               headers=auth_headers
           )
           elapsed = time.time() - start

           assert response.status_code == 200
           assert elapsed < 1.0  # Should complete in < 1 second

       async def test_analytics_performance(
           self,
           client: AsyncClient,
           auth_headers
       ):
           """Test analytics endpoint performance"""
           start = time.time()
           response = await client.get(
               "/api/v1/analytics/monthly/2024/1",
               headers=auth_headers
           )
           elapsed = time.time() - start

           assert response.status_code == 200
           assert elapsed < 0.5  # Should complete in < 500ms
   ```

**Acceptance Criteria:**
- Performance tests created
- Response times acceptable
- No performance regressions

---

## 🧪 Testing & Verification

### Test Execution

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_service.py

# Run with verbose output
pytest -v
```

### Test Coverage Goals

- Services: > 90%
- CRUD operations: > 85%
- Endpoints: > 80%
- Overall: > 80%

---

## 📦 Deliverables

1. ✅ Test infrastructure setup
2. ✅ Unit tests for all services
3. ✅ Integration tests for all endpoints
4. ✅ Test coverage > 80%
5. ✅ Code quality tools configured
6. ✅ Performance tests
7. ✅ Test documentation

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Async test errors | Use pytest-asyncio with auto mode |
| Database connection fails | Check test database URL |
| Fixtures not working | Ensure proper scope and async |
| Coverage too low | Add tests for edge cases |
| Tests too slow | Use test database, not production |

---

## 🔄 Next Sprint Preview

**Sprint 8: Deployment & Documentation**
- Production configuration
- Deployment setup
- API documentation
- Deployment checklist
- Monitoring setup

---

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)

