"""
Database management for Personal Finance Application
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

class DatabaseManager:
    def __init__(self, db_name: str = "finance.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Budgets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, category)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, username: str, password_hash: str) -> bool:
        """Create a new user"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception:
            return False
    
    def get_user(self, username: str) -> Optional[Tuple]:
        """Get user by username"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password_hash FROM users WHERE username = ?",
                    (username,)
                )
                return cursor.fetchone()
        except Exception:
            return None
    
    def authenticate_user(self, username: str, password_hash: str) -> Optional[Tuple]:
        """Authenticate user credentials"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
                    (username, password_hash)
                )
                return cursor.fetchone()
        except Exception:
            return None
    
    def add_transaction(self, user_id: int, trans_type: str, amount: float, 
                       description: str, category: str, date: str) -> bool:
        """Add a new transaction"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO transactions 
                       (user_id, type, amount, description, category, date) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (user_id, trans_type, amount, description, category, date)
                )
                conn.commit()
                return True
        except Exception:
            return False
    
    def get_user_transactions(self, user_id: int) -> List[Tuple]:
        """Get all transactions for a user"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT id, user_id, type, amount, description, category, date 
                       FROM transactions WHERE user_id = ? 
                       ORDER BY date DESC, id DESC''',
                    (user_id,)
                )
                return cursor.fetchall()
        except Exception:
            return []
    
    def get_transaction(self, trans_id: int, user_id: int) -> Optional[Tuple]:
        """Get specific transaction"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT id, user_id, type, amount, description, category, date 
                       FROM transactions WHERE id = ? AND user_id = ?''',
                    (trans_id, user_id)
                )
                return cursor.fetchone()
        except Exception:
            return None
    
    def update_transaction(self, trans_id: int, amount: float, description: str, 
                          category: str, date: str) -> bool:
        """Update existing transaction"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''UPDATE transactions 
                       SET amount = ?, description = ?, category = ?, date = ? 
                       WHERE id = ?''',
                    (amount, description, category, date, trans_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def delete_transaction(self, trans_id: int) -> bool:
        """Delete transaction"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def get_monthly_report(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Generate monthly financial report"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Get monthly totals
                cursor.execute(
                    '''SELECT type, SUM(amount) FROM transactions 
                       WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
                       GROUP BY type''',
                    (user_id, str(year), f"{month:02d}")
                )
                
                totals = dict(cursor.fetchall())
                total_income = totals.get('income', 0)
                total_expenses = totals.get('expense', 0)
                
                # Get income by category
                cursor.execute(
                    '''SELECT category, SUM(amount) FROM transactions 
                       WHERE user_id = ? AND type = 'income' 
                       AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
                       GROUP BY category''',
                    (user_id, str(year), f"{month:02d}")
                )
                income_by_category = dict(cursor.fetchall())
                
                # Get expenses by category
                cursor.execute(
                    '''SELECT category, SUM(amount) FROM transactions 
                       WHERE user_id = ? AND type = 'expense' 
                       AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
                       GROUP BY category''',
                    (user_id, str(year), f"{month:02d}")
                )
                expenses_by_category = dict(cursor.fetchall())
                
                return {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net_savings': total_income - total_expenses,
                    'income_by_category': income_by_category,
                    'expenses_by_category': expenses_by_category
                }
        except Exception:
            return {
                'total_income': 0,
                'total_expenses': 0,
                'net_savings': 0,
                'income_by_category': {},
                'expenses_by_category': {}
            }
    
    def get_yearly_report(self, user_id: int, year: int) -> Dict[str, Any]:
        """Generate yearly financial report"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Get yearly totals
                cursor.execute(
                    '''SELECT type, SUM(amount) FROM transactions 
                       WHERE user_id = ? AND strftime('%Y', date) = ?
                       GROUP BY type''',
                    (user_id, str(year))
                )
                
                totals = dict(cursor.fetchall())
                total_income = totals.get('income', 0)
                total_expenses = totals.get('expense', 0)
                
                # Get monthly summary
                cursor.execute(
                    '''SELECT strftime('%m', date) as month, type, SUM(amount) 
                       FROM transactions 
                       WHERE user_id = ? AND strftime('%Y', date) = ?
                       GROUP BY month, type
                       ORDER BY month''',
                    (user_id, str(year))
                )
                
                monthly_data = {}
                for row in cursor.fetchall():
                    month, trans_type, amount = row
                    month_int = int(month)
                    if month_int not in monthly_data:
                        monthly_data[month_int] = {'income': 0, 'expenses': 0}
                    
                    if trans_type == 'income':
                        monthly_data[month_int]['income'] = amount
                    else:
                        monthly_data[month_int]['expenses'] = amount
                
                monthly_summary = []
                for month in range(1, 13):
                    data = monthly_data.get(month, {'income': 0, 'expenses': 0})
                    monthly_summary.append({
                        'month': month,
                        'income': data['income'],
                        'expenses': data['expenses'],
                        'savings': data['income'] - data['expenses']
                    })
                
                return {
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net_savings': total_income - total_expenses,
                    'monthly_summary': monthly_summary
                }
        except Exception:
            return {
                'total_income': 0,
                'total_expenses': 0,
                'net_savings': 0,
                'monthly_summary': []
            }
    
    def get_category_summary(self, user_id: int) -> Dict[str, Dict[str, float]]:
        """Get category-wise summary"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Income categories
                cursor.execute(
                    '''SELECT category, SUM(amount) FROM transactions 
                       WHERE user_id = ? AND type = 'income'
                       GROUP BY category''',
                    (user_id,)
                )
                income_categories = dict(cursor.fetchall())
                
                # Expense categories
                cursor.execute(
                    '''SELECT category, SUM(amount) FROM transactions 
                       WHERE user_id = ? AND type = 'expense'
                       GROUP BY category''',
                    (user_id,)
                )
                expense_categories = dict(cursor.fetchall())
                
                return {
                    'income_categories': income_categories,
                    'expense_categories': expense_categories
                }
        except Exception:
            return {'income_categories': {}, 'expense_categories': {}}
    
    def set_budget(self, user_id: int, category: str, amount: float) -> bool:
        """Set budget for a category"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT OR REPLACE INTO budgets (user_id, category, amount) 
                       VALUES (?, ?, ?)''',
                    (user_id, category, amount)
                )
                conn.commit()
                return True
        except Exception:
            return False
    
    def get_user_budgets(self, user_id: int) -> List[Tuple]:
        """Get all budgets for a user"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, user_id, category, amount FROM budgets WHERE user_id = ?",
                    (user_id,)
                )
                return cursor.fetchall()
        except Exception:
            return []
    
    def get_category_budget(self, user_id: int, category: str) -> Optional[float]:
        """Get budget amount for specific category"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT amount FROM budgets WHERE user_id = ? AND category = ?",
                    (user_id, category)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception:
            return None
    
    def update_budget(self, budget_id: int, amount: float) -> bool:
        """Update budget amount"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE budgets SET amount = ? WHERE id = ?",
                    (amount, budget_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def delete_budget(self, budget_id: int) -> bool:
        """Delete budget"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def get_monthly_spending(self, user_id: int, category: str, month_year: str) -> float:
        """Get total spending for a category in a specific month"""
        try:
            year, month = month_year.split('-')
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT COALESCE(SUM(amount), 0) FROM transactions 
                       WHERE user_id = ? AND category = ? AND type = 'expense'
                       AND strftime('%Y', date) = ? AND strftime('%m', date) = ?''',
                    (user_id, category, year, f"{int(month):02d}")
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0
    
    def get_user_backup_data(self, user_id: int) -> Dict[str, Any]:
        """Get all user data for backup"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Get transactions
                cursor.execute(
                    '''SELECT type, amount, description, category, date 
                       FROM transactions WHERE user_id = ?''',
                    (user_id,)
                )
                transactions = [
                    {
                        'type': row[0],
                        'amount': row[1],
                        'description': row[2],
                        'category': row[3],
                        'date': row[4]
                    }
                    for row in cursor.fetchall()
                ]
                
                # Get budgets
                cursor.execute(
                    "SELECT category, amount FROM budgets WHERE user_id = ?",
                    (user_id,)
                )
                budgets = [
                    {'category': row[0], 'amount': row[1]}
                    for row in cursor.fetchall()
                ]
                
                return {
                    'backup_date': datetime.now().isoformat(),
                    'transactions': transactions,
                    'budgets': budgets
                }
        except Exception:
            return {'backup_date': datetime.now().isoformat(), 'transactions': [], 'budgets': []}
    
    def restore_user_data(self, user_id: int, backup_data: Dict[str, Any]) -> bool:
        """Restore user data from backup"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Clear existing data
                cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
                
                # Restore transactions
                for trans in backup_data.get('transactions', []):
                    cursor.execute(
                        '''INSERT INTO transactions 
                           (user_id, type, amount, description, category, date) 
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (user_id, trans['type'], trans['amount'], 
                         trans['description'], trans['category'], trans['date'])
                    )
                
                # Restore budgets
                for budget in backup_data.get('budgets', []):
                    cursor.execute(
                        "INSERT INTO budgets (user_id, category, amount) VALUES (?, ?, ?)",
                        (user_id, budget['category'], budget['amount'])
                    )
                
                conn.commit()
                return True
        except Exception:
            return False