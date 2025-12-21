"""
Financial Dashboard Module - CustomTkinter
Password-protected analytics and financial overview for gym owner
"""
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import date, datetime, timedelta
from typing import Dict, List

class OwnerDashboard(ctk.CTkFrame):
    # Password for owner access
    OWNER_PASSWORD = "babyrose.1234"
    
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.is_authenticated = False
        self.setup_ui()
        self.prompt_password()
    
    def prompt_password(self):
        """Prompt for owner password"""
        password = simpledialog.askstring(
            "Financial Dashboard Access",
            "Enter password to access financial dashboard:",
            show='*'
        )
        if password == self.OWNER_PASSWORD:
            self.is_authenticated = True
            self.load_dashboard()
        elif password is None:
            # User cancelled - show message
            self.show_access_denied()
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")
            self.show_access_denied()
    
    def show_access_denied(self):
        """Show access denied message"""
        denied_label = ctk.CTkLabel(
            self,
            text="Access Denied\nPlease enter the correct password to view financial dashboard.",
            font=ctk.CTkFont(size=18),
            text_color="#ef4444"
        )
        denied_label.pack(expand=True)
    
    def setup_ui(self):
        """Create the financial dashboard UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Financial Dashboard",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(anchor="w", pady=(0, 25))
    
    def load_dashboard(self):
        """Load dashboard content after authentication"""
        # Clear any existing content
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") != "Financial Dashboard":
                widget.destroy()
        
        # Create scrollable frame for all content
        scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Financial Overview Section
        self.create_financial_section(scrollable_frame)
        
        # Analytics Section
        self.create_analytics_section(scrollable_frame)
        
        # Recent Payments Section
        self.create_recent_payments_section(scrollable_frame)
    
    def create_financial_section(self, parent):
        """Create financial metrics section"""
        # Section title
        section_title = ctk.CTkLabel(
            parent,
            text="Financial Overview",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0f172a"
        )
        section_title.pack(anchor="w", pady=(0, 15), padx=20)
        
        # Financial cards container
        financial_frame = ctk.CTkFrame(parent, fg_color="transparent")
        financial_frame.pack(fill="x", padx=20, pady=(0, 30))
        
        # Get financial data
        daily_revenue = self.db.get_daily_revenue()
        monthly_revenue = self.db.get_monthly_revenue()
        total_revenue = self.db.get_total_revenue()
        
        # Calculate today's date for display
        today = date.today()
        current_month = today.strftime("%B %Y")
        
        # Financial cards
        financial_cards = [
            ("Daily Revenue", f"₹{daily_revenue:,.2f}", f"Today ({today.strftime('%d %b %Y')})", "#3b82f6"),
            ("Monthly Revenue", f"₹{monthly_revenue:,.2f}", current_month, "#10b981"),
            ("Total Revenue", f"₹{total_revenue:,.2f}", "All Time", "#8b5cf6"),
        ]
        
        for label, value, subtitle, color in financial_cards:
            card = self.create_financial_card(financial_frame, label, value, subtitle, color)
            card.pack(side="left", padx=7, fill="both", expand=True)
    
    def create_financial_card(self, parent, title, value, subtitle, color):
        """Create a financial metric card"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=12,
            height=140
        )
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="#64748b"
        )
        title_label.pack(pady=(20, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        subtitle_label.pack()
        
        return card
    
    def create_analytics_section(self, parent):
        """Create analytics section with various metrics"""
        # Section title
        section_title = ctk.CTkLabel(
            parent,
            text="Analytics & Insights",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0f172a"
        )
        section_title.pack(anchor="w", pady=(0, 15), padx=20)
        
        # Analytics container (two columns)
        analytics_container = ctk.CTkFrame(parent, fg_color="transparent")
        analytics_container.pack(fill="both", expand=True, padx=20, pady=(0, 30))
        analytics_container.grid_columnconfigure(0, weight=1)
        analytics_container.grid_columnconfigure(1, weight=1)
        
        # Left column - Members by Trainer
        trainer_frame = ctk.CTkFrame(
            analytics_container,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=12
        )
        trainer_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        trainer_title = ctk.CTkLabel(
            trainer_frame,
            text="Members per Trainer",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a"
        )
        trainer_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        trainers_data = self.db.get_members_by_trainer()
        if trainers_data:
            for trainer in trainers_data:
                trainer_card = self.create_trainer_card(trainer_frame, trainer)
                trainer_card.pack(fill="x", padx=20, pady=(0, 10))
        else:
            no_trainers = ctk.CTkLabel(
                trainer_frame,
                text="No active trainers found",
                font=ctk.CTkFont(size=14),
                text_color="#64748b"
            )
            no_trainers.pack(pady=20)
        
        # Right column - Membership Type Distribution
        membership_frame = ctk.CTkFrame(
            analytics_container,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=12
        )
        membership_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        
        membership_title = ctk.CTkLabel(
            membership_frame,
            text="Membership Type Distribution",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a"
        )
        membership_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        membership_data = self.db.get_membership_type_distribution()
        if membership_data:
            for mem_type in membership_data:
                type_card = self.create_membership_card(membership_frame, mem_type)
                type_card.pack(fill="x", padx=20, pady=(0, 10))
        else:
            no_members = ctk.CTkLabel(
                membership_frame,
                text="No active members found",
                font=ctk.CTkFont(size=14),
                text_color="#64748b"
            )
            no_members.pack(pady=20)
        
        # Payment Frequency Distribution (full width)
        frequency_frame = ctk.CTkFrame(
            analytics_container,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=12
        )
        frequency_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        frequency_title = ctk.CTkLabel(
            frequency_frame,
            text="Payment Frequency Distribution",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a"
        )
        frequency_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        frequency_data = self.db.get_payment_frequency_distribution()
        if frequency_data:
            frequency_container = ctk.CTkFrame(frequency_frame, fg_color="transparent")
            frequency_container.pack(fill="x", padx=20, pady=(0, 20))
            
            for freq in frequency_data:
                freq_card = self.create_frequency_card(frequency_container, freq)
                freq_card.pack(side="left", padx=10, fill="x", expand=True)
        else:
            no_freq = ctk.CTkLabel(
                frequency_frame,
                text="No payment frequency data available",
                font=ctk.CTkFont(size=14),
                text_color="#64748b"
            )
            no_freq.pack(pady=20)
    
    def create_trainer_card(self, parent, trainer_data: Dict):
        """Create a card showing trainer and member count"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            border_width=1,
            border_color="#cbd5e1",
            corner_radius=8
        )
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=12)
        
        trainer_name_label = ctk.CTkLabel(
            content_frame,
            text=trainer_data['trainer_name'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#0f172a"
        )
        trainer_name_label.pack(side="left")
        
        count_label = ctk.CTkLabel(
            content_frame,
            text=f"{trainer_data['member_count']} members",
            font=ctk.CTkFont(size=14),
            text_color="#3b82f6"
        )
        count_label.pack(side="right")
        
        return card
    
    def create_membership_card(self, parent, membership_data: Dict):
        """Create a card showing membership type and count"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            border_width=1,
            border_color="#cbd5e1",
            corner_radius=8
        )
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=12)
        
        type_label = ctk.CTkLabel(
            content_frame,
            text=membership_data['membership_type'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#0f172a"
        )
        type_label.pack(side="left")
        
        count_label = ctk.CTkLabel(
            content_frame,
            text=f"{membership_data['count']} members",
            font=ctk.CTkFont(size=14),
            text_color="#10b981"
        )
        count_label.pack(side="right")
        
        return card
    
    def create_frequency_card(self, parent, frequency_data: Dict):
        """Create a card showing payment frequency and count"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            border_width=1,
            border_color="#cbd5e1",
            corner_radius=8,
            height=100
        )
        
        freq_label = ctk.CTkLabel(
            card,
            text=frequency_data['payment_frequency'],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f172a"
        )
        freq_label.pack(pady=(15, 5))
        
        count_label = ctk.CTkLabel(
            card,
            text=f"{frequency_data['count']}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#8b5cf6"
        )
        count_label.pack()
        
        return card
    
    def create_recent_payments_section(self, parent):
        """Create recent payments section"""
        # Section title
        section_title = ctk.CTkLabel(
            parent,
            text="Recent Payments",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0f172a"
        )
        section_title.pack(anchor="w", pady=(0, 15), padx=20)
        
        # Recent payments frame
        payments_frame = ctk.CTkFrame(
            parent,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=12
        )
        payments_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Get recent payments
        recent_payments = self.db.get_recent_payments(limit=10)
        
        if recent_payments:
            # Header row
            header_frame = ctk.CTkFrame(payments_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            headers = ["Date", "Member", "Amount", "Notes"]
            for i, header in enumerate(headers):
                header_label = ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#64748b"
                )
                if i == 0:
                    header_label.pack(side="left", padx=(0, 20))
                elif i == 1:
                    header_label.pack(side="left", padx=(0, 20), expand=True, fill="x")
                elif i == 2:
                    header_label.pack(side="left", padx=(0, 20))
                else:
                    header_label.pack(side="left")
            
            # Payment rows
            for payment in recent_payments:
                payment_row = self.create_payment_row(payments_frame, payment)
                payment_row.pack(fill="x", padx=20, pady=(0, 8))
        else:
            no_payments = ctk.CTkLabel(
                payments_frame,
                text="No payments recorded yet",
                font=ctk.CTkFont(size=14),
                text_color="#64748b"
            )
            no_payments.pack(pady=30)
    
    def create_payment_row(self, parent, payment_data: Dict):
        """Create a row showing payment details"""
        row = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=6
        )
        
        content_frame = ctk.CTkFrame(row, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # Date
        payment_date = payment_data['payment_date']
        if isinstance(payment_date, str):
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        date_label = ctk.CTkLabel(
            content_frame,
            text=payment_date.strftime('%d %b %Y'),
            font=ctk.CTkFont(size=13),
            text_color="#0f172a",
            width=100
        )
        date_label.pack(side="left", padx=(0, 20))
        
        # Member name
        member_label = ctk.CTkLabel(
            content_frame,
            text=payment_data.get('member_name', 'N/A'),
            font=ctk.CTkFont(size=13),
            text_color="#0f172a"
        )
        member_label.pack(side="left", padx=(0, 20), expand=True, fill="x")
        
        # Amount
        amount_label = ctk.CTkLabel(
            content_frame,
            text=f"₹{payment_data['amount']:,.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#10b981",
            width=100
        )
        amount_label.pack(side="left", padx=(0, 20))
        
        # Notes
        notes_text = payment_data.get('notes', '') or 'N/A'
        notes_label = ctk.CTkLabel(
            content_frame,
            text=notes_text[:30] + ('...' if len(notes_text) > 30 else ''),
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
            width=150
        )
        notes_label.pack(side="left")
        
        return row

