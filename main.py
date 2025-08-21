#!/usr/bin/env python3
"""
Personal Finance Management Application
Project ID: UY6758GH

A command-line application for managing personal finances including
income tracking, expense management, budgeting, and financial reporting.
"""

from finance_manager import FinanceManager
from utils import clear_screen, print_header, get_user_input

def main():
    """Main application entry point"""
    clear_screen()
    print_header("Personal Finance Manager")
    
    finance_manager = FinanceManager()
    
    while True:
        if not finance_manager.current_user:
            # User not logged in
            print("\n=== Authentication Menu ===")
            print("1. Login")
            print("2. Register")
            print("3. Exit")
            
            choice = get_user_input("Enter your choice (1-3): ")
            
            if choice == "1":
                finance_manager.login()
            elif choice == "2":
                finance_manager.register()
            elif choice == "3":
                print("Thank you for using Personal Finance Manager!")
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            # User logged in - show main menu
            print(f"\n=== Welcome, {finance_manager.current_user}! ===")
            print("1. Add Income")
            print("2. Add Expense")
            print("3. View Transactions")
            print("4. Update Transaction")
            print("5. Delete Transaction")
            print("6. Generate Reports")
            print("7. Manage Budget")
            print("8. Backup Data")
            print("9. Restore Data")
            print("10. Logout")
            
            choice = get_user_input("Enter your choice (1-10): ")
            
            if choice == "1":
                finance_manager.add_income()
            elif choice == "2":
                finance_manager.add_expense()
            elif choice == "3":
                finance_manager.view_transactions()
            elif choice == "4":
                finance_manager.update_transaction()
            elif choice == "5":
                finance_manager.delete_transaction()
            elif choice == "6":
                finance_manager.generate_reports()
            elif choice == "7":
                finance_manager.manage_budget()
            elif choice == "8":
                finance_manager.backup_data()
            elif choice == "9":
                finance_manager.restore_data()
            elif choice == "10":
                finance_manager.logout()
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()