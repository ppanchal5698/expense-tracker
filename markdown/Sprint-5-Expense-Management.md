# Sprint 5: Expense Management

## 📋 Sprint Overview

**Duration:** 5-6 days
**Objective:** Implement complete expense management system with CRUD operations, advanced filtering, pagination, and validation.

**Success Criteria:**
- ✅ Expense CRUD operations implemented
- ✅ Expense endpoints with filtering
- ✅ Date range queries working
- ✅ Category and amount filtering
- ✅ Pagination implemented
- ✅ Tag filtering support
- ✅ All endpoints tested and documented

---

## 🎯 Sprint Goals

1. Implement expense CRUD operations
2. Create expense management endpoints
3. Add advanced filtering (date, category, amount, tags)
4. Implement pagination
5. Add expense validation
6. Support payment methods and tags

---

## 📝 Detailed Tasks

### Task 1: Expense Pydantic Schemas

**Estimated Time:** 1.5 hours

**Steps:**
1. Create `app/schemas/expense.py`:
   ```python
   from pydantic import BaseModel, Field, ConfigDict
   from datetime import date, datetime
   from typing import Optional, List
   from uuid import UUID
   from decimal import Decimal
   from app.core.constants import PaymentMethod

   class ExpenseBase(BaseModel):
       description: Optional[str] = Field(None, max_length=255)
       amount: Decimal = Field(..., gt=0, decimal_places=2)
       date: date
       payment_method: Optional[PaymentMethod] = None
       tags: Optional[List[str]] = Field(None, max_items=10)
       notes: Optional[str] = None

   class ExpenseCreate(ExpenseBase):
       category_id: UUID

   class ExpenseUpdate(BaseModel):
       description: Optional[str] = Field(None, max_length=255)
       amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
       date: Optional[date] = None
       category_id: Optional[UUID] = None
       payment_method: Optional[PaymentMethod] = None
       tags: Optional[List[str]] = Field(None, max_items=10)
       notes: Optional[str] = None

   class ExpenseResponse(ExpenseBase):
       id: UUID
       user_id: UUID
       category_id: UUID
       created_at: datetime
       updated_at: datetime

       model_config = ConfigDict(from_attributes=True)

   class ExpenseListResponse(BaseModel):
       total: int
       items: List[ExpenseResponse]
       page: int
       per_page: int
       total_pages: int

   class ExpenseFilterParams(BaseModel):
       start_date: Optional[date] = None
       end_date: Optional[date] = None
       category_id: Optional[UUID] = None
       min_amount: Optional[Decimal] = None
       max_amount: Optional[Decimal] = None
       payment_method: Optional[PaymentMethod] = None
       tags: Optional[List[str]] = None
   ```

2. Update `app/schemas/__init__.py`:
   ```python
   from app.schemas.expense import (
       ExpenseBase,
       ExpenseCreate,
       ExpenseUpdate,
       ExpenseResponse,
       ExpenseListResponse,
       ExpenseFilterParams
   )
   ```

**Acceptance Criteria:**
- All expense schemas created
- Validation rules defined
- Amount validation (gt=0)
- Date validation
- Schemas can be imported

---

### Task 2: Expense CRUD Operations

**Estimated Time:** 3 hours

**Steps:**
1. Create `app/crud/expense.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select, func, and_, or_
   from typing import Optional, List, Tuple
   from uuid import UUID
   from datetime import date
   from decimal import Decimal
   from app.database.models import Expense
   from app.crud.base import CRUDBase
   from app.core.constants import PaymentMethod

   class CRUDExpense(CRUDBase[Expense]):
       async def get_by_user(
           self,
           db: AsyncSession,
           user_id: UUID,
           skip: int = 0,
           limit: int = 10
       ) -> Tuple[List[Expense], int]:
           """Get all expenses for a user"""
           # Count total
           count_query = select(func.count()).select_from(Expense).where(
               Expense.user_id == user_id
           )
           total = await db.scalar(count_query)

           # Fetch items
           query = select(Expense).where(
               Expense.user_id == user_id
           ).order_by(Expense.date.desc(), Expense.created_at.desc())

           query = query.offset(skip).limit(limit)
           result = await db.execute(query)
           items = result.scalars().all()
           return items, total

       async def get_by_user_and_date_range(
           self,
           db: AsyncSession,
           user_id: UUID,
           start_date: Optional[date] = None,
           end_date: Optional[date] = None,
           category_id: Optional[UUID] = None,
           min_amount: Optional[Decimal] = None,
           max_amount: Optional[Decimal] = None,
           payment_method: Optional[PaymentMethod] = None,
           tags: Optional[List[str]] = None,
           skip: int = 0,
           limit: int = 10
       ) -> Tuple[List[Expense], int]:
           """Get expenses with filters"""
           conditions = [Expense.user_id == user_id]

           if start_date:
               conditions.append(Expense.date >= start_date)
           if end_date:
               conditions.append(Expense.date <= end_date)
           if category_id:
               conditions.append(Expense.category_id == category_id)
           if min_amount:
               conditions.append(Expense.amount >= min_amount)
           if max_amount:
               conditions.append(Expense.amount <= max_amount)
           if payment_method:
               conditions.append(Expense.payment_method == payment_method.value)
           if tags:
               # PostgreSQL array contains operator
               conditions.append(Expense.tags.contains(tags))

           # Count total
           count_query = select(func.count()).select_from(Expense).where(
               and_(*conditions)
           )
           total = await db.scalar(count_query)

           # Fetch items
           query = select(Expense).where(
               and_(*conditions)
           ).order_by(Expense.date.desc(), Expense.created_at.desc())

           query = query.offset(skip).limit(limit)
           result = await db.execute(query)
           items = result.scalars().all()
           return items, total

       async def get_monthly_summary(
           self,
           db: AsyncSession,
           user_id: UUID,
           year: int,
           month: int
       ) -> List[dict]:
           """Get expenses grouped by category for a month"""
           from sqlalchemy import extract
           from app.database.models import Category

           query = select(
               Expense.category_id,
               Category.name.label("category_name"),
               func.sum(Expense.amount).label("total"),
               func.count(Expense.id).label("count")
           ).join(
               Category, Expense.category_id == Category.id
           ).where(
               and_(
                   Expense.user_id == user_id,
                   extract("year", Expense.date) == year,
                   extract("month", Expense.date) == month
               )
           ).group_by(Expense.category_id, Category.name)

           result = await db.execute(query)
           return [
               {
                   "category_id": str(row.category_id),
                   "category_name": row.category_name,
                   "total": float(row.total),
                   "count": row.count
               }
               for row in result.all()
           ]

       async def get_total_by_date_range(
           self,
           db: AsyncSession,
           user_id: UUID,
           start_date: date,
           end_date: date
       ) -> Decimal:
           """Get total expense amount for date range"""
           query = select(func.sum(Expense.amount)).where(
               and_(
                   Expense.user_id == user_id,
                   Expense.date.between(start_date, end_date)
               )
           )
           result = await db.scalar(query)
           return result or Decimal("0.00")

   crud_expense = CRUDExpense(Expense)
   ```

**Acceptance Criteria:**
- Expense CRUD operations implemented
- Filtering functions work
- Date range queries work
- Monthly summary works
- Total calculation works

---

### Task 3: Expense Service

**Estimated Time:** 2 hours

**Steps:**
1. Create `app/services/expense_service.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.crud.expense import crud_expense
   from app.crud.category import crud_category
   from app.core.exceptions import NotFoundError, BadRequestError
   from app.schemas.expense import ExpenseCreate, ExpenseUpdate
   from uuid import UUID

   class ExpenseService:
       @staticmethod
       async def create_expense(
           db: AsyncSession,
           user_id: UUID,
           expense_data: ExpenseCreate
       ):
           """Create a new expense"""
           # Verify category exists and belongs to user
           category = await crud_category.get(db, expense_data.category_id)

           if not category:
               raise NotFoundError("Category", str(expense_data.category_id))

           if category.user_id != user_id:
               raise NotFoundError("Category", str(expense_data.category_id))

           expense_dict = expense_data.model_dump()
           expense_dict["user_id"] = user_id

           return await crud_expense.create(db, expense_dict)

       @staticmethod
       async def update_expense(
           db: AsyncSession,
           user_id: UUID,
           expense_id: UUID,
           expense_data: ExpenseUpdate
       ):
           """Update an expense"""
           expense = await crud_expense.get(db, expense_id)

           if not expense:
               raise NotFoundError("Expense", str(expense_id))

           if expense.user_id != user_id:
               raise NotFoundError("Expense", str(expense_id))

           # If category is being updated, verify it exists and belongs to user
           if expense_data.category_id:
               category = await crud_category.get(db, expense_data.category_id)
               if not category:
                   raise NotFoundError("Category", str(expense_data.category_id))
               if category.user_id != user_id:
                   raise NotFoundError("Category", str(expense_data.category_id))

           update_dict = expense_data.model_dump(exclude_unset=True)
           return await crud_expense.update(db, expense_id, update_dict)

       @staticmethod
       async def delete_expense(
           db: AsyncSession,
           user_id: UUID,
           expense_id: UUID
       ):
           """Delete an expense"""
           expense = await crud_expense.get(db, expense_id)

           if not expense:
               raise NotFoundError("Expense", str(expense_id))

           if expense.user_id != user_id:
               raise NotFoundError("Expense", str(expense_id))

           return await crud_expense.delete(db, expense_id)

   expense_service = ExpenseService()
   ```

**Acceptance Criteria:**
- Expense creation service works
- Expense update service works
- Expense deletion service works
- Category validation works
- Ownership validation works

---

### Task 4: Expense Endpoints

**Estimated Time:** 3 hours

**Steps:**
1. Create `app/api/v1/endpoints/expenses.py`:
   ```python
   from fastapi import APIRouter, Depends, Query, status
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.database.connection import get_db
   from app.dependencies import get_current_user
   from app.database.models import User
   from app.schemas.expense import (
       ExpenseCreate,
       ExpenseUpdate,
       ExpenseResponse,
       ExpenseListResponse
   )
   from app.services.expense_service import expense_service
   from app.crud.expense import crud_expense
   from app.core.exceptions import NotFoundError
   from app.core.constants import PaymentMethod
   from uuid import UUID
   from datetime import date
   from decimal import Decimal
   from typing import Optional, List

   router = APIRouter(prefix="/expenses", tags=["Expenses"])

   @router.post(
       "",
       response_model=ExpenseResponse,
       status_code=status.HTTP_201_CREATED,
       summary="Create a new expense"
   )
   async def create_expense(
       expense_data: ExpenseCreate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Create a new expense record"""
       return await expense_service.create_expense(
           db, current_user.id, expense_data
       )

   @router.get(
       "",
       response_model=ExpenseListResponse,
       summary="List expenses with filters"
   )
   async def list_expenses(
       page: int = Query(1, ge=1),
       per_page: int = Query(10, ge=1, le=100),
       start_date: Optional[date] = Query(None),
       end_date: Optional[date] = Query(None),
       category_id: Optional[UUID] = Query(None),
       min_amount: Optional[Decimal] = Query(None, ge=0),
       max_amount: Optional[Decimal] = Query(None, ge=0),
       payment_method: Optional[PaymentMethod] = Query(None),
       tags: Optional[List[str]] = Query(None),
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get expenses with optional filters"""
       skip = (page - 1) * per_page

       items, total = await crud_expense.get_by_user_and_date_range(
           db=db,
           user_id=current_user.id,
           start_date=start_date,
           end_date=end_date,
           category_id=category_id,
           min_amount=min_amount,
           max_amount=max_amount,
           payment_method=payment_method,
           tags=tags,
           skip=skip,
           limit=per_page
       )

       total_pages = (total + per_page - 1) // per_page

       return ExpenseListResponse(
           total=total,
           items=items,
           page=page,
           per_page=per_page,
           total_pages=total_pages
       )

   @router.get(
       "/{expense_id}",
       response_model=ExpenseResponse,
       summary="Get expense by ID"
   )
   async def get_expense(
       expense_id: UUID,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get a specific expense"""
       expense = await crud_expense.get(db, expense_id)

       if not expense:
           raise NotFoundError("Expense", str(expense_id))

       if expense.user_id != current_user.id:
           raise NotFoundError("Expense", str(expense_id))

       return expense

   @router.put(
       "/{expense_id}",
       response_model=ExpenseResponse,
       summary="Update expense"
   )
   async def update_expense(
       expense_id: UUID,
       expense_data: ExpenseUpdate,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Update an expense"""
       return await expense_service.update_expense(
           db, current_user.id, expense_id, expense_data
       )

   @router.delete(
       "/{expense_id}",
       status_code=status.HTTP_204_NO_CONTENT,
       summary="Delete expense"
   )
   async def delete_expense(
       expense_id: UUID,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Delete an expense"""
       await expense_service.delete_expense(
           db, current_user.id, expense_id
       )
       return None
   ```

2. Update `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import auth, users, categories, expenses

   api_router.include_router(expenses.router, prefix="/v1")
   ```

**Acceptance Criteria:**
- All expense endpoints created
- Filtering works via query parameters
- Pagination works
- Endpoints require authentication
- Ownership validation works

---

### Task 5: Advanced Filtering Implementation

**Estimated Time:** 2 hours

**Steps:**
1. Test date range filtering
2. Test category filtering
3. Test amount range filtering
4. Test payment method filtering
5. Test tag filtering (PostgreSQL array operations)
6. Test combined filters

**Acceptance Criteria:**
- All filters work independently
- Combined filters work correctly
- Filter validation works
- Performance is acceptable

---

### Task 6: Testing Expense Endpoints

**Estimated Time:** 2 hours

**Steps:**
1. Test expense creation:
   ```bash
   curl -X POST http://localhost:8000/api/v1/expenses \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 25.50,
       "date": "2024-01-15",
       "category_id": "category-uuid",
       "description": "Lunch",
       "payment_method": "card",
       "tags": ["food", "lunch"]
     }'
   ```

2. Test listing with filters:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/expenses?start_date=2024-01-01&end_date=2024-01-31&page=1&per_page=20" \
     -H "Authorization: Bearer TOKEN"
   ```

3. Test updating expense:
   ```bash
   curl -X PUT http://localhost:8000/api/v1/expenses/{id} \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 30.00,
       "description": "Updated lunch"
     }'
   ```

4. Test deleting expense:
   ```bash
   curl -X DELETE http://localhost:8000/api/v1/expenses/{id} \
     -H "Authorization: Bearer TOKEN"
   ```

**Acceptance Criteria:**
- All endpoints tested manually
- Filtering tested with various combinations
- Error cases tested

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] Create expense works
- [ ] List expenses works
- [ ] Date range filtering works
- [ ] Category filtering works
- [ ] Amount range filtering works
- [ ] Payment method filtering works
- [ ] Tag filtering works
- [ ] Combined filters work
- [ ] Pagination works
- [ ] Get expense by ID works
- [ ] Update expense works
- [ ] Delete expense works
- [ ] Cannot access another user's expenses
- [ ] Category validation works
- [ ] Amount validation (must be > 0)

### API Testing Scenarios

1. **Expense Creation:**
   - Create valid expense → 201 Created
   - Create with invalid category → 404 Not Found
   - Create with amount <= 0 → 422 Validation Error
   - Create with invalid date → 422 Validation Error

2. **Expense Filtering:**
   - List all expenses → 200 OK
   - Filter by date range → 200 OK
   - Filter by category → 200 OK
   - Filter by amount range → 200 OK
   - Filter by payment method → 200 OK
   - Filter by tags → 200 OK
   - Combined filters → 200 OK

3. **Expense Update:**
   - Update expense → 200 OK
   - Update to invalid category → 404 Not Found
   - Update another user's expense → 404 Not Found

4. **Expense Deletion:**
   - Delete expense → 204 No Content
   - Delete another user's expense → 404 Not Found

---

## 📦 Deliverables

1. ✅ Expense Pydantic schemas
2. ✅ Expense CRUD operations
3. ✅ Expense service with validation
4. ✅ Expense endpoints (CRUD)
5. ✅ Advanced filtering implementation
6. ✅ Pagination support
7. ✅ Tag filtering support

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tag filtering not working | Use PostgreSQL array contains operator |
| Date range query slow | Ensure index on date column |
| Amount filtering fails | Use Decimal type for precision |
| Pagination incorrect | Calculate skip correctly: (page-1) * per_page |
| Category validation fails | Verify category belongs to user |

---

## 🔄 Next Sprint Preview

**Sprint 6: Analytics & Reporting**
- Monthly summaries
- Yearly summaries
- Category breakdowns
- Spending trends
- Analytics endpoints

---

## 📚 Resources

- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [PostgreSQL Array Operations](https://www.postgresql.org/docs/current/arrays.html)
- [SQLAlchemy Date Functions](https://docs.sqlalchemy.org/en/20/core/functions.html)

