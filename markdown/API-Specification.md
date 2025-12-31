# API Specification Document

## 📋 Overview

Complete API endpoint reference for the Expense Management API. This document provides detailed specifications for all endpoints, request/response formats, and error codes.

---

## 🔐 Authentication

All protected endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## 📍 Base URL

- **Development:** `http://localhost:8000`
- **Production:** `https://api.yourdomain.com`

---

## 🔑 Authentication Endpoints

### POST `/api/v1/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name" // optional
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errors:**
- `409 Conflict` - Email or username already exists
- `422 Validation Error` - Invalid input data

---

### POST `/api/v1/auth/login`

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `422 Validation Error` - Invalid input

---

### POST `/api/v1/auth/refresh`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired refresh token

---

## 👤 User Endpoints

### GET `/api/v1/users/me`

Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### PUT `/api/v1/users/me`

Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "Updated Name", // optional
  "password": "newpassword123"  // optional
}
```

**Response:** `200 OK` (UserResponse)

**Errors:**
- `422 Validation Error` - Invalid input

---

### PUT `/api/v1/users/me/password`

Update user password.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**Response:** `204 No Content`

**Errors:**
- `401 Unauthorized` - Current password incorrect
- `422 Validation Error` - Invalid input

---

### DELETE `/api/v1/users/me`

Delete current user account.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

---

## 📁 Category Endpoints

### POST `/api/v1/categories`

Create a new category.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Groceries",
  "description": "Food shopping", // optional
  "color": "#10b981",            // hex color
  "icon": "🛒"                    // optional
}
```

**Response:** `201 Created` (CategoryResponse)

**Errors:**
- `409 Conflict` - Category name already exists
- `422 Validation Error` - Invalid input

---

### GET `/api/v1/categories`

List all categories for current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 100, max: 100) - Items per page

**Response:** `200 OK`
```json
{
  "total": 10,
  "items": [/* CategoryResponse[] */]
}
```

---

### GET `/api/v1/categories/{category_id}`

Get category by ID.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK` (CategoryResponse)

**Errors:**
- `404 Not Found` - Category not found or not owned by user

---

### PUT `/api/v1/categories/{category_id}`

Update category.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Updated Name",      // optional
  "description": "Updated",    // optional
  "color": "#ef4444",           // optional
  "icon": "🍕"                  // optional
}
```

**Response:** `200 OK` (CategoryResponse)

**Errors:**
- `400 Bad Request` - Cannot modify default category
- `404 Not Found` - Category not found
- `409 Conflict` - Duplicate name

---

### DELETE `/api/v1/categories/{category_id}`

Delete category.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

**Errors:**
- `400 Bad Request` - Category has associated expenses or is default
- `404 Not Found` - Category not found

---

## 💰 Expense Endpoints

### POST `/api/v1/expenses`

Create a new expense.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": "25.50",
  "date": "2024-01-15",
  "category_id": "uuid",
  "description": "Lunch",              // optional
  "payment_method": "card",            // optional: cash, card, transfer, digital_wallet, other
  "tags": ["food", "lunch"],           // optional
  "notes": "Business lunch"             // optional
}
```

**Response:** `201 Created` (ExpenseResponse)

**Errors:**
- `404 Not Found` - Category not found
- `422 Validation Error` - Invalid input

---

### GET `/api/v1/expenses`

List expenses with optional filters.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (int, default: 1, min: 1) - Page number
- `per_page` (int, default: 10, min: 1, max: 100) - Items per page
- `start_date` (date, optional) - Filter start date (YYYY-MM-DD)
- `end_date` (date, optional) - Filter end date (YYYY-MM-DD)
- `category_id` (uuid, optional) - Filter by category
- `min_amount` (decimal, optional) - Minimum amount filter
- `max_amount` (decimal, optional) - Maximum amount filter
- `payment_method` (string, optional) - Filter by payment method
- `tags` (string[], optional) - Filter by tags (comma-separated)

**Response:** `200 OK`
```json
{
  "total": 100,
  "items": [/* ExpenseResponse[] */],
  "page": 1,
  "per_page": 10,
  "total_pages": 10
}
```

**Example:**
```
GET /api/v1/expenses?start_date=2024-01-01&end_date=2024-01-31&category_id=uuid&page=1&per_page=20
```

---

### GET `/api/v1/expenses/{expense_id}`

Get expense by ID.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK` (ExpenseResponse)

**Errors:**
- `404 Not Found` - Expense not found or not owned by user

---

### PUT `/api/v1/expenses/{expense_id}`

Update expense.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": "30.00",           // optional
  "date": "2024-01-16",        // optional
  "category_id": "uuid",        // optional
  "description": "Updated",    // optional
  "payment_method": "cash",     // optional
  "tags": ["updated"],          // optional
  "notes": "Updated notes"      // optional
}
```

**Response:** `200 OK` (ExpenseResponse)

**Errors:**
- `404 Not Found` - Expense or category not found
- `422 Validation Error` - Invalid input

---

### DELETE `/api/v1/expenses/{expense_id}`

Delete expense.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - Expense not found

---

## 📊 Analytics Endpoints

### GET `/api/v1/analytics/monthly/{year}/{month}`

Get monthly expense summary.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `year` (int, 2000-2100)
- `month` (int, 1-12)

**Response:** `200 OK`
```json
{
  "year": 2024,
  "month": 1,
  "total_expenses": "1250.50",
  "expense_count": 45,
  "average_expense": "27.79",
  "category_breakdown": [
    {
      "category_id": "uuid",
      "category_name": "Food",
      "total_amount": "500.00",
      "expense_count": 20,
      "percentage": 40.0
    }
  ],
  "top_category": "Food"
}
```

---

### GET `/api/v1/analytics/yearly/{year}`

Get yearly expense summary.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `year` (int, 2000-2100)

**Response:** `200 OK`
```json
{
  "year": 2024,
  "total_expenses": "15000.00",
  "expense_count": 500,
  "average_monthly_expense": "1250.00",
  "monthly_breakdown": [
    {"month": 1, "total": "1250.50"},
    {"month": 2, "total": "1300.00"}
  ],
  "category_breakdown": [/* CategoryBreakdown[] */]
}
```

---

### GET `/api/v1/analytics/date-range`

Get summary for custom date range.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `start_date` (date, required) - Start date (YYYY-MM-DD)
- `end_date` (date, required) - End date (YYYY-MM-DD)

**Response:** `200 OK`
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "total_expenses": "1250.50",
  "expense_count": 45,
  "average_expense": "27.79",
  "daily_average": "40.34",
  "category_breakdown": [/* CategoryBreakdown[] */]
}
```

**Errors:**
- `400 Bad Request` - Start date after end date

---

### GET `/api/v1/analytics/trends`

Get spending trends over time.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `start_date` (date, required)
- `end_date` (date, required)
- `period` (string, default: "daily") - Options: daily, weekly, monthly

**Response:** `200 OK`
```json
{
  "period": "daily",
  "data_points": [
    {"date": "2024-01-01", "total": 50.00},
    {"date": "2024-01-02", "total": 75.50}
  ]
}
```

---

### GET `/api/v1/analytics/comprehensive`

Get comprehensive analytics with optional trends.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `start_date` (date, required)
- `end_date` (date, required)
- `include_trends` (bool, default: false)
- `period` (string, default: "daily") - If include_trends=true

**Response:** `200 OK`
```json
{
  "summary": {/* DateRangeSummary */},
  "trends": {/* SpendingTrend, if include_trends=true */}
}
```

---

## 🏥 Health & Status Endpoints

### GET `/health`

Application health check.

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

---

### GET `/health/db`

Database connectivity check.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Errors:**
- `503 Service Unavailable` - Database connection failed

---

## 📝 Common Response Formats

### Error Response
```json
{
  "detail": "Error message here"
}
```

### Validation Error Response
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

---

## 🔢 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 204 | No Content | Successful DELETE requests |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Server errors |

---

## 📚 Rate Limiting

Currently no rate limiting implemented. Consider adding:
- Authentication endpoints: 5 requests/minute
- Other endpoints: 100 requests/minute

---

## 🔄 Pagination

List endpoints support pagination:
- `page`: Page number (1-indexed)
- `per_page`: Items per page (default: 10, max: 100)

Response includes:
- `total`: Total number of items
- `items`: Array of items for current page
- `page`: Current page number
- `per_page`: Items per page
- `total_pages`: Total number of pages

---

## 📅 Date Formats

All dates use ISO 8601 format: `YYYY-MM-DD`

Examples:
- `2024-01-15`
- `2024-12-31`

---

## 💱 Amount Formats

All monetary amounts use Decimal with 2 decimal places:
- Valid: `25.50`, `100.00`, `0.99`
- Invalid: `25.5`, `$25.50`, `25,50`

---

## 🔍 Filtering Examples

### Date Range
```
GET /api/v1/expenses?start_date=2024-01-01&end_date=2024-01-31
```

### Category Filter
```
GET /api/v1/expenses?category_id=550e8400-e29b-41d4-a716-446655440000
```

### Amount Range
```
GET /api/v1/expenses?min_amount=10.00&max_amount=100.00
```

### Multiple Filters
```
GET /api/v1/expenses?start_date=2024-01-01&end_date=2024-01-31&category_id=uuid&payment_method=card&page=1&per_page=20
```

---

## 📖 OpenAPI Documentation

Interactive API documentation available at:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

