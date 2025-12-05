"""
Holiday Management Module - CustomTkinter
Handles staff holiday/leave recording and viewing
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date, datetime

class HolidayManagement(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.setup_ui()
        self.refresh_holiday_list()
    
    def setup_ui(self):
        """Create the holiday management UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Holiday Management",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(anchor="w", pady=(0, 25))
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # Form
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
            text="Record Holiday/Leave",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        form_title.pack(pady=(20, 20))
        
        # Staff selection
        staff_label = ctk.CTkLabel(
            form_frame,
            text="Staff Member *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        staff_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.staff_combo = ctk.CTkComboBox(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1"
        )
        self.staff_combo.pack(fill="x", padx=20, pady=(0, 10))
        self.update_staff_list()
        
        # Start date
        start_label = ctk.CTkLabel(
            form_frame,
            text="Start Date *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        start_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.start_date = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1",
            placeholder_text="YYYY-MM-DD"
        )
        self.start_date.pack(fill="x", padx=20, pady=(0, 10))
        
        # End date
        end_label = ctk.CTkLabel(
            form_frame,
            text="End Date *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        end_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.end_date = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1",
            placeholder_text="YYYY-MM-DD"
        )
        self.end_date.pack(fill="x", padx=20, pady=(0, 10))
        
        # Reason
        reason_label = ctk.CTkLabel(
            form_frame,
            text="Reason",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        reason_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.reason_input = ctk.CTkEntry(
            form_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1"
        )
        self.reason_input.pack(fill="x", padx=20, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Record Holiday",
            command=self.record_holiday,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=40
        )
        add_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
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
        
        # List
        list_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8
        )
        list_frame.pack(side="right", fill="both", padx=(7, 0), expand=True)
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="Holiday Records",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        list_title.pack(pady=(20, 10))
        
        # Table
        table_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        columns = ('ID', 'Staff Name', 'Start Date', 'End Date', 'Days', 'Reason', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh List",
            command=self.refresh_holiday_list,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=13),
            height=35
        )
        refresh_btn.pack(fill="x")
    
    def update_staff_list(self):
        """Update staff dropdown"""
        staff = self.db.get_all_staff()
        staff_names = [f"{s['name']} (ID: {s['id']})" for s in staff]
        self.staff_combo.configure(values=staff_names)
        if staff_names:
            self.staff_combo.set(staff_names[0])
    
    def record_holiday(self):
        """Record a holiday"""
        if not self.staff_combo.get():
            messagebox.showwarning("Error", "Please select a staff member!")
            return
        
        try:
            staff_name = self.staff_combo.get().split(" (ID: ")[0]
            staff_id = int(self.staff_combo.get().split("(ID: ")[1].rstrip(")"))
        except:
            messagebox.showerror("Error", "Invalid staff selection!")
            return
        
        try:
            start_date = datetime.strptime(self.start_date.get(), '%Y-%m-%d').date()
            end_date = datetime.strptime(self.end_date.get(), '%Y-%m-%d').date()
            
            if end_date < start_date:
                messagebox.showerror("Error", "End date must be after start date!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in YYYY-MM-DD format!")
            return
        
        reason = self.reason_input.get().strip()
        
        try:
            self.db.add_holiday(staff_id, start_date, end_date, reason)
            messagebox.showinfo("Success", f"Holiday recorded for '{staff_name}'!")
            self.clear_form()
            self.refresh_holiday_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record holiday: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        self.update_staff_list()
        self.start_date.delete(0, "end")
        self.end_date.delete(0, "end")
        self.reason_input.delete(0, "end")
    
    def refresh_holiday_list(self):
        """Refresh the holiday list"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        holidays = self.db.get_all_holidays()
        for h in holidays:
            start = datetime.strptime(h['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(h['end_date'], '%Y-%m-%d').date()
            days = (end - start).days + 1
            
            self.tree.insert('', 'end', values=(
                h['id'],
                h['staff_name'],
                h['start_date'],
                h['end_date'],
                days,
                h.get('reason', ''),
                h.get('status', 'approved').title()
            ))
