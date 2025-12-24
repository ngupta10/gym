"""
Member Management Module - CustomTkinter
Handles member registration, removal, and viewing
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, Entry, simpledialog
from datetime import date, datetime
import sqlite3
import os

class MemberManagement(ctk.CTkFrame):
    # Password for protected operations
    PROTECTED_PASSWORD = "1234"
    _editing_item = None  # Track currently editing item to prevent multiple password prompts
    
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.selected_members = set()  # Track selected member IDs
        self.setup_ui()
        self.refresh_member_list()
    
    def verify_password(self) -> bool:
        """Verify password for protected operations"""
        password = simpledialog.askstring("Password Required", "Enter password to continue:", show='*')
        if password == self.PROTECTED_PASSWORD:
            return True
        elif password is None:
            # User cancelled
            return False
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")
            return False
    
    def setup_ui(self):
        """Create the member management UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Member Management",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(anchor="w", pady=(0, 25))
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        # Configure grid for side-by-side layout
        main_frame.grid_columnconfigure(0, weight=0, minsize=450)  # Form has minimum width
        main_frame.grid_columnconfigure(1, weight=1)  # List takes remaining space
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left side - Registration form
        form_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8,
            width=450
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 7), pady=0)
        form_frame.grid_propagate(False)  # Prevent shrinking below width
        form_frame.grid_rowconfigure(0, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame inside form_frame
        self.scrollable_form = ctk.CTkScrollableFrame(
            form_frame,
            fg_color="transparent"
        )
        self.scrollable_form.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        form_title = ctk.CTkLabel(
            self.scrollable_form,
            text="Register New Member",
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
            ("Join Date *", "join_date", "entry"),
            ("Membership Type *", "membership_type", "combo", ["Standard", "Personal Training"]),
            ("Fee Amount (₹) *", "fee_amount", "entry"),
            ("Payment Frequency *", "payment_frequency", "combo", ["Daily", "Monthly", "Quarterly", "Yearly"]),
        ]
        
        for label_text, key, field_type, *options in fields:
            label = ctk.CTkLabel(
                self.scrollable_form,
                text=label_text,
                font=ctk.CTkFont(size=14),
                text_color="#1a1a2e"
            )
            label.pack(anchor="w", padx=20, pady=(10, 5))
            
            if field_type == "entry":
                widget = ctk.CTkEntry(
                    self.scrollable_form,
                    height=35,
                    font=ctk.CTkFont(size=14),
                    border_width=1,
                    border_color="#cbd5e1"
                )
                if key == "join_date":
                    widget.insert(0, date.today().strftime('%Y-%m-%d'))
                    widget.configure(placeholder_text="YYYY-MM-DD")
            else:  # combo
                widget = ctk.CTkComboBox(
                    self.scrollable_form,
                    values=options[0] if options else [],
                    height=35,
                    font=ctk.CTkFont(size=14),
                    border_width=1,
                    border_color="#cbd5e1"
                )
                if key == "membership_type":
                    widget.set("Standard")
                    # Bind to show/hide trainer field
                    widget.configure(command=self.on_membership_type_change)
                elif key == "payment_frequency":
                    widget.set("Monthly")
            
            widget.pack(fill="x", padx=20, pady=(0, 10))
            self.form_widgets[key] = widget
        
        # Trainer selection field (initially hidden)
        self.trainer_label = ctk.CTkLabel(
            self.scrollable_form,
            text="Select Trainer *",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        
        self.trainer_combo = ctk.CTkComboBox(
            self.scrollable_form,
            values=[],
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1"
        )
        
        # Initially hide trainer field
        self.trainer_label.pack_forget()
        self.trainer_combo.pack_forget()
        
        # Buttons
        button_frame = ctk.CTkFrame(self.scrollable_form, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        register_btn = ctk.CTkButton(
            button_frame,
            text="Register Member",
            command=self.register_member,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=40
        )
        register_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
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
        
        # Right side - Member list
        list_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8
        )
        list_frame.grid(row=0, column=1, sticky="nsew", padx=(7, 0), pady=0)
        # Configure grid for proper layout
        list_frame.grid_rowconfigure(0, weight=0)  # Title row (fixed)
        list_frame.grid_rowconfigure(1, weight=0)  # Headers info row (fixed)
        list_frame.grid_rowconfigure(2, weight=0)  # Search row (fixed)
        list_frame.grid_rowconfigure(3, weight=1)  # Table row (expandable)
        list_frame.grid_rowconfigure(4, weight=0)  # Action buttons row (fixed, always visible)
        list_frame.grid_columnconfigure(0, weight=1)
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="Members List",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        list_title.grid(row=0, column=0, sticky="w", pady=(20, 10), padx=20)
        
        # Column headers info label
        headers_info = ctk.CTkLabel(
            list_frame,
            text="Column Order: Select | ID | Name | Email | Phone | Join Date | Type | Frequency | Trainer | Fee | Next Payment | Status",
            font=ctk.CTkFont(size=12),
            text_color="#64748b"
        )
        headers_info.grid(row=1, column=0, sticky="w", pady=(0, 10), padx=20)
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1",
            placeholder_text="Search by name..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Status filter
        filter_label = ctk.CTkLabel(
            search_frame,
            text="Filter:",
            font=ctk.CTkFont(size=14),
            text_color="#1a1a2e"
        )
        filter_label.pack(side="left", padx=(0, 10))
        
        self.status_filter = ctk.CTkComboBox(
            search_frame,
            values=["Active Only", "Inactive Only", "All Members"],
            height=35,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color="#cbd5e1",
            command=self.on_filter_change
        )
        self.status_filter.set("Active Only")
        self.status_filter.pack(side="left", padx=(0, 10))
        
        # Select All/Deselect All buttons
        select_all_btn = ctk.CTkButton(
            search_frame,
            text="Select All",
            command=self.select_all_members,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=12),
            height=30,
            width=90
        )
        select_all_btn.pack(side="left", padx=(0, 5))
        
        deselect_all_btn = ctk.CTkButton(
            search_frame,
            text="Deselect All",
            command=self.deselect_all_members,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=12),
            height=30,
            width=90
        )
        deselect_all_btn.pack(side="left", padx=(0, 0))
        
        # Table
        table_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        table_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        columns = ('Select', 'ID', 'Name', 'Email', 'Phone', 'Join Date', 'Type', 'Frequency', 'Trainer', 'Fee', 'Next Payment', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure style for Excel-like appearance
        style = ttk.Style()
        
        # Excel-like Treeview styling with grid lines
        style.configure("Treeview", 
                       background="white", 
                       fieldbackground="white", 
                       foreground="black",
                       rowheight=22,
                       borderwidth=1,
                       relief="solid",
                       font=('Arial', 13))
        
        # Header styling with black text for visibility
        style.configure("Treeview.Heading", 
                       background="#f8fafc",  # Light background
                       foreground="black",  # Black text for visibility
                       borderwidth=1,
                       relief="solid",
                       font=('Arial', 14, 'bold'),
                       padding=(8, 8))
        
        # Ensure header cells have borders
        style.map("Treeview.Heading",
                 background=[("active", "#e2e8f0")],  # Slightly darker on hover
                 relief=[("pressed", "sunken"), ("!pressed", "solid")])
        
        # Selected row styling (light blue like Excel)
        style.map("Treeview", 
                 background=[("selected", "#D0E3F0")],  # Light blue selection
                 foreground=[("selected", "black")])
        
        # Set alternating row colors like Excel
        self.tree.tag_configure("evenrow", background="#F2F2F2")  # Light gray
        self.tree.tag_configure("oddrow", background="white")
        
        # Excel-like column widths and alignment
        column_widths = {
            'Select': 60,
            'ID': 50,
            'Name': 150,
            'Email': 180,
            'Phone': 120,
            'Join Date': 110,
            'Type': 130,
            'Frequency': 100,
            'Trainer': 150,
            'Fee': 100,
            'Next Payment': 120,
            'Status': 80
        }
        
        for col in columns:
            # Configure column headers with proper text
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=column_widths.get(col, 100), anchor='w', minwidth=50)
        
        # Bind click on Select column to toggle selection
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Ensure headers are visible - explicitly set show parameter
        self.tree.configure(show='headings')
        
        # Make headers more prominent by ensuring they're always visible
        # Force header visibility
        try:
            # This ensures the heading row is always displayed
            self.tree['show'] = 'headings'
        except:
            pass
        
        # Make table editable (but not on Select column)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.editing_item = None
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Use grid layout for scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights for proper resizing
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons (always visible at bottom) - with horizontal scroll
        action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        action_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame for buttons
        scrollable_button_frame = ctk.CTkScrollableFrame(
            action_frame,
            orientation="horizontal",
            fg_color="transparent"
        )
        scrollable_button_frame.grid(row=0, column=0, sticky="ew")
        scrollable_button_frame.grid_columnconfigure(0, weight=1)
        
        # Button container inside scrollable frame
        button_container = ctk.CTkFrame(scrollable_button_frame, fg_color="transparent")
        button_container.pack(fill="x", expand=True)
        
        save_btn = ctk.CTkButton(
            button_container,
            text="Save Changes",
            command=self.save_changes,
            fg_color="#10b981",
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            width=120
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        view_btn = ctk.CTkButton(
            button_container,
            text="View Details",
            command=self.view_member_details,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            width=120
        )
        view_btn.pack(side="left", padx=(0, 10))
        
        toggle_status_btn = ctk.CTkButton(
            button_container,
            text="Toggle Status (Bulk)",
            command=self.toggle_member_status,
            fg_color="#f59e0b",
            hover_color="#d97706",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            width=120
        )
        toggle_status_btn.pack(side="left", padx=(0, 10))
        
        remove_btn = ctk.CTkButton(
            button_container,
            text="Remove Member",
            command=self.remove_member,
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            width=130
        )
        remove_btn.pack(side="left", padx=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            button_container,
            text="Refresh List",
            command=self.refresh_member_list,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=13),
            height=35,
            width=120
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Fix ID Reuse button (utility function)
        fix_id_btn = ctk.CTkButton(
            button_container,
            text="Fix ID Reuse",
            command=self.fix_id_reuse,
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            font=ctk.CTkFont(size=13),
            height=35,
            width=120
        )
        fix_id_btn.pack(side="left")
    
    def on_membership_type_change(self, value=None):
        """Show/hide trainer selection based on membership type"""
        membership_type = self.form_widgets['membership_type'].get()
        
        if membership_type == "Personal Training":
            # Load trainers and show field
            trainers = self.db.get_trainers()
            if trainers:
                trainer_names = [f"{t['name']} (ID: {t['id']})" for t in trainers]
                self.trainer_combo.configure(values=trainer_names)
                if trainer_names:
                    self.trainer_combo.set(trainer_names[0])
                
                # Show trainer field
                self.trainer_label.pack(anchor="w", padx=20, pady=(10, 5))
                self.trainer_combo.pack(fill="x", padx=20, pady=(0, 10))
            else:
                messagebox.showwarning("No Trainers", "No active trainers found. Please add trainers in Staff Management first.")
                self.form_widgets['membership_type'].set("Standard")
        else:
            # Hide trainer field
            self.trainer_label.pack_forget()
            self.trainer_combo.pack_forget()
    
    def register_member(self):
        """Register a new member"""
        # Validate
        if not self.form_widgets['name'].get().strip():
            messagebox.showwarning("Error", "Name is required!")
            return
        
        try:
            fee_amount = float(self.form_widgets['fee_amount'].get())
            if fee_amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Please enter a valid fee amount!")
            return
        
        # Get form data
        name = self.form_widgets['name'].get().strip()
        email = self.form_widgets['email'].get().strip()
        phone = self.form_widgets['phone'].get().strip()
        membership_type = self.form_widgets['membership_type'].get()
        payment_frequency = self.form_widgets['payment_frequency'].get()
        
        # Parse join date
        try:
            join_date_str = self.form_widgets['join_date'].get().strip()
            if join_date_str:
                join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
            else:
                join_date = date.today()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid join date in YYYY-MM-DD format!")
            return
        
        try:
            # Get trainer_id if Personal Training
            trainer_id = None
            if membership_type == "Personal Training":
                trainer_selection = self.trainer_combo.get()
                if trainer_selection:
                    # Extract trainer ID from selection (format: "Name (ID: 123)")
                    try:
                        trainer_id = int(trainer_selection.split("ID: ")[1].rstrip(")"))
                    except (IndexError, ValueError):
                        messagebox.showerror("Error", "Please select a valid trainer!")
                        return
                else:
                    messagebox.showerror("Error", "Please select a trainer for Personal Training membership!")
                    return
            
            # Add member (ID will be auto-generated)
            member_id = self.db.add_member(
                name, email, phone, join_date,
                membership_type, fee_amount, payment_frequency, trainer_id
            )
            
            messagebox.showinfo("Success", f"Member '{name}' registered successfully!")
            self.clear_form()
            self.refresh_member_list()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Failed to register member: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register member: {str(e)}")
    
    def clear_form(self):
        """Clear the registration form"""
        for key, widget in self.form_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                if key == "join_date":
                    widget.insert(0, date.today().strftime('%Y-%m-%d'))
            elif isinstance(widget, ctk.CTkComboBox):
                if key == "membership_type":
                    widget.set("Standard")
                    # Bind to show/hide trainer field
                    widget.configure(command=self.on_membership_type_change)
                elif key == "payment_frequency":
                    widget.set("Monthly")
        
        # Hide trainer field when clearing form
        self.trainer_label.pack_forget()
        self.trainer_combo.pack_forget()
    
    def refresh_member_list(self, search_term=""):
        """Refresh the member list"""
        # Clear existing items and preserve selected members
        # (selected_members set persists across refreshes)
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filter selection
        filter_value = self.status_filter.get() if hasattr(self, 'status_filter') else "Active Only"
        
        # Get members based on filter
        if filter_value == "Active Only":
            members = self.db.get_all_members(active_only=True)
        elif filter_value == "Inactive Only":
            all_members = self.db.get_all_members(active_only=False)
            members = [m for m in all_members if m.get('status', 'active').lower() == 'inactive']
        else:  # All Members
            members = self.db.get_all_members(active_only=False)
        
        # Filter by search term if provided
        if search_term:
            search_term_lower = search_term.lower()
            # Check if search term is numeric (could be an ID)
            is_numeric = search_term.strip().isdigit()
            filtered_members = []
            for m in members:
                # Search by name (case-insensitive)
                if search_term_lower in m['name'].lower():
                    filtered_members.append(m)
                # Search by ID if search term is numeric
                elif is_numeric and str(m['id']) == search_term.strip():
                    filtered_members.append(m)
            members = filtered_members
        
        # Get all trainers for name lookup
        trainers = self.db.get_trainers()
        trainer_dict = {t['id']: t['name'] for t in trainers}
        
        for idx, member in enumerate(members):
            next_payment = member.get('next_payment_date', 'N/A')
            status = member.get('status', 'active').title()
            
            # Get trainer name
            trainer_id = member.get('trainer_id')
            trainer_name = trainer_dict.get(trainer_id, 'N/A') if trainer_id else 'N/A'
            # Only show trainer if membership type is Personal Training
            if member.get('membership_type') != 'Personal Training':
                trainer_name = 'N/A'
            
            # Alternate row colors for Excel-like appearance
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            
            join_date = member.get('join_date', 'N/A')
            
            # Check if member is selected
            is_selected = member['id'] in self.selected_members
            select_text = "☑" if is_selected else "☐"
            
            self.tree.insert('', 'end', values=(
                select_text,  # Select column (index 0)
                member['id'],  # ID column (index 1)
                member['name'],  # Name column (index 2)
                member.get('email', ''),  # Email column (index 3)
                member.get('phone', ''),  # Phone column (index 4)
                join_date,  # Join Date column (index 5)
                member['membership_type'],  # Type column (index 6)
                member.get('payment_frequency', 'Monthly'),  # Frequency column (index 7)
                trainer_name,  # Trainer column (index 8)
                f"₹{member['fee_amount']:.2f}",  # Fee column (index 9)
                next_payment,  # Next Payment column (index 10)
                status  # Status column (index 11)
            ), tags=(tag, str(member['id'])))
    
    def on_search(self, event=None):
        """Handle search input"""
        search_term = self.search_entry.get()
        self.refresh_member_list(search_term)
    
    def on_filter_change(self, value=None):
        """Handle status filter change"""
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        self.refresh_member_list(search_term)
    
    def on_double_click(self, event):
        """Handle double-click to edit cell"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.tree.selection()[0] if self.tree.selection() else None
            if not item:
                return
            
            # Check if we're already editing this item (prevent multiple password prompts)
            if self._editing_item == item:
                return
            
            column = self.tree.identify_column(event.x)
            column_index = int(column.replace('#', '')) - 1
            columns = ('Select', 'ID', 'Name', 'Email', 'Phone', 'Join Date', 'Type', 'Frequency', 'Trainer', 'Fee', 'Next Payment', 'Status')
            
            # Don't allow editing Select column (use checkbox click instead)
            if column_index == 0:  # Select column
                return
            
            # Don't allow editing ID column
            if column_index == 1:  # ID column
                return
            
            # Don't allow editing Status column (use Toggle Status button instead)
            if column_index == 11:  # Status column (last column, index 11)
                return
            
            # Don't allow editing Next Payment column (it's calculated)
            if column_index == 10:  # Next Payment column
                messagebox.showinfo("Info", "Next Payment date is automatically calculated. Change Join Date, Type, or Frequency to update it.")
                return
            
            # Verify password before allowing edits (only once per editing session)
            if self._editing_item is None:
                if not self.verify_password():
                    return
                self._editing_item = item
            
            # Get current value
            current_values = list(self.tree.item(item, 'values'))
            current_value = current_values[column_index] if column_index < len(current_values) else ""
            
            # Get bbox for positioning
            bbox = self.tree.bbox(item, column)
            if not bbox:
                return
            
            # Check if this is a dropdown column (Type or Frequency)
            if column_index == 6:  # Type (Membership Type) column (now index 6 after Select column)
                # Use Combobox for membership type
                from tkinter import ttk as ttk_widgets
                edit_combo = ttk_widgets.Combobox(self.tree, 
                                                  values=["Standard", "Personal Training"],
                                                  font=('Arial', 13),
                                                  state="readonly")
                edit_combo.set(str(current_value))
                
                def save_edit_combo(event=None):
                    if not edit_combo.winfo_exists():
                        return
                    new_value = edit_combo.get()
                    if new_value:
                        current_values[column_index] = new_value
                        self.tree.item(item, values=tuple(current_values))
                        # Auto-recalculate next payment date
                        self._recalculate_payment_date_for_item(item)
                    edit_combo.destroy()
                    self._editing_item = None  # Reset editing flag
                
                def cancel_edit_combo(event=None):
                    if edit_combo.winfo_exists():
                        edit_combo.destroy()
                    self._editing_item = None  # Reset editing flag
                
                # Only bind to ComboboxSelected - don't use FocusOut as it fires when dropdown opens
                edit_combo.bind("<<ComboboxSelected>>", save_edit_combo)
                edit_combo.bind("<Escape>", cancel_edit_combo)
                # Use after_idle to ensure combobox is fully created before focusing
                self.tree.after_idle(lambda: edit_combo.focus_set())
                edit_combo.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                
            elif column_index == 7:  # Frequency (Payment Frequency) column (now index 7 after Select column)
                # Use Combobox for payment frequency
                from tkinter import ttk as ttk_widgets
                edit_combo = ttk_widgets.Combobox(self.tree, 
                                                  values=["Daily", "Monthly", "Quarterly", "Yearly"],
                                                  font=('Arial', 13),
                                                  state="readonly")
                edit_combo.set(str(current_value))
                
                def save_edit_combo(event=None):
                    if not edit_combo.winfo_exists():
                        return
                    new_value = edit_combo.get()
                    if new_value:
                        current_values[column_index] = new_value
                        self.tree.item(item, values=tuple(current_values))
                        # Auto-recalculate next payment date
                        self._recalculate_payment_date_for_item(item)
                    edit_combo.destroy()
                    self._editing_item = None  # Reset editing flag
                
                def cancel_edit_combo(event=None):
                    if edit_combo.winfo_exists():
                        edit_combo.destroy()
                    self._editing_item = None  # Reset editing flag
                
                # Only bind to ComboboxSelected - don't use FocusOut as it fires when dropdown opens
                edit_combo.bind("<<ComboboxSelected>>", save_edit_combo)
                edit_combo.bind("<Escape>", cancel_edit_combo)
                # Use after_idle to ensure combobox is fully created before focusing
                self.tree.after_idle(lambda: edit_combo.focus_set())
                edit_combo.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                
            elif column_index == 8:  # Trainer column (now index 8 after Select column)
                # Use Combobox for trainer selection
                from tkinter import ttk as ttk_widgets
                trainers = self.db.get_trainers()
                if not trainers:
                    messagebox.showwarning("No Trainers", "No active trainers available. Please add trainers in Staff Management first.")
                    self._editing_item = None
                    return
                
                trainer_options = ["N/A"] + [f"{t['name']} (ID: {t['id']})" for t in trainers]
                edit_combo = ttk_widgets.Combobox(self.tree, 
                                                  values=trainer_options,
                                                  font=('Arial', 13),
                                                  state="readonly")
                # Set current trainer or "N/A"
                if current_value and current_value != 'N/A':
                    # Find matching trainer in options
                    trainer_match = next((opt for opt in trainer_options if current_value in opt), "N/A")
                    edit_combo.set(trainer_match)
                else:
                    edit_combo.set("N/A")
                
                def save_edit_combo(event=None):
                    if not edit_combo.winfo_exists():
                        return
                    new_value = edit_combo.get()
                    # Extract trainer name for display
                    if new_value == "N/A":
                        display_name = "N/A"
                        trainer_id_value = None
                    else:
                        # Extract ID from "Name (ID: 123)" format
                        try:
                            trainer_id_value = int(new_value.split("(ID: ")[1].rstrip(")"))
                            display_name = new_value.split(" (ID:")[0]  # Just the name
                        except:
                            display_name = new_value
                            trainer_id_value = None
                    
                    current_values[column_index] = display_name
                    self.tree.item(item, values=tuple(current_values))
                    edit_combo.destroy()
                    self._editing_item = None
                    
                    # Update trainer_id in database
                    try:
                        member_id = int(current_values[1])  # ID is second column (after Select)
                        self.db.update_member(member_id, trainer_id=trainer_id_value)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to update trainer: {str(e)}")
                
                def cancel_edit_combo(event=None):
                    if edit_combo.winfo_exists():
                        edit_combo.destroy()
                    self._editing_item = None
                
                edit_combo.bind("<<ComboboxSelected>>", save_edit_combo)
                edit_combo.bind("<Escape>", cancel_edit_combo)
                self.tree.after_idle(lambda: edit_combo.focus_set())
                edit_combo.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                
            else:
                # Use regular Entry for other editable columns
                edit_entry = Entry(self.tree, 
                                  font=('Arial', 13),
                                  borderwidth=1,
                                  relief="solid")
                edit_entry.insert(0, str(current_value))
                edit_entry.select_range(0, "end")
                edit_entry.focus()
                
                def save_edit(event=None):
                    if not edit_entry.winfo_exists():
                        return
                    new_value = edit_entry.get()
                    current_values[column_index] = new_value
                    self.tree.item(item, values=tuple(current_values))
                    edit_entry.destroy()
                    self._editing_item = None  # Reset editing flag
                    # If join_date changed, recalculate payment date
                    if column_index == 5:  # Join Date column (now index 5 after Select column)
                        self._recalculate_payment_date_for_item(item)
                
                def cancel_edit(event=None):
                    if edit_entry.winfo_exists():
                        edit_entry.destroy()
                    self._editing_item = None  # Reset editing flag
                
                edit_entry.bind("<Return>", save_edit)
                edit_entry.bind("<Escape>", cancel_edit)
                edit_entry.bind("<FocusOut>", save_edit)
                edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
    
    def _recalculate_payment_date_for_item(self, item):
        """Recalculate next payment date for a table item based on current values"""
        values = list(self.tree.item(item, 'values'))
        if len(values) < 12:
            return
        
        try:
            member_id = int(values[1])  # ID is second column (after Select)
            join_date_str = values[5] if values[5] and values[5] != 'N/A' else None
            payment_frequency = values[7] if len(values) > 7 else 'Monthly'  # Frequency is now column 7
            
            if join_date_str:
                try:
                    join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
                    # Recalculate next payment date
                    next_payment = self.db._calculate_next_payment_date(join_date, payment_frequency)
                    # Update the Next Payment column (index 10, after Fee column)
                    values[10] = next_payment.strftime('%Y-%m-%d')
                    self.tree.item(item, values=tuple(values))
                except ValueError:
                    pass  # Invalid date format, skip
        except (ValueError, IndexError):
            pass  # Invalid data, skip
    
    def save_changes(self):
        """Save changes made to the table"""
        # Verify password before saving changes
        if not self.verify_password():
            return
        
        updated_count = 0
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if len(values) >= 12:  # 12 columns: Select, ID, Name, Email, Phone, Join Date, Type, Frequency, Trainer, Fee, Next Payment, Status
                try:
                    member_id = int(values[1])  # ID is second column (after Select)
                    
                    # Get current member data from database for comparison
                    current_member = self.db.get_member(member_id)
                    if not current_member:
                        continue
                    
                    updates = {
                        'name': values[2],
                        'email': values[3] if values[3] else None,
                        'phone': values[4] if values[4] else None,
                        'join_date': values[5] if values[5] and values[5] != 'N/A' else None,
                        'membership_type': values[6],
                        'payment_frequency': values[7] if len(values) > 7 else 'Monthly',  # Frequency column
                    }
                    
                    # Handle trainer (column 8) - trainer_id is updated separately if changed via dropdown
                    # Trainer name is just for display, actual trainer_id update happens in dropdown handler
                    
                    # Parse fee amount (now column 9)
                    fee_str = values[9].replace('₹', '').replace(',', '').strip()
                    try:
                        updates['fee_amount'] = float(fee_str)
                    except:
                        pass
                    
                    # Validate and parse join_date if provided
                    join_date_changed = False
                    new_join_date = None
                    if updates.get('join_date'):
                        try:
                            # Validate date format
                            new_join_date = datetime.strptime(updates['join_date'], '%Y-%m-%d').date()
                            join_date_changed = True
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid date format for member ID {member_id}. Use YYYY-MM-DD format.")
                            continue
                    
                    # Check if membership_type, payment_frequency, or join_date changed
                    membership_type_changed = updates['membership_type'] != current_member.get('membership_type', '')
                    payment_frequency_changed = updates['payment_frequency'] != current_member.get('payment_frequency', 'Monthly')
                    
                    # Handle trainer_id when changing membership type
                    if membership_type_changed:
                        if updates['membership_type'] == "Personal Training":
                            # If changing to Personal Training, check if trainer_id exists
                            if not current_member.get('trainer_id'):
                                # Prompt for trainer selection or set to None
                                trainers = self.db.get_trainers()
                                if trainers:
                                    # Auto-select first trainer (or could prompt user)
                                    updates['trainer_id'] = trainers[0]['id']
                                else:
                                    messagebox.showwarning("Warning", f"Member {current_member['name']} changed to Personal Training but no trainers available. Please assign a trainer manually.")
                        else:
                            # Changing from Personal Training to Standard, remove trainer_id
                            updates['trainer_id'] = None
                    
                    # Recalculate next_payment_date if join_date, payment_frequency, or membership_type changed
                    if join_date_changed and new_join_date:
                        # Use new join date and payment frequency
                        next_payment = self.db._calculate_next_payment_date(new_join_date, updates['payment_frequency'])
                        updates['next_payment_date'] = next_payment
                    elif payment_frequency_changed:
                        # Payment frequency changed, recalculate from current join_date
                        join_date_to_use = new_join_date if new_join_date else datetime.strptime(current_member.get('join_date', date.today().isoformat()), '%Y-%m-%d').date()
                        next_payment = self.db._calculate_next_payment_date(join_date_to_use, updates['payment_frequency'])
                        updates['next_payment_date'] = next_payment
                    
                    self.db.update_member(member_id, **updates)
                    updated_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update member: {str(e)}")
        
        if updated_count > 0:
            messagebox.showinfo("Success", f"Updated {updated_count} member(s)!")
            self.refresh_member_list(self.search_entry.get())
    
    def view_member_details(self):
        """View details of selected member"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a member to view details.")
            return
        
        item = self.tree.item(selection[0])
        member_id = int(item['values'][1])  # ID is second column (after Select)
        
        # Get member details from database
        members = self.db.get_all_members(active_only=False)
        member = next((m for m in members if m['id'] == member_id), None)
        
        if member:
            details = f"""Member Details:

ID: {member['id']}
Name: {member['name']}
Email: {member.get('email', 'N/A')}
Phone: {member.get('phone', 'N/A')}
Join Date: {member.get('join_date', 'N/A')}
Membership Type: {member['membership_type']}
Fee Amount: ₹{member['fee_amount']:.2f}
Payment Frequency: {member['payment_frequency']}
Next Payment: {member.get('next_payment_date', 'N/A')}
Status: {member.get('status', 'active').title()}"""
            
            messagebox.showinfo("Member Details", details)
    
    def on_tree_click(self, event):
        """Handle clicks on the treeview, especially the Select column"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            if item and column == "#1":  # Select column (first data column, index 0)
                values = list(self.tree.item(item, 'values'))
                # Verify we have the right structure
                if len(values) < 2:
                    return
                # Try to get ID from index 1, but handle if it's not there
                try:
                    # ID should be at index 1 (after Select at index 0)
                    member_id = int(values[1])
                except (ValueError, IndexError):
                    # Fallback: try to find ID in the values
                    # If values[1] is a name, then values[0] might be ID
                    try:
                        member_id = int(values[0])
                        # If this works, it means Select column wasn't included
                        # So we need to insert it
                        values.insert(0, "☐")
                    except (ValueError, IndexError):
                        return
                
                # Toggle selection
                if member_id in self.selected_members:
                    self.selected_members.remove(member_id)
                    values[0] = "☐"
                else:
                    self.selected_members.add(member_id)
                    values[0] = "☑"
                
                # Update the row
                self.tree.item(item, values=values)
    
    def select_all_members(self):
        """Select all visible members"""
        for item in self.tree.get_children():
            values = list(self.tree.item(item, 'values'))
            if len(values) < 2:
                continue
            # Check if first value is Select checkbox (☐ or ☑)
            if values[0] in ("☐", "☑"):
                # Select column is present, ID is at index 1
                try:
                    member_id = int(values[1])
                except (ValueError, IndexError):
                    continue
            else:
                # Select column is missing, ID is at index 0
                try:
                    member_id = int(values[0])
                    values.insert(0, "☑")  # Add Select column
                except (ValueError, IndexError):
                    continue
            self.selected_members.add(member_id)
            values[0] = "☑"
            self.tree.item(item, values=values)
    
    def deselect_all_members(self):
        """Deselect all visible members"""
        for item in self.tree.get_children():
            values = list(self.tree.item(item, 'values'))
            if len(values) < 2:
                continue
            # Check if first value is Select checkbox (☐ or ☑)
            if values[0] in ("☐", "☑"):
                # Select column is present, ID is at index 1
                try:
                    member_id = int(values[1])
                except (ValueError, IndexError):
                    continue
            else:
                # Select column is missing, ID is at index 0
                try:
                    member_id = int(values[0])
                    values.insert(0, "☐")  # Add Select column
                except (ValueError, IndexError):
                    continue
            self.selected_members.discard(member_id)
            values[0] = "☐"
            self.tree.item(item, values=values)
    
    def toggle_member_status(self):
        """Toggle member active/inactive status for selected members"""
        if not self.selected_members:
            messagebox.showinfo("Info", "Please select one or more members to toggle status.")
            return
        
        # Get all members from database
        all_members = self.db.get_all_members(active_only=False)
        member_dict = {m['id']: m for m in all_members}
        
        # Process each selected member
        success_count = 0
        failed_count = 0
        activated_count = 0
        deactivated_count = 0
        
        for member_id in list(self.selected_members):
            member = member_dict.get(member_id)
            if not member:
                failed_count += 1
                continue
            
            current_status_db = member.get('status', 'active').lower()
            new_status = 'inactive' if current_status_db == 'active' else 'active'
            
            try:
                self.db.update_member(member_id, status=new_status)
                success_count += 1
                if new_status == 'active':
                    activated_count += 1
                else:
                    deactivated_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to toggle status for member {member_id}: {str(e)}")
        
        # Show result message
        if success_count > 0:
            status_parts = []
            if activated_count > 0:
                status_parts.append(f"{activated_count} activated")
            if deactivated_count > 0:
                status_parts.append(f"{deactivated_count} deactivated")
            
            message = f"Successfully toggled status for {success_count} member(s): {', '.join(status_parts)}"
            if failed_count > 0:
                message += f"\n{failed_count} member(s) failed to update."
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", f"Failed to toggle status for all {failed_count} member(s).")
        
        # Clear all selections after operation
        self.selected_members.clear()
        
        # Refresh the list (this will also update checkboxes to show deselected state)
        self.refresh_member_list(self.search_entry.get())
    
    def remove_member(self):
        """Remove selected member(s) - supports multi-select deletion"""
        # Verify password before removing
        if not self.verify_password():
            return
        
        # Use selected_members if available, otherwise use tree selection
        if self.selected_members:
            member_ids = list(self.selected_members)
        else:
            # Fallback to tree selection (single selection)
            selection = self.tree.selection()
            if not selection:
                messagebox.showinfo("Info", "Please select one or more members using the checkboxes, then click 'Remove Member'.")
                return
            item = self.tree.item(selection[0])
            values = item['values']
            if len(values) < 2:
                messagebox.showinfo("Info", "Please select one or more members using the checkboxes, then click 'Remove Member'.")
                return
            member_ids = [int(values[1])]  # ID is in second column (index 1)
        
        if not member_ids:
            messagebox.showinfo("Info", "Please select one or more members using the checkboxes, then click 'Remove Member'.")
            return
        
        # Get member names for confirmation
        all_members = self.db.get_all_members(active_only=False)
        member_dict = {m['id']: m for m in all_members}
        
        if len(member_ids) == 1:
            member_id = member_ids[0]
            member_name = member_dict.get(member_id, {}).get('name', f'ID {member_id}')
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete member '{member_name}' (ID: {member_id})?\n\nThis action cannot be undone and will free up the ID for reuse."):
                try:
                    self.db.remove_member(member_id)
                    messagebox.showinfo("Success", f"Member '{member_name}' (ID: {member_id}) deleted successfully!\nThe ID {member_id} is now available for reuse.")
                    # Clear all selections after removal
                    self.selected_members.clear()
                    self.refresh_member_list(self.search_entry.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove member: {str(e)}")
        else:
            # Multi-select deletion
            member_names = [member_dict.get(mid, {}).get('name', f'ID {mid}') for mid in member_ids]
            names_list = '\n'.join([f"  - {name} (ID: {mid})" for name, mid in zip(member_names, member_ids)])
            if messagebox.askyesno("Confirm Bulk Deletion", 
                                  f"Are you sure you want to permanently delete {len(member_ids)} selected member(s)?\n\n"
                                  f"Members to be deleted:\n{names_list}\n\n"
                                  f"This action cannot be undone and will free up the IDs for reuse."):
                success_count = 0
                failed_members = []
                for member_id in member_ids:
                    try:
                        self.db.remove_member(member_id)
                        success_count += 1
                    except Exception as e:
                        member_name = member_dict.get(member_id, {}).get('name', f'ID {member_id}')
                        failed_members.append(f"{member_name} (ID: {member_id})")
                        print(f"Failed to remove member {member_id}: {str(e)}")
                
                # Show result message
                if success_count > 0:
                    message = f"Successfully deleted {success_count} out of {len(member_ids)} member(s)!\nThe deleted IDs are now available for reuse."
                    if failed_members:
                        message += f"\n\nFailed to delete:\n" + "\n".join(failed_members)
                    messagebox.showinfo("Success", message)
                else:
                    messagebox.showerror("Error", f"Failed to delete all {len(member_ids)} member(s).")
                
                # Clear all selections after removal
                self.selected_members.clear()
                self.refresh_member_list(self.search_entry.get())
    
    def fix_id_reuse(self):
        """Fix ID reuse issue by resetting SQLite sequence"""
        # Verify password before fixing IDs
        if not self.verify_password():
            return
        
        # Show confirmation dialog
        confirm_msg = (
            "This will reset the database ID sequence to allow reuse of deleted member IDs.\n\n"
            "Use this if you manually deleted members from the database and want new members\n"
            "to reuse those deleted IDs instead of continuing from the highest ID.\n\n"
            "Do you want to continue?"
        )
        
        if not messagebox.askyesno("Fix ID Reuse", confirm_msg):
            return
        
        try:
            import sqlite3
            import os
            
            # Get database path from the database connection
            # The database object stores the path in db_path attribute
            db_path = getattr(self.db, 'db_path', 'gym_management.db')
            
            # If path is relative, try to find the actual database file
            if not os.path.isabs(db_path) and not os.path.exists(db_path):
                # Try common locations
                possible_paths = [
                    "dist/gym_management.db",
                    "gym_management.db",
                    os.path.join(os.path.dirname(__file__), "dist", "gym_management.db"),
                    os.path.join(os.path.dirname(__file__), "gym_management.db"),
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        db_path = path
                        break
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get current max ID from members table
            cursor.execute("SELECT COALESCE(MAX(id), 0) FROM members")
            max_id = cursor.fetchone()[0]
            
            # Get all existing IDs
            cursor.execute("SELECT id FROM members ORDER BY id")
            existing_ids = {row[0] for row in cursor.fetchall()}
            
            # Find next available ID
            next_id = 1
            while next_id in existing_ids:
                next_id += 1
            
            # Check if sqlite_sequence table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
            sequence_exists = cursor.fetchone() is not None
            
            old_seq = None
            if sequence_exists:
                # Check if members table has an entry in sqlite_sequence
                cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'members'")
                seq_row = cursor.fetchone()
                
                if seq_row:
                    old_seq = seq_row[0]
                    # Reset sequence to match max ID
                    cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'members'", (max_id,))
                    conn.commit()
            
            conn.close()
            
            # Show success message with details
            result_msg = (
                f"✓ ID reuse fix completed!\n\n"
                f"Current maximum ID: {max_id}\n"
            )
            
            if old_seq is not None:
                result_msg += f"Sequence reset from {old_seq} to {max_id}\n\n"
            else:
                result_msg += "No sequence adjustment needed\n\n"
            
            result_msg += (
                f"Next available ID: {next_id}\n"
                f"Total existing members: {len(existing_ids)}\n\n"
                f"New members will now reuse deleted IDs starting from {next_id}."
            )
            
            messagebox.showinfo("ID Reuse Fix Complete", result_msg)
            
            # Refresh the member list to show updated data
            self.refresh_member_list(self.search_entry.get())
            
        except Exception as e:
            error_msg = f"Failed to fix ID reuse:\n{str(e)}"
            messagebox.showerror("Error", error_msg)
