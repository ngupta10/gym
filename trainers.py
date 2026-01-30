"""
Trainers Module - CustomTkinter
View all members assigned to each trainer
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date, datetime
from typing import List, Dict, Optional

class Trainers(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.current_trainer_id = None
        self.setup_ui()
        self.load_trainers()
    
    def setup_ui(self):
        """Create the trainers UI"""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Trainers & Students",
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
        
        # Trainer selection section
        self.create_trainer_selection()
        
        # Summary card
        self.create_summary_card()
        
        # Members table
        self.create_table()
    
    def create_trainer_selection(self):
        """Create trainer selection dropdown"""
        selection_frame = ctk.CTkFrame(self, fg_color="#f8fafc", corner_radius=8, border_width=1, border_color="#e2e8f0")
        selection_frame.pack(fill="x", pady=(0, 20), padx=0)
        
        inner_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=15)
        
        label = ctk.CTkLabel(
            inner_frame,
            text="Select Trainer:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1a1a2e"
        )
        label.pack(side="left", padx=(0, 15))
        
        self.trainer_combo = ctk.CTkComboBox(
            inner_frame,
            values=["Select a trainer..."],
            command=self.on_trainer_selected,
            width=400,
            height=35,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=14)
        )
        self.trainer_combo.pack(side="left")
        self.trainer_combo.set("Select a trainer...")
    
    def create_summary_card(self):
        """Create summary card showing member count"""
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", pady=(0, 20))
        
        # Will be populated when trainer is selected
        self.summary_label = ctk.CTkLabel(
            self.summary_frame,
            text="Select a trainer to view their students",
            font=ctk.CTkFont(size=16),
            text_color="#64748b"
        )
        self.summary_label.pack()
    
    def create_table(self):
        """Create scrollable table for members"""
        # Container for table and scrollbars
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color="transparent",
            scrollbar_button_color="#cbd5e1",
            scrollbar_button_hover_color="#94a3b8"
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Create table using ttk.Treeview
        table_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create Treeview with horizontal scrollbar
        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = (
            "ID", "Name", "Email", "Phone", "Join Date", "Membership Type",
            "Fee Amount", "Payment Frequency", "Last Payment", "Next Payment", "Status"
        )
        
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=20,
            xscrollcommand=h_scrollbar.set
        )
        h_scrollbar.config(command=self.tree.xview)
        
        # Configure column headings and widths
        column_widths = {
            "ID": 50,
            "Name": 150,
            "Email": 180,
            "Phone": 120,
            "Join Date": 100,
            "Membership Type": 140,
            "Fee Amount": 100,
            "Payment Frequency": 130,
            "Last Payment": 100,
            "Next Payment": 100,
            "Status": 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#ffffff",
                       foreground="#1a1a2e",
                       fieldbackground="#ffffff",
                       rowheight=30,
                       font=("Arial", 11))
        style.configure("Treeview.Heading",
                       background="#f1f5f9",
                       foreground="#0f172a",
                       font=("Arial", 11, "bold"),
                       relief="flat")
        style.map("Treeview",
                 background=[("selected", "#3b82f6")],
                 foreground=[("selected", "#ffffff")])
        
        # Pack treeview
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=v_scrollbar.set)
        
        # Initially empty
        self.refresh_table()
    
    def load_trainers(self):
        """Load all trainers into the dropdown"""
        trainers = self.db.get_trainers(active_only=True)
        
        if not trainers:
            self.trainer_combo.configure(values=["No trainers available"])
            messagebox.showinfo("No Trainers", "No active trainers found in the system.")
            return
        
        # Format: "Name (ID: 123)"
        trainer_values = ["Select a trainer..."] + [
            f"{trainer['name']} (ID: {trainer['id']})" for trainer in trainers
        ]
        
        self.trainer_combo.configure(values=trainer_values)
        self.trainer_combo.set("Select a trainer...")
    
    def on_trainer_selected(self, selection):
        """Handle trainer selection"""
        if not selection or selection == "Select a trainer..." or selection == "No trainers available":
            self.current_trainer_id = None
            self.refresh_table()
            self.update_summary()
            return
        
        try:
            # Extract trainer ID from selection (format: "Name (ID: 123)")
            trainer_id = int(selection.split("ID: ")[1].rstrip(")"))
            self.current_trainer_id = trainer_id
            self.refresh_table()
            self.update_summary()
        except (IndexError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to parse trainer selection: {str(e)}")
    
    def update_summary(self):
        """Update summary card with member count"""
        if not self.current_trainer_id:
            self.summary_label.configure(
                text="Select a trainer to view their students",
                text_color="#64748b"
            )
            return
        
        members = self.db.get_members_for_trainer(self.current_trainer_id, active_only=True)
        count = len(members)
        
        # Get trainer name
        trainer = self.db.get_staff(self.current_trainer_id)
        trainer_name = trainer['name'] if trainer else "Unknown"
        
        self.summary_label.configure(
            text=f"📊 {trainer_name} is training {count} active student(s)",
            text_color="#0f172a",
            font=ctk.CTkFont(size=16, weight="bold")
        )
    
    def refresh_table(self):
        """Refresh the members table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.current_trainer_id:
            return
        
        # Get members for selected trainer
        members = self.db.get_members_for_trainer(self.current_trainer_id, active_only=True)
        
        if not members:
            return
        
        # Populate table
        for member in members:
            values = (
                member.get('id', ''),
                member.get('name', ''),
                member.get('email', '') or 'N/A',
                member.get('phone', '') or 'N/A',
                member.get('join_date', ''),
                member.get('membership_type', ''),
                f"₹{member.get('fee_amount', 0):,.2f}",
                member.get('payment_frequency', ''),
                member.get('last_payment_date', '') or 'N/A',
                member.get('next_payment_date', '') or 'N/A',
                member.get('status', 'active').title()
            )
            self.tree.insert("", "end", values=values)
    
    def refresh_data(self):
        """Refresh all data"""
        self.load_trainers()
        if self.current_trainer_id:
            self.refresh_table()
            self.update_summary()
