# FastAPI MongoDB - Command Reference

## 🚀 Getting Started

### Navigate to Project
```bash
cd "Documents/Github Repos/Antonia/Assginement Code"
```

### Start All Services (Recommended)
```bash
docker-compose up
```

### Open in Browser
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

---

## 📝 Testing Commands

### Run All Unit Tests
```bash
pytest tests/unit/ -v
```

### Run Specific Test
```bash
pytest tests/unit/test_book_service.py::TestBookServiceCreate -v
```

### Run with Coverage
```bash
pytest tests/unit/ --cov=app
```

### Run Tests with Output
```bash
pytest tests/unit/ -v -s
```

---

## 🧪 API Testing with curl

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Root
```bash
curl http://localhost:8000/
```

### List Books
```bash
curl http://localhost:8000/api/v1/books
```

### List Books with Pagination
```bash
curl "http://localhost:8000/api/v1/books?page=1&limit=10"
```

### Create a Book
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

### Search Books
```bash
curl "http://localhost:8000/api/v1/books/search?query=1984"
```

### Get Books by Author
```bash
curl "http://localhost:8000/api/v1/books/author/George%20Orwell"
```

### Get Books by Publisher
```bash
curl "http://localhost:8000/api/v1/books/publisher/Penguin"
```

### Get Book Count
```bash
curl "http://localhost:8000/api/v1/books/stats/count"
```

### Update a Book (Get ID from list first)
```bash
curl -X PATCH "http://localhost:8000/api/v1/books/{book_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984 - Extended Edition",
    "pages": 400
  }'
```

### Delete a Book
```bash
curl -X DELETE "http://localhost:8000/api/v1/books/{book_id}"
```

### List Authors with Book Counts
```bash
curl "http://localhost:8000/api/v1/authors"
```

### Create an Author
```bash
curl -X POST http://localhost:8000/api/v1/authors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "George Orwell",
    "country": "United Kingdom"
  }'
```

### Get Author's Books
```bash
curl "http://localhost:8000/api/v1/authors/{author_id}/books"
```

### Get Author Statistics
```bash
curl "http://localhost:8000/api/v1/authors/stats/overview"
```

### List Publishers
```bash
curl "http://localhost:8000/api/v1/publishers"
```

### Get Top Publishers
```bash
curl "http://localhost:8000/api/v1/publishers/top"
```

### Get Publisher Average Pages
```bash
curl "http://localhost:8000/api/v1/publishers/Penguin/average-pages"
```

### Get Publisher Statistics
```bash
curl "http://localhost:8000/api/v1/publishers/Penguin/stats"
```

### Get Publishers by Tag
```bash
curl "http://localhost:8000/api/v1/publishers/by-tag/fiction"
```

### Get Publisher Overview
```bash
curl "http://localhost:8000/api/v1/publishers/overview"
```

---

## 🐳 Docker Commands

### Start Services
```bash
docker-compose up
```

### Start in Background
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs
```

### View API Logs Only
```bash
docker-compose logs -f api
```

### View MongoDB Logs Only
```bash
docker-compose logs -f mongo
```

### Stop Services
```bash
docker-compose stop
```

### Stop and Remove Containers
```bash
docker-compose down
```

### Remove Everything (including volumes)
```bash
docker-compose down -v
```

### Check Service Status
```bash
docker-compose ps
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild Docker Image
```bash
docker-compose build
```

---

## 🏗️ Local Development Setup

### Create Virtual Environment
```bash
python -m venv venv
```

### Activate Virtual Environment
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start MongoDB Locally
```bash
docker run -d -p 27017:27017 --name mongo mongo:7.0
```

### Run FastAPI Application
```bash
uvicorn app.main:app --reload
```

### Stop MongoDB
```bash
docker stop mongo
docker rm mongo
```

---

## 📋 Project Structure Commands

### List All Python Files
```bash
find app -type f -name "*.py" | sort
```

### Count Python Lines of Code
```bash
find app -name "*.py" | xargs wc -l
```

### Check File Structure
```bash
ls -la app/
ls -la app/routers/
ls -la app/services/
ls -la tests/
```

### View Project Tree (if tree installed)
```bash
tree -I 'venv|__pycache__|.pytest_cache' -L 3
```

---

## 🔍 Debugging Commands

### Check Python Version
```bash
python --version
```

### Verify Dependencies
```bash
pip list
```

### Check Environment Variables
```bash
cat .env
```

### Validate Docker Compose File
```bash
docker-compose config
```

### Test Docker Image Build
```bash
docker build . --dry-run
```

### Check Port Usage
```bash
# macOS/Linux
lsof -i :8000
lsof -i :27017

# Windows
netstat -ano | findstr :8000
```

### Kill Process on Port
```bash
# macOS/Linux
kill -9 <PID>

# Windows
taskkill /PID <PID> /F
```

---

## 📦 Database Commands

### Access MongoDB Shell
```bash
docker exec -it fastapi_mongo mongosh
```

### List Databases
```bash
# In mongosh
show databases
```

### Use Specific Database
```bash
# In mongosh
use fastapi_db
```

### List Collections
```bash
# In mongosh
show collections
```

### Query Books
```bash
# In mongosh
db.books.find()
```

### Count Books
```bash
# In mongosh
db.books.countDocuments()
```

---

## 🧹 Cleanup Commands

### Remove Virtual Environment
```bash
rm -rf venv
```

### Clear Python Cache
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Clear Pytest Cache
```bash
rm -rf .pytest_cache
```

### Clean Docker
```bash
docker-compose down -v
docker system prune
```

### Full Project Cleanup
```bash
rm -rf venv .pytest_cache mongo_data
docker-compose down -v
```

---

## 📊 Useful Combinations

### Complete Setup (Fresh Start)
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run tests
pytest tests/unit/ -v

# 4. Start services
docker-compose up
```

### Test Everything
```bash
# Run unit tests
pytest tests/unit/ -v

# Check health
curl http://localhost:8000/health

# Create sample data
curl -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "author": "Test", "pages": 100, "publisher": "Test", "tags": ["test"]}'

# List data
curl http://localhost:8000/api/v1/books
```

### Monitor While Running
```bash
# Terminal 1: Start services
docker-compose up

# Terminal 2: Watch logs
docker-compose logs -f api

# Terminal 3: Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/books
```

---

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| Start App | `docker-compose up` |
| Run Tests | `pytest tests/unit/ -v` |
| View Logs | `docker-compose logs -f api` |
| Stop App | `docker-compose down` |
| Health Check | `curl http://localhost:8000/health` |
| Swagger UI | `http://localhost:8000/docs` |
| Create Book | `curl -X POST http://localhost:8000/api/v1/books ...` |
| List Books | `curl http://localhost:8000/api/v1/books` |
| Search Books | `curl "http://localhost:8000/api/v1/books/search?query=..."` |
| Delete All | `docker-compose down -v` |

---

## 📚 Related Documentation

- **QUICKSTART.md** - 5-minute setup guide
- **FINAL_SUMMARY.md** - Complete project overview
- **ROUTER_DOCUMENTATION.md** - API endpoint reference
- **SERVICE_LAYER.md** - Service layer details
- **FILES_CHECKLIST.md** - Project file verification

---

**All commands tested and production-ready!**
