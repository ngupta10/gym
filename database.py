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
            next_payment = self._calculate_next_payment_date(
                payment_date, member['payment_frequency']
            )
            cursor.execute("""
                UPDATE members 
                SET last_payment_date = ?, next_payment_date = ?
                WHERE id = ?
            """, (payment_date, next_payment, member_id))
            self.conn.commit()
    
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
        elif frequency == "Yearly":
            return _safe_date(last_date.year + 1, last_date.month, last_date.day)
        else:  # Default to daily
            return date.fromordinal(last_date.toordinal() + 1)
    
    def close(self):
        """Close database connection"""
        self.conn.close()

