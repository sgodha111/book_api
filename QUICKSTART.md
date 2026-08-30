# FastAPI MongoDB CRUD - Quick Start Guide

## ⚡ 5-Minute Setup

### Option 1: Docker Compose (Recommended - Easiest)

```bash
# Navigate to project directory
cd "Documents/Github Repos/Antonia/Assginement Code"

# Start services (MongoDB + FastAPI)
docker-compose up

# Wait for output showing "Uvicorn running on http://0.0.0.0:8000"
```

✅ **Done!** Your API is now running at `http://localhost:8000`

### Option 2: Local Development (Without Docker)

```bash
# Setup Python environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Start MongoDB in a separate terminal
docker run -d -p 27017:27017 --name mongo mongo:7.0

# Run the FastAPI app
uvicorn app.main:app --reload

# App will be at http://localhost:8000
```

---

## 📚 API Documentation

Once running, access interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/unit/ -v
```

### Test Individual Endpoints with curl

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Create a Book
```bash
curl -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "pages": 328,
    "publisher": "Penguin",
    "tags": ["fiction", "dystopian"]
  }'
```

#### List Books with Pagination
```bash
curl "http://localhost:8000/api/v1/books?page=1&limit=10"
```

#### Search Books
```bash
curl "http://localhost:8000/api/v1/books/search?query=orwell"
```

#### Get Books by Author
```bash
curl "http://localhost:8000/api/v1/books/author/George%20Orwell"
```

#### Update a Book (Get ID first, then PATCH)
```bash
curl -X PATCH "http://localhost:8000/api/v1/books/{book_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984 - Revised Edition",
    "pages": 350
  }'
```

#### Delete a Book
```bash
curl -X DELETE "http://localhost:8000/api/v1/books/{book_id}"
```

#### Get Book Statistics
```bash
curl "http://localhost:8000/api/v1/books/stats/count"
```

#### Get Authors with Book Counts
```bash
curl "http://localhost:8000/api/v1/authors"
```

#### Get Publisher Statistics
```bash
curl "http://localhost:8000/api/v1/publishers/overview"
```

#### Get Top Publishers
```bash
curl "http://localhost:8000/api/v1/publishers/top"
```

---

## 🔍 Complete API Endpoints

### Books (9 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/books` | List all books with pagination |
| POST | `/api/v1/books` | Create a new book |
| GET | `/api/v1/books/{id}` | Get a specific book |
| PATCH | `/api/v1/books/{id}` | Update a book |
| DELETE | `/api/v1/books/{id}` | Delete a book |
| GET | `/api/v1/books/search` | Search books |
| GET | `/api/v1/books/author/{name}` | Filter by author |
| GET | `/api/v1/books/publisher/{name}` | Filter by publisher |
| GET | `/api/v1/books/stats/count` | Get book count |

### Authors (7 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/authors` | List authors with book counts |
| POST | `/api/v1/authors` | Create an author |
| GET | `/api/v1/authors/{id}` | Get author details |
| PATCH | `/api/v1/authors/{id}` | Update author |
| DELETE | `/api/v1/authors/{id}` | Delete author |
| GET | `/api/v1/authors/{id}/books` | Get author's books |
| GET | `/api/v1/authors/stats/overview` | Author statistics |

### Publishers (7 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/publishers` | List publishers |
| POST | `/api/v1/publishers` | Create publisher |
| GET | `/api/v1/publishers/top` | Top publishers |
| GET | `/api/v1/publishers/{name}/average-pages` | Average pages |
| GET | `/api/v1/publishers/{name}/stats` | Publisher stats |
| GET | `/api/v1/publishers/by-tag/{tag}` | Filter by tag |
| GET | `/api/v1/publishers/overview` | Overview statistics |

### Health & Docs (2 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |

---

## 🛑 Stopping Services

### Docker Compose
```bash
# Stop services (keeps data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

### Local Development
```bash
# Stop FastAPI: Ctrl+C in terminal
# Stop MongoDB: docker stop mongo
# Or: docker rm mongo -f
```

---

## 📋 Project Structure

```
.
├── app/
│   ├── main.py              ← FastAPI application
│   ├── config.py            ← Settings
│   ├── models/              ← Database & exceptions
│   ├── schemas/             ← Pydantic models
│   ├── services/            ← Business logic
│   ├── routers/             ← API endpoints
│   ├── repositories/        ← Data access
│   └── utils/               ← Pagination helpers
├── tests/
│   ├── conftest.py          ← Pytest fixtures
│   └── unit/
│       └── test_book_service.py
├── docker-compose.yml       ← Docker orchestration
├── Dockerfile               ← Container image
├── requirements.txt         ← Python dependencies
├── pyproject.toml           ← Project config
└── .env                     ← Environment variables
```

---

## 🔧 Configuration

Edit `.env` to customize:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=fastapi_db
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 💡 Tips

1. **Live Reload**: When using local dev, changes to Python files auto-reload
2. **Database View**: Use MongoDB Compass to visualize data at `mongodb://localhost:27017`
3. **API Testing**: Use Swagger UI at `/docs` for interactive testing
4. **Logs**: Check Docker logs with `docker-compose logs -f api`

---

## ✅ Success Checklist

- [ ] Services started (docker-compose up)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Swagger UI loads (`http://localhost:8000/docs`)
- [ ] Create a book (POST /api/v1/books)
- [ ] List books (GET /api/v1/books)
- [ ] Search books (GET /api/v1/books/search?query=...)
- [ ] Update a book (PATCH /api/v1/books/{id})
- [ ] Delete a book (DELETE /api/v1/books/{id})
- [ ] Test authors endpoints
- [ ] Test publishers endpoints

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml or find process
lsof -i :8000
kill -9 <PID>
```

### MongoDB Connection Error
```bash
# Check if MongoDB is running
docker-compose ps

# Restart MongoDB
docker-compose restart mongo
```

### Python Version Issue
```bash
# Ensure Python 3.12+
python --version

# Use specific version
python3.12 -m venv venv
```

### Dependency Issues
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Next Steps

1. ✅ Run the application locally
2. ✅ Test all endpoints in Swagger UI
3. ✅ Create sample data
4. ✅ Run full test suite
5. 📝 Deploy to your favorite platform (AWS, Heroku, DigitalOcean)

**Everything is ready. Enjoy your production-grade FastAPI + MongoDB app!** 🚀
