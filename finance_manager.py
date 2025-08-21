"""
Core Finance Manager class handling all financial operations
"""

import sqlite3
import hashlib
import getpass
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import DatabaseManager
from utils import get_user_input, validate_amount, validate_date, clear_screen

class FinanceManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
        self.current_user_id = None
        
        # Predefined categories
        self.income_categories = [
            "Salary", "Freelance", "Investment", "Business", "Gift", "Other"
        ]
        self.expense_categories = [
            "Food", "Rent", "Transportation", "Entertainment", "Healthcare",
            "Shopping", "Utilities", "Education", "Travel", "Other"
        ]
    
    def register(self):
        """Register a new user"""
        clear_screen()
        print("=== User Registration ===")
        
        username = get_user_input("Enter username: ").strip()
        if not username:
            print("Username cannot be empty!")
            return
        
        # Check if username exists
        if self.db.get_user(username):
            print("Username already exists! Please choose a different one.")
            return
        
        password = getpass.getpass("Enter password: ")
        if len(password) < 6:
            print("Password must be at least 6 characters long!")
            return
        
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords don't match!")
            return
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user
        if self.db.create_user(username, password_hash):
            print(f"User '{username}' registered successfully!")
        else:
            print("Registration failed. Please try again.")
    
    def login(self):
        """Login user"""
        clear_screen()
        print("=== User Login ===")
        
        username = get_user_input("Enter username: ").strip()
        password = getpass.getpass("Enter password: ")
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = self.db.authenticate_user(username, password_hash)
        if user:
            self.current_user = username
            self.current_user_id = user[0]
            print(f"Welcome back, {username}!")
        else:
            print("Invalid username or password!")
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.current_user_id = None
        print("Logged out successfully!")
    
    def add_income(self):
        """Add income transaction"""
        clear_screen()
        print("=== Add Income ===")
        
        amount = validate_amount(get_user_input("Enter amount: $"))
        if amount is None:
            return
        
        description = get_user_input("Enter description: ").strip()
        if not description:
            print("Description cannot be empty!")
            return
        
        print("\nIncome Categories:")
        for i, category in enumerate(self.income_categories, 1):
            print(f"{i}. {category}")
        
        try:
            cat_choice = int(get_user_input("Select category (number): "))
            if 1 <= cat_choice <= len(self.income_categories):
                category = self.income_categories[cat_choice - 1]
            else:
                print("Invalid category selection!")
                return
        except ValueError:
            print("Please enter a valid number!")
            return
        
        date_str = get_user_input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if not validate_date(date_str):
            print("Invalid date format!")
            return
        
        if self.db.add_transaction(self.current_user_id, "income", amount, 
                                 description, category, date_str):
            print("Income added successfully!")
        else:
            print("Failed to add income!")
    
    def add_expense(self):
        """Add expense transaction"""
        clear_screen()
        print("=== Add Expense ===")
        
        amount = validate_amount(get_user_input("Enter amount: $"))
        if amount is None:
            return
        
        description = get_user_input("Enter description: ").strip()
        if not description:
            print("Description cannot be empty!")
            return
        
        print("\nExpense Categories:")
        for i, category in enumerate(self.expense_categories, 1):
            print(f"{i}. {category}")
        
        try:
            cat_choice = int(get_user_input("Select category (number): "))
            if 1 <= cat_choice <= len(self.expense_categories):
                category = self.expense_categories[cat_choice - 1]
            else:
                print("Invalid category selection!")
                return
        except ValueError:
            print("Please enter a valid number!")
            return
        
        date_str = get_user_input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if not validate_date(date_str):
            print("Invalid date format!")
            return
        
        # Check budget before adding expense
        self._check_budget_warning(category, amount, date_str)
        
        if self.db.add_transaction(self.current_user_id, "expense", amount, 
                                 description, category, date_str):
            print("Expense added successfully!")
        else:
            print("Failed to add expense!")
    
    def view_transactions(self):
        """View all transactions"""
        clear_screen()
        print("=== Transaction History ===")
        
        transactions = self.db.get_user_transactions(self.current_user_id)
        
        if not transactions:
            print("No transactions found.")
            return
        
        print(f"{'ID':<5} {'Type':<8} {'Amount':<12} {'Category':<15} {'Description':<20} {'Date':<12}")
        print("-" * 80)
        
        for transaction in transactions:
            trans_id, _, trans_type, amount, description, category, date = transaction
            amount_str = f"${amount:.2f}"
            print(f"{trans_id:<5} {trans_type:<8} {amount_str:<12} {category:<15} {description[:18]:<20} {date:<12}")
        
        input("\nPress Enter to continue...")
    
    def update_transaction(self):
        """Update existing transaction"""
        clear_screen()
        print("=== Update Transaction ===")
        
        try:
            trans_id = int(get_user_input("Enter transaction ID to update: "))
        except ValueError:
            print("Please enter a valid transaction ID!")
            return
        
        transaction = self.db.get_transaction(trans_id, self.current_user_id)
        if not transaction:
            print("Transaction not found or you don't have permission to update it!")
            return
        
        _, _, trans_type, old_amount, old_desc, old_category, old_date = transaction
        
        print(f"\nCurrent transaction details:")
        print(f"Type: {trans_type}")
        print(f"Amount: ${old_amount:.2f}")
        print(f"Description: {old_desc}")
        print(f"Category: {old_category}")
        print(f"Date: {old_date}")
        
        print("\nEnter new values (press Enter to keep current value):")
        
        # Update amount
        new_amount_str = get_user_input(f"Amount (${old_amount:.2f}): ").strip()
        new_amount = validate_amount(new_amount_str) if new_amount_str else old_amount
        if new_amount is None:
            new_amount = old_amount
        
        # Update description
        new_desc = get_user_input(f"Description ({old_desc}): ").strip()
        if not new_desc:
            new_desc = old_desc
        
        # Update category
        categories = self.income_categories if trans_type == "income" else self.expense_categories
        print(f"\nCurrent category: {old_category}")
        print("Categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        cat_input = get_user_input("Select new category (number) or press Enter to keep current: ").strip()
        if cat_input:
            try:
                cat_choice = int(cat_input)
                if 1 <= cat_choice <= len(categories):
                    new_category = categories[cat_choice - 1]
                else:
                    new_category = old_category
            except ValueError:
                new_category = old_category
        else:
            new_category = old_category
        
        # Update date
        new_date = get_user_input(f"Date ({old_date}): ").strip()
        if not new_date:
            new_date = old_date
        elif not validate_date(new_date):
            print("Invalid date format! Keeping original date.")
            new_date = old_date
        
        if self.db.update_transaction(trans_id, new_amount, new_desc, new_category, new_date):
            print("Transaction updated successfully!")
        else:
            print("Failed to update transaction!")
    
    def delete_transaction(self):
        """Delete transaction"""
        clear_screen()
        print("=== Delete Transaction ===")
        
        try:
            trans_id = int(get_user_input("Enter transaction ID to delete: "))
        except ValueError:
            print("Please enter a valid transaction ID!")
            return
        
        transaction = self.db.get_transaction(trans_id, self.current_user_id)
        if not transaction:
            print("Transaction not found or you don't have permission to delete it!")
            return
        
        _, _, trans_type, amount, desc, category, date = transaction
        print(f"\nTransaction to delete:")
        print(f"Type: {trans_type}")
        print(f"Amount: ${amount:.2f}")
        print(f"Description: {desc}")
        print(f"Category: {category}")
        print(f"Date: {date}")
        
        confirm = get_user_input("\nAre you sure you want to delete this transaction? (y/N): ").lower()
        if confirm == 'y':
            if self.db.delete_transaction(trans_id):
                print("Transaction deleted successfully!")
            else:
                print("Failed to delete transaction!")
        else:
            print("Deletion cancelled.")
    
    def generate_reports(self):
        """Generate financial reports"""
        clear_screen()
        print("=== Financial Reports ===")
        print("1. Monthly Report")
        print("2. Yearly Report")
        print("3. Category Summary")
        
        choice = get_user_input("Select report type (1-3): ")
        
        if choice == "1":
            self._generate_monthly_report()
        elif choice == "2":
            self._generate_yearly_report()
        elif choice == "3":
            self._generate_category_summary()
        else:
            print("Invalid choice!")
    
    def _generate_monthly_report(self):
        """Generate monthly financial report"""
        month_year = get_user_input("Enter month and year (YYYY-MM) or press Enter for current month: ").strip()
        
        if not month_year:
            now = datetime.now()
            month_year = now.strftime("%Y-%m")
        
        try:
            year, month = map(int, month_year.split("-"))
            if not (1 <= month <= 12):
                raise ValueError
        except ValueError:
            print("Invalid month format! Use YYYY-MM")
            return
        
        report = self.db.get_monthly_report(self.current_user_id, year, month)
        
        print(f"\n=== Monthly Report for {month_year} ===")
        print(f"Total Income: ${report['total_income']:.2f}")
        print(f"Total Expenses: ${report['total_expenses']:.2f}")
        print(f"Net Savings: ${report['net_savings']:.2f}")
        
        if report['income_by_category']:
            print("\nIncome by Category:")
            for category, amount in report['income_by_category'].items():
                print(f"  {category}: ${amount:.2f}")
        
        if report['expenses_by_category']:
            print("\nExpenses by Category:")
            for category, amount in report['expenses_by_category'].items():
                print(f"  {category}: ${amount:.2f}")
        
        input("\nPress Enter to continue...")
    
    def _generate_yearly_report(self):
        """Generate yearly financial report"""
        year_str = get_user_input("Enter year (YYYY) or press Enter for current year: ").strip()
        
        if not year_str:
            year = datetime.now().year
        else:
            try:
                year = int(year_str)
            except ValueError:
                print("Invalid year format!")
                return
        
        report = self.db.get_yearly_report(self.current_user_id, year)
        
        print(f"\n=== Yearly Report for {year} ===")
        print(f"Total Income: ${report['total_income']:.2f}")
        print(f"Total Expenses: ${report['total_expenses']:.2f}")
        print(f"Net Savings: ${report['net_savings']:.2f}")
        
        if report['monthly_summary']:
            print("\nMonthly Summary:")
            for month_data in report['monthly_summary']:
                month_name = datetime(year, month_data['month'], 1).strftime("%B")
                print(f"  {month_name}: Income ${month_data['income']:.2f}, "
                      f"Expenses ${month_data['expenses']:.2f}, "
                      f"Savings ${month_data['savings']:.2f}")
        
        input("\nPress Enter to continue...")
    
    def _generate_category_summary(self):
        """Generate category-wise summary"""
        print("\n=== Category Summary ===")
        
        summary = self.db.get_category_summary(self.current_user_id)
        
        if summary['income_categories']:
            print("\nIncome Categories (Total):")
            for category, amount in summary['income_categories'].items():
                print(f"  {category}: ${amount:.2f}")
        
        if summary['expense_categories']:
            print("\nExpense Categories (Total):")
            for category, amount in summary['expense_categories'].items():
                print(f"  {category}: ${amount:.2f}")
        
        input("\nPress Enter to continue...")
    
    def manage_budget(self):
        """Manage budget settings"""
        clear_screen()
        print("=== Budget Management ===")
        print("1. Set Monthly Budget")
        print("2. View Current Budgets")
        print("3. Update Budget")
        print("4. Delete Budget")
        
        choice = get_user_input("Select option (1-4): ")
        
        if choice == "1":
            self._set_budget()
        elif choice == "2":
            self._view_budgets()
        elif choice == "3":
            self._update_budget()
        elif choice == "4":
            self._delete_budget()
        else:
            print("Invalid choice!")
    
    def _set_budget(self):
        """Set monthly budget for a category"""
        print("\nExpense Categories:")
        for i, category in enumerate(self.expense_categories, 1):
            print(f"{i}. {category}")
        
        try:
            cat_choice = int(get_user_input("Select category (number): "))
            if 1 <= cat_choice <= len(self.expense_categories):
                category = self.expense_categories[cat_choice - 1]
            else:
                print("Invalid category selection!")
                return
        except ValueError:
            print("Please enter a valid number!")
            return
        
        amount = validate_amount(get_user_input(f"Enter monthly budget for {category}: $"))
        if amount is None:
            return
        
        if self.db.set_budget(self.current_user_id, category, amount):
            print(f"Budget set for {category}: ${amount:.2f}/month")
        else:
            print("Failed to set budget!")
    
    def _view_budgets(self):
        """View current budgets"""
        budgets = self.db.get_user_budgets(self.current_user_id)
        
        if not budgets:
            print("No budgets set.")
            return
        
        print("\nCurrent Monthly Budgets:")
        print(f"{'Category':<15} {'Budget':<12} {'Spent':<12} {'Remaining':<12} {'Status'}")
        print("-" * 65)
        
        current_month = datetime.now().strftime("%Y-%m")
        
        for budget in budgets:
            category, budget_amount = budget[2], budget[3]
            spent = self.db.get_monthly_spending(self.current_user_id, category, current_month)
            remaining = budget_amount - spent
            status = "Over Budget" if remaining < 0 else "On Track"
            
            print(f"{category:<15} ${budget_amount:<11.2f} ${spent:<11.2f} ${remaining:<11.2f} {status}")
        
        input("\nPress Enter to continue...")
    
    def _update_budget(self):
        """Update existing budget"""
        budgets = self.db.get_user_budgets(self.current_user_id)
        
        if not budgets:
            print("No budgets set.")
            return
        
        print("\nCurrent Budgets:")
        for i, budget in enumerate(budgets, 1):
            print(f"{i}. {budget[2]}: ${budget[3]:.2f}")
        
        try:
            choice = int(get_user_input("Select budget to update (number): "))
            if 1 <= choice <= len(budgets):
                budget = budgets[choice - 1]
                category = budget[2]
                
                new_amount = validate_amount(get_user_input(f"Enter new budget amount for {category}: $"))
                if new_amount is None:
                    return
                
                if self.db.update_budget(budget[0], new_amount):
                    print(f"Budget updated for {category}: ${new_amount:.2f}/month")
                else:
                    print("Failed to update budget!")
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!")
    
    def _delete_budget(self):
        """Delete existing budget"""
        budgets = self.db.get_user_budgets(self.current_user_id)
        
        if not budgets:
            print("No budgets set.")
            return
        
        print("\nCurrent Budgets:")
        for i, budget in enumerate(budgets, 1):
            print(f"{i}. {budget[2]}: ${budget[3]:.2f}")
        
        try:
            choice = int(get_user_input("Select budget to delete (number): "))
            if 1 <= choice <= len(budgets):
                budget = budgets[choice - 1]
                category = budget[2]
                
                confirm = get_user_input(f"Delete budget for {category}? (y/N): ").lower()
                if confirm == 'y':
                    if self.db.delete_budget(budget[0]):
                        print(f"Budget deleted for {category}")
                    else:
                        print("Failed to delete budget!")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!")
    
    def _check_budget_warning(self, category: str, amount: float, date_str: str):
        """Check if expense exceeds budget and warn user"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_year = date_obj.strftime("%Y-%m")
            
            budget = self.db.get_category_budget(self.current_user_id, category)
            if budget:
                current_spending = self.db.get_monthly_spending(self.current_user_id, category, month_year)
                new_total = current_spending + amount
                
                if new_total > budget:
                    print(f"\n⚠️  WARNING: This expense will exceed your monthly budget for {category}!")
                    print(f"Budget: ${budget:.2f}")
                    print(f"Current spending: ${current_spending:.2f}")
                    print(f"New total: ${new_total:.2f}")
                    print(f"Over budget by: ${new_total - budget:.2f}")
                    
                    confirm = get_user_input("Do you want to continue? (y/N): ").lower()
                    if confirm != 'y':
                        print("Expense cancelled.")
                        return False
        except Exception as e:
            pass  # Continue if budget check fails
        
        return True
    
    def backup_data(self):
        """Backup user data to JSON file"""
        clear_screen()
        print("=== Backup Data ===")
        
        try:
            backup_data = self.db.get_user_backup_data(self.current_user_id)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"finance_backup_{self.current_user}_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"Data backed up successfully to: {filename}")
            
        except Exception as e:
            print(f"Backup failed: {str(e)}")
        
        input("Press Enter to continue...")
    
    def restore_data(self):
        """Restore user data from JSON file"""
        clear_screen()
        print("=== Restore Data ===")
        
        filename = get_user_input("Enter backup filename: ").strip()
        
        if not os.path.exists(filename):
            print("Backup file not found!")
            return
        
        try:
            with open(filename, 'r') as f:
                backup_data = json.load(f)
            
            print("\n⚠️  WARNING: This will replace all your current data!")
            confirm = get_user_input("Are you sure you want to restore? (y/N): ").lower()
            
            if confirm == 'y':
                if self.db.restore_user_data(self.current_user_id, backup_data):
                    print("Data restored successfully!")
                else:
                    print("Restore failed!")
            else:
                print("Restore cancelled.")
                
        except Exception as e:
            print(f"Restore failed: {str(e)}")
        
        input("Press Enter to continue...")