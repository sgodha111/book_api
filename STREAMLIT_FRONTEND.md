# Streamlit Frontend - Books Catalog Management

Complete guide for using the Streamlit web interface for the Books API.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Running the App](#running-the-app)
4. [Features](#features)

---

## 🎯 Overview

The Streamlit frontend provides a user-friendly web interface to interact with the Books API. It includes four main tabs:

1. **Browse Books** - View, filter, and manage books
2. **Add Book** - Create or edit books
3. **Search** - Full-text search across books
4. **Analytics** - View collection statistics

### Key Features

✅ Beautiful, intuitive UI
✅ Real-time filtering and sorting
✅ Full-text search capability
✅ Add, edit, and delete books
✅ Analytics dashboard with charts
✅ Pagination support
✅ Error handling and validation
✅ Responsive design

---

## 💻 Installation

### Prerequisites

- Python 3.12+
- FastAPI backend running (http://localhost:8000)
- pip package manager

### Setup

1. **Install dependencies:**

```bash
pip install streamlit requests pandas
```

Or use the requirements.txt:

```bash
pip install -r requirements.txt
```

2. **Verify FastAPI backend is running:**

```bash
python -m uvicorn app.main:app --reload
```

---

## 🚀 Running the App

### Start the Streamlit app:

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## ✨ Features

### 📚 Browse Books

**Purpose:** View and manage your book collection

**Features:**
- Display books in a formatted table
- Real-time filtering (author, publisher, tags, pages)
- Sorting options (title, author, pages, created_at, updated_at)
- Pagination (10 books per page)
- Edit and delete books

### ➕ Add Book

**Purpose:** Create new books or edit existing ones

**Features:**
- Form with validation
- Required fields marked with *
- Tags input (comma-separated)
- Success/error messages
- Auto-fill when editing

**Fields:**
- **Title** (required)
- **Author** (required)
- **Publisher** (required)
- **Pages** (required, 1-50000)
- **Tags** (optional)

### 🔎 Search

**Purpose:** Find books using full-text search

**Features:**
- Searches across: title, author, publisher
- Case-insensitive matching
- Real-time search results

### 📊 Analytics

**Purpose:** View collection statistics and insights

**Displays:**
- Total books, average pages, min/max pages
- Books by tag (bar chart)
- Most common publisher
- Total unique tags

---

## 🔧 Configuration

### Environment Variables

```bash
# Set custom API URL (default: http://localhost:8000)
export API_URL=http://api.example.com
streamlit run streamlit_app.py
```

---

## 🐛 Troubleshooting

### "Cannot connect to API"

1. Verify FastAPI backend is running
2. Check API URL: `curl http://localhost:8000/health`
3. Ensure no firewall blocking connections

### "No books in Browse tab"

1. Did you add books in "Add Book" tab?
2. Try removing all filters
3. Check error messages

### Port already in use

```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502
```

---

**Version:** 1.0.0
**Compatible with:** FastAPI v0.104+, Streamlit v1.28+
