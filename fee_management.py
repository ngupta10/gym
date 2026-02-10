"""
Fee Management Module - CustomTkinter
Handles payment recording and fee tracking
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date, datetime

class FeeManagement(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.setup_ui()
        self.refresh_payment_list()
        self.update_alerts()
    
    def setup_ui(self):
        """Create the fee management UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Fee & Payment Management",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(anchor="w", pady=(0, 25))
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # Left side - Payment form
        form_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8
        )
        form_frame.pack(side="left", fill="both", padx=(0, 7), expand=True)
        form_frame.grid_rowconfigure(0, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame for the form
        scrollable_form = ctk.CTkScrollableFrame(
            form_frame,
            fg_color="transparent"
        )
        scrollable_form.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        form_title = ctk.CTkLabel(
            scrollable_form,
            text="Record Payment",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        form_title.pack(pady=(20, 20))
        
        # Member search
        member_label = ctk.CTkLabel(
            scrollable_form,
            text="Search Member (Name/ID/Phone/Email) *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        member_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.member_search = ctk.CTkEntry(
            scrollable_form,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1",
            placeholder_text="Type to search..."
        )
        self.member_search.pack(fill="x", padx=20, pady=(0, 5))
        self.member_search.bind("<KeyRelease>", self.on_search_member)
        
        # Member selection dropdown (filtered results)
        self.member_combo = ctk.CTkComboBox(
            scrollable_form,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1",
            command=self.on_member_selected
        )
        self.member_combo.pack(fill="x", padx=20, pady=(0, 10))
        self.update_member_list()
        
        # Amount
        amount_label = ctk.CTkLabel(
            scrollable_form,
            text="Amount (₹) *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        amount_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.amount_input = ctk.CTkEntry(
            scrollable_form,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1"
        )
        self.amount_input.pack(fill="x", padx=20, pady=(0, 10))
        
        # Payment date
        date_label = ctk.CTkLabel(
            scrollable_form,
            text="Payment Date *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        date_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.payment_date = ctk.CTkEntry(
            scrollable_form,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1",
            placeholder_text="YYYY-MM-DD"
        )
        self.payment_date.insert(0, date.today().strftime('%Y-%m-%d'))
        self.payment_date.pack(fill="x", padx=20, pady=(0, 10))
        
        # Notes
        notes_label = ctk.CTkLabel(
            scrollable_form,
            text="Notes",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        notes_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.notes_input = ctk.CTkEntry(
            scrollable_form,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1"
        )
        self.notes_input.pack(fill="x", padx=20, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(scrollable_form, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        record_btn = ctk.CTkButton(
            button_frame,
            text="Record Payment",
            command=self.record_payment,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=40
        )
        record_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            command=self.clear_form,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=14),
            height=40
        )
        clear_btn.pack(side="left", fill="x", expand=True)
        
        # Right side
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", padx=(7, 0), expand=True)
        
        # Member info
        info_frame = ctk.CTkFrame(
            right_frame,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8
        )
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_title = ctk.CTkLabel(
            info_frame,
            text="Member Payment Info",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        info_title.pack(pady=(20, 10))
        
        self.member_info_label = ctk.CTkLabel(
            info_frame,
            text="Select a member to view payment details",
            font=ctk.CTkFont(size=14),
            text_color="#64748b",
            wraplength=400
        )
        self.member_info_label.pack(padx=20, pady=(0, 20))
        
        # Payment history
        history_frame = ctk.CTkFrame(
            right_frame,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8
        )
        history_frame.pack(fill="both", expand=True)
        
        history_title = ctk.CTkLabel(
            history_frame,
            text="Payment History",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        history_title.pack(pady=(20, 10))
        
        # Filter section
        filter_frame = ctk.CTkFrame(history_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="Filters:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1a1a2e"
        )
        filter_label.pack(anchor="w", pady=(0, 8))
        
        # Filter inputs row
        filter_inputs_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_inputs_frame.pack(fill="x")
        
        # Member Name filter
        name_label = ctk.CTkLabel(
            filter_inputs_frame,
            text="Member Name:",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
            width=100
        )
        name_label.pack(side="left", padx=(0, 5))
        
        self.filter_name = ctk.CTkEntry(
            filter_inputs_frame,
            placeholder_text="Filter by name...",
            width=150,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.filter_name.pack(side="left", padx=(0, 10))
        self.filter_name.bind("<KeyRelease>", lambda e: self.refresh_payment_list())
        
        # Member ID filter
        id_label = ctk.CTkLabel(
            filter_inputs_frame,
            text="Member ID:",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
            width=80
        )
        id_label.pack(side="left", padx=(0, 5))
        
        self.filter_id = ctk.CTkEntry(
            filter_inputs_frame,
            placeholder_text="Filter by ID...",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.filter_id.pack(side="left", padx=(0, 10))
        self.filter_id.bind("<KeyRelease>", lambda e: self.refresh_payment_list())
        
        # Date filter
        date_label = ctk.CTkLabel(
            filter_inputs_frame,
            text="Date:",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
            width=50
        )
        date_label.pack(side="left", padx=(0, 5))
        
        self.filter_date = ctk.CTkEntry(
            filter_inputs_frame,
            placeholder_text="YYYY-MM-DD",
            width=120,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        self.filter_date.pack(side="left", padx=(0, 10))
        self.filter_date.bind("<KeyRelease>", lambda e: self.refresh_payment_list())
        
        # Clear filters button
        clear_filters_btn = ctk.CTkButton(
            filter_inputs_frame,
            text="Clear Filters",
            command=self.clear_filters,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=11),
            width=100,
            height=30
        )
        clear_filters_btn.pack(side="left")
        
        # Table
        table_frame = ctk.CTkFrame(history_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        columns = ('Member ID', 'Member', 'Amount', 'Date', 'Notes')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configure column widths
        column_widths = {
            'Member ID': 80,
            'Member': 150,
            'Amount': 100,
            'Date': 100,
            'Notes': 200
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Alerts
        alerts_frame = ctk.CTkFrame(
            right_frame,
            fg_color="#ffffff",
            border_width=0
        )
        alerts_frame.pack(fill="x", pady=(15, 0))
        
        self.alerts_label = ctk.CTkLabel(
            alerts_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e",
            wraplength=400
        )
        self.alerts_label.pack(pady=10)
    
    def update_member_list(self, search_term=""):
        """Update member dropdown with search filtering"""
        members = self.db.get_all_members(active_only=False)
        
        # Filter members based on search term
        if search_term:
            search_term = search_term.lower().strip()
            filtered_members = []
            for m in members:
                # Search in name, id, phone, email
                if (search_term in m['name'].lower() or
                    search_term in str(m['id']) or
                    (m.get('phone') and search_term in str(m['phone']).lower()) or
                    (m.get('email') and search_term in str(m['email']).lower())):
                    filtered_members.append(m)
            members = filtered_members
        
        member_names = [f"{m['name']} (ID: {m['id']})" for m in members]
        self.member_combo.configure(values=member_names)
        if member_names:
            self.member_combo.set(member_names[0])
            self.on_member_selected(member_names[0])
        else:
            self.member_combo.set("")
            self.member_info_label.configure(text="No members found")
    
    def on_search_member(self, event=None):
        """Handle member search input"""
        search_term = self.member_search.get()
        self.update_member_list(search_term)
    
    def on_member_selected(self, value):
        """Handle member selection"""
        try:
            member_id = int(value.split("(ID: ")[1].rstrip(")"))
            members = self.db.get_all_members()
            member = next((m for m in members if m['id'] == member_id), None)
            
            if member:
                info = f"""Name: {member['name']}
Membership: {member['membership_type']}
Fee: ₹{member['fee_amount']:.2f} ({member['payment_frequency']})
Next Payment: {member.get('next_payment_date', 'N/A')}"""
                self.member_info_label.configure(text=info)
                
                # Auto-fill amount
                if not self.amount_input.get():
                    self.amount_input.insert(0, str(member['fee_amount']))
        except:
            pass
    
    def record_payment(self):
        """Record a payment"""
        if not self.member_combo.get():
            messagebox.showwarning("Error", "Please select a member!")
            return
        
        try:
            member_id = int(self.member_combo.get().split("(ID: ")[1].rstrip(")"))
        except:
            messagebox.showerror("Error", "Invalid member selection!")
            return
        
        try:
            amount = float(self.amount_input.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")
            return
        
        try:
            payment_date = datetime.strptime(self.payment_date.get(), '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date in YYYY-MM-DD format!")
            return
        
        notes = self.notes_input.get().strip()
        
        try:
            self.db.record_payment(member_id, amount, payment_date, notes)
            messagebox.showinfo("Success", "Payment recorded successfully!")
            self.clear_form()
            self.refresh_payment_list()
            self.update_alerts()
            self.update_member_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record payment: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        self.member_search.delete(0, "end")
        self.update_member_list()
        self.amount_input.delete(0, "end")
        self.payment_date.delete(0, "end")
        self.payment_date.insert(0, date.today().strftime('%Y-%m-%d'))
        self.notes_input.delete(0, "end")
    
    def refresh_payment_list(self):
        """Refresh payment history with filters"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all payments
        payments = self.db.get_all_payments()
        
        # Apply filters
        filtered_payments = self.apply_filters(payments)
        
        # Populate table
        for p in filtered_payments:
            self.tree.insert('', 'end', values=(
                p.get('member_id', 'N/A'),  # Member ID
                p.get('member_name', 'N/A'),  # Member Name
                f"₹{p['amount']:.2f}",
                p['payment_date'],
                p.get('notes', '')
            ))
    
    def apply_filters(self, payments):
        """Apply filters to payment list"""
        filtered = payments
        
        # Filter by member name
        name_filter = self.filter_name.get().strip().lower()
        if name_filter:
            filtered = [p for p in filtered if name_filter in p.get('member_name', '').lower()]
        
        # Filter by member ID
        id_filter = self.filter_id.get().strip()
        if id_filter:
            try:
                # Try to match exact ID
                target_id = int(id_filter)
                filtered = [p for p in filtered if p.get('member_id') == target_id]
            except ValueError:
                # If not a number, try string match
                filtered = [p for p in filtered if id_filter in str(p.get('member_id', ''))]
        
        # Filter by date
        date_filter = self.filter_date.get().strip()
        if date_filter:
            try:
                # Try to parse as date
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                filtered = [p for p in filtered if self._matches_date(p.get('payment_date'), filter_date)]
            except ValueError:
                # If invalid date format, try string match
                filtered = [p for p in filtered if date_filter in str(p.get('payment_date', ''))]
        
        return filtered
    
    def _matches_date(self, payment_date, filter_date):
        """Check if payment date matches filter date"""
        if not payment_date:
            return False
        
        # Convert payment_date to date object if it's a string
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            except ValueError:
                return False
        
        return payment_date == filter_date
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_name.delete(0, "end")
        self.filter_id.delete(0, "end")
        self.filter_date.delete(0, "end")
        self.refresh_payment_list()
    
    def update_alerts(self):
        """Update payment alerts"""
        overdue = self.db.get_overdue_members()
        due_soon = self.db.get_due_soon_members()  # Frequency-aware reminders
        
        alerts = []
        if overdue:
            alerts.append(f"⚠️ {len(overdue)} Overdue Payment(s)")
        if due_soon:
            alerts.append(f"🔔 {len(due_soon)} Payment(s) Due Soon")
        
        if alerts:
            self.alerts_label.configure(text="\n".join(alerts), text_color="#dc2626")
        else:
            self.alerts_label.configure(text="No payment alerts", text_color="#166534")
