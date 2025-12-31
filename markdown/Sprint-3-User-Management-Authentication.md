# Sprint 3: User Management & Authentication

## 📋 Sprint Overview

**Duration:** 4-5 days
**Objective:** Implement complete user management system with registration, authentication, JWT tokens, and user profile management.

**Success Criteria:**
- ✅ User registration endpoint working
- ✅ User login endpoint with JWT tokens
- ✅ Token refresh endpoint implemented
- ✅ User profile CRUD operations
- ✅ Password update functionality
- ✅ Account deletion
- ✅ Default categories created for new users
- ✅ All endpoints tested and documented

---

## 🎯 Sprint Goals

1. Implement user registration with validation
2. Create login endpoint with JWT token generation
3. Implement token refresh mechanism
4. Build user profile management endpoints
5. Add password update functionality
6. Implement account deletion
7. Auto-create default categories for new users

---

## 📝 Detailed Tasks

### Task 1: Pydantic Schemas for Users

**Estimated Time:** 1.5 hours

**Steps:**
1. Create `app/schemas/__init__.py`:
   ```python
   from app.schemas.user import (
       UserBase,
       UserCreate,
       UserUpdate,
       UserResponse,
       UserLogin,
       Token,
       TokenRefresh
   )

   __all__ = [
       "UserBase",
       "UserCreate",
       "UserUpdate",
       "UserResponse",
       "UserLogin",
       "Token",
       "TokenRefresh"
   ]
   ```

2. Create `app/schemas/user.py`:
   ```python
   from pydantic import BaseModel, EmailStr, Field, ConfigDict
   from datetime import datetime
   from typing import Optional
   from uuid import UUID

   class UserBase(BaseModel):
       email: EmailStr
       username: str = Field(..., min_length=3, max_length=100, pattern="^[a-zA-Z0-9_]+$")
       full_name: Optional[str] = Field(None, max_length=255)

   class UserCreate(UserBase):
       password: str = Field(..., min_length=8, max_length=100)

   class UserUpdate(BaseModel):
       full_name: Optional[str] = Field(None, max_length=255)
       password: Optional[str] = Field(None, min_length=8, max_length=100)

   class UserResponse(UserBase):
       id: UUID
       is_active: bool
       is_verified: bool
       created_at: datetime
       updated_at: datetime

       model_config = ConfigDict(from_attributes=True)

   class UserLogin(BaseModel):
       email: EmailStr
       password: str

   class Token(BaseModel):
       access_token: str
       refresh_token: str
       token_type: str = "bearer"

   class TokenRefresh(BaseModel):
       refresh_token: str

   class PasswordUpdate(BaseModel):
       current_password: str
       new_password: str = Field(..., min_length=8, max_length=100)
   ```

**Acceptance Criteria:**
- All user schemas created
- Validation rules defined
- Schemas can be imported and used

---

### Task 2: User CRUD Operations

**Estimated Time:** 2.5 hours

**Steps:**
1. Create `app/crud/__init__.py`:
   ```python
   from app.crud.user import crud_user
   from app.crud.base import CRUDBase

   __all__ = ["crud_user", "CRUDBase"]
   ```

2. Create `app/crud/base.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select, func
   from typing import TypeVar, Generic, Type, Optional, List
   from uuid import UUID

   T = TypeVar("T")

   class CRUDBase(Generic[T]):
       def __init__(self, model: Type[T]):
           self.model = model

       async def create(self, db: AsyncSession, obj_in: dict) -> T:
           db_obj = self.model(**obj_in)
           db.add(db_obj)
           await db.commit()
           await db.refresh(db_obj)
           return db_obj

       async def get(self, db: AsyncSession, id: UUID) -> Optional[T]:
           query = select(self.model).where(self.model.id == id)
           result = await db.execute(query)
           return result.scalar_one_or_none()

       async def get_by_email(self, db: AsyncSession, email: str) -> Optional[T]:
           query = select(self.model).where(self.model.email == email)
           result = await db.execute(query)
           return result.scalar_one_or_none()

       async def get_by_username(self, db: AsyncSession, username: str) -> Optional[T]:
           query = select(self.model).where(self.model.username == username)
           result = await db.execute(query)
           return result.scalar_one_or_none()

       async def update(self, db: AsyncSession, id: UUID, obj_in: dict) -> Optional[T]:
           db_obj = await self.get(db, id)
           if not db_obj:
               return None

           for field, value in obj_in.items():
               if value is not None:
                   setattr(db_obj, field, value)

           await db.commit()
           await db.refresh(db_obj)
           return db_obj

       async def delete(self, db: AsyncSession, id: UUID) -> bool:
           db_obj = await self.get(db, id)
           if not db_obj:
               return False

           await db.delete(db_obj)
           await db.commit()
           return True
   ```

3. Create `app/crud/user.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select
   from typing import Optional
   from uuid import UUID
   from app.database.models import User
   from app.crud.base import CRUDBase

   class CRUDUser(CRUDBase[User]):
       async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
           query = select(User).where(User.email == email)
           result = await db.execute(query)
           return result.scalar_one_or_none()

       async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
           query = select(User).where(User.username == username)
           result = await db.execute(query)
           return result.scalar_one_or_none()

       async def create_user(
           self,
           db: AsyncSession,
           user_in: dict,
           hashed_password: str
       ) -> User:
           """Create a new user with hashed password"""
           user_data = {
               **user_in,
               "hashed_password": hashed_password
           }
           return await self.create(db, user_data)

   crud_user = CRUDUser(User)
   ```

**Acceptance Criteria:**
- Base CRUD class implemented
- User-specific CRUD operations work
- Email and username lookup functions work

---

### Task 3: Authentication Service

**Estimated Time:** 2 hours

**Steps:**
1. Create `app/services/__init__.py`:
   ```python
   from app.services.auth_service import AuthService

   __all__ = ["AuthService"]
   ```

2. Create `app/services/auth_service.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.crud.user import crud_user
   from app.core.security import (
       verify_password,
       get_password_hash,
       create_access_token,
       create_refresh_token,
       verify_token
   )
   from app.core.exceptions import (
       UnauthorizedError,
       ConflictError,
       NotFoundError
   )
   from app.core.constants import DEFAULT_CATEGORIES
   from app.database.models import Category
   from app.schemas.user import UserCreate, UserLogin, Token
   from uuid import UUID

   class AuthService:
       @staticmethod
       async def register_user(
           db: AsyncSession,
           user_data: UserCreate
       ) -> Token:
           """Register a new user and return tokens"""
           # Check if email exists
           existing_user = await crud_user.get_by_email(db, user_data.email)
           if existing_user:
               raise ConflictError("Email already registered")

           # Check if username exists
           existing_username = await crud_user.get_by_username(db, user_data.username)
           if existing_username:
               raise ConflictError("Username already taken")

           # Hash password
           hashed_password = get_password_hash(user_data.password)

           # Create user
           user_dict = user_data.model_dump(exclude={"password"})
           user = await crud_user.create_user(
               db,
               user_dict,
               hashed_password
           )

           # Create default categories
           await AuthService._create_default_categories(db, user.id)

           # Generate tokens
           token_data = {"sub": str(user.id), "email": user.email}
           access_token = create_access_token(token_data)
           refresh_token = create_refresh_token(token_data)

           return Token(
               access_token=access_token,
               refresh_token=refresh_token
           )

       @staticmethod
       async def login_user(
           db: AsyncSession,
           login_data: UserLogin
       ) -> Token:
           """Authenticate user and return tokens"""
           user = await crud_user.get_by_email(db, login_data.email)

           if not user:
               raise UnauthorizedError("Invalid email or password")

           if not verify_password(login_data.password, user.hashed_password):
               raise UnauthorizedError("Invalid email or password")

           if not user.is_active:
               raise UnauthorizedError("User account is inactive")

           # Generate tokens
           token_data = {"sub": str(user.id), "email": user.email}
           access_token = create_access_token(token_data)
           refresh_token = create_refresh_token(token_data)

           return Token(
               access_token=access_token,
               refresh_token=refresh_token
           )

       @staticmethod
       async def refresh_access_token(refresh_token: str) -> Token:
           """Generate new access token from refresh token"""
           payload = verify_token(refresh_token, "refresh")

           if payload is None:
               raise UnauthorizedError("Invalid or expired refresh token")

           user_id = payload.get("sub")
           email = payload.get("email")

           if not user_id:
               raise UnauthorizedError("Invalid token payload")

           # Generate new tokens
           token_data = {"sub": user_id, "email": email}
           new_access_token = create_access_token(token_data)
           new_refresh_token = create_refresh_token(token_data)

           return Token(
               access_token=new_access_token,
               refresh_token=new_refresh_token
           )

       @staticmethod
       async def _create_default_categories(
           db: AsyncSession,
           user_id: UUID
       ):
           """Create default categories for a new user"""
           for category_data in DEFAULT_CATEGORIES:
               category = Category(
                   user_id=user_id,
                   **category_data
               )
               db.add(category)
           await db.commit()

   auth_service = AuthService()
   ```

**Acceptance Criteria:**
- Registration service works
- Login service works
- Token refresh works
- Default categories created for new users

---

### Task 4: Authentication Endpoints

**Estimated Time:** 2.5 hours

**Steps:**
1. Create `app/api/__init__.py`:
   ```python
   # Empty file
   ```

2. Create `app/api/v1/__init__.py`:
   ```python
   # Empty file
   ```

3. Create `app/api/v1/endpoints/__init__.py`:
   ```python
   # Empty file
   ```

4. Create `app/api/v1/endpoints/auth.py`:
   ```python
   from fastapi import APIRouter, Depends, status
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.database.connection import get_db
   from app.schemas.user import UserCreate, UserLogin, Token, TokenRefresh
   from app.services.auth_service import auth_service

   router = APIRouter(prefix="/auth", tags=["Authentication"])

   @router.post(
       "/register",
       response_model=Token,
       status_code=status.HTTP_201_CREATED,
       summary="Register a new user"
   )
   async def register(
       user_data: UserCreate,
       db: AsyncSession = Depends(get_db)
   ):
       """Register a new user account"""
       return await auth_service.register_user(db, user_data)

   @router.post(
       "/login",
       response_model=Token,
       summary="Login user"
   )
   async def login(
       login_data: UserLogin,
       db: AsyncSession = Depends(get_db)
   ):
       """Authenticate user and receive access tokens"""
       return await auth_service.login_user(db, login_data)

   @router.post(
       "/refresh",
       response_model=Token,
       summary="Refresh access token"
   )
   async def refresh_token(token_data: TokenRefresh):
       """Get new access token using refresh token"""
       return await auth_service.refresh_access_token(token_data.refresh_token)
   ```

5. Create `app/api/v1/router.py`:
   ```python
   from fastapi import APIRouter
   from app.api.v1.endpoints import auth

   api_router = APIRouter()

   api_router.include_router(auth.router, prefix="/v1")

   # Future routers will be added here
   # api_router.include_router(expenses.router, prefix="/v1")
   # api_router.include_router(categories.router, prefix="/v1")
   # api_router.include_router(users.router, prefix="/v1")
   ```

6. Update `app/main.py`:
   ```python
   from app.api.v1.router import api_router

   app.include_router(api_router, prefix="/api")
   ```

**Acceptance Criteria:**
- Registration endpoint works
- Login endpoint works
- Refresh token endpoint works
- Endpoints return correct status codes
- OpenAPI documentation generated

---

### Task 5: User Profile Endpoints

**Estimated Time:** 2 hours

**Steps:**
1. Create `app/api/v1/endpoints/users.py`:
   ```python
   from fastapi import APIRouter, Depends, status
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.database.connection import get_db
   from app.dependencies import get_current_user
   from app.database.models import User
   from app.schemas.user import UserResponse, UserUpdate, PasswordUpdate
   from app.crud.user import crud_user
   from app.core.security import verify_password, get_password_hash
   from app.core.exceptions import UnauthorizedError, BadRequestError

   router = APIRouter(prefix="/users", tags=["Users"])

   @router.get(
       "/me",
       response_model=UserResponse,
       summary="Get current user profile"
   )
   async def get_current_user_profile(
       current_user: User = Depends(get_current_user)
   ):
       """Get the authenticated user's profile"""
       return current_user

   @router.put(
       "/me",
       response_model=UserResponse,
       summary="Update current user profile"
   )
   async def update_current_user_profile(
       user_update: UserUpdate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Update the authenticated user's profile"""
       update_data = user_update.model_dump(exclude_unset=True)

       # Remove password from update_data (handled separately)
       password = update_data.pop("password", None)

       if update_data:
           updated_user = await crud_user.update(db, current_user.id, update_data)
           if not updated_user:
               raise BadRequestError("Failed to update user")
           current_user = updated_user

       if password:
           hashed_password = get_password_hash(password)
           await crud_user.update(db, current_user.id, {"hashed_password": hashed_password})
           await db.refresh(current_user)

       return current_user

   @router.put(
       "/me/password",
       status_code=status.HTTP_204_NO_CONTENT,
       summary="Update user password"
   )
   async def update_password(
       password_data: PasswordUpdate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Update user password with current password verification"""
       if not verify_password(password_data.current_password, current_user.hashed_password):
           raise UnauthorizedError("Current password is incorrect")

       hashed_password = get_password_hash(password_data.new_password)
       await crud_user.update(db, current_user.id, {"hashed_password": hashed_password})

       return None

   @router.delete(
       "/me",
       status_code=status.HTTP_204_NO_CONTENT,
       summary="Delete current user account"
   )
   async def delete_current_user(
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Delete the authenticated user's account"""
       await crud_user.delete(db, current_user.id)
       return None
   ```

2. Update `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import auth, users

   api_router.include_router(users.router, prefix="/v1")
   ```

**Acceptance Criteria:**
- Get profile endpoint works
- Update profile endpoint works
- Password update endpoint works
- Account deletion works
- All endpoints require authentication

---

### Task 6: Testing Authentication Flow

**Estimated Time:** 1.5 hours

**Steps:**
1. Test registration:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "username": "testuser",
       "password": "testpass123",
       "full_name": "Test User"
     }'
   ```

2. Test login:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "testpass123"
     }'
   ```

3. Test protected endpoint:
   ```bash
   curl -X GET http://localhost:8000/api/v1/users/me \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

4. Test token refresh:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{
       "refresh_token": "YOUR_REFRESH_TOKEN"
     }'
   ```

**Acceptance Criteria:**
- All endpoints tested manually
- Registration creates user and default categories
- Login returns valid tokens
- Protected endpoints require authentication
- Token refresh works

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] User registration works
- [ ] Duplicate email/username rejected
- [ ] Login with correct credentials works
- [ ] Login with wrong credentials fails
- [ ] Access token works for protected endpoints
- [ ] Refresh token generates new access token
- [ ] Get user profile works
- [ ] Update user profile works
- [ ] Password update works with correct current password
- [ ] Password update fails with wrong current password
- [ ] Account deletion works
- [ ] Default categories created for new users
- [ ] Inactive users cannot login

### API Testing Scenarios

1. **Registration Flow:**
   - Register new user → Get tokens
   - Try duplicate email → 409 Conflict
   - Try duplicate username → 409 Conflict
   - Invalid email format → 422 Validation Error

2. **Login Flow:**
   - Login with correct credentials → Get tokens
   - Login with wrong password → 401 Unauthorized
   - Login with non-existent email → 401 Unauthorized

3. **Token Flow:**
   - Use access token → Access protected endpoint
   - Use expired token → 401 Unauthorized
   - Use refresh token → Get new tokens
   - Use invalid refresh token → 401 Unauthorized

4. **Profile Management:**
   - Get profile without token → 401 Unauthorized
   - Get profile with token → 200 OK
   - Update profile → 200 OK
   - Update password → 204 No Content
   - Delete account → 204 No Content

---

## 📦 Deliverables

1. ✅ User Pydantic schemas
2. ✅ User CRUD operations
3. ✅ Authentication service
4. ✅ Registration endpoint
5. ✅ Login endpoint
6. ✅ Token refresh endpoint
7. ✅ User profile endpoints
8. ✅ Password update endpoint
9. ✅ Account deletion endpoint
10. ✅ Default categories creation

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Email validation fails | Ensure using EmailStr from pydantic |
| Password hash mismatch | Verify using same CryptContext |
| Token not working | Check SECRET_KEY matches |
| Default categories not created | Verify transaction commits |
| Duplicate email error | Check unique constraint in database |

---

## 🔄 Next Sprint Preview

**Sprint 4: Category Management**
- Category CRUD operations
- Category endpoints
- Category validation
- Category ownership checks

---

## 📚 Resources

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [JWT Authentication](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Pydantic Email Validation](https://docs.pydantic.dev/latest/concepts/validators/)

