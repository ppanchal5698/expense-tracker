# Sprint 4: Category Management

## 📋 Sprint Overview

**Duration:** 3-4 days
**Objective:** Implement complete category management system with CRUD operations, validation, and ownership checks.

**Success Criteria:**
- ✅ Category CRUD operations implemented
- ✅ Category endpoints created
- ✅ Category ownership validation
- ✅ Default categories management
- ✅ Category deletion with expense validation
- ✅ All endpoints tested and documented

---

## 🎯 Sprint Goals

1. Implement category CRUD operations
2. Create category management endpoints
3. Add category ownership validation
4. Handle category deletion with expense checks
5. Support default and custom categories
6. Implement category filtering and search

---

## 📝 Detailed Tasks

### Task 1: Category Pydantic Schemas

**Estimated Time:** 1 hour

**Steps:**
1. Create `app/schemas/category.py`:
   ```python
   from pydantic import BaseModel, Field, ConfigDict
   from datetime import datetime
   from typing import Optional
   from uuid import UUID

   class CategoryBase(BaseModel):
       name: str = Field(..., min_length=1, max_length=100)
       description: Optional[str] = None
       color: str = Field(default="#3182ce", pattern="^#[0-9A-Fa-f]{6}$")
       icon: Optional[str] = Field(None, max_length=50)
       is_default: bool = False

   class CategoryCreate(CategoryBase):
       pass

   class CategoryUpdate(BaseModel):
       name: Optional[str] = Field(None, min_length=1, max_length=100)
       description: Optional[str] = None
       color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
       icon: Optional[str] = Field(None, max_length=50)

   class CategoryResponse(CategoryBase):
       id: UUID
       user_id: UUID
       created_at: datetime
       updated_at: datetime

       model_config = ConfigDict(from_attributes=True)

   class CategoryListResponse(BaseModel):
       total: int
       items: list[CategoryResponse]
   ```

2. Update `app/schemas/__init__.py`:
   ```python
   from app.schemas.category import (
       CategoryBase,
       CategoryCreate,
       CategoryUpdate,
       CategoryResponse,
       CategoryListResponse
   )
   ```

**Acceptance Criteria:**
- All category schemas created
- Validation rules defined (name length, color format)
- Schemas can be imported

---

### Task 2: Category CRUD Operations

**Estimated Time:** 2.5 hours

**Steps:**
1. Create `app/crud/category.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select, func, and_
   from typing import List, Optional
   from uuid import UUID
   from app.database.models import Category
   from app.crud.base import CRUDBase

   class CRUDCategory(CRUDBase[Category]):
       async def get_by_user(
           self,
           db: AsyncSession,
           user_id: UUID,
           skip: int = 0,
           limit: int = 100
       ) -> tuple[List[Category], int]:
           """Get all categories for a user"""
           # Count total
           count_query = select(func.count()).select_from(Category).where(
               Category.user_id == user_id
           )
           total = await db.scalar(count_query)

           # Fetch items
           query = select(Category).where(
               Category.user_id == user_id
           ).order_by(Category.is_default.desc(), Category.name.asc())

           query = query.offset(skip).limit(limit)
           result = await db.execute(query)
           items = result.scalars().all()
           return items, total

       async def get_by_user_and_name(
           self,
           db: AsyncSession,
           user_id: UUID,
           name: str
       ) -> Optional[Category]:
           """Get category by user and name"""
           query = select(Category).where(
               and_(
                   Category.user_id == user_id,
                   Category.name == name
               )
           )
           result = await db.execute(query)
           return result.scalar_one_or_none()

       async def get_default_categories(
           self,
           db: AsyncSession,
           user_id: UUID
       ) -> List[Category]:
           """Get all default categories for a user"""
           query = select(Category).where(
               and_(
                   Category.user_id == user_id,
                   Category.is_default == True
               )
           )
           result = await db.execute(query)
           return result.scalars().all()

       async def has_expenses(
           self,
           db: AsyncSession,
           category_id: UUID
       ) -> bool:
           """Check if category has associated expenses"""
           from app.database.models import Expense
           query = select(func.count()).select_from(Expense).where(
               Expense.category_id == category_id
           )
           count = await db.scalar(query)
           return count > 0 if count else False

   crud_category = CRUDCategory(Category)
   ```

**Acceptance Criteria:**
- Category CRUD operations implemented
- User-specific queries work
- Default category filtering works
- Expense check function works

---

### Task 3: Category Service

**Estimated Time:** 1.5 hours

**Steps:**
1. Create `app/services/category_service.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.crud.category import crud_category
   from app.core.exceptions import (
       NotFoundError,
       ConflictError,
       BadRequestError
   )
   from app.schemas.category import CategoryCreate, CategoryUpdate
   from uuid import UUID

   class CategoryService:
       @staticmethod
       async def create_category(
           db: AsyncSession,
           user_id: UUID,
           category_data: CategoryCreate
       ):
           """Create a new category for user"""
           # Check for duplicate name
           existing = await crud_category.get_by_user_and_name(
               db, user_id, category_data.name
           )
           if existing:
               raise ConflictError(f"Category '{category_data.name}' already exists")

           # Prevent creating default categories (they're system-managed)
           if category_data.is_default:
               raise BadRequestError("Cannot create default categories manually")

           category_dict = category_data.model_dump()
           category_dict["user_id"] = user_id

           return await crud_category.create(db, category_dict)

       @staticmethod
       async def update_category(
           db: AsyncSession,
           user_id: UUID,
           category_id: UUID,
           category_data: CategoryUpdate
       ):
           """Update a category"""
           category = await crud_category.get(db, category_id)

           if not category:
               raise NotFoundError("Category", str(category_id))

           if category.user_id != user_id:
               raise NotFoundError("Category", str(category_id))

           # Prevent modifying default categories
           if category.is_default:
               raise BadRequestError("Cannot modify default categories")

           # Check for duplicate name if name is being updated
           if category_data.name and category_data.name != category.name:
               existing = await crud_category.get_by_user_and_name(
                   db, user_id, category_data.name
               )
               if existing:
                   raise ConflictError(f"Category '{category_data.name}' already exists")

           update_dict = category_data.model_dump(exclude_unset=True)
           return await crud_category.update(db, category_id, update_dict)

       @staticmethod
       async def delete_category(
           db: AsyncSession,
           user_id: UUID,
           category_id: UUID
       ):
           """Delete a category"""
           category = await crud_category.get(db, category_id)

           if not category:
               raise NotFoundError("Category", str(category_id))

           if category.user_id != user_id:
               raise NotFoundError("Category", str(category_id))

           # Prevent deleting default categories
           if category.is_default:
               raise BadRequestError("Cannot delete default categories")

           # Check if category has expenses
           has_expenses = await crud_category.has_expenses(db, category_id)
           if has_expenses:
               raise BadRequestError(
                   "Cannot delete category with associated expenses. "
                   "Please reassign or delete expenses first."
               )

           return await crud_category.delete(db, category_id)

   category_service = CategoryService()
   ```

**Acceptance Criteria:**
- Category creation service works
- Category update service works
- Category deletion service works
- Ownership validation works
- Default category protection works

---

### Task 4: Category Endpoints

**Estimated Time:** 2 hours

**Steps:**
1. Create `app/api/v1/endpoints/categories.py`:
   ```python
   from fastapi import APIRouter, Depends, Query, status
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.database.connection import get_db
   from app.dependencies import get_current_user
   from app.database.models import User
   from app.schemas.category import (
       CategoryCreate,
       CategoryUpdate,
       CategoryResponse,
       CategoryListResponse
   )
   from app.services.category_service import category_service
   from app.crud.category import crud_category
   from app.core.exceptions import NotFoundError
   from uuid import UUID

   router = APIRouter(prefix="/categories", tags=["Categories"])

   @router.post(
       "",
       response_model=CategoryResponse,
       status_code=status.HTTP_201_CREATED,
       summary="Create a new category"
   )
   async def create_category(
       category_data: CategoryCreate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Create a new expense category"""
       return await category_service.create_category(
           db, current_user.id, category_data
       )

   @router.get(
       "",
       response_model=CategoryListResponse,
       summary="List all categories"
   )
   async def list_categories(
       skip: int = Query(0, ge=0),
       limit: int = Query(100, ge=1, le=100),
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get all categories for the current user"""
       items, total = await crud_category.get_by_user(
           db, current_user.id, skip, limit
       )
       return CategoryListResponse(total=total, items=items)

   @router.get(
       "/{category_id}",
       response_model=CategoryResponse,
       summary="Get category by ID"
   )
   async def get_category(
       category_id: UUID,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get a specific category"""
       category = await crud_category.get(db, category_id)

       if not category:
           raise NotFoundError("Category", str(category_id))

       if category.user_id != current_user.id:
           raise NotFoundError("Category", str(category_id))

       return category

   @router.put(
       "/{category_id}",
       response_model=CategoryResponse,
       summary="Update category"
   )
   async def update_category(
       category_id: UUID,
       category_data: CategoryUpdate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Update a category"""
       return await category_service.update_category(
           db, current_user.id, category_id, category_data
       )

   @router.delete(
       "/{category_id}",
       status_code=status.HTTP_204_NO_CONTENT,
       summary="Delete category"
   )
   async def delete_category(
       category_id: UUID,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Delete a category"""
       await category_service.delete_category(
           db, current_user.id, category_id
       )
       return None
   ```

2. Update `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import auth, users, categories

   api_router.include_router(categories.router, prefix="/v1")
   ```

**Acceptance Criteria:**
- All category endpoints created
- Endpoints require authentication
- Ownership validation works
- CRUD operations work correctly

---

### Task 5: Category Validation & Error Handling

**Estimated Time:** 1 hour

**Steps:**
1. Add validation for category name uniqueness per user
2. Add validation for color format (hex color)
3. Add validation for icon length
4. Test error scenarios:
   - Duplicate category name
   - Invalid color format
   - Trying to modify default category
   - Trying to delete category with expenses
   - Accessing another user's category

**Acceptance Criteria:**
- All validations work
- Error messages are clear
- Appropriate HTTP status codes returned

---

### Task 6: Testing Category Endpoints

**Estimated Time:** 1.5 hours

**Steps:**
1. Test category creation:
   ```bash
   curl -X POST http://localhost:8000/api/v1/categories \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Groceries",
       "description": "Food shopping",
       "color": "#10b981",
       "icon": "🛒"
     }'
   ```

2. Test listing categories:
   ```bash
   curl -X GET http://localhost:8000/api/v1/categories \
     -H "Authorization: Bearer TOKEN"
   ```

3. Test updating category:
   ```bash
   curl -X PUT http://localhost:8000/api/v1/categories/{id} \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated Name",
       "color": "#ef4444"
     }'
   ```

4. Test deleting category:
   ```bash
   curl -X DELETE http://localhost:8000/api/v1/categories/{id} \
     -H "Authorization: Bearer TOKEN"
   ```

**Acceptance Criteria:**
- All endpoints tested manually
- Error cases tested
- Default categories visible but not modifiable

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] Create category works
- [ ] Duplicate category name rejected
- [ ] List categories returns user's categories
- [ ] Get category by ID works
- [ ] Update category works
- [ ] Delete empty category works
- [ ] Delete category with expenses fails
- [ ] Cannot modify default categories
- [ ] Cannot delete default categories
- [ ] Cannot access another user's categories
- [ ] Color validation works
- [ ] Pagination works

### API Testing Scenarios

1. **Category Creation:**
   - Create valid category → 201 Created
   - Create duplicate name → 409 Conflict
   - Create with invalid color → 422 Validation Error
   - Try to create default category → 400 Bad Request

2. **Category Retrieval:**
   - List categories → 200 OK with user's categories
   - Get existing category → 200 OK
   - Get non-existent category → 404 Not Found
   - Get another user's category → 404 Not Found

3. **Category Update:**
   - Update category → 200 OK
   - Update to duplicate name → 409 Conflict
   - Update default category → 400 Bad Request
   - Update another user's category → 404 Not Found

4. **Category Deletion:**
   - Delete empty category → 204 No Content
   - Delete category with expenses → 400 Bad Request
   - Delete default category → 400 Bad Request
   - Delete another user's category → 404 Not Found

---

## 📦 Deliverables

1. ✅ Category Pydantic schemas
2. ✅ Category CRUD operations
3. ✅ Category service with business logic
4. ✅ Category endpoints (CRUD)
5. ✅ Ownership validation
6. ✅ Default category protection
7. ✅ Expense association checks

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Duplicate category name | Check unique constraint per user |
| Cannot delete category | Verify no expenses associated |
| Default category modification | Check is_default flag before update |
| Color validation fails | Ensure hex color format (#RRGGBB) |
| Ownership check fails | Verify user_id matches current_user.id |

---

## 🔄 Next Sprint Preview

**Sprint 5: Expense Management**
- Expense CRUD operations
- Expense endpoints with filtering
- Date range queries
- Category validation
- Amount filtering

---

## 📚 Resources

- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [SQLAlchemy Filtering](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)
- [Pydantic Field Validation](https://docs.pydantic.dev/latest/concepts/fields/)

