# Architecture Visual Guide

## 1️⃣ THREE-TIER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Browse     │  │  Add Book    │  │  Analytics   │     │
│  │   Books      │  │   Form       │  │  Dashboard   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│              STREAMLIT FRONTEND (Port 8501)               │
│              HTTP Requests via REST API                   │
└────────────────────────┬────────────────────────────────────┘
                         │
         HTTP / JSON Communication (Port 8000)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  APPLICATION TIER                           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend                                    │  │
│  │  ├─ Routers (Books, Authors, Publishers)           │  │
│  │  ├─ Services (Business Logic)                       │  │
│  │  ├─ Repositories (Data Access)                      │  │
│  │  ├─ Schemas (Validation)                            │  │
│  │  └─ Middleware (Logging, Rate Limiting)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  REST Endpoints, Async Processing, Error Handling          │
└────────────────────────┬────────────────────────────────────┘
                         │
         MongoDB Driver (Motor) - Async
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    DATA TIER                                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MongoDB Database (Port 27017)                      │  │
│  │  ├─ Database: fastapi_db                            │  │
│  │  ├─ Collections: books, authors, publishers         │  │
│  │  ├─ Indexes: text search, range queries             │  │
│  │  └─ Persistence: Volumes (mongo_data)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Document Storage, Aggregation Pipelines, Indexing         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ COMPONENT BREAKDOWN

### FRONTEND LAYER (Streamlit)

```
streamlit_app.py (500+ lines)
├── Page Configuration
│   ├── Title: "Books Catalog"
│   ├── Layout: Wide
│   └── Icon: 📚
│
├── Custom Styling
│   ├── CSS (gradient header, cards)
│   ├── Colors (primary blue #1f77b4)
│   └── Responsive design
│
├── Navigation Tabs
│   ├── 📖 Browse Books
│   │   ├── Card-based display
│   │   ├── Sidebar filters
│   │   ├── Pagination
│   │   └── Edit/Delete buttons
│   │
│   ├── ➕ Add Book
│   │   ├── Form fields
│   │   ├── Two-column layout
│   │   ├── Validation
│   │   └── Submit button
│   │
│   ├── 🔍 Search
│   │   ├── Text input
│   │   ├── Real-time results
│   │   └── Result cards
│   │
│   └── 📊 Analytics
│       ├── KPI metrics
│       ├── Charts (Plotly)
│       ├── Statistics tables
│       └── Collection info
│
└── Utility Functions
    ├── API Communication
    ├── Data Formatting
    ├── State Management
    └── Event Handlers

     ↓ HTTP GET/POST/PUT/DELETE ↓

API_BASE_URL = "http://localhost:8000"
```

### BACKEND LAYER (FastAPI)

```
app/main.py
├── FastAPI Instance
├── CORS Configuration
├── Middleware Setup
├── Router Registration
├── Error Handlers
└── Startup/Shutdown

     ↓ All Requests Flow Through ↓

Middleware Chain:
├── RequestLoggingMiddleware
│   └─ Logs all requests/responses as JSON
│
└── RateLimitMiddleware
    └─ Enforces 100 requests/minute per IP

     ↓ Route Matching ↓

app/routers/books.py (365 lines)
├── GET /api/v1/books → list_books()
│   ├─ Filters (author, publisher, tags, pages)
│   ├─ Sorting (created_at, title, pages)
│   ├─ Pagination (page, limit)
│   └─ Returns: PaginatedResponse[List[BookList]]
│
├── GET /api/v1/books/stats → get_book_stats()
│   ├─ Aggregation pipeline
│   └─ Returns: Statistics object
│
├── GET /api/v1/books/search → search_books()
│   ├─ Full-text search
│   └─ Returns: List[BookResponse]
│
├── GET /api/v1/books/{id} → get_book()
│   └─ Returns: BookResponse
│
├── POST /api/v1/books → create_book()
│   ├─ Validates BookCreate schema
│   └─ Returns: BookResponse (201)
│
├── PUT /api/v1/books/{id} → update_book()
│   ├─ Validates BookUpdate schema
│   └─ Returns: BookResponse
│
└── DELETE /api/v1/books/{id} → delete_book()
    └─ Returns: 204 No Content

     ↓ Dependency Injection ↓

get_book_service(db=Depends(get_db)) → BookService

     ↓ Service Layer ↓

app/services/book_service.py
├── BookService Class
├── Business Logic
├── Validation
├── Error Handling
└── Database Operations

     ↓ Repository Pattern ↓

app/repositories/book.py
├── BookRepository Class
├── Query Building
├── Database Calls (Motor)
└── Result Mapping

     ↓ Schemas (Pydantic) ↓

app/schemas/book.py
├── BookCreate (POST body)
├── BookUpdate (PUT body)
├── BookResponse (JSON response)
└── Validation Rules
```

### DATABASE LAYER (MongoDB)

```
MongoDB Instance (fastapi_db)
│
├── Collections:
│   │
│   ├── books
│   │   ├── Document Example:
│   │   │   {
│   │   │     "_id": ObjectId("..."),
│   │   │     "title": "1984",
│   │   │     "author": "George Orwell",
│   │   │     "publisher": "Penguin Books",
│   │   │     "pages": 328,
│   │   │     "tags": ["fiction", "dystopian"],
│   │   │     "created_at": ISODate("..."),
│   │   │     "updated_at": ISODate("...")
│   │   │   }
│   │   │
│   │   └── Indexes:
│   │       ├── "title" (text search)
│   │       ├── "author" (text search)
│   │       ├── "publisher" (text search)
│   │       ├── "tags" (array index)
│   │       └── "created_at" (sort)
│   │
│   ├── authors
│   │   └── Similar structure
│   │
│   └── publishers
│       └── Similar structure
│
├── Persistence:
│   ├── Volume: mongo_data (/data/db)
│   ├── Survives: Container restarts
│   └── Shared: Via Docker volume
│
└── Queries:
    ├── Simple: db.books.findOne({ _id: ... })
    ├── Range: db.books.find({ pages: { $gte: 100 } })
    ├── Text: db.books.find({ $text: { $search: "..." } })
    ├── Array: db.books.find({ tags: { $in: [...] } })
    └── Aggregation: db.books.aggregate([...])
```

---

## 3️⃣ DATA FLOW EXAMPLES

### Example 1: Add a Book

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (Streamlit)                                        │
│ User fills form and clicks "Add Book"                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ POST /api/v1/books
                       │ Content-Type: application/json
                       │ Body: {
                       │   "title": "1984",
                       │   "author": "George Orwell",
                       │   "publisher": "Penguin",
                       │   "pages": 328,
                       │   "tags": ["fiction", "dystopian"]
                       │ }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND (FastAPI)                                           │
│                                                             │
│ 1. Route: @router.post("")                                 │
│    ├─ Receives request                                     │
│    └─ Extracts JSON body                                   │
│                                                             │
│ 2. Validation (Pydantic)                                   │
│    ├─ BookCreate schema validates                          │
│    ├─ Type checking                                        │
│    └─ Field validation                                     │
│                                                             │
│ 3. Dependency Injection                                    │
│    └─ get_book_service() provides BookService             │
│                                                             │
│ 4. Service Logic                                           │
│    ├─ Check for duplicates                                │
│    ├─ Build document                                      │
│    └─ Call repository                                     │
│                                                             │
│ 5. Repository                                              │
│    └─ Calls database insert                               │
│                                                             │
│ 6. Error Handling                                          │
│    ├─ Catch exceptions                                    │
│    ├─ Map to HTTP status                                  │
│    └─ Return error response                               │
│                                                             │
│ 7. Response                                                │
│    ├─ Status: 201 Created                                 │
│    ├─ Body: Complete book object with ID                 │
│    └─ Headers: Content-Type, Location                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP 201 + JSON Response
                       │ {
                       │   "_id": "507f1f77bcf86cd799439011",
                       │   "title": "1984",
                       │   "author": "George Orwell",
                       │   "publisher": "Penguin",
                       │   "pages": 328,
                       │   "tags": ["fiction", "dystopian"],
                       │   "created_at": "2026-08-31T10:30:00Z"
                       │ }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ DATABASE (MongoDB)                                          │
│ Document inserted into books collection                    │
│ Index updated                                              │
│ Data persisted to disk                                     │
└─────────────────────────────────────────────────────────────┘
                       │
                       │ Back to Frontend
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (Streamlit)                                        │
│ ✅ Book added successfully                                 │
│ Display success message                                    │
│ Clear form                                                 │
│ Update book list                                           │
└─────────────────────────────────────────────────────────────┘
```

### Example 2: Browse Books with Filters

```
User selects:
├─ Author: "Orwell"
├─ Publisher: "Penguin"
├─ Tags: "fiction"
└─ Clicks Browse

┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (Streamlit)                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ GET /api/v1/books?
                       │   page=1&
                       │   limit=10&
                       │   author=Orwell&
                       │   publisher=Penguin&
                       │   tags=fiction&
                       │   sort_by=created_at&
                       │   order=desc
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND (FastAPI) - list_books()                            │
│                                                             │
│ 1. Parse Parameters                                        │
│    ├─ page=1, limit=10                                    │
│    ├─ author=Orwell                                       │
│    ├─ publisher=Penguin                                   │
│    ├─ tags=["fiction"]                                    │
│    └─ sort_by=created_at, order=desc                      │
│                                                             │
│ 2. Query Building in Service                              │
│    ├─ Create filter dict:                                 │
│    │   {                                                   │
│    │     "$and": [                                         │
│    │       { "author": { "$regex": "Orwell" } },          │
│    │       { "publisher": { "$regex": "Penguin" } },      │
│    │       { "tags": { "$in": ["fiction"] } }             │
│    │     ]                                                 │
│    │   }                                                   │
│    └─ Create sort spec: { "created_at": -1 }             │
│                                                             │
│ 3. Repository Call                                        │
│    ├─ Skip: (1-1)*10 = 0                                  │
│    ├─ Limit: 10                                           │
│    └─ Find + Sort + Limit                                 │
│                                                             │
│ 4. Count Results                                          │
│    └─ Total matching documents                            │
│                                                             │
│ 5. Build Response                                         │
│    ├─ Pagination metadata                                 │
│    ├─ Results list                                        │
│    └─ Has next/prev flags                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP 200 + JSON
                       │ {
                       │   "data": [{...}, {...}, ...],
                       │   "pagination": {
                       │     "page": 1,
                       │     "limit": 10,
                       │     "total": 5,
                       │     "pages": 1,
                       │     "has_next": false,
                       │     "has_prev": false
                       │   }
                       │ }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (Streamlit)                                        │
│ Display matching books in cards                            │
│ Show pagination info                                       │
│ Display applied filters                                    │
└─────────────────────────────────────────────────────────────┘
```

### Example 3: Analytics Dashboard

```
User clicks Analytics tab

┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (Streamlit)                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ GET /api/v1/books/stats
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND (FastAPI) - get_book_stats()                        │
│                                                             │
│ MongoDB Aggregation Pipeline:                              │
│                                                             │
│ db.books.aggregate([                                       │
│   {                                                         │
│     "$group": {                                             │
│       "_id": "$tags",                                       │
│       "count": { "$sum": 1 }                               │
│     }                                                       │
│   },                                                        │
│   {                                                         │
│     "$facet": {                                             │
│       "total": [{ "$count": "total" }],                    │
│       "avgPages": [{ "$avg": "$pages" }],                  │
│       "minPages": [{ "$min": "$pages" }],                  │
│       "maxPages": [{ "$max": "$pages" }],                  │
│       "byTag": [                                            │
│         { "$group": { "_id": "$tags", "count": 1 } }       │
│       ]                                                     │
│     }                                                       │
│   }                                                         │
│ ])                                                          │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP 200 + JSON
                       │ {
                       │   "total_books": 1,
                       │   "avg_pages": 328.0,
                       │   "min_pages": 328,
                       │   "max_pages": 328,
                       │   "books_by_tag": {...},
                       │   "most_common_publisher": "Penguin"
                       │ }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (Streamlit)                                        │
│ ├─ KPI Cards (4 columns)                                   │
│ ├─ Bar Chart (Books by Tag)                                │
│ ├─ Statistics Table                                        │
│ └─ Publisher Summary                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 4️⃣ KEY TECHNOLOGIES & THEIR ROLES

```
PRESENTATION
├─ Streamlit 1.28+         → Interactive web UI
├─ Plotly 5.17+           → Interactive charts
├─ Altair 5.1+            → Data visualization
├─ Pandas 2.0+            → Data manipulation
└─ Requests 2.31+         → HTTP client

APPLICATION
├─ FastAPI 0.104+         → Web framework
├─ Uvicorn 0.24+          → ASGI server
├─ Pydantic v2 2.4+       → Data validation
├─ Motor 3.3+             → Async MongoDB driver
└─ Python-multipart       → Form data handling

DATABASE
└─ MongoDB 7.0            → NoSQL document database

INFRASTRUCTURE
├─ Docker 29.3+           → Containerization
├─ Docker Compose 5.1+    → Service orchestration
├─ Terraform 1.5+         → Infrastructure as Code
└─ GitHub Actions         → CI/CD automation

TESTING
├─ Pytest 7.4+            → Test framework
├─ Pytest-asyncio 0.21+   → Async testing
└─ Mongomock-motor        → Mock MongoDB
```

---

## 5️⃣ NECESSARY vs OPTIONAL COMPONENTS

### ✅ NECESSARY (Core Application)

```
┌─ FastAPI Backend
│  ├─ Routers (Book endpoints)
│  ├─ Services (Business logic)
│  ├─ Repositories (DB queries)
│  └─ Schemas (Validation)
│
├─ MongoDB
│  ├─ books collection
│  └─ Indexes
│
├─ Streamlit Frontend
│  ├─ Browse tab
│  ├─ Add Book form
│  └─ Edit/Delete
│
└─ Docker Compose
   └─ 3-service orchestration

→ 100% needed for functionality
```

### ➕ RECOMMENDED (Production Quality)

```
├─ Rate Limiting
│  └─ Prevent API abuse
│
├─ Structured Logging
│  └─ Debugging & monitoring
│
├─ Health Checks
│  └─ Service readiness
│
├─ Error Handling
│  └─ Graceful failures
│
└─ Testing
   └─ Quality assurance

→ 80% recommended for production
```

### ⭕ OPTIONAL (Nice-to-Have)

```
├─ Advanced Filtering
│  └─ Author, Publisher, Tags filters
│
├─ Analytics Dashboard
│  └─ Statistics & charts
│
├─ Full-Text Search
│  └─ Text-based queries
│
├─ Terraform/AWS
│  └─ Cloud infrastructure
│
├─ CI/CD Pipeline
│  └─ Automated testing
│
└─ 25+ Documentation Files
   └─ Only keep essential

→ 50% optional, depends on use case
```

---

**Summary**: The application consists of 3 main tiers (Frontend, Backend, Database), with recommended middleware and optional advanced features. All core components are production-ready and working correctly.

