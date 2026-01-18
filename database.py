"""
Database module for Gym Management System
Handles all database operations using SQLite
"""
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class Database:
    def __init__(self, db_path: str = "gym_management.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.create_tables()
        self.migrate_database()  # Run migrations for existing databases
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        # Members table - Using PRIMARY KEY without AUTOINCREMENT to allow ID reuse
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                join_date DATE NOT NULL,
                membership_type TEXT NOT NULL,
                fee_amount REAL NOT NULL,
                payment_frequency TEXT NOT NULL,
                last_payment_date DATE,
                next_payment_date DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Staff table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                position TEXT,
                hire_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Holidays/Leave table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'approved',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff(id)
            )
        """)
        
        # Payment history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)
        
        # Lockers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lockers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                locker_number TEXT,
                fee_amount REAL NOT NULL,
                payment_frequency TEXT NOT NULL,
                start_date DATE NOT NULL,
                last_payment_date DATE,
                next_payment_date DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)
        
        # Locker payment history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locker_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                locker_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (locker_id) REFERENCES lockers(id),
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)
        
        self.conn.commit()
    
    def migrate_database(self):
        """Migrate existing database schema to add new columns"""
        cursor = self.conn.cursor()
        
        # Check if trainer_id column exists in members table
        cursor.execute("PRAGMA table_info(members)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'trainer_id' not in columns:
            try:
                cursor.execute("ALTER TABLE members ADD COLUMN trainer_id INTEGER")
                self.conn.commit()
                print("Database migrated: Added trainer_id column to members table")
            except sqlite3.OperationalError as e:
                print(f"Migration warning: {e}")
        
        # Migration: Reset SQLite sequence for ID reuse
        # If the table was created with AUTOINCREMENT, SQLite maintains a sequence table
        # We need to reset it to allow ID reuse
        try:
            # Check if sqlite_sequence table exists and has an entry for members
            cursor.execute("""
                SELECT name, seq FROM sqlite_sequence WHERE name = 'members'
            """)
            sequence_row = cursor.fetchone()
            if sequence_row:
                # Get the current highest ID from the actual members table
                cursor.execute("SELECT COALESCE(MAX(id), 0) FROM members")
                max_id_row = cursor.fetchone()
                max_id = max_id_row[0] if max_id_row else 0
                
                # Update the sequence to match the actual max ID
                # This ensures IDs can be reused properly
                cursor.execute("""
                    UPDATE sqlite_sequence SET seq = ? WHERE name = 'members'
                """, (max_id,))
                self.conn.commit()
                print(f"Database migrated: Reset SQLite sequence for members table (max_id: {max_id})")
        except sqlite3.OperationalError:
            # sqlite_sequence table doesn't exist or members table doesn't use AUTOINCREMENT
            # This is fine - it means we're already using manual ID assignment
            pass
        except Exception as e:
            print(f"Migration warning (sequence reset): {e}")
        
        self.conn.commit()
    
    def _get_next_available_id(self) -> int:
        """Find the next available (lowest unused) member ID"""
        cursor = self.conn.cursor()
        
        # Get all existing IDs from the members table
        cursor.execute("SELECT id FROM members ORDER BY id")
        existing_ids = {row[0] for row in cursor.fetchall()}
        
        # Find the lowest unused ID starting from 1
        next_id = 1
        while next_id in existing_ids:
            next_id += 1
        
        # CRITICAL: Reset SQLite sequence table if it exists
        # This ensures that even if the table was created with AUTOINCREMENT,
        # SQLite won't try to use a higher sequence number
        try:
            # Check if sqlite_sequence table exists and has entry for members
            cursor.execute("SELECT name FROM sqlite_sequence WHERE name = 'members'")
            if cursor.fetchone():
                # Reset the sequence to match our calculated next_id
                # This prevents SQLite from trying to use a higher ID
                cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'members'", (next_id - 1,))
                self.conn.commit()
        except sqlite3.OperationalError:
            # sqlite_sequence table doesn't exist - that's fine, table doesn't use AUTOINCREMENT
            pass
        except Exception as e:
            # Log but don't fail - we'll still use the calculated next_id
            print(f"Warning: Could not reset SQLite sequence: {e}")
        
        return next_id
    
    # Member operations
    def add_member(self, name: str, email: str, phone: str, join_date: date,
                   membership_type: str, fee_amount: float, payment_frequency: str,
                   trainer_id: int = None) -> int:
        """Add a new member with reusable ID"""
        cursor = self.conn.cursor()
        
        # Get the next available ID (reuses deleted IDs)
        member_id = self._get_next_available_id()
        
        # Calculate next payment date based on frequency
        next_payment = self._calculate_next_payment_date(join_date, payment_frequency)
        
        cursor.execute("""
            INSERT INTO members (id, name, email, phone, join_date, membership_type,
                               fee_amount, payment_frequency, next_payment_date, trainer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (member_id, name, email, phone, join_date, membership_type, fee_amount, payment_frequency, next_payment, trainer_id))
        
        self.conn.commit()
        return member_id
    
    def update_member(self, member_id: int, **kwargs):
        """Update member fields"""
        cursor = self.conn.cursor()
        allowed_fields = ['name', 'email', 'phone', 'membership_type', 'fee_amount', 
                         'payment_frequency', 'join_date', 'next_payment_date', 'status', 'trainer_id']
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(member_id)
            cursor.execute(f"""
                UPDATE members SET {', '.join(updates)} WHERE id = ?
            """, values)
            self.conn.commit()
    
    def get_all_members(self, active_only: bool = True) -> List[Dict]:
        """Get all members"""
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM members WHERE status = 'active' ORDER BY id ASC")
        else:
            cursor.execute("SELECT * FROM members ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_member(self, member_id: int) -> Optional[Dict]:
        """Get a specific member by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def remove_member(self, member_id: int):
        """Hard delete a member (permanently remove from database to allow ID reuse)"""
        cursor = self.conn.cursor()
        # Delete related payments first (to handle foreign key constraints)
        cursor.execute("DELETE FROM payments WHERE member_id = ?", (member_id,))
        # Delete the member (this frees up the ID for reuse)
        cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        self.conn.commit()
    
    def update_member_payment(self, member_id: int, payment_date: date):
        """Update member's payment and calculate next payment date"""
        cursor = self.conn.cursor()
        member = self.get_member(member_id)
        if member:
            payment_frequency = member['payment_frequency']
            
            # For daily payments, use the actual payment date to calculate next payment
            # For all other frequencies, use the original due date to preserve billing cycle day
            if payment_frequency == "Daily":
                base_date = payment_date
            else:
                # Use the original due date (next_payment_date) to calculate next payment,
                # not the actual payment date. This preserves the billing cycle day.
                original_due_date = member.get('next_payment_date')
                if not original_due_date:
                    raise ValueError(f"Member {member_id} has no next_payment_date set. Cannot calculate next payment.")
                
                # Convert to date if it's a string
                if isinstance(original_due_date, str):
                    original_due_date = datetime.strptime(original_due_date, '%Y-%m-%d').date()
                
                base_date = original_due_date
            
            # Calculate next payment date
            next_payment = self._calculate_next_payment_date(
                base_date, payment_frequency
            )
            cursor.execute("""
                UPDATE members 
                SET last_payment_date = ?, next_payment_date = ?
                WHERE id = ?
            """, (payment_date, next_payment, member_id))
            self.conn.commit()
    
    def fix_payment_dates(self) -> int:
        """
        Fix inconsistent payment dates for all active members.
        This handles cases where:
        1. last_payment_date > next_payment_date (late payment)
        2. last_payment_date == next_payment_date (payment on due date, but next not updated)
        3. next_payment_date is too close to last_payment_date for the frequency (e.g., 1 day for Monthly)
        
        Returns the number of members fixed.
        """
        cursor = self.conn.cursor()
        today = date.today()
        fixed_count = 0
        
        # Get all active members
        cursor.execute("""
            SELECT id, last_payment_date, next_payment_date, payment_frequency
            FROM members 
            WHERE status = 'active'
            AND last_payment_date IS NOT NULL
            AND next_payment_date IS NOT NULL
        """)
        
        members = cursor.fetchall()
        
        for member_row in members:
            member_id = member_row[0]
            last_payment = member_row[1]
            next_payment = member_row[2]
            frequency = member_row[3]
            
            # Convert to date objects if strings
            if isinstance(last_payment, str):
                last_payment = datetime.strptime(last_payment, '%Y-%m-%d').date()
            if isinstance(next_payment, str):
                next_payment = datetime.strptime(next_payment, '%Y-%m-%d').date()
            
            days_diff = (next_payment - last_payment).days
            needs_fix = False
            
            # Check if inconsistent: last_payment_date >= next_payment_date
            if last_payment >= next_payment:
                needs_fix = True
            # Check if next_payment_date is too close for the frequency
            elif frequency == "Daily":
                if days_diff != 1:
                    needs_fix = True
            elif frequency == "Monthly":
                # For monthly, should be at least 25 days (allowing for month variations)
                if days_diff < 25:
                    needs_fix = True
            elif frequency == "Quarterly":
                # For quarterly, should be at least 80 days
                if days_diff < 80:
                    needs_fix = True
            elif frequency == "6 Months" or frequency == "Semi-Annual":
                # For 6 months, should be at least 150 days
                if days_diff < 150:
                    needs_fix = True
            elif frequency == "Yearly" or frequency == "Annual":
                # For yearly, should be at least 300 days
                if days_diff < 300:
                    needs_fix = True
            
            if needs_fix:
                # Fix the next_payment_date
                if frequency == "Daily":
                    # For daily, next payment is last payment + 1 day
                    fixed_next_payment = date.fromordinal(last_payment.toordinal() + 1)
                else:
                    # For other frequencies, preserve billing cycle day
                    # Get the billing cycle day from the member's join_date or last_payment_date
                    # First, try to get join_date to determine billing cycle day
                    cursor.execute("SELECT join_date FROM members WHERE id = ?", (member_id,))
                    join_date_row = cursor.fetchone()
                    if join_date_row and join_date_row[0]:
                        if isinstance(join_date_row[0], str):
                            join_date = datetime.strptime(join_date_row[0], '%Y-%m-%d').date()
                        else:
                            join_date = join_date_row[0]
                        billing_day = join_date.day
                    else:
                        # Fallback to last_payment_date day
                        billing_day = last_payment.day
                    
                    # Calculate next payment from last_payment_date, preserving billing cycle day
                    # For monthly: add 1 month to last_payment_date, but use billing_day
                    if frequency == "Monthly":
                        if last_payment.month == 12:
                            candidate = date(last_payment.year + 1, 1, billing_day)
                        else:
                            candidate = date(last_payment.year, last_payment.month + 1, billing_day)
                    elif frequency == "Quarterly":
                        month = last_payment.month + 3
                        year = last_payment.year
                        if month > 12:
                            month -= 12
                            year += 1
                        candidate = date(year, month, billing_day)
                    elif frequency == "6 Months" or frequency == "Semi-Annual":
                        month = last_payment.month + 6
                        year = last_payment.year
                        if month > 12:
                            month -= 12
                            year += 1
                        candidate = date(year, month, billing_day)
                    elif frequency == "Yearly" or frequency == "Annual":
                        candidate = date(last_payment.year + 1, last_payment.month, billing_day)
                    else:
                        # Default to monthly
                        if last_payment.month == 12:
                            candidate = date(last_payment.year + 1, 1, billing_day)
                        else:
                            candidate = date(last_payment.year, last_payment.month + 1, billing_day)
                    
                    # Handle invalid dates (e.g., Jan 31 -> Feb 31)
                    from calendar import monthrange
                    try:
                        fixed_next_payment = candidate
                    except ValueError:
                        # Day doesn't exist in target month, use last day
                        last_day = monthrange(candidate.year, candidate.month)[1]
                        fixed_next_payment = date(candidate.year, candidate.month, last_day)
                    
                    # Ensure it's ahead of last_payment_date
                    if fixed_next_payment <= last_payment:
                        fixed_next_payment = self._calculate_next_payment_date(fixed_next_payment, frequency)
                
                # Update the database
                cursor.execute("""
                    UPDATE members 
                    SET next_payment_date = ?
                    WHERE id = ?
                """, (fixed_next_payment, member_id))
                fixed_count += 1
        
        if fixed_count > 0:
            self.conn.commit()
        
        return fixed_count
    
    def get_overdue_members(self) -> List[Dict]:
        """Get members with overdue payments"""
        cursor = self.conn.cursor()
        today = date.today()
        cursor.execute("""
            SELECT * FROM members 
            WHERE status = 'active' 
            AND next_payment_date < ?
            ORDER BY next_payment_date
        """, (today,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_due_soon_members(self, days: int = None) -> List[Dict]:
        """Get members with payments due soon, frequency-aware"""
        cursor = self.conn.cursor()
        today = date.today()
        
        # Get all active members
        cursor.execute("""
            SELECT * FROM members 
            WHERE status = 'active' 
            AND next_payment_date >= ?
            ORDER BY next_payment_date
        """, (today,))
        all_members = [dict(row) for row in cursor.fetchall()]
        
        # Filter based on payment frequency
        due_soon = []
        for member in all_members:
            # Handle date conversion (could be string or date object)
            next_payment_str = member['next_payment_date']
            if isinstance(next_payment_str, str):
                next_payment = date.fromisoformat(next_payment_str)
            else:
                next_payment = next_payment_str
            frequency = member.get('payment_frequency', 'Monthly')
            
            # Calculate reminder period based on frequency
            if days is None:
                # Auto-calculate based on frequency
                if frequency == "Daily":
                    reminder_days = 0  # Alert same day
                elif frequency == "Monthly":
                    reminder_days = 7  # 7 days before monthly payment
                elif frequency == "Quarterly":
                    reminder_days = 14  # 2 weeks before quarterly payment
                elif frequency == "Yearly":
                    reminder_days = 30  # 1 month before yearly payment
                else:
                    reminder_days = 7  # Default
            else:
                reminder_days = days
            
            # Check if payment is due within reminder period
            days_until = (next_payment - today).days
            if 0 <= days_until <= reminder_days:
                due_soon.append(member)
        
        return due_soon
    
    # Staff operations
    def add_staff(self, name: str, email: str, phone: str, position: str, hire_date: date) -> int:
        """Add a new staff member"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO staff (name, email, phone, position, hire_date)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, phone, position, hire_date))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_staff(self, active_only: bool = True) -> List[Dict]:
        """Get all staff members"""
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM staff WHERE status = 'active' ORDER BY name")
        else:
            cursor.execute("SELECT * FROM staff ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_trainers(self, active_only: bool = True) -> List[Dict]:
        """Get all trainers (staff with position = 'Trainer')"""
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM staff WHERE position = 'Trainer' AND status = 'active' ORDER BY name")
        else:
            cursor.execute("SELECT * FROM staff WHERE position = 'Trainer' ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_staff(self, staff_id: int) -> Optional[Dict]:
        """Get a specific staff member by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def remove_staff(self, staff_id: int):
        """Soft delete a staff member"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE staff SET status = 'inactive' WHERE id = ?", (staff_id,))
        self.conn.commit()
    
    # Holiday operations
    def add_holiday(self, staff_id: int, start_date: date, end_date: date, reason: str = "") -> int:
        """Add a holiday/leave record for staff"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO holidays (staff_id, start_date, end_date, reason)
            VALUES (?, ?, ?, ?)
        """, (staff_id, start_date, end_date, reason))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_staff_holidays(self, staff_id: int) -> List[Dict]:
        """Get all holidays for a specific staff member"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT h.*, s.name as staff_name 
            FROM holidays h
            JOIN staff s ON h.staff_id = s.id
            WHERE h.staff_id = ?
            ORDER BY h.start_date DESC
        """, (staff_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_holidays(self, start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get all holidays, optionally filtered by date range"""
        cursor = self.conn.cursor()
        if start_date and end_date:
            cursor.execute("""
                SELECT h.*, s.name as staff_name 
                FROM holidays h
                JOIN staff s ON h.staff_id = s.id
                WHERE h.start_date <= ? AND h.end_date >= ?
                ORDER BY h.start_date
            """, (end_date, start_date))
        else:
            cursor.execute("""
                SELECT h.*, s.name as staff_name 
                FROM holidays h
                JOIN staff s ON h.staff_id = s.id
                ORDER BY h.start_date DESC
            """)
        return [dict(row) for row in cursor.fetchall()]
    
    # Payment operations
    def add_payment(self, member_id: int, amount: float, payment_date: date, notes: str = ""):
        """Record a payment"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO payments (member_id, amount, payment_date, notes)
            VALUES (?, ?, ?, ?)
        """, (member_id, amount, payment_date, notes))
        self.conn.commit()
        # Update member's payment dates
        self.update_member_payment(member_id, payment_date)
    
    def get_member_payments(self, member_id: int) -> List[Dict]:
        """Get payment history for a member"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM payments 
            WHERE member_id = ?
            ORDER BY payment_date DESC
        """, (member_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_payments(self) -> List[Dict]:
        """Get all payments with member names"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, m.name as member_name 
            FROM payments p
            JOIN members m ON p.member_id = m.id
            ORDER BY p.payment_date DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def record_payment(self, member_id: int, amount: float, payment_date: date, notes: str = ""):
        """Record a payment (alias for add_payment)"""
        return self.add_payment(member_id, amount, payment_date, notes)
    
    def get_daily_revenue(self, target_date: date = None) -> float:
        """Get total revenue for a specific date (defaults to today)"""
        if target_date is None:
            target_date = date.today()
        cursor = self.conn.cursor()
        date_str = target_date.strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments
            WHERE DATE(payment_date) = DATE(?)
        """, (date_str,))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    
    def get_monthly_revenue(self, year: int = None, month: int = None) -> float:
        """Get total revenue for a specific month (defaults to current month)"""
        if year is None or month is None:
            today = date.today()
            year = today.year
            month = today.month
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM payments
            WHERE strftime('%Y', payment_date) = ? AND strftime('%m', payment_date) = ?
        """, (str(year), f"{month:02d}"))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    
    def get_total_revenue(self) -> float:
        """Get total revenue from all time"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM payments")
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    
    def get_members_by_trainer(self) -> List[Dict]:
        """Get count of members per trainer"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                s.id as trainer_id,
                s.name as trainer_name,
                COUNT(m.id) as member_count
            FROM staff s
            LEFT JOIN members m ON s.id = m.trainer_id AND m.status = 'active'
            WHERE s.position = 'Trainer' AND s.status = 'active'
            GROUP BY s.id, s.name
            ORDER BY member_count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_membership_type_distribution(self) -> List[Dict]:
        """Get count of members by membership type"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                membership_type,
                COUNT(*) as count
            FROM members
            WHERE status = 'active'
            GROUP BY membership_type
            ORDER BY count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_payment_frequency_distribution(self) -> List[Dict]:
        """Get count of members by payment frequency"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                payment_frequency,
                COUNT(*) as count
            FROM members
            WHERE status = 'active'
            GROUP BY payment_frequency
            ORDER BY count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_payments(self, limit: int = 10) -> List[Dict]:
        """Get recent payments"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, m.name as member_name 
            FROM payments p
            JOIN members m ON p.member_id = m.id
            ORDER BY p.payment_date DESC, p.created_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Helper methods
    def _calculate_next_payment_date(self, last_date: date, frequency: str) -> date:
        """Calculate next payment date based on frequency"""
        def _safe_date(year: int, month: int, day: int) -> date:
            """Create a date, adjusting day if it doesn't exist in the target month"""
            try:
                return date(year, month, day)
            except ValueError:
                # Day doesn't exist in target month (e.g., Jan 31 → Feb 31)
                # Use the last day of the target month instead
                from calendar import monthrange
                last_day = monthrange(year, month)[1]
                return date(year, month, last_day)
        
        if frequency == "Daily":
            # Add 1 day
            return date.fromordinal(last_date.toordinal() + 1)
        elif frequency == "Monthly":
            # Add 1 month
            if last_date.month == 12:
                return _safe_date(last_date.year + 1, 1, last_date.day)
            else:
                return _safe_date(last_date.year, last_date.month + 1, last_date.day)
        elif frequency == "Quarterly":
            # Add 3 months
            month = last_date.month + 3
            year = last_date.year
            if month > 12:
                month -= 12
                year += 1
            return _safe_date(year, month, last_date.day)
        elif frequency == "6 Months" or frequency == "Semi-Annual":
            # Add 6 months
            month = last_date.month + 6
            year = last_date.year
            if month > 12:
                month -= 12
                year += 1
            return _safe_date(year, month, last_date.day)
        elif frequency == "Yearly" or frequency == "Annual":
            return _safe_date(last_date.year + 1, last_date.month, last_date.day)
        else:  # Default to daily
            return date.fromordinal(last_date.toordinal() + 1)
    
    # Locker Management Methods
    def assign_locker(self, member_id: int, locker_number: str, fee_amount: float, 
                     payment_frequency: str, start_date: date) -> int:
        """Assign a locker to a member and automatically record initial payment"""
        cursor = self.conn.cursor()
        
        # Calculate next payment date based on frequency
        next_payment = self._calculate_next_payment_date(start_date, payment_frequency)
        
        # Insert locker record
        cursor.execute("""
            INSERT INTO lockers (member_id, locker_number, fee_amount, payment_frequency,
                               start_date, last_payment_date, next_payment_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        """, (member_id, locker_number, fee_amount, payment_frequency, start_date, start_date, next_payment))
        
        locker_id = cursor.lastrowid
        
        # Automatically record the initial payment
        cursor.execute("""
            INSERT INTO locker_payments (locker_id, member_id, amount, payment_date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (locker_id, member_id, fee_amount, start_date, f"Initial locker assignment payment"))
        
        self.conn.commit()
        return locker_id
    
    def record_locker_payment(self, locker_id: int, payment_date: date, amount: float, notes: str = ""):
        """Record a locker payment"""
        cursor = self.conn.cursor()
        
        # Get locker details
        cursor.execute("SELECT * FROM lockers WHERE id = ?", (locker_id,))
        locker = cursor.fetchone()
        if not locker:
            raise ValueError(f"Locker with ID {locker_id} not found")
        
        locker_dict = dict(locker)
        
        # Insert payment record
        cursor.execute("""
            INSERT INTO locker_payments (locker_id, member_id, amount, payment_date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (locker_id, locker_dict['member_id'], amount, payment_date, notes))
        
        # Update locker payment dates
        payment_frequency = locker_dict['payment_frequency']
        
        # For daily payments, use the actual payment date to calculate next payment
        # For all other frequencies, use the original due date to preserve billing cycle day
        if payment_frequency == "Daily":
            base_date = payment_date
        else:
            # Use the original due date (next_payment_date) to calculate next payment,
            # not the actual payment date. This preserves the billing cycle day.
            original_due_date = locker_dict.get('next_payment_date')
            if not original_due_date:
                raise ValueError(f"Locker {locker_id} has no next_payment_date set. Cannot calculate next payment.")
            
            # Convert to date if it's a string
            if isinstance(original_due_date, str):
                original_due_date = datetime.strptime(original_due_date, '%Y-%m-%d').date()
            
            base_date = original_due_date
        
        # Calculate next payment date
        next_payment = self._calculate_next_payment_date(base_date, payment_frequency)
        cursor.execute("""
            UPDATE lockers 
            SET last_payment_date = ?, next_payment_date = ?
            WHERE id = ?
        """, (payment_date, next_payment, locker_id))
        
        self.conn.commit()
    
    def get_all_lockers(self, active_only: bool = False) -> List[Dict]:
        """Get all lockers with member information"""
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute("""
                SELECT l.*, m.name as member_name, m.phone as member_phone, m.email as member_email
                FROM lockers l
                JOIN members m ON l.member_id = m.id
                WHERE l.status = 'active'
                ORDER BY l.id DESC
            """)
        else:
            cursor.execute("""
                SELECT l.*, m.name as member_name, m.phone as member_phone, m.email as member_email
                FROM lockers l
                JOIN members m ON l.member_id = m.id
                ORDER BY l.id DESC
            """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_locker(self, locker_id: int) -> Optional[Dict]:
        """Get a specific locker by ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.*, m.name as member_name, m.phone as member_phone, m.email as member_email
            FROM lockers l
            JOIN members m ON l.member_id = m.id
            WHERE l.id = ?
        """, (locker_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_overdue_locker_payments(self) -> List[Dict]:
        """Get lockers with overdue payments"""
        cursor = self.conn.cursor()
        today = date.today()
        cursor.execute("""
            SELECT l.*, m.name as member_name, m.phone as member_phone, m.email as member_email
            FROM lockers l
            JOIN members m ON l.member_id = m.id
            WHERE l.status = 'active' 
            AND l.next_payment_date < ?
            ORDER BY l.next_payment_date ASC
        """, (today,))
        return [dict(row) for row in cursor.fetchall()]
    
    def search_lockers(self, search_term: str) -> List[Dict]:
        """Search lockers by member ID, name, phone, email, or locker number"""
        cursor = self.conn.cursor()
        search_pattern = f"%{search_term}%"
        
        # Check if search term is numeric (could be member ID or locker number)
        is_numeric = search_term.strip().isdigit()
        
        if is_numeric:
            # Search by ID or locker number
            cursor.execute("""
                SELECT l.*, m.name as member_name, m.phone as member_phone, m.email as member_email
                FROM lockers l
                JOIN members m ON l.member_id = m.id
                WHERE l.member_id = ? OR l.locker_number LIKE ?
                ORDER BY l.id DESC
            """, (int(search_term), search_pattern))
        else:
            # Search by name, phone, email, or locker number
            cursor.execute("""
                SELECT l.*, m.name as member_name, m.phone as member_phone, m.email as member_email
                FROM lockers l
                JOIN members m ON l.member_id = m.id
                WHERE m.name LIKE ? OR m.phone LIKE ? OR m.email LIKE ? OR l.locker_number LIKE ?
                ORDER BY l.id DESC
            """, (search_pattern, search_pattern, search_pattern, search_pattern))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_locker_payments(self, locker_id: int) -> List[Dict]:
        """Get payment history for a specific locker"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM locker_payments
            WHERE locker_id = ?
            ORDER BY payment_date DESC, created_at DESC
        """, (locker_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_locker_status(self, locker_id: int, status: str):
        """Update locker status (active/inactive)"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE lockers SET status = ? WHERE id = ?", (status, locker_id))
        self.conn.commit()
    
    def remove_locker(self, locker_id: int):
        """Remove/unassign a locker (set status to inactive)"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE lockers SET status = 'inactive' WHERE id = ?", (locker_id,))
        self.conn.commit()
    
    # Locker Revenue Analytics Methods
    def get_daily_locker_revenue(self) -> float:
        """Get total locker revenue for today"""
        cursor = self.conn.cursor()
        today = date.today()
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM locker_payments 
            WHERE DATE(payment_date) = DATE(?)
        """, (today,))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    
    def get_monthly_locker_revenue(self) -> float:
        """Get total locker revenue for current month"""
        cursor = self.conn.cursor()
        today = date.today()
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM locker_payments 
            WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', ?)
        """, (today,))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    
    def get_annual_locker_revenue(self) -> float:
        """Get total locker revenue for current year"""
        cursor = self.conn.cursor()
        today = date.today()
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM locker_payments 
            WHERE strftime('%Y', payment_date) = strftime('%Y', ?)
        """, (today,))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    
    def get_ytd_locker_revenue(self) -> float:
        """Get year-to-date locker revenue (from Jan 1 to today)"""
        cursor = self.conn.cursor()
        today = date.today()
        year_start = date(today.year, 1, 1)
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM locker_payments 
            WHERE DATE(payment_date) >= DATE(?) AND DATE(payment_date) <= DATE(?)
        """, (year_start, today))
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0.0
    
    def close(self):
        """Close database connection"""
        self.conn.close()

