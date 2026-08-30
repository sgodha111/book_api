# Advanced Features & Filtering Guide

Complete documentation for advanced query filtering, search, statistics, rate limiting, and logging features.

## 📋 Table of Contents

1. [Advanced Query Filtering](#advanced-query-filtering)
2. [Full-Text Search](#full-text-search)
3. [Book Statistics](#book-statistics)
4. [Rate Limiting](#rate-limiting)
5. [Request/Response Logging](#requestresponse-logging)
6. [Examples](#examples)

---

## 🔍 Advanced Query Filtering

The `GET /api/v1/books` endpoint now supports advanced filtering with multiple parameters.

### Filtering Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | int | Page number (1-indexed) | `?page=1` |
| `limit` | int | Items per page (1-100) | `?limit=10` |
| `search` | string | Search title/author | `?search=orwell` |
| `author` | string | Filter by author (case-insensitive) | `?author=George` |
| `publisher` | string | Filter by publisher (case-insensitive) | `?publisher=Penguin` |
| `tags` | string | Comma-separated tags (match any) | `?tags=fiction,dystopian` |
| `min_pages` | int | Minimum page count | `?min_pages=100` |
| `max_pages` | int | Maximum page count | `?max_pages=500` |
| `sort_by` | string | Sort field (created_at, title, author, pages, updated_at) | `?sort_by=pages` |
| `order` | string | Sort direction (asc, desc) | `?order=desc` |

### Sorting Options

```
sort_by values:
  - created_at  (default) - Sort by creation time
  - updated_at  - Sort by last update time
  - title       - Sort by book title (A-Z)
  - author      - Sort by author name (A-Z)
  - pages       - Sort by page count (numeric)

order values:
  - desc  (default) - Descending order
  - asc   - Ascending order
```

### Query Building

Filters are combined with **AND** logic (all must match):

```
GET /api/v1/books?author=Orwell&publisher=Penguin&min_pages=200
```

This returns books that match ALL criteria:
- Author contains "Orwell" (case-insensitive)
- Publisher contains "Penguin" (case-insensitive)
- Pages >= 200

Tags are matched with **OR** logic (match any tag):

```
GET /api/v1/books?tags=python,fiction,dystopian
```

This returns books that have ANY of these tags.

### Response Format

```json
{
  "data": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "1984",
      "author": "George Orwell",
      "pages": 328,
      "publisher": "Penguin",
      "tags": ["fiction", "dystopian"],
      "created_at": "2024-08-30T10:00:00",
      "updated_at": "2024-08-30T10:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 42,
    "has_next": true,
    "has_prev": false,
    "total_pages": 5
  }
}
```

---

## 🔎 Full-Text Search

The `GET /api/v1/books/search?q={query}` endpoint performs full-text search across title, author, and publisher fields.

### Search Endpoint

**Endpoint:** `GET /api/v1/books/search`

**Parameters:**
- `q` (required): Search query string
- `page` (optional): Page number, default: 1
- `limit` (optional): Items per page, default: 10

**Search Behavior:**
- Case-insensitive
- Searches across: title, author, publisher
- Uses regex pattern matching
- Returns all matching books with pagination

### Search vs Filter

| Feature | `/books?search=` | `/books/search?q=` |
|---------|------------------|-------------------|
| Search fields | title, author | title, author, publisher |
| Combine with filters | Yes | No (separate endpoint) |
| Use case | Quick filter | Comprehensive full-text search |

### Example Requests

```bash
# Search for books by an author
curl "http://localhost:8000/api/v1/books/search?q=Orwell"

# Search for books by publisher
curl "http://localhost:8000/api/v1/books/search?q=Penguin"

# Search by title with pagination
curl "http://localhost:8000/api/v1/books/search?q=python&page=1&limit=20"
```

---

## 📊 Book Statistics

The `GET /api/v1/books/stats` endpoint provides comprehensive statistics about the book collection.

### Statistics Endpoint

**Endpoint:** `GET /api/v1/books/stats`

**No parameters required**

**Response Fields:**

```json
{
  "total_books": 42,
  "avg_pages": 325.5,
  "min_pages": 108,
  "max_pages": 1516,
  "books_by_tag": {
    "fiction": 15,
    "dystopian": 8,
    "python": 3,
    "technical": 5,
    ...
  },
  "most_common_publisher": "Penguin"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total_books` | int | Total number of books in collection |
| `avg_pages` | float | Average pages per book (rounded to 2 decimals) |
| `min_pages` | int | Minimum page count in collection |
| `max_pages` | int | Maximum page count in collection |
| `books_by_tag` | object | Count of books per tag |
| `most_common_publisher` | string | Publisher with most books |

### Statistics Use Cases

- **Dashboard metrics:** Display collection statistics
- **Analytics:** Understand book collection composition
- **Content planning:** Identify most common publishers and tags
- **Collection insights:** Analyze page count distribution

### Example Request

```bash
# Get all statistics
curl "http://localhost:8000/api/v1/books/stats"

# Response
{
  "total_books": 42,
  "avg_pages": 325.5,
  "min_pages": 108,
  "max_pages": 1516,
  "books_by_tag": {
    "fiction": 15,
    "dystopian": 8,
    "python": 3,
    "technical": 5
  },
  "most_common_publisher": "Penguin"
}
```

---

## 🚦 Rate Limiting

Built-in rate limiting protects the API from excessive requests.

### Rate Limit Configuration

- **Limit:** 100 requests per minute per IP address
- **Reset:** Automatic reset every minute
- **Exception:** Health check endpoint (`/health`) is exempt

### Rate Limit Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1693386900
X-Process-Time: 0.023
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per minute |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |
| `X-Process-Time` | Request processing time in seconds |

### Rate Limit Exceeded Response

When limit is exceeded, you receive a `429 Too Many Requests` response:

```json
{
  "detail": "Rate limit exceeded. Maximum 100 requests per minute.",
  "retry_after": 60
}
```

### Handling Rate Limits

**Best Practices:**

1. **Implement Backoff Logic**
   ```python
   import time
   import requests

   def fetch_with_retry(url, max_retries=3):
       for attempt in range(max_retries):
           response = requests.get(url)
           if response.status_code == 429:
               wait_time = int(response.json()["retry_after"])
               print(f"Rate limited. Waiting {wait_time}s...")
               time.sleep(wait_time)
               continue
           return response
       raise Exception("Max retries exceeded")
   ```

2. **Respect Rate Limit Headers**
   ```python
   remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
   if remaining < 10:
       print("Approaching rate limit, slowing down...")
       time.sleep(1)
   ```

3. **Batch Requests**
   - Combine multiple filters in one request instead of separate requests
   - Use pagination efficiently

4. **Cache Results**
   - Cache responses locally to avoid repeated requests
   - Set appropriate cache TTL based on data freshness requirements

---

## 📝 Request/Response Logging

All requests and responses are automatically logged in structured JSON format.

### Log Structure

**Request Log:**
```json
{
  "event": "request_received",
  "timestamp": "2024-08-30T10:30:45.123456",
  "method": "GET",
  "path": "/api/v1/books",
  "query_params": {"author": "Orwell", "limit": "10"},
  "client_ip": "192.168.1.100"
}
```

**Response Log:**
```json
{
  "event": "response_sent",
  "timestamp": "2024-08-30T10:30:45.234567",
  "method": "GET",
  "path": "/api/v1/books",
  "status_code": 200,
  "response_time_ms": 89.23,
  "client_ip": "192.168.1.100"
}
```

**Rate Limit Exceeded Log:**
```json
{
  "event": "rate_limit_exceeded",
  "timestamp": "2024-08-30T10:30:50.345678",
  "client_ip": "192.168.1.100",
  "path": "/api/v1/books",
  "requests_count": 100
}
```

### Log Fields

| Field | Description |
|-------|-------------|
| `event` | Event type (request_received, response_sent, rate_limit_exceeded) |
| `timestamp` | ISO 8601 formatted timestamp |
| `method` | HTTP method (GET, POST, PATCH, DELETE) |
| `path` | Request path |
| `query_params` | Query parameters dictionary |
| `status_code` | HTTP status code |
| `response_time_ms` | Response time in milliseconds |
| `client_ip` | Client IP address |
| `requests_count` | (Rate limit) Number of requests in window |

### Accessing Logs

Logs are sent to stdout as JSON, which allows integration with:
- **CloudWatch** (AWS) - Automatic collection
- **ELK Stack** - Elasticsearch, Logstash, Kibana
- **Splunk** - Log aggregation
- **DataDog** - Monitoring and analytics
- **New Relic** - APM and monitoring

### Structured Logging Benefits

1. **Queryable:** Easy to search and filter logs
2. **Parseable:** Automatic parsing by logging services
3. **Metrics:** Extract metrics from structured data
4. **Debugging:** Complete request/response information
5. **Monitoring:** Track performance and errors

### Example: Querying Logs in CloudWatch

```
fields @timestamp, method, path, status_code, response_time_ms
| filter event = "response_sent"
| stats avg(response_time_ms) as avg_time, max(response_time_ms) as max_time by path
```

---

## 💡 Examples

### Example 1: Find Recently Added Fiction Books

```bash
curl "http://localhost:8000/api/v1/books?tags=fiction&sort_by=created_at&order=desc&limit=5"
```

Returns the 5 most recently added fiction books.

### Example 2: Find Long Technical Books

```bash
curl "http://localhost:8000/api/v1/books?tags=technical&min_pages=800&sort_by=pages&order=desc"
```

Returns all technical books with 800+ pages, sorted by page count (longest first).

### Example 3: Find Books by Author and Publisher

```bash
curl "http://localhost:8000/api/v1/books?author=Mark&publisher=O%27Reilly&sort_by=title"
```

Returns books by authors with "Mark" in their name, published by O'Reilly, sorted alphabetically.

### Example 4: Complex Multi-Filter Query

```bash
curl "http://localhost:8000/api/v1/books?\
author=Scott&\
min_pages=150&\
max_pages=400&\
tags=fiction,romance&\
sort_by=pages&\
order=asc&\
limit=20&\
page=1"
```

Returns books matching ALL criteria:
- Author contains "Scott"
- Pages between 150-400
- Has either "fiction" or "romance" tag
- Sorted by pages (shortest first)
- Limited to 20 results on page 1

### Example 5: Search Across All Fields

```bash
curl "http://localhost:8000/api/v1/books/search?q=1984&limit=10"
```

Searches for "1984" across title, author, and publisher fields.

### Example 6: Get Collection Statistics

```bash
curl "http://localhost:8000/api/v1/books/stats"
```

Returns comprehensive statistics about the book collection.

### Example 7: Pagination with Filters

```bash
# First page
curl "http://localhost:8000/api/v1/books?tags=fiction&limit=10&page=1"

# Check pagination metadata
# {
#   "pagination": {
#     "page": 1,
#     "limit": 10,
#     "total": 45,
#     "has_next": true,
#     "total_pages": 5
#   }
# }

# Get next page
curl "http://localhost:8000/api/v1/books?tags=fiction&limit=10&page=2"
```

### Example 8: Sort by Different Fields

```bash
# Sort by title alphabetically
curl "http://localhost:8000/api/v1/books?sort_by=title&order=asc"

# Sort by pages (shortest to longest)
curl "http://localhost:8000/api/v1/books?sort_by=pages&order=asc"

# Sort by author (A-Z)
curl "http://localhost:8000/api/v1/books?sort_by=author&order=asc"

# Sort by update time (newest first)
curl "http://localhost:8000/api/v1/books?sort_by=updated_at&order=desc"
```

### Example 9: Handling Rate Limits

```python
import time
import requests

def fetch_books_with_backoff(base_url, filters):
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.get(base_url, params=filters)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("X-RateLimit-Reset", 60))
            print(f"Rate limited. Retrying in {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        return response.json()
    
    raise Exception("Max retries exceeded")

# Usage
books = fetch_books_with_backoff(
    "http://localhost:8000/api/v1/books",
    {"tags": "fiction", "limit": 100}
)
```

### Example 10: Implementing Caching

```python
import requests
from datetime import datetime, timedelta

class CachedBooksClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)
    
    def get_books(self, **filters):
        # Create cache key
        cache_key = tuple(sorted(filters.items()))
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data
        
        # Fetch from API
        response = requests.get(self.base_url, params=filters)
        data = response.json()
        
        # Cache result
        self.cache[cache_key] = (data, datetime.now())
        
        return data

# Usage
client = CachedBooksClient("http://localhost:8000/api/v1/books")
books = client.get_books(tags="fiction", limit=20)
```

---

## 🎯 Feature Summary

| Feature | Endpoint | Method | Purpose |
|---------|----------|--------|---------|
| Advanced Filtering | `/api/v1/books` | GET | Filter by author, publisher, tags, pages, sort |
| Full-Text Search | `/api/v1/books/search` | GET | Search across title, author, publisher |
| Statistics | `/api/v1/books/stats` | GET | Get collection statistics and metrics |
| Rate Limiting | All endpoints | - | 100 requests/minute per IP |
| Request Logging | All endpoints | - | Structured JSON logging |
| Response Logging | All endpoints | - | Structured JSON logging with timing |

---

## 🔗 Related Documentation

- [README.md](README.md) - Project overview
- [COMMANDS.md](COMMANDS.md) - CLI commands
- [CI_CD.md](CI_CD.md) - CI/CD documentation

---

**Updated:** 2024-08-30
**Version:** 1.1.0 (Advanced Features)
