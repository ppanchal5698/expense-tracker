# Architecture Overview

## 📋 System Architecture

This document provides a comprehensive overview of the Expense Management API architecture, including system design, component interactions, and data flow.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Web App, Mobile App, Postman, cURL)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/REST API
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                        │  │
│  │  - Request Routing                                     │  │
│  │  - Authentication Middleware                          │  │
│  │  - CORS Middleware                                     │  │
│  │  - Exception Handling                                 │  │
│  │  - Request Validation                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   API Routes  │  │   Services   │  │     CRUD     │     │
│  │  (Endpoints)  │→ │  (Business  │→ │  (Database  │     │
│  │               │  │   Logic)    │  │  Operations) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Schemas    │  │   Security   │  │  Exceptions │     │
│  │  (Pydantic)  │  │   (JWT,      │  │   (Custom   │     │
│  │              │  │   Hashing)   │  │   Errors)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SQLAlchemy ORM                           │  │
│  │  - Async Session Management                           │  │
│  │  - Connection Pooling                                 │  │
│  │  - Query Building                                    │  │
│  │  - Relationship Mapping                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Alembic Migrations                            │  │
│  │  - Schema Version Control                            │  │
│  │  - Migration Scripts                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Supabase (PostgreSQL)                         │  │
│  │  - User Data                                          │  │
│  │  - Expenses                                           │  │
│  │  - Categories                                         │  │
│  │  - Indexes & Constraints                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

### Authentication Flow

```
1. Client Request
   └─> POST /api/v1/auth/login
       │
       ▼
2. Auth Endpoint
   └─> AuthService.login_user()
       │
       ├─> Validate credentials
       ├─> Verify password (bcrypt)
       └─> Generate JWT tokens
           │
           ▼
3. Response
   └─> { access_token, refresh_token }
```

### Protected Endpoint Flow

```
1. Client Request
   └─> GET /api/v1/expenses
       │ Headers: Authorization: Bearer <token>
       │
       ▼
2. FastAPI Middleware
   └─> HTTPBearer dependency
       │
       ├─> Extract token
       └─> Verify token (JWT)
           │
           ▼
3. Authentication Dependency
   └─> get_current_user()
       │
       ├─> Decode JWT token
       ├─> Extract user_id
       ├─> Fetch user from DB
       └─> Return User object
           │
           ▼
4. Endpoint Handler
   └─> ExpenseService.list_expenses()
       │
       ├─> Apply filters
       ├─> Query database
       └─> Return results
           │
           ▼
5. Response
   └─> { items: [...], total: 100, page: 1 }
```

---

## 📦 Component Architecture

### Layer 1: API Layer (`app/api/`)

**Responsibility:** HTTP request handling, routing, validation

```
api/
├── v1/
│   ├── endpoints/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User profile endpoints
│   │   ├── categories.py    # Category endpoints
│   │   ├── expenses.py      # Expense endpoints
│   │   └── analytics.py     # Analytics endpoints
│   └── router.py            # Route aggregation
```

**Key Components:**
- FastAPI routers
- Request/response models
- Query parameter validation
- HTTP status codes

---

### Layer 2: Service Layer (`app/services/`)

**Responsibility:** Business logic, orchestration, validation

```
services/
├── auth_service.py          # Authentication logic
├── expense_service.py       # Expense business logic
├── category_service.py      # Category business logic
└── analytics_service.py    # Analytics calculations
```

**Key Responsibilities:**
- Business rule enforcement
- Data transformation
- Cross-cutting concerns
- Error handling

---

### Layer 3: Data Access Layer (`app/crud/`)

**Responsibility:** Database operations, queries

```
crud/
├── base.py                  # Generic CRUD operations
├── user.py                  # User database operations
├── expense.py               # Expense queries
└── category.py              # Category queries
```

**Key Features:**
- Async database operations
- Query building
- Filtering and pagination
- Relationship handling

---

### Layer 4: Data Models (`app/database/`)

**Responsibility:** Database schema, ORM models

```
database/
├── models.py                # SQLAlchemy models
├── connection.py            # Database connection
└── session.py               # Session management
```

**Key Components:**
- SQLAlchemy models
- Relationships
- Indexes
- Constraints

---

### Layer 5: Core Utilities (`app/core/`)

**Responsibility:** Configuration, security, utilities

```
core/
├── config.py                # Application settings
├── security.py              # JWT, password hashing
├── exceptions.py            # Custom exceptions
└── constants.py             # Application constants
```

---

## 🔐 Security Architecture

### Authentication Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. POST /auth/login
       │    { email, password }
       ▼
┌─────────────────────┐
│   Auth Endpoint     │
└──────┬──────────────┘
       │ 2. Validate input
       ▼
┌─────────────────────┐
│   Auth Service      │
└──────┬──────────────┘
       │ 3. Query user by email
       ▼
┌─────────────────────┐
│   Database          │
└──────┬──────────────┘
       │ 4. Return user + hashed_password
       ▼
┌─────────────────────┐
│   Auth Service      │
└──────┬──────────────┘
       │ 5. Verify password (bcrypt)
       │ 6. Generate JWT tokens
       ▼
┌─────────────────────┐
│   JWT Generation    │
│   - access_token    │
│   - refresh_token   │
└──────┬──────────────┘
       │ 7. Return tokens
       ▼
┌─────────────┐
│   Client    │
│  (Stores    │
│   tokens)   │
└─────────────┘
```

### Authorization Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. Request with Bearer token
       ▼
┌─────────────────────┐
│   HTTPBearer        │
│   Dependency        │
└──────┬──────────────┘
       │ 2. Extract token
       ▼
┌─────────────────────┐
│   JWT Verification  │
│   - Decode token    │
│   - Verify signature│
│   - Check expiration│
└──────┬──────────────┘
       │ 3. Extract user_id
       ▼
┌─────────────────────┐
│   Database Query    │
│   - Fetch user       │
│   - Check is_active  │
└──────┬──────────────┘
       │ 4. Return User object
       ▼
┌─────────────────────┐
│   Endpoint Handler  │
│   - Use current_user│
│   - Check ownership │
└─────────────────────┘
```

---

## 💾 Data Flow Architecture

### Create Expense Flow

```
1. Client
   POST /api/v1/expenses
   {
     "amount": 25.50,
     "date": "2024-01-15",
     "category_id": "uuid"
   }
   │
   ▼
2. Expense Endpoint
   - Validate request (Pydantic)
   - Extract current_user
   │
   ▼
3. Expense Service
   - Validate category exists
   - Check category ownership
   - Prepare expense data
   │
   ▼
4. CRUD Expense
   - Create expense record
   - Set user_id
   - Set timestamps
   │
   ▼
5. Database
   - Insert into expenses table
   - Return created record
   │
   ▼
6. Response
   - Serialize to ExpenseResponse
   - Return 201 Created
```

### Query Expenses Flow

```
1. Client
   GET /api/v1/expenses?start_date=2024-01-01&category_id=uuid
   │
   ▼
2. Expense Endpoint
   - Parse query parameters
   - Validate dates
   - Extract current_user
   │
   ▼
3. CRUD Expense
   - Build query with filters
   - Apply date range
   - Apply category filter
   - Apply user_id filter
   - Add pagination
   │
   ▼
4. Database
   - Execute query with indexes
   - Return results + count
   │
   ▼
5. Response
   - Serialize to ExpenseListResponse
   - Include pagination metadata
   - Return 200 OK
```

---

## 🔄 Database Architecture

### Connection Pooling

```
┌─────────────────────┐
│   FastAPI App       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Connection Pool    │
│  (SQLAlchemy)       │
│  - Min: 5           │
│  - Max: 20          │
│  - Overflow: 10     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Supabase          │
│   PostgreSQL        │
│   - Port: 5432      │
│   - Pooler: 6543    │
└─────────────────────┘
```

### Transaction Management

```
Request Start
    │
    ▼
┌─────────────────────┐
│  AsyncSession       │
│  (Context Manager)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Database Operation │
│  - Query            │
│  - Insert           │
│  - Update           │
│  - Delete           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Commit/Rollback    │
│  (Auto on exit)     │
└─────────────────────┘
```

---

## 📊 Analytics Architecture

### Monthly Summary Calculation

```
1. Request
   GET /api/v1/analytics/monthly/2024/1
   │
   ▼
2. Analytics Service
   - Get expenses for month
   │
   ├─> Group by category
   ├─> Sum amounts per category
   ├─> Count expenses per category
   └─> Calculate percentages
       │
       ▼
3. Database Aggregation
   SELECT category_id,
          SUM(amount) as total,
          COUNT(*) as count
   FROM expenses
   WHERE user_id = ?
     AND EXTRACT(year FROM date) = 2024
     AND EXTRACT(month FROM date) = 1
   GROUP BY category_id
   │
   ▼
4. Response
   {
     "year": 2024,
     "month": 1,
     "total_expenses": 1250.50,
     "category_breakdown": [...]
   }
```

---

## 🛡️ Error Handling Architecture

### Exception Flow

```
Request
   │
   ▼
┌─────────────────────┐
│  Endpoint Handler   │
└──────────┬──────────┘
           │
           ├─> Success ──> Response 200/201
           │
           └─> Exception
               │
               ▼
┌─────────────────────┐
│  Exception Handler  │
│  (Middleware)       │
└──────────┬──────────┘
           │
           ├─> ValidationError ──> 422
           ├─> NotFoundError ──> 404
           ├─> UnauthorizedError ──> 401
           ├─> ConflictError ──> 409
           └─> Generic Exception ──> 500
               │
               ▼
┌─────────────────────┐
│  Error Response     │
│  {                  │
│    "detail": "..."  │
│  }                  │
└─────────────────────┘
```

---

## 🔧 Middleware Stack

```
Request
   │
   ▼
┌─────────────────────┐
│  CORS Middleware    │
│  - Check origin     │
│  - Add headers      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Trusted Host       │
│  - Validate host    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Request Logging    │
│  - Log request      │
│  - Track timing     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Exception Handler  │
│  - Catch errors     │
│  - Format response  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Endpoint Handler   │
└─────────────────────┘
```

---

## 📈 Scalability Considerations

### Horizontal Scaling

```
                    ┌─────────────┐
                    │  Load       │
                    │  Balancer   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  FastAPI    │    │  FastAPI    │    │  FastAPI    │
│  Instance 1 │    │  Instance 2 │    │  Instance 3 │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Supabase      │
                 │   PostgreSQL    │
                 │   (Shared DB)   │
                 └─────────────────┘
```

### Database Scaling

- **Connection Pooling:** Manage connections efficiently
- **Read Replicas:** For analytics queries (future)
- **Caching:** Redis for frequently accessed data (future)
- **Indexing:** Optimize query performance

---

## 🔍 Monitoring Architecture

```
┌─────────────────────┐
│   Application       │
└──────────┬──────────┘
           │
           ├─> Health Checks ──> /health, /health/db
           ├─> Request Logs ──> Structured logging
           ├─> Error Tracking ──> Sentry (optional)
           └─> Metrics ──> /metrics endpoint
               │
               ▼
┌─────────────────────┐
│   Monitoring        │
│   - Uptime          │
│   - Response times  │
│   - Error rates    │
│   - Database perf  │
└─────────────────────┘
```

---

## 🚀 Deployment Architecture

### Production Setup

```
┌─────────────────────┐
│   Domain/DNS        │
│   api.example.com   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   HTTPS/SSL         │
│   (Let's Encrypt)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Hosting Platform   │
│   (Railway/Render)   │
│   - Uvicorn workers │
│   - Auto-scaling    │
└──────────┬──────────┘
           │
           ├─> Application ──> FastAPI
           │
           └─> Database ──> Supabase
```

---

## 📚 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API Framework** | FastAPI | REST API framework |
| **Server** | Uvicorn | ASGI server |
| **Database ORM** | SQLAlchemy 2.0 | Async ORM |
| **Database** | PostgreSQL (Supabase) | Data storage |
| **Migrations** | Alembic | Schema versioning |
| **Validation** | Pydantic v2 | Data validation |
| **Authentication** | JWT (python-jose) | Token-based auth |
| **Password Hashing** | bcrypt (passlib) | Secure password storage |
| **Testing** | pytest + pytest-asyncio | Test framework |
| **Code Quality** | Black, Ruff, MyPy | Linting & formatting |

---

## 🔄 Data Relationships

```
User (1) ──< (Many) Categories
  │
  │ (1)
  │
  └──< (Many) Expenses ──> (Many) Categories
```

**Key Relationships:**
- User has many Categories
- User has many Expenses
- Category has many Expenses
- Expense belongs to one Category
- Expense belongs to one User

---

## 🎯 Architecture Principles

1. **Separation of Concerns:** Clear layer boundaries
2. **Dependency Injection:** FastAPI dependencies
3. **Async/Await:** Non-blocking I/O operations
4. **Type Safety:** Type hints throughout
5. **Validation:** Pydantic schemas at boundaries
6. **Error Handling:** Centralized exception handling
7. **Security First:** Authentication and authorization
8. **Performance:** Database indexing and query optimization
9. **Testability:** Testable architecture with dependency injection
10. **Scalability:** Stateless design for horizontal scaling

---

**Last Updated:** Project Start
**Status:** Architecture Defined ✅

