# Streamlit Frontend - Quick Start Guide

Get the Streamlit web interface running in 5 minutes.

## ⚡ Quick Start (5 minutes)

### Step 1: Install Dependencies (1 min)

```bash
pip install streamlit requests pandas
```

### Step 2: Start the FastAPI Backend (1 min)

Terminal 1:
```bash
python -m uvicorn app.main:app --reload
```

Expected: `INFO: Uvicorn running on http://127.0.0.1:8000`

### Step 3: Start the Streamlit App (1 min)

Terminal 2:
```bash
streamlit run streamlit_app.py
```

Expected: `Local URL: http://localhost:8501`

### Step 4: Open in Browser

Navigate to: **http://localhost:8501**

---

## 🎯 First Steps

### 1. Add a Book

1. Click "Add Book" tab
2. Fill form:
   - Title: "1984"
   - Author: "George Orwell"
   - Publisher: "Penguin"
   - Pages: "328"
   - Tags: "fiction, dystopian"
3. Click "✅ Submit"

### 2. Browse Books

1. Click "Browse Books" tab
2. See your new book
3. Try filters and sorting
4. Click "✏️ Edit" or "🗑️ Delete"

### 3. Search

1. Click "Search" tab
2. Enter "1984"
3. See results

### 4. Analytics

1. Click "Analytics" tab
2. View statistics and charts

---

## 🔧 Configuration

### Custom API URL

```bash
export API_URL=http://api.example.com:8000
streamlit run streamlit_app.py
```

---

## 🐛 Troubleshooting

### "Cannot connect to API"
- Is FastAPI running? (Terminal 1)
- Try: `curl http://localhost:8000/health`

### "No books showing"
- Did you add books first?
- Remove all filters

### Port in use
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

## 🎓 Next Steps

1. Read STREAMLIT_FRONTEND.md for detailed docs
2. Explore all features
3. Add multiple books
4. Check analytics

---

## Quick Commands

```bash
# Terminal 1: Start API
python -m uvicorn app.main:app --reload

# Terminal 2: Start Frontend
streamlit run streamlit_app.py
```

Enjoy! 🚀
