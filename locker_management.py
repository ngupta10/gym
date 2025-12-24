"""
Locker Management Module - CustomTkinter
Handles locker assignment, fee recording, and locker management
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date, datetime
from typing import Optional

class LockerManagement(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.setup_ui()
        self.refresh_locker_list()
    
    def setup_ui(self):
        """Create the locker management UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Locker Management",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(anchor="w", pady=(0, 25))
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=0, minsize=400)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left side - Forms
        form_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8,
            width=400
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 7), pady=0)
        form_frame.grid_propagate(False)
        form_frame.grid_rowconfigure(0, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable form
        scrollable_form = ctk.CTkScrollableFrame(
            form_frame,
            fg_color="transparent"
        )
        scrollable_form.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Assign Locker Section
        self.create_assign_section(scrollable_form)
        
        # Record Payment Section
        self.create_payment_section(scrollable_form)
        
        # Right side - List and Actions
        list_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        list_frame.grid(row=0, column=1, sticky="nsew", padx=(7, 0), pady=0)
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Search and Actions
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Lockers:",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by ID, name, phone, email, or locker number...",
            width=300
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Overdue Payments Button
        overdue_btn = ctk.CTkButton(
            search_frame,
            text="View Overdue Payments",
            command=self.show_overdue_payments,
            fg_color="#ef4444",
            hover_color="#dc2626",
            width=180
        )
        overdue_btn.pack(side="left", padx=(0, 10))
        
        # Remove Locker Button
        remove_btn = ctk.CTkButton(
            search_frame,
            text="Remove Locker",
            command=self.remove_locker,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            width=150
        )
        remove_btn.pack(side="left")
        
        # Locker List
        self.create_locker_list(list_frame)
    
    def create_assign_section(self, parent):
        """Create locker assignment form"""
        section_title = ctk.CTkLabel(
            parent,
            text="Assign Locker",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        section_title.pack(pady=(20, 15))
        
        # Member Selection
        member_id_label = ctk.CTkLabel(
            parent,
            text="Select Member *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        member_id_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Get all active members for dropdown
        members = self.db.get_all_members(active_only=True)
        member_options = [f"{m['id']} - {m['name']}" for m in members]
        
        self.member_combo = ctk.CTkComboBox(
            parent,
            values=member_options if member_options else ["No active members"],
            width=350,
            command=self.on_member_selected
        )
        self.member_combo.pack(fill="x", padx=20, pady=(0, 15))
        self.selected_member_id = None
        
        # Locker Number
        locker_num_label = ctk.CTkLabel(
            parent,
            text="Locker Number",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        locker_num_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.locker_num_entry = ctk.CTkEntry(
            parent,
            placeholder_text="e.g., L-101",
            width=350
        )
        self.locker_num_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Fee Amount
        fee_label = ctk.CTkLabel(
            parent,
            text="Fee Amount (₹) *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        fee_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.fee_entry = ctk.CTkEntry(
            parent,
            placeholder_text="Enter fee amount",
            width=350
        )
        self.fee_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Payment Frequency
        freq_label = ctk.CTkLabel(
            parent,
            text="Payment Frequency *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        freq_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.frequency_combo = ctk.CTkComboBox(
            parent,
            values=["Monthly", "Quarterly", "6 Months", "Yearly"],
            width=350
        )
        self.frequency_combo.set("Monthly")
        self.frequency_combo.pack(fill="x", padx=20, pady=(0, 15))
        
        # Start Date
        start_date_label = ctk.CTkLabel(
            parent,
            text="Start Date *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        start_date_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.start_date_entry = ctk.CTkEntry(
            parent,
            placeholder_text="YYYY-MM-DD",
            width=350
        )
        self.start_date_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Assign Button
        assign_btn = ctk.CTkButton(
            parent,
            text="Assign Locker",
            command=self.assign_locker,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            width=350
        )
        assign_btn.pack(padx=20, pady=(0, 30))
    
    def create_payment_section(self, parent):
        """Create payment recording form"""
        section_title = ctk.CTkLabel(
            parent,
            text="Record Locker Payment",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        section_title.pack(pady=(20, 15))
        
        # Locker ID
        locker_id_label = ctk.CTkLabel(
            parent,
            text="Locker ID *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        locker_id_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.payment_locker_id_entry = ctk.CTkEntry(
            parent,
            placeholder_text="Enter locker ID",
            width=350
        )
        self.payment_locker_id_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Payment Amount
        amount_label = ctk.CTkLabel(
            parent,
            text="Payment Amount (₹) *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        amount_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.payment_amount_entry = ctk.CTkEntry(
            parent,
            placeholder_text="Enter payment amount",
            width=350
        )
        self.payment_amount_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Payment Date
        payment_date_label = ctk.CTkLabel(
            parent,
            text="Payment Date *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        payment_date_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.payment_date_entry = ctk.CTkEntry(
            parent,
            placeholder_text="YYYY-MM-DD (default: today)",
            width=350
        )
        self.payment_date_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Notes
        notes_label = ctk.CTkLabel(
            parent,
            text="Notes",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        notes_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.payment_notes_entry = ctk.CTkEntry(
            parent,
            placeholder_text="Optional notes",
            width=350
        )
        self.payment_notes_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Record Payment Button
        record_btn = ctk.CTkButton(
            parent,
            text="Record Payment",
            command=self.record_payment,
            fg_color="#10b981",
            hover_color="#059669",
            width=350
        )
        record_btn.pack(padx=20, pady=(0, 30))
    
    def create_locker_list(self, parent):
        """Create locker list with Treeview"""
        # List frame
        list_container = ctk.CTkFrame(parent, fg_color="transparent")
        list_container.pack(fill="both", expand=True)
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        # Treeview with scrollbars
        tree_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Member", "Locker #", "Fee", "Frequency", "Last Payment", "Next Payment", "Status"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=20
        )
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Configure columns
        columns = {
            "ID": 60,
            "Member": 150,
            "Locker #": 80,
            "Fee": 80,
            "Frequency": 100,
            "Last Payment": 100,
            "Next Payment": 100,
            "Status": 80
        }
        
        for col, width in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#0f172a")
        style.configure("Treeview.Heading", background="#f8fafc", foreground="black", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#3b82f6")])
        
        self.tree.grid(row=0, column=0, sticky="nsew")
    
    def on_member_selected(self, choice):
        """Handle member selection from dropdown"""
        if choice and " - " in choice:
            member_id = int(choice.split(" - ")[0])
            self.selected_member_id = member_id
    
    def assign_locker(self):
        """Assign a locker to a member"""
        try:
            # Get member ID from dropdown
            if not self.selected_member_id:
                selected = self.member_combo.get()
                if not selected or selected == "No active members":
                    messagebox.showerror("Error", "Please select a member")
                    return
                if " - " in selected:
                    member_id = int(selected.split(" - ")[0])
                else:
                    messagebox.showerror("Error", "Please select a valid member")
                    return
            else:
                member_id = self.selected_member_id
            
            locker_number = self.locker_num_entry.get().strip() or None
            fee_amount = float(self.fee_entry.get().strip())
            payment_frequency = self.frequency_combo.get()
            start_date_str = self.start_date_entry.get().strip()
            
            if not start_date_str:
                messagebox.showerror("Error", "Please enter a start date")
                return
            
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            
            # Verify member exists
            member = self.db.get_member(member_id)
            if not member:
                messagebox.showerror("Error", f"Member with ID {member_id} not found")
                return
            
            # Assign locker
            locker_id = self.db.assign_locker(
                member_id, locker_number, fee_amount, payment_frequency, start_date
            )
            
            messagebox.showinfo("Success", f"Locker assigned successfully!\nLocker ID: {locker_id}")
            
            # Clear form
            self.member_combo.set("")
            self.selected_member_id = None
            self.locker_num_entry.delete(0, "end")
            self.fee_entry.delete(0, "end")
            self.frequency_combo.set("Monthly")
            self.start_date_entry.delete(0, "end")
            
            # Refresh member list in case new members were added
            self.refresh_member_dropdown()
            
            # Refresh list
            self.refresh_locker_list()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign locker: {str(e)}")
    
    def refresh_member_dropdown(self):
        """Refresh the member dropdown with latest members"""
        members = self.db.get_all_members(active_only=True)
        member_options = [f"{m['id']} - {m['name']}" for m in members]
        self.member_combo.configure(values=member_options if member_options else ["No active members"])
    
    def record_payment(self):
        """Record a locker payment"""
        try:
            locker_id = int(self.payment_locker_id_entry.get().strip())
            amount = float(self.payment_amount_entry.get().strip())
            payment_date_str = self.payment_date_entry.get().strip()
            notes = self.payment_notes_entry.get().strip()
            
            # Use today's date if not provided
            if payment_date_str:
                payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date()
            else:
                payment_date = date.today()
            
            # Record payment
            self.db.record_locker_payment(locker_id, payment_date, amount, notes)
            
            messagebox.showinfo("Success", "Payment recorded successfully!")
            
            # Clear form
            self.payment_locker_id_entry.delete(0, "end")
            self.payment_amount_entry.delete(0, "end")
            self.payment_date_entry.delete(0, "end")
            self.payment_notes_entry.delete(0, "end")
            
            # Refresh list
            self.refresh_locker_list()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record payment: {str(e)}")
    
    def show_overdue_payments(self):
        """Show members with overdue locker payments"""
        overdue = self.db.get_overdue_locker_payments()
        
        if not overdue:
            messagebox.showinfo("No Overdue Payments", "All locker payments are up to date!")
            return
        
        # Create a new window to display overdue payments
        overdue_window = ctk.CTkToplevel(self)
        overdue_window.title("Overdue Locker Payments")
        overdue_window.geometry("900x500")
        
        title = ctk.CTkLabel(
            overdue_window,
            text=f"Overdue Locker Payments ({len(overdue)} found)",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(pady=20)
        
        # Treeview for overdue payments
        tree_frame = ctk.CTkFrame(overdue_window, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        overdue_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Member", "Locker #", "Fee", "Frequency", "Last Payment", "Next Payment", "Days Overdue"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            height=15
        )
        
        v_scrollbar.config(command=overdue_tree.yview)
        
        columns = {
            "ID": 60,
            "Member": 150,
            "Locker #": 80,
            "Fee": 80,
            "Frequency": 100,
            "Last Payment": 100,
            "Next Payment": 100,
            "Days Overdue": 100
        }
        
        for col, width in columns.items():
            overdue_tree.heading(col, text=col)
            overdue_tree.column(col, width=width, anchor="center")
        
        overdue_tree.grid(row=0, column=0, sticky="nsew")
        
        # Populate tree
        today = date.today()
        for locker in overdue:
            next_payment = locker.get('next_payment_date')
            if isinstance(next_payment, str):
                next_payment = datetime.strptime(next_payment, "%Y-%m-%d").date()
            
            days_overdue = (today - next_payment).days
            
            overdue_tree.insert('', 'end', values=(
                locker['id'],
                locker.get('member_name', 'N/A'),
                locker.get('locker_number', 'N/A'),
                f"₹{locker['fee_amount']:.2f}",
                locker['payment_frequency'],
                locker.get('last_payment_date', 'N/A'),
                locker.get('next_payment_date', 'N/A'),
                f"{days_overdue} days"
            ))
    
    def on_search(self, event=None):
        """Handle search input"""
        search_term = self.search_entry.get()
        if search_term.strip():
            lockers = self.db.search_lockers(search_term)
        else:
            lockers = self.db.get_all_lockers()
        
        self.populate_locker_list(lockers)
    
    def refresh_locker_list(self, search_term=""):
        """Refresh the locker list"""
        if search_term:
            lockers = self.db.search_lockers(search_term)
        else:
            lockers = self.db.get_all_lockers()
        
        self.populate_locker_list(lockers)
    
    def remove_locker(self):
        """Remove/unassign a locker"""
        # Get selected item from treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a locker from the list to remove")
            return
        
        # Get locker details from selected item
        item_values = self.tree.item(selected_item[0], 'values')
        locker_id = int(item_values[0])
        member_name = item_values[1]
        locker_number = item_values[2]
        
        # Confirm removal
        confirm_msg = (
            f"Are you sure you want to remove/unassign this locker?\n\n"
            f"Locker ID: {locker_id}\n"
            f"Member: {member_name}\n"
            f"Locker Number: {locker_number}\n\n"
            f"This will set the locker status to inactive."
        )
        
        if messagebox.askyesno("Confirm Removal", confirm_msg):
            try:
                self.db.remove_locker(locker_id)
                messagebox.showinfo("Success", f"Locker {locker_id} has been removed/unassigned successfully!")
                # Refresh list
                self.refresh_locker_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove locker: {str(e)}")
    
    def populate_locker_list(self, lockers):
        """Populate the locker list treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate with locker data
        for locker in lockers:
            self.tree.insert('', 'end', values=(
                locker['id'],
                locker.get('member_name', 'N/A'),
                locker.get('locker_number', 'N/A'),
                f"₹{locker['fee_amount']:.2f}",
                locker['payment_frequency'],
                locker.get('last_payment_date', 'N/A'),
                locker.get('next_payment_date', 'N/A'),
                locker.get('status', 'active').title()
            ))

