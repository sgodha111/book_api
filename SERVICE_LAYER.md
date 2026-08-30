# Service Layer Documentation

## Overview

The service layer provides business logic and abstracts database operations. Services handle:
- Business logic validation
- Database interactions via dependency injection
- Aggregation queries and complex operations
- Error handling with custom exceptions
- Structured logging

## Architecture

```
┌─────────────────────────────────────────┐
│         API Routes (to be created)      │
│                                         │
│  GET /api/v1/books/{id}                │
│  POST /api/v1/books                    │
│  PATCH /api/v1/books/{id}              │
│  DELETE /api/v1/books/{id}             │
└────────────┬────────────────────────────┘
             │ dependency injection
             ▼
┌─────────────────────────────────────────┐
│         Service Layer                   │
│                                         │
│  ├─ BookService                         │
│  ├─ AuthorService                       │
│  └─ PublisherService                    │
└────────────┬────────────────────────────┘
             │ database operations
             ▼
┌─────────────────────────────────────────┐
│         Database Layer                  │
│                                         │
│  ├─ MongoDB Collections                 │
│  ├─ Aggregation Pipelines               │
│  └─ Index Lookups                       │
└─────────────────────────────────────────┘
```

## Service Descriptions

### BookService

**Location**: `app/services/book_service.py`

**Purpose**: Manages all book-related business logic and database operations.

**Methods**:

| Method | Parameters | Returns | Raises |
|--------|-----------|---------|--------|
| `create_book` | `BookCreate` | `BookResponse` | `DuplicateBook` |
| `get_book` | `book_id: str` | `BookResponse` | `BookNotFound` |
| `list_books` | `PaginationParams, search: str` | `tuple[list[BookList], PaginationMeta]` | None |
| `update_book` | `book_id: str, BookUpdate` | `BookResponse` | `BookNotFound` |
| `delete_book` | `book_id: str` | `bool` | `BookNotFound` |
| `search_books` | `query: str, PaginationParams` | `tuple[list[BookList], PaginationMeta]` | None |
| `count_books` | None | `int` | None |
| `get_books_by_author` | `author: str, PaginationParams` | `tuple[list[BookList], PaginationMeta]` | None |
| `get_books_by_publisher` | `publisher: str, PaginationParams` | `tuple[list[BookList], PaginationMeta]` | None |

**Features**:
- ✅ Automatic duplicate detection before creation
- ✅ Timestamp management (created_at, updated_at)
- ✅ Partial update support (PATCH)
- ✅ Full-text search (title, author, tags)
- ✅ Pagination with metadata
- ✅ Filter by author or publisher
- ✅ Structured logging on all operations

**Usage Example**:
```python
service = BookService(db)

# Create a book
book = await service.create_book(BookCreate(
    title="1984",
    author="George Orwell",
    pages=328,
    publisher="Penguin",
    tags=["fiction", "dystopian"]
))

# List with pagination
books, pagination = await service.list_books(
    PaginationParams(page=1, limit=10),
    search="Orwell"
)

# Update
updated = await service.update_book(
    book.id,
    BookUpdate(pages=330)
)

# Delete
await service.delete_book(book.id)
```

### AuthorService

**Location**: `app/services/author_service.py`

**Purpose**: Manages author data with aggregation queries for computing book counts.

**Methods**:

| Method | Parameters | Returns | Raises |
|--------|-----------|---------|--------|
| `create_author` | `AuthorCreate` | `AuthorResponse` | `DuplicateAuthor` |
| `get_author` | `author_id: str` | `AuthorResponse` | `AuthorNotFound` |
| `list_authors_with_counts` | None | `List[AuthorResponse]` | None |
| `update_author` | `author_id: str, name: str, birth_date` | `AuthorResponse` | `AuthorNotFound` |
| `delete_author` | `author_id: str` | `bool` | `AuthorNotFound` |
| `get_author_stats` | None | `dict` | None |

**Aggregation Queries**:

1. **Book Count Aggregation** (`list_authors_with_counts`)
   - Uses `$lookup` to join with books collection
   - Computes book count per author
   - Returns sorted by author name

2. **Statistics Aggregation** (`get_author_stats`)
   - Computes average books per author
   - Finds max and min books by author
   - Returns statistics dictionary

**Features**:
- ✅ MongoDB aggregation pipeline for efficiency
- ✅ $lookup join with books collection
- ✅ Automatic book count computation
- ✅ Author statistics (avg, min, max books)
- ✅ Structured logging

**Usage Example**:
```python
service = AuthorService(db)

# Create author
author = await service.create_author(AuthorCreate(
    id="orwell_george",
    name="George Orwell",
    birth_date=date(1903, 6, 25)
))

# Get with book count
author = await service.get_author("orwell_george")
# Returns: AuthorResponse with book_count computed from books collection

# List all with counts (single aggregation query)
authors = await service.list_authors_with_counts()
# Efficiently computes counts for all authors

# Get statistics
stats = await service.get_author_stats()
# Returns: {
#   "total_authors": 50,
#   "average_books_per_author": 3.2,
#   "max_books_by_author": 15,
#   "min_books_by_author": 1
# }
```

### PublisherService

**Location**: `app/services/publisher_service.py`

**Purpose**: Manages publisher data with statistical aggregations.

**Methods**:

| Method | Parameters | Returns | Raises |
|--------|-----------|---------|--------|
| `create_publisher` | `name: str` | `dict` | `DatabaseError` |
| `get_publisher_avg_pages` | `publisher_name: str` | `float` | `DatabaseError` |
| `get_all_publishers_with_stats` | None | `List[dict]` | None |
| `get_publisher_stats` | `publisher_name: str` | `dict` | `DatabaseError` |
| `get_top_publishers` | `limit: int = 10` | `List[dict]` | None |
| `get_publisher_by_tag_count` | `tag: str, limit: int = 10` | `List[dict]` | None |

**Aggregation Features**:

1. **Average Pages Query** (`get_publisher_avg_pages`)
   - Computes average pages for publisher's books
   - Returns float rounded to 2 decimals

2. **Complete Statistics** (`get_all_publishers_with_stats`)
   - Groups books by publisher
   - Computes count, avg, min, max pages
   - Sorts by book count descending

3. **Publisher Details** (`get_publisher_stats`)
   - Total books
   - Average/min/max pages
   - Unique authors count

4. **Top Publishers** (`get_top_publishers`)
   - Ranked by book count
   - Includes average pages
   - Configurable limit

5. **Tag-based Search** (`get_publisher_by_tag_count`)
   - Publishers with most books having a tag
   - Useful for genre analysis

**Usage Example**:
```python
service = PublisherService(db)

# Create publisher
pub = await service.create_publisher("Penguin Books")

# Get average pages
avg = await service.get_publisher_avg_pages("Penguin Books")
# Returns: 287.45

# Get top 5 publishers
top = await service.get_top_publishers(limit=5)
# Returns: [
#   {"name": "Penguin", "book_count": 52, "avg_pages": 287.45},
#   {"name": "Oxford", "book_count": 38, "avg_pages": 256.12},
#   ...
# ]

# Get detailed statistics
stats = await service.get_publisher_stats("Penguin Books")
# Returns: {
#   "publisher_name": "Penguin Books",
#   "total_books": 52,
#   "avg_pages": 287.45,
#   "min_pages": 100,
#   "max_pages": 500,
#   "unique_authors_count": 23
# }

# Publishers with fiction books
fiction_pubs = await service.get_publisher_by_tag_count("fiction", limit=10)
```

## Key Design Patterns

### 1. Dependency Injection

All services accept database instance in constructor:

```python
class BookService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["books"]
```

This allows:
- Easy testing with mock databases
- Flexibility in database selection
- Clear dependency graph

### 2. Separation of Concerns

**Repository Layer** (data access):
- Raw database operations
- Duplicate checking
- Basic CRUD

**Service Layer** (business logic):
- Complex queries
- Aggregations
- Statistics
- Business rules
- Error handling

**Route Layer** (HTTP handling):
- Endpoint definitions
- Request/response mapping
- Parameter validation

### 3. Aggregation Pipelines

MongoDB aggregation is used for:
- Efficient multi-stage queries
- Statistical computations
- Joins between collections
- Minimal data transfer

**Example**: Count books by author
```python
pipeline = [
    {
        "$lookup": {
            "from": "books",
            "let": {"author_name": "$name"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$author", "$$author_name"]}}},
                {"$count": "count"}
            ],
            "as": "books"
        }
    },
    {
        "$addFields": {
            "book_count": {
                "$cond": [
                    {"$eq": [{"$size": "$books"}, 0]},
                    0,
                    {"$arrayElemAt": ["$books.count", 0]}
                ]
            }
        }
    }
]
```

## Logging Strategy

All services use structured logging:

```python
self.logger = logging.getLogger(__name__)

# Info level - successful operations
self.logger.info(f"Book created: {result.inserted_id}")

# Debug level - not found / validation
self.logger.debug(f"Book not found: {book_id}")

# Warning level - duplicates / unusual conditions
self.logger.warning(f"Duplicate book attempted: {title}")

# Error level - failures (raised as exceptions)
self.logger.error(f"Database operation failed: {error}")
```

## Error Handling

Services raise custom exceptions:

```python
# Resource not found
raise BookNotFound(book_id)

# Duplicate or constraint violation
raise DuplicateBook("book with this title")

# Database errors
raise DatabaseError("Operation failed")
```

These are caught by FastAPI's exception handlers and converted to HTTP responses.

## Type Safety

All methods have full type hints:

```python
async def create_book(self, book_data: BookCreate) -> BookResponse:
    """Create book."""
    ...

async def list_books(
    self,
    pagination: PaginationParams,
    search: Optional[str] = None,
) -> tuple[list[BookList], PaginationMeta]:
    """List books with pagination."""
    ...
```

## Testing

Services are designed for easy testing:

```python
# Test with mock database
from mongomock_motor import AsyncMongoMockClient

async def test_create_book():
    client = AsyncMongoMockClient()
    db = client["test_db"]
    service = BookService(db)
    
    book = await service.create_book(BookCreate(...))
    assert book.id is not None
    assert book.title == "..."
```

## Performance Considerations

1. **Indexes**: MongoDB automatically creates indexes on:
   - book.title, book.author
   - book.created_at (sort)
   - author._id (primary)
   - publisher.name

2. **Aggregation**: Used for multi-stage computations
   - Computed on server (not in Python)
   - Minimal data transfer
   - Efficient grouping and joining

3. **Pagination**: Limits result sets
   - Max 100 items per page
   - Offset-based (skip/limit)
   - Metadata for navigation

4. **Caching**: Ready for Redis integration
   - Service layer can cache at top level
   - No changes needed to interface

## Statistics

**Total Methods**: 21
- BookService: 9 methods
- AuthorService: 6 methods
- PublisherService: 6 methods

**Aggregation Queries**: 6
- Book count by author
- Author statistics
- Publisher statistics
- Top publishers
- Publisher by tag
- Publisher overview

**Error Types Handled**: 6
- BookNotFound
- InvalidBook
- DuplicateBook
- AuthorNotFound
- DuplicateAuthor
- DatabaseError

**Code Quality**:
- ✅ 100% Type Hints
- ✅ Full Async/Await
- ✅ Comprehensive Logging
- ✅ Custom Exceptions
- ✅ Docstrings
- ✅ Dependency Injection

---

**Next Phase**: Create API routes to expose these services via HTTP endpoints.
