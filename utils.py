"""
Utility functions for Personal Finance Application
"""

import os
import re
from datetime import datetime
from typing import Optional, Tuple

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Print formatted header"""
    print("=" * 60)
    print(f"{title:^60}")
    print("=" * 60)

def get_user_input(prompt: str) -> str:
    """Get user input with prompt"""
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return ""
    except EOFError:
        return ""

def validate_amount(amount_str: str) -> Optional[float]:
    """Validate and convert amount string to float"""
    if not amount_str:
        print("Amount cannot be empty!")
        return None
    
    # Remove dollar sign and spaces
    amount_str = amount_str.replace('$', '').replace(',', '').strip()
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("Amount must be greater than 0!")
            return None
        if amount > 999999999:
            print("Amount is too large!")
            return None
        return round(amount, 2)
    except ValueError:
        print("Invalid amount format! Please enter a valid number.")
        return None

def validate_date(date_str: str) -> bool:
    """Validate date string in YYYY-MM-DD format"""
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def get_month_name(month: int) -> str:
    """Get month name from month number"""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[month - 1] if 1 <= month <= 12 else "Unknown"

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username:
        return False
    
    # Username should be 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 50:
        return False, "Password must be less than 50 characters"
    
    # Check for at least one letter and one number
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        return False, "Password must contain at least one letter and one number"
    
    return True, "Password is valid"

def truncate_string(text: str, max_length: int) -> str:
    """Truncate string to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def get_current_month_year() -> str:
    """Get current month and year in YYYY-MM format"""
    return datetime.now().strftime("%Y-%m")

def get_current_year() -> int:
    """Get current year"""
    return datetime.now().year

def parse_month_year(month_year_str: str) -> Optional[Tuple[int, int]]:
    """Parse month-year string and return (year, month) tuple"""
    try:
        year, month = map(int, month_year_str.split('-'))
        if 1 <= month <= 12 and 1900 <= year <= 2100:
            return year, month
        return None
    except (ValueError, AttributeError):
        return None