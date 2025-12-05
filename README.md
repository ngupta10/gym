# Gym Management System

A simple desktop application for managing gym operations including members, staff, holidays, and fee payments.

## Features

### 🏋️ Member Management
- Register new members with membership details
- Remove/deactivate members
- View member information and details
- Track membership types and payment schedules

### 👔 Staff Management
- Add new staff members
- Remove/deactivate staff
- View staff details and information
- Track staff positions and hire dates

### 🏖️ Holiday & Leave Management
- Record staff holidays and leave
- View holiday records
- Track leave dates and reasons
- Filter holidays by date range

### 💰 Fee & Payment Management
- Record member payments
- Track payment history
- Automatic calculation of next payment dates
- **Payment Alerts:**
  - Overdue payment notifications
  - Upcoming payment reminders (7 days in advance)
- View payment details for each member

### 📊 Dashboard
- Overview statistics (members, staff, alerts)
- Real-time payment alerts
- Quick access to all features

## Requirements

- **Python 3.7 or higher**
- **tkinter** (usually included with Python)
  - If not available:
    - Ubuntu/Debian: `sudo apt-get install python3-tk`
    - macOS: Usually included
    - Windows: Included with Python

## Installation

1. Clone or download this repository
2. Ensure Python 3.7+ is installed
3. No additional packages needed! The application uses only Python standard library.

## Usage

1. Run the application:
```bash
python main.py
```

2. The application will automatically create a SQLite database file (`gym_management.db`) in the same directory on first run.

3. Navigate through the application using the sidebar menu:
   - **Dashboard**: Overview and alerts
   - **Members**: Manage gym members
   - **Staff**: Manage staff members
   - **Holidays**: Record and view staff holidays
   - **Fees & Payments**: Record payments and view alerts

## Database

The application uses SQLite database (`gym_management.db`) which is created automatically. The database includes:

- **members**: Member information and payment schedules
- **staff**: Staff member details
- **holidays**: Staff holiday/leave records
- **payments**: Payment history

## Features in Detail

### Member Registration
When registering a member, you need to provide:
- Name (required)
- Email (optional)
- Phone (optional)
- Membership Type (Standard, Premium, VIP, Student, Senior)
- Fee Amount (required)
- Payment Frequency (Daily, Monthly, Quarterly, Yearly)

The system automatically calculates the next payment date based on the payment frequency.

### Payment Alerts
The system automatically tracks:
- **Overdue Payments**: Members whose payment date has passed
- **Due Soon**: Members with payments due within 7 days

Alerts are displayed on the Dashboard and in the Fee Management section.

### Staff Holidays
Record staff holidays with:
- Staff member selection
- Start and end dates
- Reason (optional)

## File Structure

```
gym/
├── main.py                 # Main application entry point
├── database.py             # Database operations
├── member_management.py   # Member management module
├── staff_management.py     # Staff management module
├── holiday_management.py  # Holiday management module
├── fee_management.py      # Fee and payment management
├── requirements.txt       # Requirements (none needed!)
├── README.md             # This file
└── gym_management.db     # SQLite database (created automatically)
```

## Notes

- All data is stored locally in SQLite database
- Members and staff are "soft deleted" (status set to inactive) when removed
- Payment dates are automatically calculated based on payment frequency
- The application is designed for single-user desktop use

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'tkinter'`
- **Solution**: Install tkinter for your system (see Requirements section)

**Issue**: Database errors
- **Solution**: Ensure you have write permissions in the application directory

**Issue**: Application won't start
- **Solution**: Check Python version with `python --version` (needs 3.7+)

## License

This is a simple application for gym management. Feel free to modify and use as needed.

## Support

For issues or questions, check the code comments or modify as needed for your specific requirements.

