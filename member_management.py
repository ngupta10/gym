"""
Member Management Module - CustomTkinter
Handles member registration, removal, and viewing
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, Entry, simpledialog
from datetime import date, datetime
import sqlite3

class MemberManagement(ctk.CTkFrame):
    # Password for protected operations
    PROTECTED_PASSWORD = "1234"
    _editing_item = None  # Track currently editing item to prevent multiple password prompts
    
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
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
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="Members List",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1a1a2e"
        )
        list_title.pack(pady=(20, 10))
        
        # Column headers info label
        headers_info = ctk.CTkLabel(
            list_frame,
            text="Column Order: ID | Name | Email | Phone | Join Date | Type | Frequency | Trainer | Fee | Next Payment | Status",
            font=ctk.CTkFont(size=12),
            text_color="#64748b"
        )
        headers_info.pack(pady=(0, 10), padx=20)
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
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
        self.status_filter.pack(side="left", padx=(0, 0))
        
        # Table
        table_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        columns = ('ID', 'Name', 'Email', 'Phone', 'Join Date', 'Type', 'Frequency', 'Trainer', 'Fee', 'Next Payment', 'Status')
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
        
        # Excel-like header styling (blue header like Excel)
        style.configure("Treeview.Heading", 
                       background="#4472C4",  # Excel blue header
                       foreground="white",
                       borderwidth=1,
                       relief="solid",
                       font=('Arial', 14, 'bold'),
                       padding=(8, 8))
        
        # Ensure header cells have borders
        style.map("Treeview.Heading",
                 background=[("active", "#4472C4")],
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
        
        # Ensure headers are visible - explicitly set show parameter
        self.tree.configure(show='headings')
        
        # Make headers more prominent by ensuring they're always visible
        # Force header visibility
        try:
            # This ensures the heading row is always displayed
            self.tree['show'] = 'headings'
        except:
            pass
        
        # Make table editable
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
        
        # Action buttons
        action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        save_btn = ctk.CTkButton(
            action_frame,
            text="Save Changes",
            command=self.save_changes,
            fg_color="#10b981",
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35
        )
        save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        view_btn = ctk.CTkButton(
            action_frame,
            text="View Details",
            command=self.view_member_details,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35
        )
        view_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        toggle_status_btn = ctk.CTkButton(
            action_frame,
            text="Toggle Status",
            command=self.toggle_member_status,
            fg_color="#f59e0b",
            hover_color="#d97706",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35
        )
        toggle_status_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        remove_btn = ctk.CTkButton(
            action_frame,
            text="Remove Member",
            command=self.remove_member,
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35
        )
        remove_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh List",
            command=self.refresh_member_list,
            fg_color="#64748b",
            hover_color="#475569",
            font=ctk.CTkFont(size=13),
            height=35
        )
        refresh_btn.pack(side="left", fill="x", expand=True)
    
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
        # Clear existing items
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
            search_term = search_term.lower()
            members = [m for m in members if search_term in m['name'].lower()]
        
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
            
            self.tree.insert('', 'end', values=(
                member['id'],
                member['name'],
                member.get('email', ''),
                member.get('phone', ''),
                join_date,
                member['membership_type'],
                member.get('payment_frequency', 'Monthly'),
                trainer_name,
                f"₹{member['fee_amount']:.2f}",
                next_payment,
                status
            ), tags=(tag, member['id']))
    
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
            columns = ('ID', 'Name', 'Email', 'Phone', 'Join Date', 'Type', 'Frequency', 'Trainer', 'Fee', 'Next Payment', 'Status')
            
            # Don't allow editing ID column
            if column_index == 0:  # ID column
                return
            
            # Don't allow editing Status column (use Toggle Status button instead)
            if column_index == 10:  # Status column (last column, index 10)
                return
            
            # Don't allow editing Next Payment column (it's calculated)
            if column_index == 9:  # Next Payment column
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
            if column_index == 5:  # Type (Membership Type) column
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
                
            elif column_index == 6:  # Frequency (Payment Frequency) column
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
                
            elif column_index == 7:  # Trainer column
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
                        member_id = int(current_values[0])  # ID is first column
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
                    if column_index == 4:  # Join Date column
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
        if len(values) < 11:
            return
        
        try:
            member_id = int(values[0])  # ID is first column
            join_date_str = values[4] if values[4] and values[4] != 'N/A' else None
            payment_frequency = values[6] if len(values) > 6 else 'Monthly'  # Frequency is now column 6
            
            if join_date_str:
                try:
                    join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
                    # Recalculate next payment date
                    next_payment = self.db._calculate_next_payment_date(join_date, payment_frequency)
                    # Update the Next Payment column (index 9, after Fee column)
                    values[9] = next_payment.strftime('%Y-%m-%d')
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
            if len(values) >= 11:  # 11 columns: ID, Name, Email, Phone, Join Date, Type, Frequency, Trainer, Fee, Next Payment, Status
                try:
                    member_id = int(values[0])  # ID is first column
                    
                    # Get current member data from database for comparison
                    current_member = self.db.get_member(member_id)
                    if not current_member:
                        continue
                    
                    updates = {
                        'name': values[1],
                        'email': values[2] if values[2] else None,
                        'phone': values[3] if values[3] else None,
                        'join_date': values[4] if values[4] and values[4] != 'N/A' else None,
                        'membership_type': values[5],
                        'payment_frequency': values[6] if len(values) > 6 else 'Monthly',  # Frequency column
                    }
                    
                    # Handle trainer (column 7) - trainer_id is updated separately if changed via dropdown
                    # Trainer name is just for display, actual trainer_id update happens in dropdown handler
                    
                    # Parse fee amount (now column 8)
                    fee_str = values[8].replace('₹', '').replace(',', '').strip()
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
        member_id = int(item['values'][0])  # ID is first column
        
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
    
    def toggle_member_status(self):
        """Toggle member active/inactive status"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a member to toggle status.")
            return
        
        item = self.tree.item(selection[0])
        member_id = int(item['values'][0])  # ID is first column
        member_name = item['values'][1]  # Name is second column
        
        # Get current status from database
        members = self.db.get_all_members(active_only=False)
        member = next((m for m in members if m['id'] == member_id), None)
        
        if not member:
            messagebox.showerror("Error", "Member not found!")
            return
        
        current_status_db = member.get('status', 'active').lower()
        new_status = 'inactive' if current_status_db == 'active' else 'active'
        
        try:
            self.db.update_member(member_id, status=new_status)
            status_text = "activated" if new_status == 'active' else "deactivated"
            messagebox.showinfo("Success", f"Member '{member_name}' {status_text} successfully!")
            self.refresh_member_list(self.search_entry.get())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle status: {str(e)}")
    
    def remove_member(self):
        """Remove/deactivate selected member"""
        # Verify password before removing
        if not self.verify_password():
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a member to remove.")
            return
        
        item = self.tree.item(selection[0])
        member_id = int(item['values'][0])  # ID is first column
        member_name = item['values'][1]  # Name is second column
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove '{member_name}'?"):
            try:
                self.db.remove_member(member_id)
                messagebox.showinfo("Success", f"Member '{member_name}' removed successfully!")
                self.refresh_member_list(self.search_entry.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove member: {str(e)}")
