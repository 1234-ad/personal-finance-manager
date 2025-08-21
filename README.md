# Personal Finance Management Application

**Project ID:** UY6758GH

A comprehensive command-line application for managing personal finances, including income tracking, expense management, budgeting, and financial reporting.

## Features

### 🔐 User Authentication
- Secure user registration with unique usernames
- Password-protected login system
- Encrypted password storage using SHA-256 hashing

### 💰 Transaction Management
- Add, update, and delete income and expense entries
- Categorized transactions (Food, Rent, Salary, etc.)
- Date-based transaction tracking
- Comprehensive transaction history

### 📊 Financial Reports
- Monthly financial reports with category breakdowns
- Yearly financial summaries
- Category-wise spending analysis
- Income vs. expense tracking
- Net savings calculations

### 🎯 Budget Management
- Set monthly budgets for different expense categories
- Real-time budget tracking and warnings
- Budget vs. actual spending comparisons
- Overspending notifications

### 💾 Data Management
- SQLite database for reliable data storage
- Complete data backup to JSON files
- Data restoration from backup files
- Secure data persistence

### 🧪 Testing & Quality
- Comprehensive unit test suite
- Input validation and error handling
- User-friendly interface with clear navigation

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/1234-ad/personal-finance-manager.git
   cd personal-finance-manager
   ```

2. **Ensure Python 3.6+ is installed:**
   ```bash
   python --version
   ```

3. **No additional dependencies required** - uses only Python standard library

## Usage

### Starting the Application
```bash
python main.py
```

### First Time Setup
1. Run the application
2. Select "Register" to create a new account
3. Enter a unique username and secure password
4. Login with your credentials

### Main Features

#### Adding Transactions
- **Income:** Select "Add Income" and follow prompts
- **Expenses:** Select "Add Expense" and choose from predefined categories

#### Managing Budgets
1. Select "Manage Budget"
2. Set monthly limits for expense categories
3. Receive warnings when approaching or exceeding limits

#### Generating Reports
- **Monthly Reports:** View income, expenses, and savings for specific months
- **Yearly Reports:** Annual financial summary with monthly breakdowns
- **Category Reports:** Spending patterns by category

#### Data Backup & Restore
- **Backup:** Creates timestamped JSON files with all your data
- **Restore:** Restore from previous backup files

## File Structure

```
personal-finance-manager/
├── main.py                 # Application entry point
├── finance_manager.py      # Core finance management logic
├── database.py            # Database operations and management
├── utils.py               # Utility functions and validation
├── test_finance_manager.py # Unit tests
├── requirements.txt       # Dependencies (none required)
├── README.md             # This file
└── finance.db            # SQLite database (created automatically)
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `password_hash`: SHA-256 hashed password
- `created_at`: Account creation timestamp

### Transactions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `type`: 'income' or 'expense'
- `amount`: Transaction amount
- `description`: Transaction description
- `category`: Transaction category
- `date`: Transaction date
- `created_at`: Record creation timestamp

### Budgets Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `category`: Budget category
- `amount`: Budget amount
- `created_at`: Budget creation timestamp

## Categories

### Income Categories
- Salary
- Freelance
- Investment
- Business
- Gift
- Other

### Expense Categories
- Food
- Rent
- Transportation
- Entertainment
- Healthcare
- Shopping
- Utilities
- Education
- Travel
- Other

## Testing

Run the comprehensive test suite:

```bash
python test_finance_manager.py
```

The test suite covers:
- Database operations
- User authentication
- Transaction management
- Budget functionality
- Utility functions
- Input validation

## Security Features

- **Password Hashing:** SHA-256 encryption for password storage
- **User Isolation:** Each user can only access their own data
- **Input Validation:** Comprehensive validation for all user inputs
- **Error Handling:** Graceful error handling throughout the application

## Error Handling

The application includes robust error handling for:
- Invalid user inputs
- Database connection issues
- File operation errors
- Data validation failures
- Authentication errors

## Backup Format

Backup files are saved in JSON format with the following structure:
```json
{
  "backup_date": "2024-01-01T12:00:00",
  "transactions": [
    {
      "type": "income",
      "amount": 1000.0,
      "description": "Salary",
      "category": "Salary",
      "date": "2024-01-01"
    }
  ],
  "budgets": [
    {
      "category": "Food",
      "amount": 500.0
    }
  ]
}
```

## Development Timeline

This project was completed following a structured 25-day development plan:

- **Days 1-5:** User Registration and Authentication
- **Days 6-10:** Income and Expense Tracking
- **Days 11-15:** Financial Reports
- **Days 16-20:** Budgeting System
- **Days 21-23:** Data Persistence
- **Days 24-25:** Testing and Documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please contact: internship.innobyteservices@gmail.com

## Future Enhancements

Potential improvements for future versions:
- Web-based interface
- Data visualization with charts
- Multi-currency support
- Recurring transaction templates
- Advanced reporting features
- Mobile application
- Cloud synchronization
- Investment tracking
- Bill reminders
- Financial goal setting

---

**Project completed as part of InnoByteServices internship program.**