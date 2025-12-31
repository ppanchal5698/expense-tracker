# Sprint 2: Core Configuration & Security

## 📋 Sprint Overview

**Duration:** 2-3 days
**Objective:** Implement core configuration management, security utilities (JWT, password hashing), exception handling, and middleware.

**Success Criteria:**
- ✅ Complete settings management with validation
- ✅ JWT token creation and verification working
- ✅ Password hashing and verification implemented
- ✅ Custom exception classes defined
- ✅ Global exception handler middleware configured
- ✅ CORS middleware configured
- ✅ Security utilities tested

---

## 🎯 Sprint Goals

1. Complete settings configuration with all required variables
2. Implement JWT token generation and verification
3. Implement password hashing with bcrypt
4. Create custom exception classes
5. Set up global error handling middleware
6. Configure CORS for API access

---

## 📝 Detailed Tasks

### Task 1: Complete Settings Configuration

**Estimated Time:** 1.5 hours

**Steps:**
1. Update `app/core/__init__.py`:
   ```python
   from app.core.config import settings
   from app.core.security import verify_password, get_password_hash, create_access_token, verify_token

   __all__ = ["settings", "verify_password", "get_password_hash", "create_access_token", "verify_token"]
   ```

2. Complete `app/core/config.py`:
   ```python
   from pydantic_settings import BaseSettings
   from typing import List
   from functools import lru_cache

   class Settings(BaseSettings):
       # App Configuration
       APP_NAME: str = "Expense Management API"
       APP_VERSION: str = "1.0.0"
       DEBUG: bool = False
       ENV: str = "development"

       # Database Configuration
       DATABASE_URL: str
       DATABASE_POOL_MIN: int = 5
       DATABASE_POOL_MAX: int = 20
       DATABASE_TIMEOUT: int = 30

       # Security Configuration
       SECRET_KEY: str
       ALGORITHM: str = "HS256"
       ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
       REFRESH_TOKEN_EXPIRE_DAYS: int = 7

       # CORS Configuration
       ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

       # API Configuration
       API_TITLE: str = "Expense Management API"
       API_VERSION: str = "1.0.0"
       API_DESCRIPTION: str = "Track and analyze personal expenses"

       # Logging Configuration
       LOG_LEVEL: str = "INFO"

       class Config:
           env_file = ".env"
           case_sensitive = True
           extra = "ignore"

   @lru_cache()
   def get_settings() -> Settings:
       """Cached settings instance"""
       return Settings()

   settings = get_settings()
   ```

3. Create `app/core/constants.py`:
   ```python
   from enum import Enum

   class PaymentMethod(str, Enum):
       CASH = "cash"
       CARD = "card"
       TRANSFER = "transfer"
       DIGITAL_WALLET = "digital_wallet"
       OTHER = "other"

   class BudgetPeriod(str, Enum):
       DAILY = "daily"
       WEEKLY = "weekly"
       MONTHLY = "monthly"
       YEARLY = "yearly"

   # Default expense categories
   DEFAULT_CATEGORIES = [
       {"name": "Food", "color": "#ef4444", "icon": "🍔", "is_default": True},
       {"name": "Transport", "color": "#3b82f6", "icon": "🚗", "is_default": True},
       {"name": "Shopping", "color": "#10b981", "icon": "🛍️", "is_default": True},
       {"name": "Bills", "color": "#f59e0b", "icon": "💳", "is_default": True},
       {"name": "Entertainment", "color": "#8b5cf6", "icon": "🎬", "is_default": True},
       {"name": "Health", "color": "#ec4899", "icon": "🏥", "is_default": True},
   ]
   ```

**Acceptance Criteria:**
- Settings class complete with all required fields
- Settings loaded from `.env` file
- Constants defined for enums and defaults
- Settings validation works

---

### Task 2: Security Utilities - Password Hashing

**Estimated Time:** 1 hour

**Steps:**
1. Create `app/core/security.py`:
   ```python
   from datetime import datetime, timedelta, timezone
   from typing import Any, Optional, Dict
   from jose import JWTError, jwt
   from passlib.context import CryptContext
   from app.core.config import settings

   # Password hashing context
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

   def verify_password(plain_password: str, hashed_password: str) -> bool:
       """Verify a plain password against a hashed password"""
       return pwd_context.verify(plain_password, hashed_password)

   def get_password_hash(password: str) -> str:
       """Hash a password using bcrypt"""
       return pwd_context.hash(password)
   ```

2. Test password hashing:
   ```python
   # Test script: scripts/test_security.py
   from app.core.security import get_password_hash, verify_password

   password = "test_password_123"
   hashed = get_password_hash(password)
   print(f"Hashed: {hashed}")
   print(f"Verification: {verify_password(password, hashed)}")
   print(f"Wrong password: {verify_password('wrong', hashed)}")
   ```

**Acceptance Criteria:**
- Password hashing works correctly
- Password verification works
- Bcrypt algorithm used

---

### Task 3: JWT Token Utilities

**Estimated Time:** 2 hours

**Steps:**
1. Add JWT functions to `app/core/security.py`:
   ```python
   def create_access_token(
       data: Dict[str, Any],
       expires_delta: Optional[timedelta] = None
   ) -> str:
       """Create a JWT access token"""
       to_encode = data.copy()

       if expires_delta:
           expire = datetime.now(timezone.utc) + expires_delta
       else:
           expire = datetime.now(timezone.utc) + timedelta(
               minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
           )

       to_encode.update({"exp": expire, "type": "access"})
       encoded_jwt = jwt.encode(
           to_encode,
           settings.SECRET_KEY,
           algorithm=settings.ALGORITHM
       )
       return encoded_jwt

   def create_refresh_token(data: Dict[str, Any]) -> str:
       """Create a JWT refresh token"""
       to_encode = data.copy()
       expire = datetime.now(timezone.utc) + timedelta(
           days=settings.REFRESH_TOKEN_EXPIRE_DAYS
       )
       to_encode.update({"exp": expire, "type": "refresh"})
       encoded_jwt = jwt.encode(
           to_encode,
           settings.SECRET_KEY,
           algorithm=settings.ALGORITHM
       )
       return encoded_jwt

   def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
       """Verify a JWT token and return payload if valid"""
       try:
           payload = jwt.decode(
               token,
               settings.SECRET_KEY,
               algorithms=[settings.ALGORITHM]
           )

           # Verify token type
           if payload.get("type") != token_type:
               return None

           return payload
       except JWTError:
           return None

   def decode_token(token: str) -> Optional[Dict[str, Any]]:
       """Decode token without verification (for debugging)"""
       try:
           return jwt.decode(
               token,
               settings.SECRET_KEY,
               algorithms=[settings.ALGORITHM],
               options={"verify_signature": False}
           )
       except JWTError:
           return None
   ```

2. Test JWT tokens:
   ```python
   # Add to test script
   from app.core.security import create_access_token, create_refresh_token, verify_token
   from datetime import timedelta

   data = {"sub": "user@example.com", "user_id": "123"}
   access_token = create_access_token(data)
   refresh_token = create_refresh_token(data)

   print(f"Access token: {access_token[:50]}...")
   print(f"Refresh token: {refresh_token[:50]}...")

   # Verify tokens
   payload = verify_token(access_token, "access")
   print(f"Token payload: {payload}")
   ```

**Acceptance Criteria:**
- Access tokens created with correct expiration
- Refresh tokens created with longer expiration
- Token verification works correctly
- Invalid tokens return None

---

### Task 4: Custom Exception Classes

**Estimated Time:** 1.5 hours

**Steps:**
1. Create `app/core/exceptions.py`:
   ```python
   from fastapi import HTTPException, status

   class ExpenseAPIException(HTTPException):
       """Base exception for Expense API"""
       def __init__(
           self,
           status_code: int,
           detail: str,
           headers: dict = None
       ):
           super().__init__(status_code=status_code, detail=detail, headers=headers)

   class NotFoundError(ExpenseAPIException):
       """Resource not found"""
       def __init__(self, resource: str, identifier: str = None):
           detail = f"{resource} not found"
           if identifier:
               detail += f": {identifier}"
           super().__init__(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=detail
           )

   class UnauthorizedError(ExpenseAPIException):
       """Authentication required"""
       def __init__(self, detail: str = "Not authenticated"):
           super().__init__(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail=detail,
               headers={"WWW-Authenticate": "Bearer"}
           )

   class ForbiddenError(ExpenseAPIException):
       """Insufficient permissions"""
       def __init__(self, detail: str = "Insufficient permissions"):
           super().__init__(
               status_code=status.HTTP_403_FORBIDDEN,
               detail=detail
           )

   class ValidationError(ExpenseAPIException):
       """Validation error"""
       def __init__(self, detail: str):
           super().__init__(
               status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
               detail=detail
           )

   class ConflictError(ExpenseAPIException):
       """Resource conflict (e.g., duplicate)"""
       def __init__(self, detail: str):
           super().__init__(
               status_code=status.HTTP_409_CONFLICT,
               detail=detail
           )

   class BadRequestError(ExpenseAPIException):
       """Bad request"""
       def __init__(self, detail: str):
           super().__init__(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail=detail
           )
   ```

2. Update `app/core/__init__.py`:
   ```python
   from app.core.exceptions import (
       ExpenseAPIException,
       NotFoundError,
       UnauthorizedError,
       ForbiddenError,
       ValidationError,
       ConflictError,
       BadRequestError
   )
   ```

**Acceptance Criteria:**
- All custom exception classes created
- Exceptions inherit from HTTPException
- Appropriate status codes used
- Exceptions can be imported and used

---

### Task 5: Global Exception Handler

**Estimated Time:** 2 hours

**Steps:**
1. Create `app/middleware/__init__.py`:
   ```python
   from app.middleware.error_handler import setup_exception_handlers

   __all__ = ["setup_exception_handlers"]
   ```

2. Create `app/middleware/error_handler.py`:
   ```python
   from fastapi import Request, status
   from fastapi.responses import JSONResponse
   from fastapi.exceptions import RequestValidationError
   from sqlalchemy.exc import SQLAlchemyError
   from pydantic import ValidationError
   from app.core.exceptions import ExpenseAPIException
   from app.core.config import settings
   import logging

   logger = logging.getLogger(__name__)

   async def validation_exception_handler(
       request: Request,
       exc: RequestValidationError
   ) -> JSONResponse:
       """Handle Pydantic validation errors"""
       errors = []
       for error in exc.errors():
           field = ".".join(str(loc) for loc in error["loc"])
           errors.append({
               "field": field,
               "message": error["msg"],
               "type": error["type"]
           })

       return JSONResponse(
           status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
           content={
               "detail": "Validation error",
               "errors": errors
           }
       )

   async def expense_api_exception_handler(
       request: Request,
       exc: ExpenseAPIException
   ) -> JSONResponse:
       """Handle custom API exceptions"""
       return JSONResponse(
           status_code=exc.status_code,
           content={"detail": exc.detail},
           headers=exc.headers
       )

   async def sqlalchemy_exception_handler(
       request: Request,
       exc: SQLAlchemyError
   ) -> JSONResponse:
       """Handle SQLAlchemy database errors"""
       logger.error(f"Database error: {exc}", exc_info=True)

       if settings.DEBUG:
           return JSONResponse(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               content={
                   "detail": "Database error",
                   "error": str(exc)
               }
           )

       return JSONResponse(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           content={"detail": "Internal server error"}
       )

   async def general_exception_handler(
       request: Request,
       exc: Exception
   ) -> JSONResponse:
       """Handle unexpected exceptions"""
       logger.error(f"Unexpected error: {exc}", exc_info=True)

       if settings.DEBUG:
           return JSONResponse(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               content={
                   "detail": "Internal server error",
                   "error": str(exc)
               }
           )

       return JSONResponse(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           content={"detail": "Internal server error"}
       )

   def setup_exception_handlers(app):
       """Register all exception handlers"""
       app.add_exception_handler(
           RequestValidationError,
           validation_exception_handler
       )
       app.add_exception_handler(
           ExpenseAPIException,
           expense_api_exception_handler
       )
       app.add_exception_handler(
           SQLAlchemyError,
           sqlalchemy_exception_handler
       )
       app.add_exception_handler(
           Exception,
           general_exception_handler
       )
   ```

3. Update `app/main.py` to use exception handlers:
   ```python
   from app.middleware.error_handler import setup_exception_handlers

   # After creating app
   setup_exception_handlers(app)
   ```

**Acceptance Criteria:**
- Exception handlers registered
- Validation errors return structured responses
- Custom exceptions handled correctly
- Database errors handled gracefully
- Debug mode shows detailed errors

---

### Task 6: CORS Middleware

**Estimated Time:** 30 minutes

**Steps:**
1. Update `app/main.py`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   from app.core.config import settings

   # Add CORS middleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.ALLOWED_ORIGINS,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. Test CORS:
   ```bash
   # Using curl or browser
   curl -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS \
        http://localhost:8000/
   ```

**Acceptance Criteria:**
- CORS middleware configured
- Allowed origins work correctly
- Preflight requests handled

---

### Task 7: Authentication Dependency

**Estimated Time:** 1.5 hours

**Steps:**
1. Create `app/dependencies.py`:
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.database.connection import get_db
   from app.database.models import User
   from app.core.security import verify_token
   from app.core.exceptions import UnauthorizedError
   from sqlalchemy import select

   security = HTTPBearer()

   async def get_current_user(
       credentials: HTTPAuthorizationCredentials = Depends(security),
       db: AsyncSession = Depends(get_db)
   ) -> User:
       """Dependency to get current authenticated user"""
       token = credentials.credentials
       payload = verify_token(token, "access")

       if payload is None:
           raise UnauthorizedError("Invalid or expired token")

       user_id = payload.get("sub")
       if user_id is None:
           raise UnauthorizedError("Token missing user identifier")

       # Fetch user from database
       result = await db.execute(
           select(User).where(User.id == user_id)
       )
       user = result.scalar_one_or_none()

       if user is None:
           raise UnauthorizedError("User not found")

       if not user.is_active:
           raise UnauthorizedError("User account is inactive")

       return user

   async def get_optional_user(
       credentials: HTTPAuthorizationCredentials = Depends(security),
       db: AsyncSession = Depends(get_db)
   ) -> User | None:
       """Optional authentication - returns None if not authenticated"""
       try:
           return await get_current_user(credentials, db)
       except (UnauthorizedError, HTTPException):
           return None
   ```

2. Test dependency:
   ```python
   # Add test endpoint to main.py
   @app.get("/test-auth")
   async def test_auth(current_user: User = Depends(get_current_user)):
       return {"user_id": str(current_user.id), "email": current_user.email}
   ```

**Acceptance Criteria:**
- Authentication dependency works
- Invalid tokens raise UnauthorizedError
- Active user check works
- Optional authentication works

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] Settings load from .env correctly
- [ ] Password hashing works
- [ ] Password verification works
- [ ] JWT tokens created successfully
- [ ] JWT tokens verified correctly
- [ ] Custom exceptions raise with correct status codes
- [ ] Exception handlers catch and format errors
- [ ] CORS headers present in responses
- [ ] Authentication dependency extracts user from token
- [ ] Inactive users cannot authenticate

### Verification Commands

```bash
# Test password hashing
python scripts/test_security.py

# Test JWT tokens
python -c "from app.core.security import create_access_token; print(create_access_token({'sub': 'test'}))"

# Test exception handling
curl http://localhost:8000/test-auth
# Should return 401 Unauthorized

# Test CORS
curl -H "Origin: http://localhost:3000" -X OPTIONS http://localhost:8000/
```

---

## 📦 Deliverables

1. ✅ Complete settings configuration
2. ✅ Password hashing utilities
3. ✅ JWT token creation and verification
4. ✅ Custom exception classes
5. ✅ Global exception handlers
6. ✅ CORS middleware configured
7. ✅ Authentication dependency

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| SECRET_KEY not found | Ensure .env file has SECRET_KEY set |
| JWT decode errors | Check SECRET_KEY matches between encode/decode |
| CORS not working | Verify ALLOWED_ORIGINS includes frontend URL |
| Password hash mismatch | Ensure using same CryptContext instance |
| Exception handler not triggered | Check handler registration order in main.py |

---

## 🔄 Next Sprint Preview

**Sprint 3: User Management & Authentication**
- User CRUD operations
- Registration endpoint
- Login endpoint
- User profile endpoints
- Token refresh endpoint

---

## 📚 Resources

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT with Python-jose](https://python-jose.readthedocs.io/)
- [Passlib Documentation](https://passlib.readthedocs.io/)
- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)

