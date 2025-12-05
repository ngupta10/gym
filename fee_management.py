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
        
        form_title = ctk.CTkLabel(
            form_frame,
            text="Record Payment",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        form_title.pack(pady=(20, 20))
        
        # Member search
        member_label = ctk.CTkLabel(
            form_frame,
            text="Search Member (Name/ID/Phone/Email) *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        member_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.member_search = ctk.CTkEntry(
            form_frame,
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
            form_frame,
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
            form_frame,
            text="Amount (₹) *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        amount_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.amount_input = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1"
        )
        self.amount_input.pack(fill="x", padx=20, pady=(0, 10))
        
        # Payment date
        date_label = ctk.CTkLabel(
            form_frame,
            text="Payment Date *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        date_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.payment_date = ctk.CTkEntry(
            form_frame,
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
            form_frame,
            text="Notes",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        notes_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.notes_input = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1"
        )
        self.notes_input.pack(fill="x", padx=20, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
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
        
        # Table
        table_frame = ctk.CTkFrame(history_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        columns = ('ID', 'Member', 'Amount', 'Date', 'Notes')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
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
        """Refresh payment history"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        payments = self.db.get_all_payments()
        for p in payments:
            self.tree.insert('', 'end', values=(
                p['id'],
                p['member_name'],
                f"₹{p['amount']:.2f}",
                p['payment_date'],
                p.get('notes', '')
            ))
    
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
