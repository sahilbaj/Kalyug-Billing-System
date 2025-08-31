
"""
Configuration settings for the Sales Management System
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database file
DATABASE_FILE = DATA_DIR / "sales_data.json"

# Application settings
APP_SETTINGS = {
    "title": "Sales Management System",
    "geometry": "1200x800",
    "min_width": 800,
    "min_height": 600,
}

# Default products
DEFAULT_PRODUCTS = [
    {"name": "Coffee", "price": 3.50, "category": "Beverages"},
    {"name": "Tea", "price": 2.50, "category": "Beverages"},
    {"name": "Espresso", "price": 4.00, "category": "Beverages"},
    {"name": "Cappuccino", "price": 4.50, "category": "Beverages"},
    {"name": "Soda", "price": 2.00, "category": "Beverages"},
    {"name": "Sandwich", "price": 8.00, "category": "Food"},
    {"name": "Burger", "price": 12.00, "category": "Food"},
    {"name": "Pizza", "price": 15.00, "category": "Food"},
    {"name": "Salad", "price": 7.50, "category": "Food"},
    {"name": "Pasta", "price": 10.00, "category": "Food"},
    {"name": "Fries", "price": 5.00, "category": "Food"},
    {"name": "Ice Cream", "price": 4.50, "category": "Desserts"},
]

# UI Colors
COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "success": "#F18F01",
    "warning": "#C73E1D",
    "background": "#F5F5F5",
    "text": "#333333",
}

# Table settings
TABLE_SETTINGS = {
    "max_tables": 50,
    "auto_save": True,
    "save_interval": 30,  # seconds
}
