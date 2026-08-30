# API Router Documentation

## Overview

The router layer provides HTTP endpoints that expose the service layer functionality. All routers follow RESTful conventions with proper status codes, error handling, and consistent response formats.

## Architecture

```
HTTP Requests
    ↓
APIRouter Layer (app/routers/)
├─ books.py
├─ authors.py  
└─ publishers.py
    ↓
Service Layer (app/services/)
    ↓
Database Layer (Motor + MongoDB)
```

## API Base URL

```
http://localhost:8000/api/v1
```

## Books Router (`/api/v1/books`)

### Endpoints

#### 1. List Books
```
GET /books?page=1&limit=10&search=query
```

**Query Parameters:**
- `page` (int, default: 1) - Page number (1-indexed)
- `limit` (int, default: 10) - Items per page (1-100)
- `search` (str, optional) - Search query for title/author

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "1984",
      "author": "George Orwell",
      "pages": 328,
      "publisher": "Penguin",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 50,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 2. Get Single Book
```
GET /books/{book_id}
```

**Path Parameters:**
- `book_id` (str) - MongoDB ObjectId

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "1984",
  "author": "George Orwell",
  "pages": 328,
  "publisher": "Penguin",
  "tags": ["fiction", "dystopian"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- 404 Not Found - Book doesn't exist

#### 3. Create Book
```
POST /books
Content-Type: application/json

{
  "title": "1984",
  "author": "George Orwell",
  "pages": 328,
  "publisher": "Penguin",
  "tags": ["fiction", "dystopian"]
}
```

**Request Body:**
- `title` (str, 1-255 chars) - Book title
- `author` (str, 1-255 chars) - Author name
- `pages` (int, 1-50000) - Number of pages
- `publisher` (str, 1-255 chars) - Publisher name
- `tags` (list, optional, max 10) - Book tags/genres

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "1984",
  "author": "George Orwell",
  "pages": 328,
  "publisher": "Penguin",
  "tags": ["fiction", "dystopian"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- 409 Conflict - Book with same title/author exists
- 422 Unprocessable Entity - Validation error

#### 4. Update Book
```
PATCH /books/{book_id}
Content-Type: application/json

{
  "pages": 330
}
```

**Path Parameters:**
- `book_id` (str) - MongoDB ObjectId

**Request Body (all optional):**
- `title` (str) - New title
- `author` (str) - New author
- `pages` (int) - New page count
- `publisher` (str) - New publisher
- `tags` (list) - New tags

**Response (200 OK):** Updated book

**Errors:**
- 404 Not Found - Book doesn't exist
- 422 Unprocessable Entity - Validation error

#### 5. Delete Book
```
DELETE /books/{book_id}
```

**Response (204 No Content):** Empty

**Errors:**
- 404 Not Found - Book doesn't exist

#### 6. Search Books
```
GET /books/search?query=orwell&page=1&limit=10
```

**Query Parameters:**
- `query` (str, required) - Search query
- `page` (int, default: 1) - Page number
- `limit` (int, default: 10) - Items per page

**Response (200 OK):** Paginated list of matching books

#### 7. Get Books by Author
```
GET /books/author/{author}?page=1&limit=10
```

**Path Parameters:**
- `author` (str) - Author name

**Response (200 OK):** Paginated list of books

#### 8. Get Books by Publisher
```
GET /books/publisher/{publisher}?page=1&limit=10
```

**Path Parameters:**
- `publisher` (str) - Publisher name

**Response (200 OK):** Paginated list of books

#### 9. Get Book Count
```
GET /books/stats/count
```

**Response (200 OK):**
```json
{
  "total": 50
}
```

## Authors Router (`/api/v1/authors`)

### Endpoints

#### 1. List Authors
```
GET /authors
```

**Response (200 OK):**
```json
[
  {
    "id": "orwell_george",
    "name": "George Orwell",
    "birth_date": "1903-06-25",
    "book_count": 5
  }
]
```

#### 2. Get Single Author
```
GET /authors/{author_id}
```

**Response (200 OK):** Author with book count

#### 3. Create Author
```
POST /authors
Content-Type: application/json

{
  "id": "orwell_george",
  "name": "George Orwell",
  "birth_date": "1903-06-25"
}
```

**Response (201 Created):** Created author

#### 4. Update Author
```
PATCH /authors/{author_id}?name=Eric%20Arthur%20Blair&birth_date=1903-06-25
```

**Response (200 OK):** Updated author

#### 5. Delete Author
```
DELETE /authors/{author_id}
```

**Response (204 No Content):** Empty

Note: Deleting author does NOT delete their books

#### 6. Get Author's Books
```
GET /authors/{author_id}/books?page=1&limit=10
```

**Response (200 OK):** Paginated list of books by author

#### 7. Get Author Statistics
```
GET /authors/stats/overview
```

**Response (200 OK):**
```json
{
  "total_authors": 50,
  "average_books_per_author": 3.2,
  "max_books_by_author": 15,
  "min_books_by_author": 1
}
```

## Publishers Router (`/api/v1/publishers`)

### Endpoints

#### 1. Create Publisher
```
POST /publishers?name=Penguin%20Books
```

**Response (201 Created):**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Penguin Books"
}
```

#### 2. List Publishers
```
GET /publishers
```

**Response (200 OK):**
```json
[
  {
    "name": "Penguin",
    "book_count": 52,
    "avg_pages": 287.45,
    "min_pages": 100,
    "max_pages": 500
  }
]
```

#### 3. Get Top Publishers
```
GET /publishers/top?limit=10
```

**Query Parameters:**
- `limit` (int, default: 10) - Number of top publishers

**Response (200 OK):** List of top publishers

#### 4. Get Publisher Average Pages
```
GET /publishers/{publisher_name}/average-pages
```

**Response (200 OK):**
```json
{
  "publisher": "Penguin",
  "average_pages": 287.45
}
```

**Errors:**
- 404 Not Found - No books by publisher

#### 5. Get Publisher Statistics
```
GET /publishers/{publisher_name}/stats
```

**Response (200 OK):**
```json
{
  "publisher_name": "Penguin",
  "total_books": 52,
  "avg_pages": 287.45,
  "min_pages": 100,
  "max_pages": 500,
  "unique_authors_count": 23
}
```

#### 6. Get Publishers by Tag
```
GET /publishers/by-tag/{tag}?limit=10
```

**Path Parameters:**
- `tag` (str) - Book tag/genre

**Query Parameters:**
- `limit` (int, default: 10) - Number of publishers

**Response (200 OK):**
```json
[
  {
    "name": "Penguin",
    "book_count": 30,
    "tag": "fiction"
  }
]
```

#### 7. Get Publishers Overview
```
GET /publishers/overview
```

**Response (200 OK):**
```json
{
  "unique_publishers": 100,
  "total_books": 500,
  "avg_pages": 250.5
}
```

## Status Codes

### Success Codes
- `200 OK` - Successful GET, PATCH, or list operation
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE

### Error Codes
- `400 Bad Request` - Invalid request format
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Duplicate resource or constraint violation
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Common Response Patterns

### Success Response
```json
{
  "id": "...",
  "title": "...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "detail": "Book with ID '507f...' not found"
}
```

### Paginated Response
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 50,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Authentication & Authorization

Currently, no authentication is implemented. All endpoints are publicly accessible.

Future implementation:
- JWT tokens
- API keys
- Role-based access control

## Rate Limiting

Currently, no rate limiting is implemented.

Future implementation:
- Per-IP rate limiting
- Per-user rate limiting
- Configurable limits per endpoint

## CORS

CORS is enabled for all origins. Configuration in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/openapi.json`

## Example Requests

### Using cURL

```bash
# List books
curl http://localhost:8000/api/v1/books

# Create book
curl -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "pages": 328,
    "publisher": "Penguin"
  }'

# Search books
curl http://localhost:8000/api/v1/books/search?query=orwell

# Get publisher stats
curl http://localhost:8000/api/v1/publishers/Penguin/stats
```

### Using Python Requests

```python
import requests

# List authors
response = requests.get('http://localhost:8000/api/v1/authors')
authors = response.json()

# Create book
book_data = {
    "title": "1984",
    "author": "George Orwell",
    "pages": 328,
    "publisher": "Penguin"
}
response = requests.post('http://localhost:8000/api/v1/books', json=book_data)
created_book = response.json()

# Get top publishers
response = requests.get('http://localhost:8000/api/v1/publishers/top?limit=5')
top_pubs = response.json()
```

## Implementation Details

### Dependency Injection

Each router uses FastAPI's dependency injection to get services:

```python
@router.get("")
async def list_books(
    service: BookService = Depends(get_book_service),
):
    return await service.list_books(...)
```

### Error Handling

Custom exceptions are automatically converted to HTTP responses by FastAPI's exception handlers:

```python
# Raises 404 automatically
try:
    book = await service.get_book(book_id)
except BookNotFound:
    # FastAPI converts to 404 response
```

### Logging

All endpoints log operations:

```
INFO: Listed books: page=1, limit=10, search=orwell
INFO: Getting book: 507f...
WARNING: Duplicate book attempted
```

## Statistics

**Total Endpoints**: 24
- Books: 9 endpoints
- Authors: 7 endpoints
- Publishers: 7 endpoints
- Health/Root: 2 endpoints

**Request Methods**:
- GET: 18
- POST: 3
- PATCH: 2
- DELETE: 2

**Status Codes Supported**:
- 200, 201, 204 (success)
- 400, 404, 409, 422, 500 (errors)

---

**Next Phase**: Integration testing and deployment
