# Sprint 1: Database Schema & Models

## 📋 Sprint Overview

**Duration:** 3-4 days
**Objective:** Design and implement complete database schema with SQLAlchemy ORM models and Alembic migrations.

**Success Criteria:**
- ✅ Database schema designed and documented
- ✅ All SQLAlchemy models created
- ✅ Alembic configured for async operations
- ✅ Initial migration created and applied
- ✅ Database relationships properly defined
- ✅ Indexes created for performance
- ✅ All tables created in Supabase

---

## 🎯 Sprint Goals

1. Design complete database schema for expense management
2. Implement SQLAlchemy ORM models with proper relationships
3. Configure Alembic for async database operations
4. Create and apply initial database migration
5. Verify schema integrity and relationships

---

## 📝 Detailed Tasks

### Task 1: Database Schema Design

**Estimated Time:** 2 hours

**Steps:**
1. Review and finalize schema design:
   - `users` table (authentication, profile)
   - `categories` table (expense categories)
   - `expenses` table (expense records)
   - `budgets` table (optional, for future use)

2. Document relationships:
   - User → Categories (one-to-many)
   - User → Expenses (one-to-many)
   - User → Budgets (one-to-many)
   - Category → Expenses (one-to-many)
   - Category → Budgets (one-to-many, optional)

3. Identify required indexes:
   - `users.email` (unique lookup)
   - `users.username` (unique lookup)
   - `categories.user_id` (filtering)
   - `expenses.user_id` (filtering)
   - `expenses.category_id` (filtering)
   - `expenses.date` (date range queries)
   - `expenses.amount` (amount filtering)

**Acceptance Criteria:**
- Schema design documented
- All relationships identified
- Indexes planned for performance

---

### Task 2: Database Connection Setup

**Estimated Time:** 1 hour

**Steps:**
1. Create `app/database/__init__.py`:
   ```python
   from app.database.connection import engine, get_db
   from app.database.models import Base

   __all__ = ["engine", "get_db", "Base"]
   ```

2. Create `app/database/connection.py`:
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from app.core.config import settings

   # Convert postgresql:// to postgresql+asyncpg://
   database_url = settings.DATABASE_URL.replace(
       "postgresql://",
       "postgresql+asyncpg://"
   )

   engine = create_async_engine(
       database_url,
       echo=settings.DEBUG,
       pool_size=settings.DATABASE_POOL_MAX,
       max_overflow=10,
       pool_pre_ping=True,
   )

   AsyncSessionLocal = sessionmaker(
       engine,
       class_=AsyncSession,
       expire_on_commit=False
   )

   async def get_db() -> AsyncSession:
       """Dependency for database session injection"""
       async with AsyncSessionLocal() as session:
           try:
               yield session
           finally:
               await session.close()
   ```

3. Test database connection:
   ```python
   # Create test script: scripts/test_connection.py
   import asyncio
   from app.database.connection import engine

   async def test_connection():
       async with engine.begin() as conn:
           result = await conn.execute("SELECT 1")
           print("✅ Database connection successful!")
           print(result.fetchone())

   if __name__ == "__main__":
       asyncio.run(test_connection())
   ```

**Acceptance Criteria:**
- Database connection module created
- Async engine configured correctly
- Connection test passes

---

### Task 3: SQLAlchemy Models Implementation

**Estimated Time:** 4 hours

**Steps:**
1. Create `app/database/models.py`:

   **Base Model:**
   ```python
   from sqlalchemy.orm import DeclarativeBase
   import uuid

   class Base(DeclarativeBase):
       """Base class for all SQLAlchemy models"""
       pass
   ```

   **User Model:**
   ```python
   from datetime import datetime
   from sqlalchemy import (
       Column, String, Boolean, DateTime, Index
   )
   from sqlalchemy.dialects.postgresql import UUID
   from sqlalchemy.orm import relationship
   from app.database.models import Base

   class User(Base):
       __tablename__ = "users"
       __table_args__ = (
           Index("idx_users_email", "email"),
           Index("idx_users_username", "username"),
       )

       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       email = Column(String(255), unique=True, nullable=False)
       username = Column(String(100), unique=True, nullable=False)
       full_name = Column(String(255))
       hashed_password = Column(String(255), nullable=False)
       is_active = Column(Boolean, default=True)
       is_verified = Column(Boolean, default=False)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

       # Relationships
       categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
       expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")
       budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")
   ```

   **Category Model:**
   ```python
   from sqlalchemy import (
       Column, String, Text, Boolean, DateTime, ForeignKey, Index
   )
   from sqlalchemy.dialects.postgresql import UUID
   from sqlalchemy.orm import relationship

   class Category(Base):
       __tablename__ = "categories"
       __table_args__ = (
           Index("idx_categories_user", "user_id"),
       )

       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
       name = Column(String(100), nullable=False)
       description = Column(Text)
       color = Column(String(7), default="#3182ce")
       icon = Column(String(50))
       is_default = Column(Boolean, default=False)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

       # Relationships
       owner = relationship("User", back_populates="categories")
       expenses = relationship("Expense", back_populates="category")
   ```

   **Expense Model:**
   ```python
   from sqlalchemy import (
       Column, String, Date, DateTime, ForeignKey, Index, ARRAY, Numeric, Text
   )

   class Expense(Base):
       __tablename__ = "expenses"
       __table_args__ = (
           Index("idx_expenses_user", "user_id"),
           Index("idx_expenses_category", "category_id"),
           Index("idx_expenses_date", "user_id", "date"),
           Index("idx_expenses_amount", "user_id", "amount"),
       )

       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
       category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
       amount = Column(Numeric(12, 2), nullable=False)
       description = Column(String(255))
       date = Column(Date, nullable=False)
       payment_method = Column(String(50))
       tags = Column(ARRAY(String(100)))
       notes = Column(Text)
       receipt_url = Column(String(500))
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

       # Relationships
       owner = relationship("User", back_populates="expenses")
       category = relationship("Category", back_populates="expenses")
   ```

   **Budget Model (Optional):**
   ```python
   class Budget(Base):
       __tablename__ = "budgets"
       __table_args__ = (
           Index("idx_budgets_user", "user_id"),
       )

       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
       category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"))
       amount = Column(Numeric(12, 2), nullable=False)
       period = Column(String(20), default="monthly")
       start_date = Column(Date, nullable=False)
       end_date = Column(Date)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

       # Relationships
       owner = relationship("User", back_populates="budgets")
   ```

2. Verify model imports:
   ```python
   # Test script: scripts/test_models.py
   from app.database.models import User, Category, Expense, Budget
   print("✅ All models imported successfully")
   ```

**Acceptance Criteria:**
- All models created with correct fields
- Relationships properly defined
- Indexes added to appropriate columns
- Models can be imported without errors

---

### Task 4: Alembic Configuration for Async

**Estimated Time:** 2 hours

**Steps:**
1. Update `alembic/env.py` for async support:
   ```python
   from logging.config import fileConfig
   from sqlalchemy import pool
   from sqlalchemy.engine import Connection
   from sqlalchemy.ext.asyncio import async_engine_from_config
   from alembic import context
   import asyncio
   from app.core.config import settings
   from app.database.models import Base

   # Import all models for autogenerate
   from app.database.models import User, Category, Expense, Budget

   config = context.config

   # Override sqlalchemy.url with async URL
   database_url = settings.DATABASE_URL.replace(
       "postgresql://",
       "postgresql+asyncpg://"
   )
   config.set_main_option("sqlalchemy.url", database_url)

   if config.config_file_name is not None:
       fileConfig(config.config_file_name)

   target_metadata = Base.metadata

   def run_migrations_offline() -> None:
       url = config.get_main_option("sqlalchemy.url")
       context.configure(
           url=url,
           target_metadata=target_metadata,
           literal_binds=True,
           dialect_opts={"paramstyle": "named"},
       )
       with context.begin_transaction():
           context.run_migrations()

   def do_run_migrations(connection: Connection) -> None:
       context.configure(connection=connection, target_metadata=target_metadata)
       with context.begin_transaction():
           context.run_migrations()

   async def run_async_migrations() -> None:
       connectable = async_engine_from_config(
           config.get_section(config.config_ini_section, {}),
           prefix="sqlalchemy.",
           poolclass=pool.NullPool,
       )
       async with connectable.connect() as connection:
           await connection.run_sync(do_run_migrations)
       await connectable.dispose()

   def run_migrations_online() -> None:
       asyncio.run(run_async_migrations())

   if context.is_offline_mode():
       run_migrations_offline()
   else:
       run_migrations_online()
   ```

2. Update `alembic.ini`:
   ```ini
   [alembic]
   script_location = alembic
   sqlalchemy.url = driver://user:pass@localhost/dbname
   # Note: This will be overridden by env.py
   ```

3. Test Alembic configuration:
   ```bash
   alembic current
   alembic history
   ```

**Acceptance Criteria:**
- Alembic configured for async operations
- All models imported in env.py
- Alembic commands execute without errors

---

### Task 5: Create Initial Migration

**Estimated Time:** 1 hour

**Steps:**
1. Generate initial migration:
   ```bash
   alembic revision --autogenerate -m "Initial schema: users, categories, expenses, budgets"
   ```

2. Review generated migration file in `alembic/versions/`:
   - Verify all tables are included
   - Check indexes are created
   - Verify foreign key constraints
   - Ensure UUID extension is enabled

3. Edit migration if needed:
   ```python
   # Add UUID extension if not auto-generated
   def upgrade():
       op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
       # ... rest of migration
   ```

4. Apply migration:
   ```bash
   alembic upgrade head
   ```

5. Verify tables created:
   ```bash
   # Using DBeaver or psql
   \dt  # List tables
   \d users  # Describe users table
   \d categories
   \d expenses
   ```

**Acceptance Criteria:**
- Migration file generated successfully
- All tables created in database
- Indexes created correctly
- Foreign keys established
- Migration can be applied and rolled back

---

### Task 6: Database Constraints & Validation

**Estimated Time:** 1 hour

**Steps:**
1. Add database-level constraints:
   - Check constraint for `expenses.amount > 0`
   - Unique constraint for `(user_id, name)` in categories
   - Not null constraints where required

2. Update models if needed:
   ```python
   # In Expense model
   from sqlalchemy import CheckConstraint

   __table_args__ = (
       # ... existing indexes
       CheckConstraint('amount > 0', name='check_amount_positive'),
   )
   ```

3. Create new migration for constraints:
   ```bash
   alembic revision --autogenerate -m "Add database constraints"
   alembic upgrade head
   ```

**Acceptance Criteria:**
- All constraints added
- Constraints enforced at database level
- Migration applied successfully

---

### Task 7: Database Seeding Script

**Estimated Time:** 1 hour

**Steps:**
1. Create `scripts/seed_categories.py`:
   ```python
   import asyncio
   from app.database.connection import AsyncSessionLocal
   from app.database.models import Category, User
   from sqlalchemy import select

   DEFAULT_CATEGORIES = [
       {"name": "Food", "color": "#ef4444", "icon": "🍔"},
       {"name": "Transport", "color": "#3b82f6", "icon": "🚗"},
       {"name": "Shopping", "color": "#10b981", "icon": "🛍️"},
       {"name": "Bills", "color": "#f59e0b", "icon": "💳"},
       {"name": "Entertainment", "color": "#8b5cf6", "icon": "🎬"},
       {"name": "Health", "color": "#ec4899", "icon": "🏥"},
   ]

   async def seed_categories():
       async with AsyncSessionLocal() as session:
           # This will be used when users are created
           print("Category seeding script ready")
           print("Default categories defined:", DEFAULT_CATEGORIES)

   if __name__ == "__main__":
       asyncio.run(seed_categories())
   ```

2. Create `scripts/reset_db.py` (development only):
   ```python
   import asyncio
   from alembic.config import Config
   from alembic import command

   async def reset_database():
       alembic_cfg = Config("alembic.ini")
       # Downgrade to base
       command.downgrade(alembic_cfg, "base")
       # Upgrade to head
       command.upgrade(alembic_cfg, "head")
       print("✅ Database reset complete")

   if __name__ == "__main__":
       asyncio.run(reset_database())
   ```

**Acceptance Criteria:**
- Seeding script created
- Reset script created (for development)
- Scripts execute without errors

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] All models can be imported
- [ ] Database connection works
- [ ] All tables created in database
- [ ] Foreign key relationships work
- [ ] Indexes created correctly
- [ ] Constraints enforced
- [ ] Migration can be rolled back and reapplied
- [ ] UUIDs generated correctly

### Verification Commands

```bash
# Check migration status
alembic current
alembic history

# Test database connection
python scripts/test_connection.py

# Verify tables
psql $DATABASE_URL -c "\dt"

# Test model imports
python -c "from app.database.models import User, Category, Expense; print('✅ Models OK')"
```

### Database Verification Queries

```sql
-- Check all tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('users', 'categories', 'expenses');

-- Check foreign keys
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY';
```

---

## 📦 Deliverables

1. ✅ Complete database schema design document
2. ✅ All SQLAlchemy models implemented
3. ✅ Alembic configured for async operations
4. ✅ Initial migration created and applied
5. ✅ Database tables created in Supabase
6. ✅ All relationships and indexes verified
7. ✅ Database seeding scripts created

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Alembic can't detect models | Import all models in `alembic/env.py` |
| UUID extension not found | Add `CREATE EXTENSION IF NOT EXISTS "uuid-ossp"` to migration |
| Async migration errors | Ensure using async_engine_from_config in env.py |
| Foreign key constraint fails | Check ondelete/onupdate settings match requirements |
| Index not created | Verify Index() in __table_args__ |

---

## 🔄 Next Sprint Preview

**Sprint 2: Core Configuration & Security**
- Complete settings management
- JWT token utilities
- Password hashing
- Exception handling
- Middleware setup

---

## 📚 Resources

- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)

