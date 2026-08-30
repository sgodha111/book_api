"""Streamlit configuration."""

import os

# API Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_TIMEOUT = 10  # seconds
API_VERSION = "v1"

# UI Configuration
PAGE_SIZE = 10  # Books per page
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Theme Configuration
PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
BACKGROUND_COLOR = "#f8f9fa"
TEXT_COLOR = "#212529"

# Feature Flags
ENABLE_ERROR_DETAILS = True
ENABLE_LOADING_SPINNER = True
ENABLE_STATUS_INDICATOR = True

# API Endpoints
BOOKS_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/books"
SEARCH_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/books/search"
STATS_ENDPOINT = f"{API_BASE_URL}/api/{API_VERSION}/books/stats"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
