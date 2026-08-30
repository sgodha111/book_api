# Advanced Features Quick Reference

Quick-lookup guide for advanced API features.

## 🔍 Advanced Filtering - GET /api/v1/books

```bash
# Filter by author
curl "http://localhost:8000/api/v1/books?author=Orwell"

# Filter by publisher
curl "http://localhost:8000/api/v1/books?publisher=Penguin"

# Filter by tags (match any)
curl "http://localhost:8000/api/v1/books?tags=fiction,dystopian"

# Filter by page range
curl "http://localhost:8000/api/v1/books?min_pages=200&max_pages=500"

# Sort by title (ascending)
curl "http://localhost:8000/api/v1/books?sort_by=title&order=asc"

# Sort by pages (descending)
curl "http://localhost:8000/api/v1/books?sort_by=pages&order=desc"

# Combined filters
curl "http://localhost:8000/api/v1/books?author=Scott&tags=fiction&min_pages=150&sort_by=pages&order=desc"
```

### Sort Options
- `created_at` (default) - Creation time
- `updated_at` - Last update time
- `title` - Book title
- `author` - Author name
- `pages` - Page count

### Order Options
- `desc` (default) - Descending
- `asc` - Ascending

---

## 🔎 Full-Text Search - GET /api/v1/books/search

```bash
# Search by title
curl "http://localhost:8000/api/v1/books/search?q=1984"

# Search by author
curl "http://localhost:8000/api/v1/books/search?q=Orwell"

# Search by publisher
curl "http://localhost:8000/api/v1/books/search?q=Penguin"

# Search with pagination
curl "http://localhost:8000/api/v1/books/search?q=fiction&limit=20&page=1"
```

**Searches across:** title, author, publisher (case-insensitive)

---

## 📊 Statistics - GET /api/v1/books/stats

```bash
# Get all statistics
curl "http://localhost:8000/api/v1/books/stats"
```

**Returns:**
- `total_books` - Total count
- `avg_pages` - Average pages
- `min_pages` - Minimum pages
- `max_pages` - Maximum pages
- `books_by_tag` - Count per tag
- `most_common_publisher` - Top publisher

---

## 🚦 Rate Limiting

**Limit:** 100 requests/minute per IP

**Response headers:**
- `X-RateLimit-Limit: 100`
- `X-RateLimit-Remaining: <N>`
- `X-RateLimit-Reset: <timestamp>`
- `X-Process-Time: <seconds>`

**When exceeded:** 429 Too Many Requests

---

## 📝 Logging

All requests/responses logged as structured JSON:

```json
{
  "event": "request_received",
  "timestamp": "2024-08-30T10:30:45",
  "method": "GET",
  "path": "/api/v1/books",
  "client_ip": "192.168.1.100"
}
```

---

## 📚 Complete Documentation

See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for:
- Detailed parameter documentation
- Response format examples
- Working code examples
- Best practices
- Python integration examples
