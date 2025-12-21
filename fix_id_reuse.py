#!/usr/bin/env python3
"""
Utility script to fix ID reuse issue in the database
This resets the SQLite sequence table to allow ID reuse
"""
import sqlite3
import sys
import os

# Try to find the database file
DB_PATH = None
possible_paths = [
    "dist/gym_management.db",  # Check dist folder first (common location)
    "gym_management.db",
    os.path.join(os.path.dirname(__file__), "dist", "gym_management.db"),
    os.path.join(os.path.dirname(__file__), "gym_management.db"),
]

for path in possible_paths:
    if os.path.exists(path):
        DB_PATH = path
        break

if not DB_PATH:
    print("Error: Could not find gym_management.db")
    print("Searched in:")
    for path in possible_paths:
        print(f"  - {path}")
    sys.exit(1)

def fix_id_sequence():
    """Reset SQLite sequence to allow ID reuse"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current max ID from members table
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM members")
        max_id = cursor.fetchone()[0]
        
        print(f"Current maximum ID in members table: {max_id}")
        
        # Check if sqlite_sequence table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
        if cursor.fetchone():
            # Check if members table has an entry in sqlite_sequence
            cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'members'")
            seq_row = cursor.fetchone()
            
            if seq_row:
                old_seq = seq_row[0]
                print(f"Current sequence value: {old_seq}")
                
                # Reset sequence to match max ID
                cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'members'", (max_id,))
                conn.commit()
                print(f"✓ Sequence reset from {old_seq} to {max_id}")
            else:
                print("No sequence entry found for 'members' table")
        else:
            print("sqlite_sequence table doesn't exist (table doesn't use AUTOINCREMENT)")
        
        # Show available IDs
        cursor.execute("SELECT id FROM members ORDER BY id")
        existing_ids = {row[0] for row in cursor.fetchall()}
        
        # Find next available ID
        next_id = 1
        while next_id in existing_ids:
            next_id += 1
        
        print(f"\nNext available ID will be: {next_id}")
        print(f"Existing IDs: {sorted(existing_ids) if existing_ids else 'None'}")
        print(f"\nDatabase file: {DB_PATH}")
        
        conn.close()
        print("\n✓ ID reuse fix completed!")
        print("You can now add new members and they will reuse deleted IDs.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("ID Reuse Fix Utility")
    print("=" * 60)
    print()
    fix_id_sequence()

