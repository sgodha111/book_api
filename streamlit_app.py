"""Polished Streamlit frontend for Books Catalog Management."""

import os
import streamlit as st
import requests
import pandas as pd
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import time

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_TIMEOUT = 10
PAGE_SIZE = 10

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Books API",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Custom Styling
# ============================================================================

st.markdown("""
    <style>
    /* Main colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #28a745;
        --danger-color: #dc3545;
        --warning-color: #ffc107;
        --background-color: #f8f9fa;
        --text-color: #212529;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cards styling */
    .book-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.3s ease;
    }
    
    .book-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Metric styling */
    .metric-card {
        border-left: 4px solid #1f77b4;
        padding-left: 1rem;
    }
    
    /* Status indicator */
    .status-connected {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-disconnected {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Button styling */
    .action-button {
        display: inline-block;
        margin: 0.25rem;
    }
    
    /* Tag styling */
    .tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.85rem;
    }
    
    /* Messages */
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Pagination */
    .pagination {
        text-align: center;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Initialization
# ============================================================================

if "books" not in st.session_state:
    st.session_state.books = []
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "edit_book_id" not in st.session_state:
    st.session_state.edit_book_id = None
if "api_status" not in st.session_state:
    st.session_state.api_status = None
if "last_sync" not in st.session_state:
    st.session_state.last_sync = None

# ============================================================================
# API Utilities
# ============================================================================

def check_api_status() -> bool:
    """Check if API is available."""
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 201]
    except Exception:
        return False

def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None
) -> Tuple[bool, any]:
    """Make HTTP request with error handling."""
    try:
        url = f"{API_URL}/api/v1{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        with st.spinner("🔄 Loading..."):
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=API_TIMEOUT)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=API_TIMEOUT)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=API_TIMEOUT)
            else:
                return False, "Invalid HTTP method"
        
        if response.status_code in [200, 201, 204]:
            if response.status_code == 204:
                return True, None
            return True, response.json()
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, error_detail
    
    except requests.ConnectionError:
        return False, f"❌ Cannot connect to API at {API_URL}"
    except requests.Timeout:
        return False, f"⏱️ API request timed out after {API_TIMEOUT}s"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def get_books(
    page: int = 1,
    limit: int = PAGE_SIZE,
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    tags: Optional[List[str]] = None,
    min_pages: Optional[int] = None,
    max_pages: Optional[int] = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> Tuple[bool, List[Dict], Dict]:
    """Fetch books with filters."""
    params = {
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "order": order,
    }
    
    if author:
        params["author"] = author
    if publisher:
        params["publisher"] = publisher
    if tags:
        params["tags"] = ",".join(tags)
    if min_pages is not None:
        params["min_pages"] = min_pages
    if max_pages is not None:
        params["max_pages"] = max_pages
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    endpoint = f"/books?{query_string}"
    
    success, response = make_request("GET", endpoint)
    
    if success:
        return True, response.get("data", []), response.get("pagination", {})
    else:
        return False, [], {}

def create_book(book_data: Dict) -> Tuple[bool, str]:
    """Create a new book."""
    success, response = make_request("POST", "/books", book_data)
    
    if success:
        return True, f"✅ Book '{response.get('title')}' created successfully!"
    else:
        return False, f"❌ Error: {response}"

def update_book(book_id: str, updates: Dict) -> Tuple[bool, str]:
    """Update an existing book."""
    success, response = make_request("PATCH", f"/books/{book_id}", updates)
    
    if success:
        return True, "✅ Book updated successfully!"
    else:
        return False, f"❌ Error: {response}"

def delete_book(book_id: str) -> Tuple[bool, str]:
    """Delete a book."""
    success, response = make_request("DELETE", f"/books/{book_id}")
    
    if success:
        return True, "✅ Book deleted successfully!"
    else:
        return False, f"❌ Error: {response}"

def search_books(query: str, page: int = 1, limit: int = PAGE_SIZE) -> Tuple[bool, List[Dict]]:
    """Full-text search for books."""
    endpoint = f"/books/search?q={query}&page={page}&limit={limit}"
    success, response = make_request("GET", endpoint)
    
    if success:
        return True, response.get("data", [])
    else:
        return False, []

def get_stats() -> Tuple[bool, Dict]:
    """Get book statistics."""
    success, response = make_request("GET", "/books/stats")
    
    if success:
        return True, response
    else:
        return False, {}

def get_all_tags() -> List[str]:
    """Get all unique tags."""
    success, books, _ = get_books(limit=1000)
    
    tags = set()
    if success:
        for book in books:
            if "tags" in book and book["tags"]:
                tags.update(book["tags"])
    
    return sorted(list(tags))

# ============================================================================
# UI Components
# ============================================================================

def render_book_card(book: Dict, show_actions: bool = True) -> None:
    """Render book as a card."""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"### 📖 {book['title']}")
        st.markdown(f"**Author:** {book['author']}")
        st.markdown(f"**Publisher:** {book['publisher']}")
        st.markdown(f"**Pages:** {book['pages']}")
        
        # Tags
        if book.get("tags"):
            tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in book["tags"]])
            st.markdown(tags_html, unsafe_allow_html=True)
    
    if show_actions:
        with col2:
            if st.button("✏️ Edit", key=f"edit_{book['id']}", use_container_width=True):
                st.session_state.edit_mode = True
                st.session_state.edit_book_id = book["id"]
                st.rerun()
        
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{book['id']}", use_container_width=True):
                success, message = delete_book(book["id"])
                if success:
                    st.success(message)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)

def render_status_bar() -> None:
    """Render API status bar."""
    col1, col2, col3 = st.columns([2, 2, 2])
    
    # Check API status
    api_status = check_api_status()
    
    with col1:
        if api_status:
            st.markdown("✅ <span class='status-connected'>API Connected</span>", unsafe_allow_html=True)
        else:
            st.markdown("❌ <span class='status-disconnected'>API Unavailable</span>", unsafe_allow_html=True)
    
    with col2:
        if st.session_state.last_sync:
            st.write(f"Last sync: {st.session_state.last_sync.strftime('%H:%M:%S')}")
    
    with col3:
        if st.button("🔄 Refresh"):
            st.session_state.last_sync = datetime.now()
            st.rerun()

# ============================================================================
# Tab: Browse Books
# ============================================================================

def tab_browse_books() -> None:
    """Browse and filter books."""
    st.header("📚 Browse Books")
    
    # Sidebar filters
    st.sidebar.subheader("🔍 Filters")
    
    author_filter = st.sidebar.text_input("Author", placeholder="Search by author...")
    publisher_filter = st.sidebar.text_input("Publisher", placeholder="Search by publisher...")
    
    all_tags = get_all_tags()
    tags_filter = st.sidebar.multiselect("Tags", options=all_tags)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_pages = st.number_input("Min Pages", min_value=0, value=0)
    with col2:
        max_pages = st.number_input("Max Pages", min_value=0, value=10000)
    
    sort_field = st.sidebar.selectbox(
        "Sort By",
        options=["created_at", "title", "author", "pages", "updated_at"]
    )
    
    sort_order = st.sidebar.radio("Order", options=["desc", "asc"], horizontal=True)
    
    # Fetch books
    success, books, pagination = get_books(
        page=st.session_state.current_page,
        author=author_filter if author_filter else None,
        publisher=publisher_filter if publisher_filter else None,
        tags=tags_filter if tags_filter else None,
        min_pages=min_pages if min_pages > 0 else None,
        max_pages=max_pages if max_pages < 10000 else None,
        sort_by=sort_field,
        order=sort_order,
    )
    
    if not success:
        st.error(f"Failed to fetch books: {books}")
        return
    
    st.session_state.last_sync = datetime.now()
    
    # Display results
    total = pagination.get("total", 0)
    total_pages = pagination.get("total_pages", 0)
    
    if books:
        # Pagination info
        start_idx = (st.session_state.current_page - 1) * PAGE_SIZE + 1
        end_idx = min(st.session_state.current_page * PAGE_SIZE, total)
        st.info(f"📊 Showing {start_idx}-{end_idx} of {total} books")
        
        # Display books as cards
        for book in books:
            render_book_card(book, show_actions=True)
            st.divider()
        
        # Pagination buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Previous"):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
        
        with col2:
            st.write(f"**Page {st.session_state.current_page} of {total_pages}**", divmod=(True,))
        
        with col3:
            if st.button("Next ➡️"):
                if st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()
    else:
        st.info("📭 No books found matching your filters")

# ============================================================================
# Tab: Add Book
# ============================================================================

def tab_add_book() -> None:
    """Add or edit a book."""
    st.header("➕ Add New Book")
    
    if st.session_state.edit_mode and st.session_state.edit_book_id:
        st.warning("📝 Editing existing book")
        is_edit = True
        button_text = "Update Book"
    else:
        is_edit = False
        button_text = "Add Book"
    
    with st.form("book_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Title *",
                value=st.session_state.form_data.get("title", ""),
                placeholder="Enter book title"
            )
            author = st.text_input(
                "Author *",
                value=st.session_state.form_data.get("author", ""),
                placeholder="Enter author name"
            )
        
        with col2:
            publisher = st.text_input(
                "Publisher *",
                value=st.session_state.form_data.get("publisher", ""),
                placeholder="Enter publisher name"
            )
            pages = st.number_input(
                "Pages *",
                min_value=1,
                max_value=50000,
                value=int(st.session_state.form_data.get("pages", 100))
            )
        
        tags_input = st.text_input(
            "Tags",
            value=st.session_state.form_data.get("tags_str", ""),
            placeholder="fiction, dystopian"
        )
        
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            submit_button = st.form_submit_button(f"✅ {button_text}", use_container_width=True)
        
        with col2:
            clear_button = st.form_submit_button("🔄 Clear", use_container_width=True)
        
        if submit_button:
            if not title or not author or not publisher:
                st.error("❌ Please fill all required fields")
            elif pages <= 0:
                st.error("❌ Pages must be greater than 0")
            else:
                book_data = {
                    "title": title,
                    "author": author,
                    "publisher": publisher,
                    "pages": pages,
                    "tags": tags
                }
                
                if is_edit:
                    success, message = update_book(st.session_state.edit_book_id, book_data)
                else:
                    success, message = create_book(book_data)
                
                if success:
                    st.success(message)
                    st.session_state.form_data = {}
                    st.session_state.edit_mode = False
                    st.session_state.edit_book_id = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)
        
        if clear_button:
            st.session_state.form_data = {}
            st.session_state.edit_mode = False
            st.session_state.edit_book_id = None
            st.rerun()

# ============================================================================
# Tab: Search
# ============================================================================

def tab_search() -> None:
    """Full-text search."""
    st.header("🔎 Search Books")
    
    search_query = st.text_input(
        "Search Query",
        placeholder="Search by title, author, or publisher..."
    )
    
    if search_query:
        success, books = search_books(search_query)
        
        if not success:
            st.error(f"Search failed: {books}")
            return
        
        if books:
            st.success(f"✅ Found {len(books)} result(s)")
            for book in books:
                render_book_card(book, show_actions=False)
                st.divider()
        else:
            st.info(f"📭 No books found matching '{search_query}'")
    else:
        st.info("Enter a search query to find books")

# ============================================================================
# Tab: Analytics
# ============================================================================

def tab_analytics() -> None:
    """Display analytics and statistics."""
    st.header("📊 Analytics & Statistics")
    
    success, stats = get_stats()
    
    if not success:
        st.error(f"Failed to load statistics: {stats}")
        return
    
    # Key metrics
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Books", stats.get("total_books", 0))
    
    with col2:
        st.metric("📄 Avg Pages", f"{stats.get('avg_pages', 0):.1f}")
    
    with col3:
        st.metric("📏 Min Pages", stats.get("min_pages", 0))
    
    with col4:
        st.metric("📈 Max Pages", stats.get("max_pages", 0))
    
    # Books by tag
    st.subheader("📚 Books by Tag")
    
    books_by_tag = stats.get("books_by_tag", {})
    
    if books_by_tag:
        chart_data = pd.DataFrame({
            "Tag": list(books_by_tag.keys()),
            "Count": list(books_by_tag.values()),
        })
        
        st.bar_chart(chart_data.set_index("Tag"), use_container_width=True)
        
        st.dataframe(chart_data, use_container_width=True, hide_index=True)
    else:
        st.info("No tag data available")
    
    # Additional info
    st.subheader("ℹ️ Collection Info")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Most Common Publisher**")
        st.write(f"🏢 {stats.get('most_common_publisher', 'N/A')}")
    
    with col2:
        st.write("**Total Unique Tags**")
        st.write(f"🏷️ {len(books_by_tag)}")

# ============================================================================
# Main App
# ============================================================================

def main() -> None:
    """Main application."""
    # Header
    st.markdown('<h1 class="main-header">📚 Books Catalog</h1>', unsafe_allow_html=True)
    
    # Status bar
    render_status_bar()
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📚 Browse", "➕ Add Book", "🔎 Search", "📊 Analytics"]
    )
    
    with tab1:
        tab_browse_books()
    
    with tab2:
        tab_add_book()
    
    with tab3:
        tab_search()
    
    with tab4:
        tab_analytics()
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: gray; font-size: 0.85rem;">
            📚 Books Catalog Management | Powered by FastAPI & Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
