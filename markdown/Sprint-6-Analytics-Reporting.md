# Sprint 6: Analytics & Reporting

## 📋 Sprint Overview

**Duration:** 4-5 days
**Objective:** Implement comprehensive analytics and reporting features including monthly/yearly summaries, category breakdowns, and spending trends.

**Success Criteria:**
- ✅ Monthly expense summaries implemented
- ✅ Yearly expense summaries implemented
- ✅ Category breakdown analytics working
- ✅ Spending trends calculated
- ✅ Analytics endpoints created
- ✅ All analytics tested and verified

---

## 🎯 Sprint Goals

1. Implement monthly expense summaries
2. Create yearly expense summaries
3. Build category breakdown analytics
4. Add spending trend calculations
5. Create analytics endpoints
6. Support date range analytics

---

## 📝 Detailed Tasks

### Task 1: Analytics Pydantic Schemas

**Estimated Time:** 1.5 hours

**Steps:**
1. Create `app/schemas/analytics.py`:
   ```python
   from pydantic import BaseModel, Field
   from datetime import date
   from typing import List, Optional
   from uuid import UUID
   from decimal import Decimal

   class CategoryBreakdown(BaseModel):
       category_id: UUID
       category_name: str
       total_amount: Decimal
       expense_count: int
       percentage: float = Field(..., ge=0, le=100)

   class MonthlySummary(BaseModel):
       year: int
       month: int
       total_expenses: Decimal
       expense_count: int
       average_expense: Decimal
       category_breakdown: List[CategoryBreakdown]
       top_category: Optional[str] = None

   class YearlySummary(BaseModel):
       year: int
       total_expenses: Decimal
       expense_count: int
       average_monthly_expense: Decimal
       monthly_breakdown: List[dict]  # {month: int, total: Decimal}
       category_breakdown: List[CategoryBreakdown]

   class SpendingTrend(BaseModel):
       period: str  # "daily", "weekly", "monthly"
       data_points: List[dict]  # [{date: date, total: Decimal}]

   class DateRangeSummary(BaseModel):
       start_date: date
       end_date: date
       total_expenses: Decimal
       expense_count: int
       average_expense: Decimal
       category_breakdown: List[CategoryBreakdown]
       daily_average: Decimal

   class AnalyticsResponse(BaseModel):
       summary: DateRangeSummary
       trends: Optional[SpendingTrend] = None
   ```

2. Update `app/schemas/__init__.py`:
   ```python
   from app.schemas.analytics import (
       CategoryBreakdown,
       MonthlySummary,
       YearlySummary,
       SpendingTrend,
       DateRangeSummary,
       AnalyticsResponse
   )
   ```

**Acceptance Criteria:**
- All analytics schemas created
- Validation rules defined
- Schemas can be imported

---

### Task 2: Analytics Service

**Estimated Time:** 4 hours

**Steps:**
1. Create `app/services/analytics_service.py`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select, func, extract, and_
   from typing import List, Optional
   from uuid import UUID
   from datetime import date, datetime, timedelta
   from decimal import Decimal
   from app.crud.expense import crud_expense
   from app.database.models import Expense, Category
   from app.schemas.analytics import (
       CategoryBreakdown,
       MonthlySummary,
       YearlySummary,
       SpendingTrend,
       DateRangeSummary
   )
   from calendar import monthrange

   class AnalyticsService:
       @staticmethod
       async def get_monthly_summary(
           db: AsyncSession,
           user_id: UUID,
           year: int,
           month: int
       ) -> MonthlySummary:
           """Get monthly expense summary"""
           # Get category breakdown
           category_data = await crud_expense.get_monthly_summary(
               db, user_id, year, month
           )

           # Calculate totals
           total_expenses = sum(Decimal(str(item["total"])) for item in category_data)
           expense_count = sum(item["count"] for item in category_data)
           average_expense = total_expenses / expense_count if expense_count > 0 else Decimal("0")

           # Calculate percentages and find top category
           category_breakdown = []
           top_category = None
           top_amount = Decimal("0")

           for item in category_data:
               amount = Decimal(str(item["total"]))
               percentage = float((amount / total_expenses * 100) if total_expenses > 0 else 0)

               category_breakdown.append(CategoryBreakdown(
                   category_id=UUID(item["category_id"]),
                   category_name=item["category_name"],
                   total_amount=amount,
                   expense_count=item["count"],
                   percentage=percentage
               ))

               if amount > top_amount:
                   top_amount = amount
                   top_category = item["category_name"]

           return MonthlySummary(
               year=year,
               month=month,
               total_expenses=total_expenses,
               expense_count=expense_count,
               average_expense=average_expense,
               category_breakdown=category_breakdown,
               top_category=top_category
           )

       @staticmethod
       async def get_yearly_summary(
           db: AsyncSession,
           user_id: UUID,
           year: int
       ) -> YearlySummary:
           """Get yearly expense summary"""
           # Get monthly totals
           monthly_totals = []
           for month in range(1, 13):
               monthly_data = await crud_expense.get_monthly_summary(
                   db, user_id, year, month
               )
               month_total = sum(Decimal(str(item["total"])) for item in monthly_data)
               monthly_totals.append({
                   "month": month,
                   "total": month_total
               })

           # Calculate yearly totals
           total_expenses = sum(item["total"] for item in monthly_totals)

           # Get all expenses for the year for count
           start_date = date(year, 1, 1)
           end_date = date(year, 12, 31)
           _, expense_count = await crud_expense.get_by_user_and_date_range(
               db, user_id, start_date, end_date, skip=0, limit=10000
           )

           average_monthly = total_expenses / 12 if total_expenses > 0 else Decimal("0")

           # Get category breakdown for the year
           category_breakdown = await AnalyticsService._get_category_breakdown_for_range(
               db, user_id, start_date, end_date, total_expenses
           )

           return YearlySummary(
               year=year,
               total_expenses=total_expenses,
               expense_count=expense_count,
               average_monthly_expense=average_monthly,
               monthly_breakdown=monthly_totals,
               category_breakdown=category_breakdown
           )

       @staticmethod
       async def get_date_range_summary(
           db: AsyncSession,
           user_id: UUID,
           start_date: date,
           end_date: date
       ) -> DateRangeSummary:
           """Get summary for a date range"""
           # Get total expenses
           total_expenses = await crud_expense.get_total_by_date_range(
               db, user_id, start_date, end_date
           )

           # Get expense count
           _, expense_count = await crud_expense.get_by_user_and_date_range(
               db, user_id, start_date, end_date, skip=0, limit=10000
           )

           # Calculate averages
           average_expense = total_expenses / expense_count if expense_count > 0 else Decimal("0")
           days = (end_date - start_date).days + 1
           daily_average = total_expenses / days if days > 0 else Decimal("0")

           # Get category breakdown
           category_breakdown = await AnalyticsService._get_category_breakdown_for_range(
               db, user_id, start_date, end_date, total_expenses
           )

           return DateRangeSummary(
               start_date=start_date,
               end_date=end_date,
               total_expenses=total_expenses,
               expense_count=expense_count,
               average_expense=average_expense,
               category_breakdown=category_breakdown,
               daily_average=daily_average
           )

       @staticmethod
       async def get_spending_trend(
           db: AsyncSession,
           user_id: UUID,
           start_date: date,
           end_date: date,
           period: str = "daily"
       ) -> SpendingTrend:
           """Get spending trend over time"""
           if period == "daily":
               return await AnalyticsService._get_daily_trend(
                   db, user_id, start_date, end_date
               )
           elif period == "weekly":
               return await AnalyticsService._get_weekly_trend(
                   db, user_id, start_date, end_date
               )
           elif period == "monthly":
               return await AnalyticsService._get_monthly_trend(
                   db, user_id, start_date, end_date
               )
           else:
               raise ValueError(f"Invalid period: {period}")

       @staticmethod
       async def _get_category_breakdown_for_range(
           db: AsyncSession,
           user_id: UUID,
           start_date: date,
           end_date: date,
           total_expenses: Decimal
       ) -> List[CategoryBreakdown]:
           """Get category breakdown for a date range"""
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
                   Expense.date.between(start_date, end_date)
               )
           ).group_by(Expense.category_id, Category.name)

           result = await db.execute(query)
           breakdown = []

           for row in result.all():
               amount = Decimal(str(row.total))
               percentage = float((amount / total_expenses * 100) if total_expenses > 0 else 0)

               breakdown.append(CategoryBreakdown(
                   category_id=row.category_id,
                   category_name=row.category_name,
                   total_amount=amount,
                   expense_count=row.count,
                   percentage=percentage
               ))

           return sorted(breakdown, key=lambda x: x.total_amount, reverse=True)

       @staticmethod
       async def _get_daily_trend(
           db: AsyncSession,
           user_id: UUID,
           start_date: date,
           end_date: date
       ) -> SpendingTrend:
           """Get daily spending trend"""
           query = select(
               Expense.date,
               func.sum(Expense.amount).label("total")
           ).where(
               and_(
                   Expense.user_id == user_id,
                   Expense.date.between(start_date, end_date)
               )
           ).group_by(Expense.date).order_by(Expense.date)

           result = await db.execute(query)
           data_points = [
               {
                   "date": row.date,
                   "total": float(row.total)
               }
               for row in result.all()
           ]

           return SpendingTrend(period="daily", data_points=data_points)

       @staticmethod
       async def _get_weekly_trend(
           db: AsyncSession,
           user_id: UUID,
           start_date: date,
           end_date: date
       ) -> SpendingTrend:
           """Get weekly spending trend"""
           # Group by week
           query = select(
               func.date_trunc("week", Expense.date).label("week_start"),
               func.sum(Expense.amount).label("total")
           ).where(
               and_(
                   Expense.user_id == user_id,
                   Expense.date.between(start_date, end_date)
               )
           ).group_by("week_start").order_by("week_start")

           result = await db.execute(query)
           data_points = [
               {
                   "date": row.week_start.date(),
                   "total": float(row.total)
               }
               for row in result.all()
           ]

           return SpendingTrend(period="weekly", data_points=data_points)

       @staticmethod
       async def _get_monthly_trend(
           db: AsyncSession,
           user_id: UUID,
           start_date: date,
           end_date: date
       ) -> SpendingTrend:
           """Get monthly spending trend"""
           query = select(
               extract("year", Expense.date).label("year"),
               extract("month", Expense.date).label("month"),
               func.sum(Expense.amount).label("total")
           ).where(
               and_(
                   Expense.user_id == user_id,
                   Expense.date.between(start_date, end_date)
               )
           ).group_by("year", "month").order_by("year", "month")

           result = await db.execute(query)
           data_points = [
               {
                   "date": date(int(row.year), int(row.month), 1),
                   "total": float(row.total)
               }
               for row in result.all()
           ]

           return SpendingTrend(period="monthly", data_points=data_points)

   analytics_service = AnalyticsService()
   ```

**Acceptance Criteria:**
- Monthly summary service works
- Yearly summary service works
- Date range summary works
- Spending trends calculated correctly
- Category breakdowns calculated

---

### Task 3: Analytics Endpoints

**Estimated Time:** 2.5 hours

**Steps:**
1. Create `app/api/v1/endpoints/analytics.py`:
   ```python
   from fastapi import APIRouter, Depends, Query, status
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.database.connection import get_db
   from app.dependencies import get_current_user
   from app.database.models import User
   from app.schemas.analytics import (
       MonthlySummary,
       YearlySummary,
       DateRangeSummary,
       SpendingTrend,
       AnalyticsResponse
   )
   from app.services.analytics_service import analytics_service
   from datetime import date
   from typing import Optional

   router = APIRouter(prefix="/analytics", tags=["Analytics"])

   @router.get(
       "/monthly/{year}/{month}",
       response_model=MonthlySummary,
       summary="Get monthly expense summary"
   )
   async def get_monthly_summary(
       year: int = Query(..., ge=2000, le=2100),
       month: int = Query(..., ge=1, le=12),
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get detailed monthly expense summary with category breakdown"""
       return await analytics_service.get_monthly_summary(
           db, current_user.id, year, month
       )

   @router.get(
       "/yearly/{year}",
       response_model=YearlySummary,
       summary="Get yearly expense summary"
   )
   async def get_yearly_summary(
       year: int = Query(..., ge=2000, le=2100),
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get detailed yearly expense summary"""
       return await analytics_service.get_yearly_summary(
           db, current_user.id, year
       )

   @router.get(
       "/date-range",
       response_model=DateRangeSummary,
       summary="Get summary for date range"
   )
   async def get_date_range_summary(
       start_date: date = Query(...),
       end_date: date = Query(...),
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get expense summary for a custom date range"""
       if start_date > end_date:
           from app.core.exceptions import BadRequestError
           raise BadRequestError("Start date must be before end date")

       return await analytics_service.get_date_range_summary(
           db, current_user.id, start_date, end_date
       )

   @router.get(
       "/trends",
       response_model=SpendingTrend,
       summary="Get spending trends"
   )
   async def get_spending_trend(
       start_date: date = Query(...),
       end_date: date = Query(...),
       period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get spending trends over time"""
       if start_date > end_date:
           from app.core.exceptions import BadRequestError
           raise BadRequestError("Start date must be before end date")

       return await analytics_service.get_spending_trend(
           db, current_user.id, start_date, end_date, period
       )

   @router.get(
       "/comprehensive",
       response_model=AnalyticsResponse,
       summary="Get comprehensive analytics"
   )
   async def get_comprehensive_analytics(
       start_date: date = Query(...),
       end_date: date = Query(...),
       include_trends: bool = Query(False),
       period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Get comprehensive analytics including summary and trends"""
       if start_date > end_date:
           from app.core.exceptions import BadRequestError
           raise BadRequestError("Start date must be before end date")

       summary = await analytics_service.get_date_range_summary(
           db, current_user.id, start_date, end_date
       )

       trends = None
       if include_trends:
           trends = await analytics_service.get_spending_trend(
               db, current_user.id, start_date, end_date, period
           )

       return AnalyticsResponse(summary=summary, trends=trends)
   ```

2. Update `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import auth, users, categories, expenses, analytics

   api_router.include_router(analytics.router, prefix="/v1")
   ```

**Acceptance Criteria:**
- All analytics endpoints created
- Endpoints require authentication
- Date validation works
- Query parameters validated

---

### Task 4: Performance Optimization

**Estimated Time:** 2 hours

**Steps:**
1. Review database queries for optimization
2. Ensure indexes are used effectively
3. Add query result caching if needed (optional)
4. Test with large datasets
5. Optimize aggregation queries

**Acceptance Criteria:**
- Queries perform well with large datasets
- Indexes utilized effectively
- Response times acceptable (< 500ms)

---

### Task 5: Testing Analytics Endpoints

**Estimated Time:** 2 hours

**Steps:**
1. Test monthly summary:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/analytics/monthly/2024/1" \
     -H "Authorization: Bearer TOKEN"
   ```

2. Test yearly summary:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/analytics/yearly/2024" \
     -H "Authorization: Bearer TOKEN"
   ```

3. Test date range summary:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/analytics/date-range?start_date=2024-01-01&end_date=2024-01-31" \
     -H "Authorization: Bearer TOKEN"
   ```

4. Test spending trends:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/analytics/trends?start_date=2024-01-01&end_date=2024-01-31&period=daily" \
     -H "Authorization: Bearer TOKEN"
   ```

5. Test comprehensive analytics:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/analytics/comprehensive?start_date=2024-01-01&end_date=2024-01-31&include_trends=true&period=weekly" \
     -H "Authorization: Bearer TOKEN"
   ```

**Acceptance Criteria:**
- All endpoints tested manually
- Results are accurate
- Edge cases handled (empty data, invalid dates)

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] Monthly summary returns correct data
- [ ] Yearly summary returns correct data
- [ ] Date range summary works
- [ ] Category breakdown percentages correct
- [ ] Spending trends calculated correctly
- [ ] Daily trend works
- [ ] Weekly trend works
- [ ] Monthly trend works
- [ ] Top category identified correctly
- [ ] Averages calculated correctly
- [ ] Empty data handled gracefully
- [ ] Invalid date ranges rejected

### Verification Queries

Test analytics with sample data:
1. Create expenses across multiple months
2. Create expenses in different categories
3. Verify monthly totals match
4. Verify category percentages sum to 100%
5. Verify trends show correct patterns

---

## 📦 Deliverables

1. ✅ Analytics Pydantic schemas
2. ✅ Analytics service with all calculations
3. ✅ Monthly summary endpoint
4. ✅ Yearly summary endpoint
5. ✅ Date range summary endpoint
6. ✅ Spending trends endpoint
7. ✅ Comprehensive analytics endpoint

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Percentages don't sum to 100% | Rounding errors - use Decimal for calculations |
| Trends missing dates | Fill in missing dates with 0 values if needed |
| Slow aggregation queries | Ensure indexes on date and user_id columns |
| Division by zero | Check for zero totals before division |
| Date truncation errors | Use proper PostgreSQL date functions |

---

## 🔄 Next Sprint Preview

**Sprint 7: Testing & Quality Assurance**
- Unit tests for all services
- Integration tests for endpoints
- Test coverage > 80%
- Code quality tools
- Performance testing

---

## 📚 Resources

- [SQLAlchemy Aggregations](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#aggregations)
- [PostgreSQL Date Functions](https://www.postgresql.org/docs/current/functions-datetime.html)
- [FastAPI Response Models](https://fastapi.tiangolo.com/tutorial/response-model/)

