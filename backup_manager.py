"""
Backup Manager Module
Handles daily database backups to Excel files
"""
import sqlite3
import os
from datetime import date, datetime, timedelta
from pathlib import Path

# Try to import pandas, but don't fail if it's not installed
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

class BackupManager:
    def __init__(self, db_path: str = "gym_management.db", backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """Create backup directory if it doesn't exist"""
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def export_to_excel(self, filename: str = None) -> str:
        """Export all database tables to an Excel file"""
        if not PANDAS_AVAILABLE:
            print("Error: pandas is required for Excel export. Install with: pip install pandas openpyxl")
            return None
        
        if filename is None:
            today = date.today().strftime('%Y-%m-%d')
            filename = f"gym_backup_{today}.xlsx"
        
        filepath = os.path.join(self.backup_dir, filename)
        
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Get all table names
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for table in tables:
                    # Read table data
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    # Write to Excel sheet
                    df.to_excel(writer, sheet_name=table, index=False)
            
            conn.close()
            return filepath
        except Exception as e:
            print(f"Backup error: {e}")
            return None
    
    def should_backup_today(self) -> bool:
        """Check if backup should be created today"""
        today = date.today().strftime('%Y-%m-%d')
        backup_file = os.path.join(self.backup_dir, f"gym_backup_{today}.xlsx")
        return not os.path.exists(backup_file)
    
    def create_daily_backup(self) -> str:
        """Create daily backup if not already created today"""
        if self.should_backup_today():
            return self.export_to_excel()
        else:
            today = date.today().strftime('%Y-%m-%d')
            return os.path.join(self.backup_dir, f"gym_backup_{today}.xlsx")
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove backup files older than keep_days"""
        try:
            cutoff_date = date.today() - timedelta(days=keep_days)
            for file in Path(self.backup_dir).glob("gym_backup_*.xlsx"):
                try:
                    # Extract date from filename
                    date_str = file.stem.split('_')[-1]
                    file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    if file_date < cutoff_date:
                        file.unlink()
                        print(f"Deleted old backup: {file.name}")
                except:
                    pass
        except Exception as e:
            print(f"Cleanup error: {e}")

