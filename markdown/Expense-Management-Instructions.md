# Grok Project: Expense Management API
## FastAPI + Supabase + SQLAlchemy + Pydantic

**Project Scope:** Build a production-grade REST API for expense tracking with user authentication, category management, and financial analytics.

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Setup Instructions](#setup-instructions)
6. [Database Schema](#database-schema)
7. [Core Implementation](#core-implementation)
8. [API Endpoints](#api-endpoints)
9. [Development Workflow](#development-workflow)
10. [Deployment Checklist](#deployment-checklist)

---

## 🎯 PROJECT OVERVIEW

### Features to Implement
- **User Management**: Registration, authentication (JWT), profile management
- **Expense Tracking**: Create, read, update, delete expenses with timestamps
- **Categories**: Predefined and custom expense categories per user
- **Analytics**: Monthly spending summaries, category breakdown, trends
- **Filtering**: Query by date range, category, amount range, tags
- **Data Validation**: Strict input validation using Pydantic v2
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes

### Success Metrics
- ✅ All CRUD operations working with zero data inconsistencies
- ✅ Response times < 200ms for 95th percentile queries
- ✅ Full test coverage for business logic (>80%)
- ✅ Auto-generated OpenAPI documentation
- ✅ Database migrations tracked with Alembic

---

## 🛠️ TECH STACK

| Component | Tool | Version | Purpose |
|-----------|------|---------|---------|
| **Framework** | FastAPI | ^0.104.0 | Modern async Python web framework |
| **Database** | Supabase (PostgreSQL) | Latest | Cloud-hosted PostgreSQL with real-time features |
| **ORM** | SQLAlchemy | ^2.0.0 | Object-relational mapping with async support |
| **Data Validation** | Pydantic | ^2.0.0 | Type checking, serialization, validation |
| **Migrations** | Alembic | ^1.13.0 | Database schema version control |
| **Server** | Uvicorn | ^0.24.0 | ASGI server for running FastAPI |
| **Auth** | Python-jose + passlib | Latest | JWT tokens and password hashing |
| **Environment** | python-dotenv | ^1.0.0 | Environment variable management |
| **Testing** | pytest + pytest-asyncio | Latest | Unit and integration tests |

---

## 📦 PREREQUISITES

### System Requirements
- Python 3.10+ (3.11+ recommended for your ML engineering work)
- PostgreSQL 14+ (via Supabase)
- pip or Poetry (for dependency management)
- Git for version control

### External Accounts
1. **Supabase Account** (free tier sufficient for development)
   - Sign up at https://supabase.com
   - Create a new project
   - Note your database credentials and connection string

2. **Environment Setup Tools**
   - VS Code with Python extension (you already use this)
   - Postman or Insomnia for API testing
   - DBeaver for database inspection

---

## 📁 PROJECT STRUCTURE

```
expense-management-api/
├── .env.example                 # Template for environment variables
├── .env                         # Local environment (git-ignored)
├── .gitignore                   # Git configuration
├── pyproject.toml               # Poetry/pip dependencies (preferred)
├── requirements.txt             # pip dependencies
├── README.md                    # Project documentation
│
├── alembic/                     # Database migrations
│   ├── versions/                # Migration scripts
│   ├── env.py                   # Migration environment config
│   └── alembic.ini              # Alembic configuration
│
├── app/
│   ├── __init__.py              # Package marker
│   ├── main.py                  # FastAPI app initialization
│   ├── settings.py              # Environment & config management
│   ├── dependencies.py          # FastAPI dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/       # Route handlers (by resource)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py      # Login, register, refresh token
│   │   │   │   ├── expenses.py  # CRUD for expenses
│   │   │   │   ├── categories.py# Category management
│   │   │   │   ├── analytics.py # Reports & insights
│   │   │   │   └── users.py     # User profile endpoints
│   │   │   └── router.py        # Route aggregation
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # App configuration & validation
│   │   ├── security.py          # JWT, password hashing, token logic
│   │   ├── constants.py         # Application constants, enums
│   │   └── exceptions.py        # Custom exception classes
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        # Database connection management
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── session.py           # Async session factory
│   │
│   ├── schemas/                 # Pydantic models for validation
│   │   ├── __init__.py
│   │   ├── base.py              # Base schemas with common fields
│   │   ├── user.py              # User request/response schemas
│   │   ├── expense.py           # Expense schemas (Create, Read, Update)
│   │   ├── category.py          # Category schemas
│   │   └── analytics.py         # Analytics response schemas
│   │
│   ├── crud/                    # Database operations (Create, Read, Update, Delete)
│   │   ├── __init__.py
│   │   ├── base.py              # Generic CRUD operations
│   │   ├── user.py              # User-specific DB operations
│   │   ├── expense.py           # Expense CRUD with filters
│   │   └── category.py          # Category CRUD
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── expense_service.py   # Expense calculations, validations
│   │   └── analytics_service.py # Analytics calculations
│   │
│   └── middleware/              # Custom middleware
│       ├── __init__.py
│       └── error_handler.py     # Global exception handling
│
├── tests/                       # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & setup
│   ├── test_auth.py             # Authentication tests
│   ├── test_expenses.py         # Expense CRUD tests
│   ├── test_categories.py       # Category tests
│   └── test_analytics.py        # Analytics tests
│
├── scripts/                     # Utility scripts
│   ├── create_db.py             # Initialize database
│   ├── seed_categories.py       # Seed default categories
│   └── reset_db.py              # Full database reset (dev only)
│
└── docker/                      # Containerization (optional)
    ├── Dockerfile
    └── docker-compose.yml

```

---

## 🚀 SETUP INSTRUCTIONS

### Step 1: Clone and Initialize

```bash
# Create project directory
mkdir expense-management-api
cd expense-management-api

# Initialize git
git init

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create pyproject.toml for Poetry (recommended for ML engineers)
poetry init  # Or use requirements.txt (step below)
```

### Step 2: Install Dependencies

**Option A: Using Poetry (Recommended)**

```bash
cat > pyproject.toml << 'EOF'
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
asyncpg = "^0.29.0"  # PostgreSQL async driver
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
EOF

poetry install
```

**Option B: Using pip**

```bash
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.13.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
EOF

pip install -r requirements.txt
```

### Step 3: Supabase Setup

1. **Create Supabase Project**
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Choose region (e.g., us-east-1)
   - Set strong database password
   - Wait for project to initialize

2. **Get Connection String**
   - Navigate to Project Settings → Database
   - Copy the connection string
   - Note: Use connection pooler (port 6543) for better performance in production

3. **Create `.env` file**

```bash
cat > .env << 'EOF'
# Environment
ENV=development
DEBUG=true

# Supabase Database
DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/postgres
DATABASE_POOL_MIN=1
DATABASE_POOL_MAX=20
DATABASE_TIMEOUT=30

# JWT Security
SECRET_KEY=$(openssl rand -hex 32)  # Generate random key
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
EOF

# Generate SECRET_KEY manually or with:
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Initialize Database with Alembic

```bash
# Initialize Alembic in your project
alembic init alembic

# Update alembic/env.py to use async
# (See Database Schema section for details)

# Create initial migration (empty)
alembic revision --autogenerate -m "Initial schema"

# Apply migration to create tables
alembic upgrade head
```

### Step 5: Verify Setup

```bash
# Create main.py and run server
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("✅ App starting...")
    yield
    # Shutdown
    print("🛑 App shutting down...")

app = FastAPI(title="Expense API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Test server
python app/main.py
# Should see: "Uvicorn running on http://127.0.0.1:8000"
# Visit http://localhost:8000/docs for OpenAPI documentation
```

---

## 🗄️ DATABASE SCHEMA

### Core Tables

#### 1. `users` Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### 2. `categories` Table

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3182ce',  -- Hex color for UI
    icon VARCHAR(50),  -- Icon name (emoji or icon library)
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

CREATE INDEX idx_categories_user ON categories(user_id);
```

#### 3. `expenses` Table

```sql
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    description VARCHAR(255),
    date DATE NOT NULL,
    payment_method VARCHAR(50),  -- cash, card, transfer, etc.
    tags VARCHAR(255)[],  -- Array of tags for filtering
    notes TEXT,
    receipt_url VARCHAR(500),  -- Optional receipt image
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_expenses_date ON expenses(user_id, date);
CREATE INDEX idx_expenses_amount ON expenses(user_id, amount);
```

#### 4. `budgets` Table (Optional)

```sql
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    period VARCHAR(20) DEFAULT 'monthly',  -- daily, weekly, monthly, yearly
    start_date DATE NOT NULL,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budgets_user ON budgets(user_id);
```

### SQLAlchemy Models

**`app/database/models.py`**

```python
from datetime import datetime
from typing import List
from sqlalchemy import (
    Column, String, Float, Date, DateTime, Boolean, 
    ForeignKey, Index, ARRAY, Numeric, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

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

---

## 💻 CORE IMPLEMENTATION

### 1. Settings & Configuration

**`app/core/config.py`**

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

### 2. Database Connection

**`app/database/connection.py`**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Async engine for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_MAX,
    max_overflow=10,
    pool_pre_ping=True,  # Test connections before use
    # Use NullPool for Supabase connection pooler to avoid session conflicts
    # Uncomment if using Supabase connection pooler:
    # poolclass=NullPool,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """Dependency for database session injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 3. Security & Authentication

**`app/core/security.py`**

```python
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and extract payload"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

### 4. Pydantic Schemas

**`app/schemas/user.py`**

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}  # For SQLAlchemy compatibility

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

**`app/schemas/expense.py`**

```python
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

class ExpenseBase(BaseModel):
    description: Optional[str] = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    date: date
    payment_method: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    category_id: UUID

class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    date: Optional[date] = None
    category_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    id: UUID
    user_id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class ExpenseListResponse(BaseModel):
    total: int
    items: List[ExpenseResponse]
    page: int
    per_page: int
```

### 5. CRUD Operations

**`app/crud/base.py`**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import TypeVar, Generic, Type, Optional, List, Any
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
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10
    ) -> tuple[List[T], int]:
        # Count total
        count_query = select(func.count()).select_from(self.model)
        total = await db.scalar(count_query)
        
        # Fetch items
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        return items, total
    
    async def update(self, db: AsyncSession, id: UUID, obj_in: dict) -> Optional[T]:
        db_obj = await self.get(db, id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
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

**`app/crud/expense.py`**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List
from uuid import UUID
from datetime import date
from decimal import Decimal
from app.database.models import Expense
from app.crud.base import CRUDBase

class CRUDExpense(CRUDBase[Expense]):
    async def get_by_user_and_date_range(
        self,
        db: AsyncSession,
        user_id: UUID,
        start_date: date,
        end_date: date,
        category_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Expense], int]:
        query = select(Expense).where(
            and_(
                Expense.user_id == user_id,
                Expense.date.between(start_date, end_date)
            )
        )
        
        if category_id:
            query = query.where(Expense.category_id == category_id)
        
        # Count total
        count_result = await db.execute(
            select(func.count()).select_from(Expense).where(
                and_(
                    Expense.user_id == user_id,
                    Expense.date.between(start_date, end_date)
                )
            )
        )
        total = count_result.scalar()
        
        # Fetch items
        query = query.order_by(Expense.date.desc()).offset(skip).limit(limit)
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
        query = select(
            Expense.category_id,
            func.sum(Expense.amount).label("total")
        ).where(
            and_(
                Expense.user_id == user_id,
                func.extract("year", Expense.date) == year,
                func.extract("month", Expense.date) == month
            )
        ).group_by(Expense.category_id)
        
        result = await db.execute(query)
        return result.all()

crud_expense = CRUDExpense(Expense)
```

---

## 🔌 API ENDPOINTS

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/login` | User login (returns tokens) |
| POST | `/api/v1/auth/refresh` | Refresh access token |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PUT | `/api/v1/users/me` | Update user profile |
| DELETE | `/api/v1/users/me` | Delete account |

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/expenses` | Create expense |
| GET | `/api/v1/expenses` | List expenses (with filters) |
| GET | `/api/v1/expenses/{id}` | Get single expense |
| PUT | `/api/v1/expenses/{id}` | Update expense |
| DELETE | `/api/v1/expenses/{id}` | Delete expense |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/categories` | Create category |
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/categories/{id}` | Get category |
| PUT | `/api/v1/categories/{id}` | Update category |
| DELETE | `/api/v1/categories/{id}` | Delete category |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/monthly/{year}/{month}` | Monthly summary |
| GET | `/api/v1/analytics/yearly/{year}` | Yearly summary |
| GET | `/api/v1/analytics/category-breakdown` | Category breakdown |

---

## 🔄 DEVELOPMENT WORKFLOW

### 1. Running the Server

```bash
# Development mode with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Visit API docs:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### 2. Database Migrations with Alembic

```bash
# Create a new migration
alembic revision --autogenerate -m "Add expense table"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### 3. Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_expenses.py

# Run with coverage
pytest --cov=app tests/
```

### 4. Code Quality

```bash
# Format code with Black
black app/

# Lint with Ruff
ruff check app/

# Type checking with Mypy (optional)
mypy app/
```

---

## ✅ DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] All tests passing (pytest coverage > 80%)
- [ ] No hardcoded secrets in code
- [ ] Environment variables documented in `.env.example`
- [ ] Database migrations applied successfully
- [ ] API documentation complete (OpenAPI/Swagger)
- [ ] Error handling covers edge cases
- [ ] Rate limiting configured (optional)
- [ ] CORS properly configured for production domain

### Environment Configuration

```bash
# Production .env template
ENV=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
SECRET_KEY=<generate-secure-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Deployment Platforms (Recommended for You)

1. **Railway** (simplest for FastAPI)
   ```bash
   railway init
   railway up
   ```

2. **AWS EC2 + Gunicorn**
   ```bash
   gunicorn "app.main:app" -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Docker + Cloud Run**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

---

## 📚 ADDITIONAL RESOURCES

### Essential Reading
1. **FastAPI Best Practices**: https://github.com/zhanymkanov/fastapi-best-practices
2. **SQLAlchemy 2.0 Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
3. **Pydantic v2 Migration**: https://docs.pydantic.dev/latest/migration/
4. **Supabase with FastAPI**: https://supabase.com/docs/guides/integrations/python

### Tools You'll Use
- **VS Code Extensions**: SQLTools (database), REST Client (API testing)
- **Database Client**: DBeaver for schema visualization
- **API Testing**: Postman collections for endpoint testing
- **Monitoring**: (optional) Sentry for error tracking

---

## 🚨 COMMON PITFALLS & SOLUTIONS

| Issue | Cause | Solution |
|-------|-------|----------|
| "Pool size exceeded" | Too many concurrent connections | Use connection pooler (port 6543 in Supabase) |
| Slow queries | Missing indexes | Add indexes on frequently queried columns |
| JWT token not validating | Secret key mismatch | Ensure `SECRET_KEY` is same across requests |
| Pydantic validation errors | Model mismatch | Use `from_attributes=True` for ORM models |
| Alembic can't detect changes | Missing imports | Import all models in `alembic/env.py` |

---

## 🎓 NEXT STEPS

1. **Phase 1**: Implement basic CRUD for users and expenses
2. **Phase 2**: Add authentication, JWT, and authorization
3. **Phase 3**: Build analytics endpoints with aggregations
4. **Phase 4**: Add filtering, pagination, and search
5. **Phase 5**: Deploy to production platform
6. **Phase 6**: Add frontend (React) integration
7. **Phase 7**: Implement real-time updates (WebSockets - optional)

---

**Good luck with your Grok project! This API foundation will scale well as you add more features.**
