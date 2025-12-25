"""
Configuration management for Vyapar Vidya
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===================== LOGGING SETUP =====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)

# ===================== API CONFIGURATION =====================

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_YOUR_GROQ_API_KEY_HERE")
GROQ_MODEL = "llama-3.1-8b-instant"

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "YOUR_GOOGLE_SHEET_ID")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")

# ===================== SHEET NAMES =====================

SHEET_SALES = "Sales"
SHEET_INVENTORY = "Inventory"
SHEET_EXPENSES = "Expenses"
SHEET_CUSTOMERS = "Customers"
SHEET_SUMMARY = "Summary"

# ===================== BUSINESS SETTINGS =====================

# GST rates (in percentage)
GST_RATES = {
    "0%": 0,
    "5%": 5,
    "12%": 12,
    "18%": 18,
    "28%": 28
}

DEFAULT_GST_RATE = 18  # Default GST rate

# Currency symbol
CURRENCY = "₹"

# Date format
DATE_FORMAT = "%Y-%m-%d"

# ===================== VALIDATION =====================

def validate_config():
    """Validate configuration and return warnings"""
    warnings = []

    if GROQ_API_KEY == "gsk_YOUR_GROQ_API_KEY_HERE":
        warnings.append("GROQ_API_KEY not set - using placeholder")

    if GOOGLE_SHEET_ID == "YOUR_GOOGLE_SHEET_ID":
        warnings.append("GOOGLE_SHEET_ID not set - using placeholder")

    if not os.path.exists(CREDENTIALS_FILE):
        warnings.append(f"Credentials file '{CREDENTIALS_FILE}' not found")

    return warnings
