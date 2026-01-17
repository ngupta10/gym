"""
Payment Alerts Module - CustomTkinter
Dedicated page for viewing and managing overdue and due soon payments
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date, datetime
from typing import List, Dict, Optional

class PaymentAlerts(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.selected_members = set()  # Track selected member IDs for bulk actions
        self.current_filter = "all"  # "all", "overdue", "due_soon"
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Create the payment alerts UI"""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Payment Alerts",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(side="left")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            title_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=120,
            height=35,
            fg_color="#3b82f6",
            hover_color="#2563eb"
        )
        refresh_btn.pack(side="right")
        
        # Summary cards
        self.create_summary_cards()
        
        # Filter tabs
        self.create_filter_tabs()
        
        # Search and actions bar
        self.create_search_bar()
        
        # Main table
        self.create_table()
        
        # Bulk actions bar
        self.create_bulk_actions()
    
    def create_summary_cards(self):
        """Create summary cards at the top"""
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        self.summary_cards_frame = cards_frame  # Store reference
        
        # Get data for summary
        overdue = self.db.get_overdue_members()
        due_soon = self.db.get_due_soon_members()
        
        overdue_total = sum(m.get('fee_amount', 0) for m in overdue)
        due_soon_total = sum(m.get('fee_amount', 0) for m in due_soon)
        total_outstanding = overdue_total + due_soon_total
        
        cards = [
            ("Overdue Payments", len(overdue), overdue_total, "#ef4444", "#fef2f2"),
            ("Due Soon", len(due_soon), due_soon_total, "#f59e0b", "#fffbeb"),
            ("Total Outstanding", len(overdue) + len(due_soon), total_outstanding, "#3b82f6", "#eff6ff"),
        ]
        
        for label, count, amount, color, bg_color in cards:
            card = ctk.CTkFrame(
                cards_frame,
                fg_color=bg_color,
                border_width=1,
                border_color=color,
                corner_radius=12,
                height=100
            )
            card.pack(side="left", fill="both", expand=True, padx=7)
            card.pack_propagate(False)
            
            # Count
            count_label = ctk.CTkLabel(
                card,
                text=str(count),
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color=color
            )
            count_label.pack(pady=(15, 5))
            
            # Label
            label_text = ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=13),
                text_color="#64748b"
            )
            label_text.pack()
            
            # Amount
            amount_label = ctk.CTkLabel(
                card,
                text=f"₹{amount:,.2f}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=color
            )
            amount_label.pack(pady=(5, 10))
    
    def create_filter_tabs(self):
        """Create filter tabs (All, Overdue, Due Soon)"""
        tabs_frame = ctk.CTkFrame(self, fg_color="transparent")
        tabs_frame.pack(fill="x", pady=(0, 15))
        
        self.filter_buttons = []
        filters = [
            ("All Alerts", "all", "#3b82f6"),
            ("Overdue Only", "overdue", "#ef4444"),
            ("Due Soon Only", "due_soon", "#f59e0b"),
        ]
        
        for label, filter_type, color in filters:
            btn = ctk.CTkButton(
                tabs_frame,
                text=label,
                command=lambda ft=filter_type: self.apply_filter(ft),
                width=150,
                height=35,
                fg_color=color if filter_type == self.current_filter else "#e2e8f0",
                hover_color=color,
                text_color="#ffffff" if filter_type == self.current_filter else "#64748b"
            )
            btn.pack(side="left", padx=5)
            self.filter_buttons.append((btn, filter_type, color))
    
    def apply_filter(self, filter_type: str):
        """Apply filter to the table"""
        self.current_filter = filter_type
        self.update_filter_buttons()
        self.refresh_table()
    
    def update_filter_buttons(self):
        """Update filter button styles based on current filter"""
        for btn, filter_type, color in self.filter_buttons:
            if filter_type == self.current_filter:
                btn.configure(fg_color=color, text_color="#ffffff")
            else:
                btn.configure(fg_color="#e2e8f0", text_color="#64748b")
    
    def create_search_bar(self):
        """Create search and action bar"""
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Search label
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        search_label.pack(side="left", padx=(0, 10))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by ID, name, phone...",
            width=300
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())
        
        # Export button
        export_btn = ctk.CTkButton(
            search_frame,
            text="📥 Export",
            command=self.export_data,
            width=120,
            height=35,
            fg_color="#10b981",
            hover_color="#059669"
        )
        export_btn.pack(side="right", padx=(5, 0))
    
    def create_table(self):
        """Create the main table with scrollbars"""
        # Table container
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Treeview frame with scrollbars
        tree_frame = ctk.CTkFrame(table_container, fg_color="transparent")
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
            columns=("Select", "ID", "Name", "Phone", "Amount", "Due Date", "Days", "Frequency", "Join Date", "Last Payment"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=20,
            selectmode="extended"
        )
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Configure columns
        columns = {
            "Select": 60,
            "ID": 60,
            "Name": 180,
            "Phone": 120,
            "Amount": 100,
            "Due Date": 110,
            "Days": 100,
            "Frequency": 100,
            "Join Date": 110,
            "Last Payment": 110
        }
        
        for col, width in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center", minwidth=width, stretch=False)
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#0f172a", rowheight=35)
        style.configure("Treeview.Heading", background="#f8fafc", foreground="black", font=("Arial", 11, "bold"))
        style.map("Treeview", background=[("selected", "#3b82f6")])
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Bind double-click for quick actions
        self.tree.bind("<Double-1>", self.on_row_double_click)
        self.tree.bind("<Button-1>", self.on_row_click)
    
    def create_bulk_actions(self):
        """Create bulk actions bar"""
        bulk_frame = ctk.CTkFrame(self, fg_color="#f8fafc", corner_radius=8, height=60)
        bulk_frame.pack(fill="x", pady=(15, 0))
        bulk_frame.pack_propagate(False)
        
        # Select all / Deselect all
        select_frame = ctk.CTkFrame(bulk_frame, fg_color="transparent")
        select_frame.pack(side="left", padx=15, pady=12)
        
        select_all_btn = ctk.CTkButton(
            select_frame,
            text="Select All",
            command=self.select_all,
            width=100,
            height=30,
            fg_color="#64748b",
            hover_color="#475569"
        )
        select_all_btn.pack(side="left", padx=(0, 5))
        
        deselect_all_btn = ctk.CTkButton(
            select_frame,
            text="Deselect All",
            command=self.deselect_all,
            width=100,
            height=30,
            fg_color="#64748b",
            hover_color="#475569"
        )
        deselect_all_btn.pack(side="left")
        
        # Bulk actions
        actions_frame = ctk.CTkFrame(bulk_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=15, pady=12)
        
        send_reminders_btn = ctk.CTkButton(
            actions_frame,
            text="📱 Send Reminders",
            command=self.send_bulk_reminders,
            width=150,
            height=30,
            fg_color="#10b981",
            hover_color="#059669"
        )
        send_reminders_btn.pack(side="left", padx=(0, 5))
        
        # Selected count
        self.selected_count_label = ctk.CTkLabel(
            actions_frame,
            text="0 selected",
            font=ctk.CTkFont(size=12),
            text_color="#64748b"
        )
        self.selected_count_label.pack(side="left", padx=10)
    
    def refresh_data(self):
        """Refresh all data"""
        # Store reference to summary cards frame
        if not hasattr(self, 'summary_cards_frame'):
            # Find and store reference to summary cards frame
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    children = widget.winfo_children()
                    if len(children) == 3 and all(isinstance(c, ctk.CTkFrame) for c in children):
                        self.summary_cards_frame = widget
                        break
        
        # Recreate summary cards
        if hasattr(self, 'summary_cards_frame'):
            self.summary_cards_frame.destroy()
        self.create_summary_cards()
        
        # Refresh table
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the table with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get data based on filter
        if self.current_filter == "overdue":
            members = self.db.get_overdue_members()
        elif self.current_filter == "due_soon":
            members = self.db.get_due_soon_members()
        else:  # all
            overdue = self.db.get_overdue_members()
            due_soon = self.db.get_due_soon_members()
            members = overdue + due_soon
        
        # Apply search filter
        search_term = self.search_entry.get().strip().lower()
        if search_term:
            members = [
                m for m in members
                if (search_term in str(m.get('id', '')).lower() or
                    search_term in m.get('name', '').lower() or
                    search_term in m.get('phone', '').lower())
            ]
        
        # Sort by due date (overdue first, then due soon)
        today = date.today()
        members.sort(key=lambda m: (
            date.fromisoformat(m['next_payment_date']) if isinstance(m['next_payment_date'], str) else m['next_payment_date']
        ))
        
        # Populate table
        for member in members:
            self.add_member_to_table(member)
    
    def add_member_to_table(self, member: Dict):
        """Add a member row to the table"""
        member_id = member['id']
        name = member.get('name', 'N/A')
        phone = member.get('phone', 'N/A')
        amount = member.get('fee_amount', 0)
        
        # Handle due date
        due_date_str = member.get('next_payment_date', '')
        if isinstance(due_date_str, str):
            due_date = date.fromisoformat(due_date_str)
        else:
            due_date = due_date_str
        
        # Calculate days overdue or days until
        today = date.today()
        if due_date < today:
            days = (today - due_date).days
            days_text = f"{days} days overdue"
            row_color = "#fef2f2"  # Light red
        else:
            days = (due_date - today).days
            days_text = f"Due in {days} days"
            row_color = "#fffbeb"  # Light orange
        
        frequency = member.get('payment_frequency', 'Monthly')
        
        # Handle join date
        join_date = member.get('join_date', 'N/A')
        if join_date and join_date != 'N/A':
            if isinstance(join_date, str):
                try:
                    join_date = date.fromisoformat(join_date).strftime('%Y-%m-%d')
                except:
                    pass
            else:
                join_date = join_date.strftime('%Y-%m-%d')
        
        # Handle last payment date
        last_payment = member.get('last_payment_date', 'N/A')
        if last_payment and last_payment != 'N/A':
            if isinstance(last_payment, str):
                try:
                    last_payment = date.fromisoformat(last_payment).strftime('%Y-%m-%d')
                except:
                    pass
            else:
                last_payment = last_payment.strftime('%Y-%m-%d')
        
        # Insert row
        item = self.tree.insert('', 'end', values=(
            "☐",  # Checkbox placeholder
            member_id,
            name,
            phone,
            f"₹{amount:.2f}",
            due_date.strftime('%Y-%m-%d'),
            days_text,
            frequency,
            join_date if join_date != 'N/A' else 'N/A',
            last_payment if last_payment != 'N/A' else 'N/A'
        ), tags=(member_id,))
        
        # Tag for styling
        self.tree.set(item, "Select", "☐")
        
        # Color code rows
        if due_date < today:
            self.tree.item(item, tags=(member_id, "overdue"))
        else:
            self.tree.item(item, tags=(member_id, "due_soon"))
    
    def on_row_click(self, event):
        """Handle row click for checkbox selection"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            if column == "#1":  # Select column
                current_value = self.tree.set(item, "Select")
                member_id = int(self.tree.set(item, "ID"))
                
                if current_value == "☐":
                    self.tree.set(item, "Select", "☑")
                    self.selected_members.add(member_id)
                else:
                    self.tree.set(item, "Select", "☐")
                    self.selected_members.discard(member_id)
                
                self.update_selected_count()
    
    def on_row_double_click(self, event):
        """Handle double-click to record payment"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            member_id = int(self.tree.set(item, "ID"))
            self.record_payment(member_id)
    
    def select_all(self):
        """Select all members in the table"""
        for item in self.tree.get_children():
            member_id = int(self.tree.set(item, "ID"))
            self.tree.set(item, "Select", "☑")
            self.selected_members.add(member_id)
        self.update_selected_count()
    
    def deselect_all(self):
        """Deselect all members"""
        for item in self.tree.get_children():
            self.tree.set(item, "Select", "☐")
        self.selected_members.clear()
        self.update_selected_count()
    
    def update_selected_count(self):
        """Update the selected count label"""
        count = len(self.selected_members)
        self.selected_count_label.configure(text=f"{count} selected")
    
    def record_payment(self, member_id: int):
        """Open payment recording dialog"""
        from fee_management import FeeManagement
        # This would ideally open a payment dialog
        # For now, show a message
        member = self.db.get_member(member_id)
        if member:
            messagebox.showinfo(
                "Record Payment",
                f"To record payment for {member.get('name', 'Member')}, please use the 'Fees & Payments' page.\n\n"
                f"Member ID: {member_id}\n"
                f"Amount Due: ₹{member.get('fee_amount', 0):.2f}"
            )
    
    def send_bulk_reminders(self):
        """Send reminders to selected members"""
        if not self.selected_members:
            messagebox.showwarning("No Selection", "Please select members to send reminders to.")
            return
        
        count = len(self.selected_members)
        if messagebox.askyesno(
            "Send Reminders",
            f"Send payment reminders to {count} selected member(s)?"
        ):
            messagebox.showinfo(
                "Reminders Sent",
                f"Reminders will be sent to {count} member(s).\n\n"
                "Please use the 'WhatsApp Messages' page to send reminders."
            )
            # Clear selection after sending
            self.deselect_all()
    
    def export_data(self):
        """Export current table data"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                import csv
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write headers
                    headers = [self.tree.heading(col)['text'] for col in self.tree['columns']]
                    writer.writerow(headers)
                    # Write data
                    for item in self.tree.get_children():
                        values = [self.tree.set(item, col) for col in self.tree['columns']]
                        writer.writerow(values)
                
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

