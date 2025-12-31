# Development Guidelines

## 📋 Overview

This document outlines development best practices, Git workflow, code standards, and collaboration guidelines for the Expense Management API project.

---

## 🌿 Git Workflow

### Branching Strategy

**Main Branches:**
- `main` - Production-ready code
- `develop` - Integration branch for features

**Supporting Branches:**
- `feature/sprint-X-task-name` - Feature development
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes

### Branch Naming Convention

```
feature/sprint-3-user-authentication
bugfix/fix-expense-filtering
hotfix/fix-security-vulnerability
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): Add user registration endpoint

Implement POST /api/v1/auth/register with email validation
and password hashing.

Closes #123
```

```
fix(expenses): Fix date filtering bug

Date range filter was excluding boundary dates. Fixed by
using >= and <= instead of > and <.

Fixes #456
```

### Workflow Steps

1. **Create Feature Branch:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/sprint-3-user-auth
   ```

2. **Develop and Commit:**
   ```bash
   # Make changes
   git add .
   git commit -m "feat(auth): Add login endpoint"
   ```

3. **Push and Create PR:**
   ```bash
   git push origin feature/sprint-3-user-auth
   # Create Pull Request on GitHub/GitLab
   ```

4. **Review and Merge:**
   - Code review
   - Tests passing
   - Merge to develop
   - Delete feature branch

5. **Deploy to Production:**
   ```bash
   git checkout main
   git merge develop
   git tag v1.0.0
   git push origin main --tags
   ```

---

## 💻 Code Standards

### Python Style Guide

**Follow PEP 8 with these modifications:**
- Line length: 100 characters
- Use Black for formatting
- Use Ruff for linting

**Format Code:**
```bash
black app/ tests/
```

**Lint Code:**
```bash
ruff check app/ tests/
```

### Code Organization

**File Structure:**
```python
# 1. Imports (standard library, third-party, local)
import os
from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import select

from app.core.config import settings
from app.database.models import User

# 2. Constants
DEFAULT_LIMIT = 10

# 3. Classes and Functions
class UserService:
    """Service for user operations."""

    @staticmethod
    async def create_user(...):
        """Create a new user."""
        pass
```

### Naming Conventions

- **Variables:** `snake_case`
- **Functions:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore`

**Examples:**
```python
# Variables
user_id = "123"
expense_amount = 25.50

# Functions
async def get_user_by_id(user_id: str):
    pass

# Classes
class ExpenseService:
    pass

# Constants
MAX_EXPENSES_PER_PAGE = 100
DEFAULT_CATEGORY_COLOR = "#3182ce"
```

### Type Hints

**Always use type hints:**
```python
from typing import Optional, List
from uuid import UUID

async def get_expense(
    db: AsyncSession,
    expense_id: UUID
) -> Optional[Expense]:
    """Get expense by ID."""
    pass
```

### Docstrings

**Use Google-style docstrings:**
```python
async def create_expense(
    db: AsyncSession,
    user_id: UUID,
    expense_data: ExpenseCreate
) -> Expense:
    """Create a new expense.

    Args:
        db: Database session
        user_id: ID of the user creating the expense
        expense_data: Expense creation data

    Returns:
        Created expense object

    Raises:
        NotFoundError: If category not found
        ValidationError: If data invalid
    """
    pass
```

---

## 🧪 Testing Standards

### Test Organization

**Test File Structure:**
```python
# tests/test_expense_service.py
import pytest
from app.services.expense_service import expense_service

@pytest.mark.asyncio
@pytest.mark.unit
class TestExpenseService:
    """Test suite for ExpenseService."""

    async def test_create_expense_success(self, test_db, test_user):
        """Test successful expense creation."""
        # Arrange
        # Act
        # Assert
        pass
```

### Test Naming

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<scenario>_<expected_result>`

**Examples:**
```python
test_create_expense_success
test_create_expense_invalid_category
test_list_expenses_with_filters
```

### Test Coverage Requirements

- **Services:** > 90%
- **CRUD Operations:** > 85%
- **Endpoints:** > 80%
- **Overall:** > 80%

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_expense_service.py

# With coverage
pytest --cov=app --cov-report=html

# Specific marker
pytest -m unit
pytest -m integration
```

---

## 📝 Documentation Standards

### Code Comments

**When to comment:**
- Complex algorithms
- Business logic explanations
- Workarounds for known issues
- Non-obvious code behavior

**Example:**
```python
# Use connection pooler port for Supabase to avoid
# connection limit issues in production
database_url = database_url.replace("5432", "6543")
```

### API Documentation

**Endpoint Documentation:**
```python
@router.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense",
    description="""
    Create a new expense record with the following:
    - Amount (must be > 0)
    - Date of expense
    - Category (must belong to user)
    - Optional: description, payment method, tags
    """,
    responses={
        201: {"description": "Expense created successfully"},
        404: {"description": "Category not found"},
        422: {"description": "Validation error"}
    }
)
```

### README Updates

**Keep README updated with:**
- Setup instructions
- Environment variables
- Running the application
- Testing instructions
- API documentation links

---

## 🔍 Code Review Checklist

### Functionality
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling appropriate
- [ ] No hardcoded values

### Code Quality
- [ ] Follows style guide
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] No code duplication
- [ ] Functions are focused

### Testing
- [ ] Tests written
- [ ] Tests passing
- [ ] Edge cases tested
- [ ] Error cases tested

### Security
- [ ] Input validation
- [ ] Authentication checks
- [ ] Authorization checks
- [ ] No sensitive data in logs
- [ ] SQL injection prevention

### Performance
- [ ] Database queries optimized
- [ ] No N+1 queries
- [ ] Pagination implemented
- [ ] Indexes used appropriately

---

## 🚀 Deployment Guidelines

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Environment variables set
- [ ] Database migrations tested
- [ ] Security audit passed
- [ ] Performance tested

### Deployment Process

1. **Merge to main:**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

2. **Tag release:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. **Deploy:**
   - Run migrations
   - Deploy application
   - Verify health checks
   - Monitor logs

4. **Post-Deployment:**
   - Smoke tests
   - Monitor error rates
   - Check performance metrics

### Rollback Procedure

1. **Identify issue:**
   - Check error logs
   - Review health endpoints
   - Identify root cause

2. **Rollback:**
   ```bash
   git checkout <previous-tag>
   # Redeploy previous version
   ```

3. **Verify:**
   - Health checks passing
   - No errors in logs
   - Application functional

---

## 🐛 Bug Fix Workflow

### Reporting Bugs

**Bug Report Template:**
```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- Python version
- Database version
- OS

**Logs:**
Relevant error logs
```

### Fixing Bugs

1. **Create bugfix branch:**
   ```bash
   git checkout -b bugfix/fix-expense-filtering
   ```

2. **Fix and test:**
   - Write failing test
   - Fix the bug
   - Test passes
   - Add regression test

3. **Commit:**
   ```bash
   git commit -m "fix(expenses): Fix date filtering bug"
   ```

4. **Merge:**
   - Create PR
   - Code review
   - Merge to develop/main

---

## 📊 Performance Guidelines

### Database Queries

**Best Practices:**
- Use indexes on filtered columns
- Avoid N+1 queries
- Use select_related/joinedload
- Limit result sets
- Use pagination

**Example:**
```python
# Good: Single query with join
query = select(Expense).join(Category).where(
    Expense.user_id == user_id
)

# Bad: N+1 queries
expenses = await get_expenses(user_id)
for expense in expenses:
    category = await get_category(expense.category_id)  # N+1!
```

### API Response Times

**Targets:**
- Simple queries: < 100ms
- Complex queries: < 200ms
- Analytics: < 500ms
- 95th percentile: < 200ms

### Caching Strategy

**Consider caching for:**
- Category lists (rarely change)
- Analytics summaries (can be stale)
- User profiles (update on change)

---

## 🔒 Security Guidelines

### Authentication
- ✅ Strong password requirements
- ✅ JWT token expiration
- ✅ Secure token storage
- ✅ Refresh token rotation

### Authorization
- ✅ User ownership checks
- ✅ Role-based access (if needed)
- ✅ Resource-level permissions

### Input Validation
- ✅ Pydantic schemas
- ✅ Type checking
- ✅ Range validation
- ✅ SQL injection prevention (ORM)

### Data Protection
- ✅ Password hashing (bcrypt)
- ✅ No sensitive data in logs
- ✅ HTTPS in production
- ✅ Secure environment variables

---

## 📚 Learning Resources

### Python
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### FastAPI
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### Git
- [Git Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## ✅ Development Checklist

### Before Starting Work
- [ ] Pull latest changes
- [ ] Create feature branch
- [ ] Review requirements

### During Development
- [ ] Write tests first (TDD if possible)
- [ ] Follow code style
- [ ] Add type hints
- [ ] Write docstrings
- [ ] Commit frequently

### Before Committing
- [ ] Run tests
- [ ] Format code (Black)
- [ ] Lint code (Ruff)
- [ ] Check type hints (MyPy)
- [ ] Review changes

### Before Merging
- [ ] All tests passing
- [ ] Code review done
- [ ] Documentation updated
- [ ] No merge conflicts

---

**Last Updated:** Project Start
**Status:** Active Guidelines ✅

