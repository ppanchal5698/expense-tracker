# Database Entity Relationship Diagram (ERD)

## 📋 Overview

This document provides a detailed Entity Relationship Diagram and database schema documentation for the Expense Management API.

---

## 🗄️ Entity Relationship Diagram

### Visual ERD (Text Representation)

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                                │
├─────────────────────────────────────────────────────────────┤
│ PK  id                  UUID                                 │
│     email              VARCHAR(255) UNIQUE NOT NULL          │
│     username           VARCHAR(100) UNIQUE NOT NULL          │
│     full_name          VARCHAR(255)                          │
│     hashed_password    VARCHAR(255) NOT NULL                 │
│     is_active          BOOLEAN DEFAULT true                  │
│     is_verified        BOOLEAN DEFAULT false                 │
│     created_at         TIMESTAMP                             │
│     updated_at         TIMESTAMP                             │
└─────────────────────────────────────────────────────────────┘
         │
         │ 1
         │
         │ has many
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      CATEGORIES                              │
├─────────────────────────────────────────────────────────────┤
│ PK  id                  UUID                                 │
│ FK  user_id            UUID → users.id (CASCADE)             │
│     name               VARCHAR(100) NOT NULL                 │
│     description        TEXT                                  │
│     color              VARCHAR(7) DEFAULT '#3182ce'           │
│     icon               VARCHAR(50)                           │
│     is_default         BOOLEAN DEFAULT false                  │
│     created_at         TIMESTAMP                             │
│     updated_at         TIMESTAMP                             │
│                                                              │
│ UNIQUE (user_id, name)                                       │
└─────────────────────────────────────────────────────────────┘
         │
         │ 1
         │
         │ has many
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                       EXPENSES                               │
├─────────────────────────────────────────────────────────────┤
│ PK  id                  UUID                                 │
│ FK  user_id            UUID → users.id (CASCADE)             │
│ FK  category_id        UUID → categories.id (RESTRICT)      │
│     amount             NUMERIC(12,2) NOT NULL                 │
│     description        VARCHAR(255)                          │
│     date               DATE NOT NULL                         │
│     payment_method     VARCHAR(50)                           │
│     tags               VARCHAR(255)[]                        │
│     notes               TEXT                                 │
│     receipt_url         VARCHAR(500)                          │
│     created_at         TIMESTAMP                             │
│     updated_at         TIMESTAMP                             │
│                                                              │
│ CHECK (amount > 0)                                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        BUDGETS                               │
│                    (Optional/Future)                         │
├─────────────────────────────────────────────────────────────┤
│ PK  id                  UUID                                 │
│ FK  user_id            UUID → users.id (CASCADE)             │
│ FK  category_id        UUID → categories.id (CASCADE)       │
│     amount             NUMERIC(12,2) NOT NULL                │
│     period             VARCHAR(20) DEFAULT 'monthly'         │
│     start_date         DATE NOT NULL                         │
│     end_date           DATE                                   │
│     created_at         TIMESTAMP                             │
│     updated_at         TIMESTAMP                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Relationship Details

### User → Categories (One-to-Many)

**Relationship:**
- One User can have many Categories
- Each Category belongs to exactly one User
- **Cascade:** When User is deleted, all Categories are deleted

**Foreign Key:**
```sql
category.user_id → user.id
ON DELETE CASCADE
```

**Index:**
```sql
CREATE INDEX idx_categories_user ON categories(user_id);
```

---

### User → Expenses (One-to-Many)

**Relationship:**
- One User can have many Expenses
- Each Expense belongs to exactly one User
- **Cascade:** When User is deleted, all Expenses are deleted

**Foreign Key:**
```sql
expense.user_id → user.id
ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(user_id, date);
CREATE INDEX idx_expenses_amount ON expenses(user_id, amount);
```

---

### Category → Expenses (One-to-Many)

**Relationship:**
- One Category can have many Expenses
- Each Expense belongs to exactly one Category
- **Restrict:** Cannot delete Category if it has Expenses

**Foreign Key:**
```sql
expense.category_id → category.id
ON DELETE RESTRICT
```

**Index:**
```sql
CREATE INDEX idx_expenses_category ON expenses(category_id);
```

---

### User → Budgets (One-to-Many) [Optional]

**Relationship:**
- One User can have many Budgets
- Each Budget belongs to exactly one User
- **Cascade:** When User is deleted, all Budgets are deleted

**Foreign Key:**
```sql
budget.user_id → user.id
ON DELETE CASCADE
```

---

### Category → Budgets (One-to-Many) [Optional]

**Relationship:**
- One Category can have many Budgets
- Each Budget can belong to one Category (nullable)
- **Cascade:** When Category is deleted, associated Budgets are deleted

**Foreign Key:**
```sql
budget.category_id → category.id
ON DELETE CASCADE
```

---

## 📋 Table Specifications

### users Table

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

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

**Field Descriptions:**
- `id`: Primary key, UUID v4
- `email`: Unique email address for login
- `username`: Unique username
- `full_name`: Optional display name
- `hashed_password`: Bcrypt hashed password
- `is_active`: Account status flag
- `is_verified`: Email verification status
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

---

### categories Table

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3182ce',
    icon VARCHAR(50),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

-- Indexes
CREATE INDEX idx_categories_user ON categories(user_id);
```

**Field Descriptions:**
- `id`: Primary key, UUID v4
- `user_id`: Foreign key to users table
- `name`: Category name (unique per user)
- `description`: Optional category description
- `color`: Hex color code for UI display
- `icon`: Icon identifier (emoji or icon name)
- `is_default`: Flag for system-created categories
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- Unique constraint on `(user_id, name)` - prevents duplicate category names per user

---

### expenses Table

```sql
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    amount NUMERIC(12, 2) NOT NULL,
    description VARCHAR(255),
    date DATE NOT NULL,
    payment_method VARCHAR(50),
    tags VARCHAR(255)[],
    notes TEXT,
    receipt_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (amount > 0)
);

-- Indexes
CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_expenses_date ON expenses(user_id, date);
CREATE INDEX idx_expenses_amount ON expenses(user_id, amount);
```

**Field Descriptions:**
- `id`: Primary key, UUID v4
- `user_id`: Foreign key to users table
- `category_id`: Foreign key to categories table
- `amount`: Expense amount (must be > 0)
- `description`: Optional expense description
- `date`: Date of expense
- `payment_method`: Payment method (cash, card, etc.)
- `tags`: Array of tags for filtering
- `notes`: Optional notes
- `receipt_url`: Optional receipt image URL
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- Check constraint: `amount > 0` - prevents negative or zero amounts
- Foreign key on `category_id` with RESTRICT - prevents deleting category with expenses

---

### budgets Table (Optional)

```sql
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    period VARCHAR(20) DEFAULT 'monthly',
    start_date DATE NOT NULL,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_budgets_user ON budgets(user_id);
```

**Field Descriptions:**
- `id`: Primary key, UUID v4
- `user_id`: Foreign key to users table
- `category_id`: Optional foreign key to categories table
- `amount`: Budget amount
- `period`: Budget period (daily, weekly, monthly, yearly)
- `start_date`: Budget start date
- `end_date`: Optional budget end date
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

---

## 🔍 Index Strategy

### Primary Indexes

**users:**
- `idx_users_email`: Fast email lookups for login
- `idx_users_username`: Fast username lookups

**categories:**
- `idx_categories_user`: Fast category queries by user

**expenses:**
- `idx_expenses_user`: Fast expense queries by user
- `idx_expenses_category`: Fast category-based filtering
- `idx_expenses_date`: Optimized date range queries
- `idx_expenses_amount`: Optimized amount range queries

**budgets:**
- `idx_budgets_user`: Fast budget queries by user

### Composite Indexes

**expenses (user_id, date):**
- Optimizes queries filtering by user and date range
- Supports sorting by date

**expenses (user_id, amount):**
- Optimizes queries filtering by user and amount range

---

## 🔐 Constraints

### Primary Keys
- All tables use UUID v4 as primary keys
- Generated automatically on insert

### Foreign Keys
- All foreign keys have referential integrity
- Cascade deletes for user-owned data
- Restrict deletes for category-expense relationship

### Unique Constraints
- `users.email`: Unique email addresses
- `users.username`: Unique usernames
- `categories(user_id, name)`: Unique category names per user

### Check Constraints
- `expenses.amount > 0`: Prevents invalid amounts

---

## 📈 Data Types

### UUID
- Used for all primary and foreign keys
- Provides globally unique identifiers
- No sequential IDs (privacy benefit)

### NUMERIC(12, 2)
- Used for monetary amounts
- 12 digits total, 2 decimal places
- Prevents floating-point precision issues
- Supports amounts up to 9,999,999,999.99

### VARCHAR
- Variable-length strings
- Appropriate limits for each field
- Prevents excessive storage

### TEXT
- Unlimited length text fields
- Used for descriptions, notes
- No length limit

### ARRAY
- PostgreSQL array type
- Used for tags in expenses
- Enables array operations and filtering

### TIMESTAMP
- Automatic timestamp management
- `created_at`: Set on insert
- `updated_at`: Updated on modification

### DATE
- Date-only values (no time)
- Used for expense dates
- Simpler than TIMESTAMP for date operations

### BOOLEAN
- True/false flags
- Default values specified
- Used for status flags

---

## 🔄 Data Flow Examples

### Creating a User with Default Categories

```
1. Insert User
   └─> users table
       │
       ▼
2. Insert Default Categories (6 categories)
   └─> categories table
       │ user_id = new_user.id
       │ is_default = true
```

### Creating an Expense

```
1. Validate Category
   └─> Check category exists
   └─> Check category.user_id = current_user.id
       │
       ▼
2. Insert Expense
   └─> expenses table
       │ user_id = current_user.id
       │ category_id = validated_category.id
       │ amount = validated_amount
```

### Deleting a Category

```
1. Check for Expenses
   └─> SELECT COUNT(*) FROM expenses WHERE category_id = ?
       │
       ├─> If count > 0: ERROR (RESTRICT constraint)
       │
       └─> If count = 0: DELETE category
```

### Querying Expenses with Filters

```
1. Build Query
   └─> SELECT * FROM expenses
       WHERE user_id = ?
         AND date BETWEEN ? AND ?
         AND category_id = ?
         AND amount BETWEEN ? AND ?
       ORDER BY date DESC
       LIMIT ? OFFSET ?
       │
       ▼
2. Use Indexes
   └─> idx_expenses_date (user_id, date)
   └─> idx_expenses_category (category_id)
   └─> idx_expenses_amount (user_id, amount)
```

---

## 🎯 Design Decisions

### Why UUID Instead of Integer IDs?

**Benefits:**
- Globally unique (no collisions)
- No sequential guessing (security)
- Distributed system friendly
- No ID generation conflicts

**Trade-offs:**
- Slightly larger storage (16 bytes vs 4-8 bytes)
- Slightly slower indexing (but negligible)

### Why CASCADE for User Deletes?

**Rationale:**
- When user deletes account, all their data should be removed
- Ensures data privacy and GDPR compliance
- Simpler than soft deletes for MVP

### Why RESTRICT for Category Deletes?

**Rationale:**
- Prevents accidental data loss
- Forces explicit expense reassignment or deletion
- Maintains data integrity

### Why Composite Indexes?

**Rationale:**
- Most queries filter by user_id + another field
- Composite indexes optimize these common queries
- Reduces index count while improving performance

---

## 📊 Sample Data Relationships

### Example User Structure

```
User: john@example.com
├── Categories (6 default + 2 custom)
│   ├── Food (default)
│   ├── Transport (default)
│   ├── Shopping (default)
│   ├── Bills (default)
│   ├── Entertainment (default)
│   ├── Health (default)
│   ├── Groceries (custom)
│   └── Travel (custom)
│
└── Expenses (150 total)
    ├── Food: 45 expenses
    ├── Transport: 30 expenses
    ├── Shopping: 25 expenses
    ├── Bills: 20 expenses
    ├── Entertainment: 15 expenses
    ├── Health: 10 expenses
    ├── Groceries: 3 expenses
    └── Travel: 2 expenses
```

---

## 🔧 Migration Strategy

### Initial Schema (Sprint 1)

```sql
-- Migration: Initial schema
-- Creates: users, categories, expenses, budgets tables
-- Creates: All indexes
-- Creates: All constraints
```

### Future Migrations

- Add indexes for performance
- Add columns for new features
- Modify constraints as needed
- All tracked via Alembic

---

## 📚 References

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **UUID Best Practices:** https://www.postgresql.org/docs/current/datatype-uuid.html
- **Index Optimization:** https://www.postgresql.org/docs/current/indexes.html

---

**Last Updated:** Project Start
**Status:** Schema Defined ✅

