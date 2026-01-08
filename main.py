"""
Gym Management System - Main Application
Modern UI using CustomTkinter (much simpler than PySide6!)
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import date, datetime
from PIL import Image, ImageTk
from database import Database
from member_management import MemberManagement
from staff_management import StaffManagement
from fee_management import FeeManagement
from backup_manager import BackupManager
from whatsapp_management import WhatsAppManagement
from owner_dashboard import OwnerDashboard
from locker_management import LockerManagement

# Helper function to get resource path (works with PyInstaller)
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class GymManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("LUWANG FITNESS - Management System")
        self.geometry("1400x900")
        
        # Initialize database
        self.db = Database()
        
        # Initialize backup manager and create daily backup (if pandas is available)
        try:
            self.backup_manager = BackupManager()
            backup_path = self.backup_manager.create_daily_backup()
            if backup_path:
                print(f"Daily backup created: {backup_path}")
            # Cleanup old backups (keep last 30 days)
            self.backup_manager.cleanup_old_backups(keep_days=30)
        except ImportError:
            print("Note: pandas not installed. Backup functionality disabled. Install with: pip install pandas openpyxl")
            self.backup_manager = None
        except Exception as e:
            print(f"Backup warning: {e}")
            self.backup_manager = None
        
        # Current active button
        self.current_active = 0
        
        # Create main UI
        self.create_main_ui()
        
        # Load dashboard
        self.show_dashboard()
    
    def create_main_ui(self):
        """Create the main UI structure"""
        # Header
        self.create_header()
        
        # Main container (sidebar + content)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Content wrapper (sidebar + content area)
        content_wrapper = ctk.CTkFrame(main_container, fg_color="transparent")
        content_wrapper.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Sidebar
        self.create_sidebar(content_wrapper)
        
        # Content area
        self.content_frame = ctk.CTkFrame(content_wrapper, fg_color="#ffffff")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Create page frames
        self.dashboard_frame = ctk.CTkFrame(self.content_frame, fg_color="#ffffff")
        self.member_frame = None
        self.staff_frame = None
        self.fee_frame = None
        self.whatsapp_frame = None
        self.locker_frame = None
        self.owner_frame = None
        
        # Copyright footer
        self.create_footer(main_container)
    
    def create_header(self):
        """Create professional header with logo"""
        header = ctk.CTkFrame(self, height=90, fg_color="#0f172a", corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=25, pady=15)
        
        # Logo
        logo_path = resource_path(os.path.join('icon', 'luwang_logo.jpeg'))
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img = img.resize((70, 70), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)
                logo_label = tk.Label(header_content, image=self.logo_image, bg="#0f172a")
                logo_label.pack(side="left", padx=(0, 20))
            except Exception as e:
                print(f"Could not load logo: {e}")
        
        # Title
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="LUWANG FITNESS",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="Management System",
            font=ctk.CTkFont(size=14),
            text_color="#94a3b8"
        )
        subtitle_label.pack(anchor="w")
    
    def create_footer(self, parent):
        """Create copyright footer"""
        footer = ctk.CTkFrame(parent, height=40, fg_color="#f8fafc", corner_radius=0)
        footer.pack(side="bottom", fill="x", padx=0, pady=0)
        footer.pack_propagate(False)
        
        copyright_text = "© 2024 Developed and Maintained by Nishant Gupta (GSTIN: 07BCIPG3976J1Z8)"
        copyright_label = ctk.CTkLabel(
            footer,
            text=copyright_text,
            font=ctk.CTkFont(size=12),
            text_color="#64748b"
        )
        copyright_label.pack(anchor="center", pady=10)
    
    def create_sidebar(self, parent):
        """Create professional sidebar navigation"""
        sidebar = ctk.CTkFrame(parent, width=240, fg_color="#1e293b", corner_radius=0)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Sidebar title
        title_label = ctk.CTkLabel(
            sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#94a3b8"
        )
        title_label.pack(pady=(25, 0), padx=20, anchor="w")
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Members", self.show_members),
            ("Staff", self.show_staff),
            ("Fees & Payments", self.show_fees),
            ("WhatsApp Messages", self.show_whatsapp),
            ("Locker Management", self.show_locker_management),
            ("Financial Dashboard", self.show_owner_dashboard),
        ]
        
        self.nav_buttons = []
        for idx, (text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                height=50,
                font=ctk.CTkFont(size=15),
                fg_color="#0f172a",
                hover_color="#1e293b",
                text_color="#ffffff",
                anchor="w",
                corner_radius=8,
                command=lambda idx=idx, cmd=command: self.navigate_to(cmd, idx)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons.append(btn)
    
    def navigate_to(self, command, index):
        """Navigate to a page and update active button"""
        self.set_active_button(index)
        command()
    
    def set_active_button(self, index):
        """Set the active button styling"""
        self.current_active = index
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(fg_color="#1e293b", font=ctk.CTkFont(size=15, weight="bold"))
            else:
                btn.configure(fg_color="#0f172a", font=ctk.CTkFont(size=15))
    
    def show_dashboard(self):
        """Show dashboard with overview and alerts"""
        self.set_active_button(0)
        self.clear_content()
        
        # Dashboard content
        content = ctk.CTkFrame(self.content_frame, fg_color="#ffffff")
        content.pack(fill="both", expand=True, padx=35, pady=35)
        
        # Title
        title = ctk.CTkLabel(
            content,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(anchor="w", pady=(0, 25))
        
        # Statistics cards
        stats_frame = ctk.CTkFrame(content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))
        
        members = self.db.get_all_members()
        staff = self.db.get_all_staff()
        overdue = self.db.get_overdue_members()
        due_soon = self.db.get_due_soon_members()  # Frequency-aware reminders
        
        stats = [
            ("Total Members", len(members), '#3b82f6'),
            ("Total Staff", len(staff), '#10b981'),
            ("Overdue Payments", len(overdue), '#ef4444'),
            ("Due Soon", len(due_soon), '#f59e0b'),
        ]
        
        for label, value, color in stats:
            card = self.create_stat_card(stats_frame, label, value, color)
            card.pack(side="left", padx=7, fill="both", expand=True)
        
        # Alerts section
        alerts_title = ctk.CTkLabel(
            content,
            text="Payment Alerts",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0f172a"
        )
        alerts_title.pack(anchor="w", pady=(0, 15))
        
        # Overdue alerts
        if overdue:
            overdue_card = self.create_alert_card(
                content,
                f"OVERDUE PAYMENTS ({len(overdue)})",
                overdue,
                '#fef2f2',
                '#dc2626'
            )
            overdue_card.pack(fill="both", expand=True, pady=(0, 10))
        
        # Due soon alerts
        if due_soon:
            due_soon_card = self.create_alert_card(
                content,
                f"PAYMENTS DUE SOON ({len(due_soon)})",
                due_soon,
                '#fffbeb',
                '#d97706'
            )
            due_soon_card.pack(fill="both", expand=True, pady=(0, 10))
        
        if not overdue and not due_soon:
            success_card = ctk.CTkFrame(
                content,
                fg_color="#f0fdf4",
                border_width=1,
                border_color="#bbf7d0",
                corner_radius=8
            )
            success_card.pack(fill="x", pady=(0, 10))
            
            success_label = ctk.CTkLabel(
                success_card,
                text="No payment alerts at this time",
                font=ctk.CTkFont(size=16),
                text_color="#166534"
            )
            success_label.pack(pady=20)
        
        self.dashboard_frame = content
    
    def create_stat_card(self, parent, label, value, color):
        """Create a professional statistics card"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=12,
            height=120
        )
        
        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=(20, 5))
        
        label_label = ctk.CTkLabel(
            card,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color="#64748b"
        )
        label_label.pack()
        
        return card
    
    def create_alert_card(self, parent, title, items, bg_color, title_color):
        """Create an alert card with scrollable content"""
        card = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            border_width=1,
            border_color=title_color,
            corner_radius=8
        )
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=title_color
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Scrollable frame for items
        # Calculate height based on number of items (max 300px, min 150px)
        max_height = min(300, max(150, len(items) * 30 + 20))
        scrollable_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent",
            height=max_height
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        for item in items:
            if isinstance(item, dict):
                if 'next_payment_date' in item:
                    days_overdue = (date.today() - datetime.strptime(item['next_payment_date'], '%Y-%m-%d').date()).days
                    text = f"{item['name']} - ₹{item['fee_amount']:.2f} ({days_overdue} days overdue)"
                else:
                    due_date = datetime.strptime(item['next_payment_date'], '%Y-%m-%d').date()
                    days_until = (due_date - date.today()).days
                    text = f"{item['name']} - ₹{item['fee_amount']:.2f} (Due in {days_until} days)"
                
                item_label = ctk.CTkLabel(
                    scrollable_frame,
                    text=text,
                    font=ctk.CTkFont(size=13),
                    text_color="#1e293b",
                    anchor="w"
                )
                item_label.pack(fill="x", padx=(10, 0), pady=2)
        
        return card
    
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_members(self):
        """Show member management page"""
        self.set_active_button(1)
        self.clear_content()
        member_mgmt = MemberManagement(self.content_frame, self.db)
        member_mgmt.pack(fill="both", expand=True, padx=35, pady=35)
        self.member_frame = member_mgmt
    
    def show_staff(self):
        """Show staff management page"""
        self.set_active_button(2)
        self.clear_content()
        staff_mgmt = StaffManagement(self.content_frame, self.db)
        staff_mgmt.pack(fill="both", expand=True, padx=35, pady=35)
        self.staff_frame = staff_mgmt
    
    def show_fees(self):
        """Show fee management page"""
        self.set_active_button(3)
        self.clear_content()
        fee_mgmt = FeeManagement(self.content_frame, self.db)
        fee_mgmt.pack(fill="both", expand=True, padx=35, pady=35)
        self.fee_frame = fee_mgmt
    
    def show_whatsapp(self):
        """Show WhatsApp management page"""
        self.set_active_button(4)
        self.clear_content()
        whatsapp_mgmt = WhatsAppManagement(self.content_frame, self.db)
        whatsapp_mgmt.pack(fill="both", expand=True, padx=35, pady=35)
        self.whatsapp_frame = whatsapp_mgmt
    
    def show_locker_management(self):
        """Show locker management page"""
        self.set_active_button(5)
        self.clear_content()
        locker_mgmt = LockerManagement(self.content_frame, self.db)
        locker_mgmt.pack(fill="both", expand=True, padx=35, pady=35)
        self.locker_frame = locker_mgmt
    
    def show_owner_dashboard(self):
        """Show financial dashboard page (password protected)"""
        self.set_active_button(6)
        self.clear_content()
        owner_dashboard = OwnerDashboard(self.content_frame, self.db)
        owner_dashboard.pack(fill="both", expand=True, padx=35, pady=35)
        self.owner_frame = owner_dashboard

def main():
    app = GymManagementApp()
    app.mainloop()

if __name__ == "__main__":
    main()
