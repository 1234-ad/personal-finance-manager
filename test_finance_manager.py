"""
Unit tests for Personal Finance Management Application
"""

import unittest
import os
import tempfile
import sqlite3
from datetime import datetime
from database import DatabaseManager
from finance_manager import FinanceManager
from utils import validate_amount, validate_date, validate_username

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.db = DatabaseManager(self.test_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.test_db.name)
    
    def test_create_user(self):
        """Test user creation"""
        result = self.db.create_user("testuser", "hashedpassword")
        self.assertTrue(result)
        
        # Test duplicate username
        result = self.db.create_user("testuser", "anotherpassword")
        self.assertFalse(result)
    
    def test_authenticate_user(self):
        """Test user authentication"""
        self.db.create_user("testuser", "hashedpassword")
        
        # Valid credentials
        user = self.db.authenticate_user("testuser", "hashedpassword")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "testuser")
        
        # Invalid credentials
        user = self.db.authenticate_user("testuser", "wrongpassword")
        self.assertIsNone(user)
    
    def test_add_transaction(self):
        """Test adding transactions"""
        self.db.create_user("testuser", "hashedpassword")
        user = self.db.authenticate_user("testuser", "hashedpassword")
        user_id = user[0]
        
        result = self.db.add_transaction(
            user_id, "income", 1000.0, "Salary", "Salary", "2024-01-01"
        )
        self.assertTrue(result)
        
        transactions = self.db.get_user_transactions(user_id)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][3], 1000.0)  # amount
    
    def test_budget_operations(self):
        """Test budget operations"""
        self.db.create_user("testuser", "hashedpassword")
        user = self.db.authenticate_user("testuser", "hashedpassword")
        user_id = user[0]
        
        # Set budget
        result = self.db.set_budget(user_id, "Food", 500.0)
        self.assertTrue(result)
        
        # Get budgets
        budgets = self.db.get_user_budgets(user_id)
        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0][2], "Food")  # category
        self.assertEqual(budgets[0][3], 500.0)   # amount
    
    def test_monthly_report(self):
        """Test monthly report generation"""
        self.db.create_user("testuser", "hashedpassword")
        user = self.db.authenticate_user("testuser", "hashedpassword")
        user_id = user[0]
        
        # Add test transactions
        self.db.add_transaction(user_id, "income", 2000.0, "Salary", "Salary", "2024-01-15")
        self.db.add_transaction(user_id, "expense", 500.0, "Groceries", "Food", "2024-01-20")
        
        report = self.db.get_monthly_report(user_id, 2024, 1)
        
        self.assertEqual(report['total_income'], 2000.0)
        self.assertEqual(report['total_expenses'], 500.0)
        self.assertEqual(report['net_savings'], 1500.0)

class TestUtils(unittest.TestCase):
    def test_validate_amount(self):
        """Test amount validation"""
        self.assertEqual(validate_amount("100"), 100.0)
        self.assertEqual(validate_amount("100.50"), 100.5)
        self.assertEqual(validate_amount("$100.50"), 100.5)
        self.assertEqual(validate_amount("1,000.50"), 1000.5)
        self.assertIsNone(validate_amount(""))
        self.assertIsNone(validate_amount("abc"))
        self.assertIsNone(validate_amount("-100"))
        self.assertIsNone(validate_amount("0"))
    
    def test_validate_date(self):
        """Test date validation"""
        self.assertTrue(validate_date("2024-01-01"))
        self.assertTrue(validate_date("2024-12-31"))
        self.assertFalse(validate_date("2024-13-01"))
        self.assertFalse(validate_date("2024-01-32"))
        self.assertFalse(validate_date("01-01-2024"))
        self.assertFalse(validate_date(""))
        self.assertFalse(validate_date("invalid"))
    
    def test_validate_username(self):
        """Test username validation"""
        self.assertTrue(validate_username("user123"))
        self.assertTrue(validate_username("test_user"))
        self.assertTrue(validate_username("User"))
        self.assertFalse(validate_username("us"))  # too short
        self.assertFalse(validate_username(""))
        self.assertFalse(validate_username("user@domain"))  # invalid chars
        self.assertFalse(validate_username("a" * 21))  # too long

class TestFinanceManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        
        # Create finance manager with test database
        self.finance_manager = FinanceManager()
        self.finance_manager.db = DatabaseManager(self.test_db.name)
        
        # Create test user
        self.finance_manager.db.create_user("testuser", "hashedpassword")
        user = self.finance_manager.db.authenticate_user("testuser", "hashedpassword")
        self.finance_manager.current_user = "testuser"
        self.finance_manager.current_user_id = user[0]
    
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.test_db.name)
    
    def test_categories(self):
        """Test predefined categories"""
        self.assertIn("Salary", self.finance_manager.income_categories)
        self.assertIn("Food", self.finance_manager.expense_categories)
        self.assertIn("Rent", self.finance_manager.expense_categories)
    
    def test_budget_warning_check(self):
        """Test budget warning functionality"""
        # Set a budget
        self.finance_manager.db.set_budget(
            self.finance_manager.current_user_id, "Food", 500.0
        )
        
        # Add some expenses
        self.finance_manager.db.add_transaction(
            self.finance_manager.current_user_id, "expense", 
            300.0, "Groceries", "Food", "2024-01-15"
        )
        
        # This should trigger a warning (300 + 300 > 500)
        result = self.finance_manager._check_budget_warning("Food", 300.0, "2024-01-20")
        # Note: This test would need user input simulation for full testing

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDatabaseManager))
    test_suite.addTest(unittest.makeSuite(TestUtils))
    test_suite.addTest(unittest.makeSuite(TestFinanceManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")