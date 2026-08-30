# FastAPI MongoDB CRUD - Project Structure

## Overview
A production-grade FastAPI application with MongoDB integration, featuring async operations, comprehensive validation, and layered architecture.

## Directory Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization, lifespan, middleware
│   ├── config.py                  # Environment config with Pydantic Settings
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py            # MongoDB connection & initialization
│   │   └── exceptions.py          # Custom HTTP exceptions
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── book.py                # Book Pydantic models
│   │   └── author.py              # Author Pydantic models
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── book.py                # Book CRUD operations
│   │
│   └── utils/
│       ├── __init__.py
│       └── pagination.py          # Pagination utilities
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   └── test_main.py               # Basic tests
│
├── .env.example                   # Environment template
├── .env                           # Local environment (git-ignored)
├── .gitignore                     # Git ignore rules
├── .dockerignore                  # Docker ignore rules
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Docker Compose services
├── README.md                      # Setup & usage guide
└── STRUCTURE.md                   # This file
```

## Key Components

### 1. Configuration (app/config.py)
- Pydantic Settings for environment variables
- Required: `MONGODB_URL`, `DATABASE_NAME`
- Optional: `ENVIRONMENT`, `LOG_LEVEL`, `API_TITLE`, `API_VERSION`
- Validation of required fields at startup

### 2. Database Layer (app/models/database.py)
- **MongoDB Singleton**: Single connection instance across app
- **Async Motor**: AsyncIOMotorClient for non-blocking MongoDB operations
- **Index Creation**: Automatic index creation for common queries
- **Connection Management**: Lifespan integration for startup/shutdown
- **Retry Logic**: Timeout and error handling

Collections:
- `books` - Book documents with indexes on title, author, publisher, created_at, tags
- `authors` - Author documents with unique ID index
- `publishers` - Publisher documents with unique name index

### 3. Schemas (Pydantic Models)

#### Book Schemas (app/schemas/book.py)
- **BookCreate**: For creating new books
  - Fields: title, author, pages, publisher, tags
  - Validation: length constraints, gt/ge, regex patterns
  
- **BookUpdate**: For updating books (all optional)
  - Enables partial updates via PATCH
  
- **BookResponse**: Full book data response
  - Includes: id, timestamps (created_at, updated_at)
  
- **BookList**: Simplified book response for list endpoints
  - Reduces payload size, faster queries

#### Author Schemas (app/schemas/author.py)
- **AuthorCreate**: Creating authors
  - Fields: id (unique), name, birth_date (optional)
  
- **AuthorResponse**: Author with aggregated data
  - Includes: book_count (computed from books collection)

### 4. Exception Handling (app/models/exceptions.py)
Custom HTTP exceptions with proper status codes:
- `BookNotFound` (404) - Resource not found
- `InvalidBook` (400) - Bad request/validation
- `DuplicateBook` (409) - Conflict/duplicate
- `AuthorNotFound` (404)
- `DuplicateAuthor` (409)
- `DatabaseError` (500) - Internal server error

### 5. Repository Pattern (app/repositories/book.py)
Data access layer with business logic:
- `create()` - Create with duplicate checking
- `get_by_id()` - Fetch single book
- `list_all()` - Paginated listing with optional search
- `update()` - Partial updates with timestamp
- `delete()` - Remove book
- `count()` - Count with filter
- `search()` - Full-text search by title/author/tags

### 6. Pagination (app/utils/pagination.py)
- **PaginationParams**: Page and limit with validation
- **PaginationMeta**: Metadata with has_next, has_prev
- **PaginatedResponse**: Generic response wrapper
- **paginate_query()**: Database query helper

Features:
- Offset calculation: `skip = (page - 1) * limit`
- Total pages computation
- has_next/has_prev flags
- Type-safe with generics

## API Endpoints (To Be Implemented)

### Root & Health
- `GET /` - Welcome endpoint
- `GET /health` - Health check with DB status

### Books (CRUD)
- `GET /api/v1/books` - List all books (paginated, searchable)
- `POST /api/v1/books` - Create new book
- `GET /api/v1/books/{book_id}` - Get single book
- `PATCH /api/v1/books/{book_id}` - Update book
- `DELETE /api/v1/books/{book_id}` - Delete book

### Authors
- `GET /api/v1/authors` - List authors
- `POST /api/v1/authors` - Create author
- `GET /api/v1/authors/{author_id}` - Get author with book count

### Search & Analytics (Future)
- `GET /api/v1/search` - Global search
- `GET /api/v1/analytics` - Statistics

## Data Models

### Book Document (MongoDB)
```json
{
  "_id": ObjectId("..."),
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "pages": 180,
  "publisher": "Scribner",
  "tags": ["fiction", "classic"],
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z")
}
```

### Author Document (MongoDB)
```json
{
  "_id": "fitzgerald_f_scott",
  "name": "F. Scott Fitzgerald",
  "birth_date": ISODate("1896-09-24T00:00:00Z")
}
```

## Testing

### Test Structure
- `tests/conftest.py` - Pytest fixtures, app factory, mock DB
- `tests/test_main.py` - Basic endpoint tests
- Ready for: repository tests, integration tests, e2e tests

### Running Tests
```bash
# All tests
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_main.py::test_root_endpoint
```

## Deployment

### Docker Build
```bash
docker build -t fastapi-mongodb:latest .
```

### Docker Compose
```bash
docker-compose up
```

### Production Checklist
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure proper `LOG_LEVEL` (INFO or WARNING)
- [ ] Use environment variables, not .env file
- [ ] Enable HTTPS (nginx reverse proxy)
- [ ] Setup MongoDB replica set
- [ ] Configure database backups
- [ ] Setup monitoring & logging aggregation
- [ ] Configure rate limiting
- [ ] Setup API key authentication

## Code Quality

### Type Hints
All code uses full type hints:
- Function parameters and returns
- Database operations
- Pydantic models
- Generic types for repositories

### Validation
- Pydantic for all request/response models
- MongoDB schema validation
- Field constraints (length, range, regex)
- Custom validators for complex logic

### Error Handling
- Custom exceptions for domain errors
- Proper HTTP status codes
- Detailed error messages
- Logging at appropriate levels

### Database Design
- Proper indexes for common queries
- Atomic operations where possible
- Transaction support (MongoDB 4.0+)
- Consistent timestamps (UTC)

## Next Steps

1. **Implement Routes** - Create `app/routes/books.py` and `app/routes/authors.py`
2. **Add Authentication** - JWT tokens, API keys
3. **Add Validation** - Server-side uniqueness constraints
4. **Add Logging Middleware** - Request/response logging
5. **Add Rate Limiting** - Prevent abuse
6. **Add Caching** - Redis for frequently accessed data
7. **Add Monitoring** - Prometheus metrics
8. **Setup CI/CD** - GitHub Actions, tests, linting
9. **API Documentation** - Add detailed docstrings
10. **Performance Testing** - Load testing, benchmarks

## Configuration Reference

### Environment Variables
```bash
# Required
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=books_db

# Optional
ENVIRONMENT=development                    # development, staging, production
LOG_LEVEL=INFO                            # DEBUG, INFO, WARNING, ERROR, CRITICAL
API_TITLE=FastAPI MongoDB CRUD
API_VERSION=1.0.0
```

### Pydantic Validation Examples
```python
# String constraints
Field(..., min_length=1, max_length=255)

# Numeric constraints
Field(..., gt=0, le=50000)          # > 0 and <= 50000
Field(..., ge=1, le=100)            # >= 1 and <= 100

# List constraints
Field(default_factory=list, max_length=10)

# Optional fields
Optional[str] = Field(None, description="...")

# Pattern matching
Field(..., regex="^[a-zA-Z0-9_-]+$")
```

## Database Performance Tips

1. **Indexing**: Indexes created automatically on:
   - Frequently queried fields (title, author)
   - Sort fields (created_at)
   - Filter fields (publisher)

2. **Query Optimization**:
   - Use pagination for large result sets
   - Use projection to fetch only needed fields
   - Use aggregation pipeline for complex queries

3. **Concurrency**:
   - Async operations prevent blocking
   - Connection pooling (Motor handles this)
   - Multiple concurrent queries supported

## License
MIT
