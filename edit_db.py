#!/usr/bin/env python3
"""
Simple script to manually edit database entries
Usage: python3 edit_db.py
"""
import sqlite3
from datetime import datetime

DB_PATH = "gym_management.db"

def show_members():
    """Display all members"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM members ORDER BY id")
    members = cursor.fetchall()
    
    print("\n" + "="*100)
    print("MEMBERS LIST")
    print("="*100)
    print(f"{'ID':<5} {'Name':<25} {'Phone':<15} {'Status':<10} {'Join Date':<12} {'Next Payment':<12}")
    print("-"*100)
    
    for member in members:
        print(f"{member['id']:<5} {member['name']:<25} {member['phone'] or 'N/A':<15} "
              f"{member['status']:<10} {member['join_date']:<12} {member['next_payment_date'] or 'N/A':<12}")
    
    conn.close()
    return members

def edit_member():
    """Edit a member's information"""
    members = show_members()
    
    try:
        member_id = int(input("\nEnter Member ID to edit (or 0 to cancel): "))
        if member_id == 0:
            return
        
        # Find the member
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        
        if not member:
            print(f"Member with ID {member_id} not found!")
            conn.close()
            return
        
        print(f"\nCurrent information for {member['name']}:")
        print(f"  Name: {member['name']}")
        print(f"  Email: {member['email'] or 'N/A'}")
        print(f"  Phone: {member['phone'] or 'N/A'}")
        print(f"  Status: {member['status']}")
        print(f"  Join Date: {member['join_date']}")
        print(f"  Next Payment Date: {member['next_payment_date'] or 'N/A'}")
        print(f"  Fee Amount: {member['fee_amount']}")
        print(f"  Payment Frequency: {member['payment_frequency']}")
        
        print("\nEnter new values (press Enter to keep current value):")
        
        new_name = input(f"Name [{member['name']}]: ").strip() or member['name']
        new_email = input(f"Email [{member['email'] or ''}]: ").strip() or member['email']
        new_phone = input(f"Phone [{member['phone'] or ''}]: ").strip() or member['phone']
        new_status = input(f"Status (active/inactive) [{member['status']}]: ").strip() or member['status']
        new_join_date = input(f"Join Date (YYYY-MM-DD) [{member['join_date']}]: ").strip() or member['join_date']
        new_next_payment = input(f"Next Payment Date (YYYY-MM-DD) [{member['next_payment_date'] or ''}]: ").strip() or member['next_payment_date']
        new_fee = input(f"Fee Amount [{member['fee_amount']}]: ").strip() or member['fee_amount']
        new_frequency = input(f"Payment Frequency (Daily/Monthly/Quarterly/Yearly) [{member['payment_frequency']}]: ").strip() or member['payment_frequency']
        
        # Update the member
        cursor.execute("""
            UPDATE members 
            SET name = ?, email = ?, phone = ?, status = ?, 
                join_date = ?, next_payment_date = ?, fee_amount = ?, payment_frequency = ?
            WHERE id = ?
        """, (new_name, new_email or None, new_phone or None, new_status, 
              new_join_date, new_next_payment or None, float(new_fee), new_frequency, member_id))
        
        conn.commit()
        conn.close()
        
        print(f"\n✓ Successfully updated member {member_id}!")
        
    except ValueError:
        print("Invalid input! Please enter a valid number.")
    except Exception as e:
        print(f"Error: {e}")

def run_sql():
    """Run custom SQL query"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\nEnter SQL query (or 'exit' to go back):")
    print("Example: UPDATE members SET status = 'active' WHERE id = 1;")
    
    while True:
        query = input("\nSQL> ").strip()
        if query.lower() == 'exit':
            break
        
        if not query:
            continue
        
        try:
            if query.upper().startswith('SELECT'):
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    print(f"\nResults ({len(results)} rows):")
                    for row in results:
                        print(dict(row))
                else:
                    print("No results found.")
            else:
                cursor.execute(query)
                conn.commit()
                print(f"✓ Query executed successfully. Rows affected: {cursor.rowcount}")
        except Exception as e:
            print(f"Error: {e}")
    
    conn.close()

def main():
    """Main menu"""
    while True:
        print("\n" + "="*50)
        print("DATABASE EDITOR")
        print("="*50)
        print("1. View all members")
        print("2. Edit a member")
        print("3. Run custom SQL query")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            show_members()
        elif choice == '2':
            edit_member()
        elif choice == '3':
            run_sql()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please select 1-4.")

if __name__ == "__main__":
    main()


