"""
Staff Management Module - CustomTkinter
Handles staff registration, removal, and viewing
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date

class StaffManagement(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.setup_ui()
        self.refresh_staff_list()
    
    def setup_ui(self):
        """Create the staff management UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Staff Management",
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
            text="Add New Staff Member",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        form_title.pack(pady=(20, 20))
        
        # Form fields
        self.form_widgets = {}
        fields = [
            ("Name *", "name", "entry"),
            ("Email", "email", "entry"),
            ("Phone", "phone", "entry"),
            ("Position *", "position", "combo", ["Trainer", "Manager", "Receptionist", "Cleaner"]),
        ]
        
        for label_text, key, field_type, *options in fields:
            label = ctk.CTkLabel(
                form_frame,
                text=label_text,
                font=ctk.CTkFont(size=14),
                text_color="#1a1a2e"
            )
            label.pack(anchor="w", padx=20, pady=(10, 5))
            
            if field_type == "entry":
                widget = ctk.CTkEntry(
                    form_frame,
                    height=35,
                    font=ctk.CTkFont(size=14),
                    border_width=1,
                    border_color="#cbd5e1"
                )
            else:  # combo
                widget = ctk.CTkComboBox(
                    form_frame,
                    values=options[0] if options else [],
                    height=35,
                    font=ctk.CTkFont(size=14),
                    border_width=1,
                    border_color="#cbd5e1"
                )
                widget.set("Trainer")
            
            widget.pack(fill="x", padx=20, pady=(0, 10))
            self.form_widgets[key] = widget
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add Staff",
            command=self.add_staff,
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
            text="Staff List",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        list_title.pack(pady=(20, 10))
        
        # Table
        table_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        columns = ('ID', 'Name', 'Email', 'Phone', 'Position', 'Hire Date', 'Status')
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
        
        remove_btn = ctk.CTkButton(
            action_frame,
            text="Remove Staff",
            command=self.remove_staff,
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35
        )
        remove_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh List",
            command=self.refresh_staff_list,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=13),
            height=35
        )
        refresh_btn.pack(side="left", fill="x", expand=True)
    
    def add_staff(self):
        """Add a new staff member"""
        if not self.form_widgets['name'].get().strip():
            messagebox.showwarning("Error", "Name is required!")
            return
        
        name = self.form_widgets['name'].get().strip()
        email = self.form_widgets['email'].get().strip()
        phone = self.form_widgets['phone'].get().strip()
        position = self.form_widgets['position'].get()
        hire_date = date.today()
        
        try:
            staff_id = self.db.add_staff(name, email, phone, position, hire_date)
            messagebox.showinfo("Success", f"Staff member '{name}' added successfully!")
            self.clear_form()
            self.refresh_staff_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add staff: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        for key, widget in self.form_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("Trainer")
    
    def refresh_staff_list(self):
        """Refresh the staff list"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        staff = self.db.get_all_staff()
        for s in staff:
            self.tree.insert('', 'end', values=(
                s['id'],
                s['name'],
                s.get('email', ''),
                s.get('phone', ''),
                s.get('position', ''),
                s['hire_date'],
                s.get('status', 'active').title()
            ))
    
    def remove_staff(self):
        """Remove selected staff"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a staff member to remove.")
            return
        
        item = self.tree.item(selection[0])
        staff_id = item['values'][0]
        staff_name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove '{staff_name}'?"):
            try:
                self.db.remove_staff(staff_id)
                messagebox.showinfo("Success", f"Staff member '{staff_name}' removed successfully!")
                self.refresh_staff_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove staff: {str(e)}")
