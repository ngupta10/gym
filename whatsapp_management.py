"""
WhatsApp Management Module
Handles sending automated WhatsApp messages for payment reminders
and custom messages to selected members
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, scrolledtext
from datetime import date, datetime, timedelta
import threading
import time

try:
    import pywhatkit as pwk
    import pyautogui
    PYWHAKIT_AVAILABLE = True
except ImportError:
    PYWHAKIT_AVAILABLE = False
    print("Warning: pywhatkit or pyautogui not installed. Browser-based WhatsApp functionality disabled.")
    print("Install with: pip install pywhatkit pyautogui")

try:
    import subprocess
    import platform
    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False



class WhatsAppManagement(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="#ffffff")
        self.db = db
        self.selected_members = {}  # Dictionary to track selected members {member_id: checkbox_var}
        self.setup_ui()
        self.refresh_member_list()
    
    def setup_ui(self):
        """Setup the UI for WhatsApp management"""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="WhatsApp Messaging",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1e293b"
        )
        title_label.pack(pady=(20, 10), padx=35, anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            self,
            text="Send automated payment reminders and custom messages to members",
            font=ctk.CTkFont(size=14),
            text_color="#64748b"
        )
        subtitle_label.pack(pady=(0, 30), padx=35, anchor="w")
        
        # Method selection and warnings
        # method_frame = ctk.CTkFrame(self, fg_color="transparent")
        # method_frame.pack(fill="x", padx=35, pady=(0, 20))
        
        # method_label = ctk.CTkLabel(
        #     method_frame,
        #     text="Using Browser Automation (pywhatkit)",
        #     font=ctk.CTkFont(size=13),
        #     text_color="#64748b"
        # )
        # method_label.pack(side="left", padx=(0, 20))
        
        # Main container with two sections
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=35, pady=(0, 35))
        
        # Left section - Automated Reminders
        left_section = ctk.CTkFrame(
            main_container,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8
        )
        left_section.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right section - Custom Messages
        right_section = ctk.CTkFrame(
            main_container,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=8
        )
        right_section.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Setup left section (Automated Reminders)
        self.setup_automated_section(left_section)
        
        # Setup right section (Custom Messages)
        self.setup_custom_section(right_section)
    
    def setup_automated_section(self, parent):
        """Setup automated payment reminder section"""
        # Configure parent to use grid for better control
        parent.grid_rowconfigure(0, weight=0)  # Title row
        parent.grid_rowconfigure(1, weight=0)  # Description row
        parent.grid_rowconfigure(2, weight=1)  # List row (expandable)
        parent.grid_rowconfigure(3, weight=0)  # Info label row
        parent.grid_rowconfigure(4, weight=0)  # Button row (always visible)
        parent.grid_columnconfigure(0, weight=1)
        
        # Section title
        section_title = ctk.CTkLabel(
            parent,
            text="Automated Payment Reminders",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1e293b"
        )
        section_title.grid(row=0, column=0, sticky="w", pady=(20, 10), padx=20)
        
        # Description
        desc_label = ctk.CTkLabel(
            parent,
            text="Send reminders to members whose fees are due in 1 day",
            font=ctk.CTkFont(size=13),
            text_color="#64748b"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(0, 20), padx=20)
        
        # Members list frame
        list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame for members
        scrollable_frame = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="white",
            border_width=1,
            border_color="#e2e8f0"
        )
        scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        self.automated_list_frame = scrollable_frame
        
        # Info label
        self.automated_info_label = ctk.CTkLabel(
            parent,
            text="No members with fees due in 1 day",
            font=ctk.CTkFont(size=13),
            text_color="#64748b"
        )
        self.automated_info_label.grid(row=3, column=0, sticky="w", pady=(10, 0), padx=20)
        
        # Send button (always visible at bottom)
        send_auto_btn = ctk.CTkButton(
            parent,
            text="Send Reminders to All",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.send_automated_reminders
        )
        send_auto_btn.grid(row=4, column=0, sticky="ew", pady=(20, 20), padx=20)
    
    def setup_custom_section(self, parent):
        """Setup custom message section"""
        # Configure parent to use grid for better control
        parent.grid_rowconfigure(0, weight=0)  # Title row
        parent.grid_rowconfigure(1, weight=0)  # Description row
        parent.grid_rowconfigure(2, weight=0)  # Search row
        parent.grid_rowconfigure(3, weight=0)  # Select buttons row
        parent.grid_rowconfigure(4, weight=1)  # List row (expandable)
        parent.grid_rowconfigure(5, weight=0)  # Message label row
        parent.grid_rowconfigure(6, weight=0)  # Message text row
        parent.grid_rowconfigure(7, weight=0)  # Button row (always visible)
        parent.grid_columnconfigure(0, weight=1)
        
        # Section title
        section_title = ctk.CTkLabel(
            parent,
            text="Custom Messages",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1e293b"
        )
        section_title.grid(row=0, column=0, sticky="w", pady=(20, 10), padx=20)
        
        # Description
        desc_label = ctk.CTkLabel(
            parent,
            text="Select members and send them a custom message",
            font=ctk.CTkFont(size=13),
            text_color="#64748b"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(0, 20), padx=20)
        
        # Search bar
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=ctk.CTkFont(size=13),
            text_color="#1e293b"
        )
        search_label.grid(row=0, column=0, padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by name, phone, or email...",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_member_list())
        
        # Select all/none buttons
        select_frame = ctk.CTkFrame(parent, fg_color="transparent")
        select_frame.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 10))
        
        select_all_btn = ctk.CTkButton(
            select_frame,
            text="Select All",
            font=ctk.CTkFont(size=12),
            height=30,
            fg_color="#64748b",
            hover_color="#475569",
            command=self.select_all_members,
            width=100
        )
        select_all_btn.pack(side="left", padx=(0, 5))
        
        select_none_btn = ctk.CTkButton(
            select_frame,
            text="Select None",
            font=ctk.CTkFont(size=12),
            height=30,
            fg_color="#64748b",
            hover_color="#475569",
            command=self.deselect_all_members,
            width=100
        )
        select_none_btn.pack(side="left")
        
        # Members list frame - scrollable with fixed height
        list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        list_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame for members
        scrollable_frame = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="white",
            border_width=1,
            border_color="#e2e8f0"
        )
        scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        self.custom_list_frame = scrollable_frame
        
        # Message input label
        message_label = ctk.CTkLabel(
            parent,
            text="Custom Message:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1e293b"
        )
        message_label.grid(row=5, column=0, sticky="w", pady=(10, 5), padx=20)
        
        # Message text box
        self.message_text = ctk.CTkTextbox(
            parent,
            height=100,
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color="#e2e8f0"
        )
        self.message_text.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.message_text.insert("1.0", "Hello! This is a message from Luwang Fitness. ")
        
        # Send button - always visible at bottom
        send_custom_btn = ctk.CTkButton(
            parent,
            text="Send to Selected Members",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.send_custom_messages
        )
        send_custom_btn.grid(row=7, column=0, sticky="ew", pady=(0, 20), padx=20)
    
    def get_members_due_in_one_day(self):
        """Get members whose fees are due in exactly 1 day"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        # Get all active members
        all_members = self.db.get_all_members(active_only=True)
        
        # Filter members whose next_payment_date is tomorrow
        due_members = []
        for member in all_members:
            next_payment = member.get('next_payment_date')
            if next_payment:
                if isinstance(next_payment, str):
                    try:
                        next_payment_date = date.fromisoformat(next_payment)
                        if next_payment_date == tomorrow:
                            due_members.append(member)
                    except ValueError:
                        continue
                elif isinstance(next_payment, date):
                    if next_payment == tomorrow:
                        due_members.append(member)
        
        return due_members
    
    def refresh_automated_list(self):
        """Refresh the automated reminders list"""
        # Clear existing widgets
        for widget in self.automated_list_frame.winfo_children():
            widget.destroy()
        
        due_members = self.get_members_due_in_one_day()
        
        if not due_members:
            self.automated_info_label.configure(text="No members with fees due in 1 day")
            return
        
        self.automated_info_label.configure(text=f"Found {len(due_members)} member(s) with fees due tomorrow")
        
        # Display members
        for idx, member in enumerate(due_members):
            member_frame = ctk.CTkFrame(
                self.automated_list_frame,
                fg_color="white" if idx % 2 == 0 else "#f8fafc",
                corner_radius=4
            )
            member_frame.pack(fill="x", padx=5, pady=2)
            
            # Member info
            info_text = f"{member['name']} (ID: {member['id']}) - Phone: {member.get('phone', 'N/A')}"
            info_label = ctk.CTkLabel(
                member_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                text_color="#1e293b",
                anchor="w"
            )
            info_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            
            # Payment info
            payment_text = f"Due: {member.get('next_payment_date', 'N/A')} | Amount: ₹{member.get('fee_amount', 0):.2f}"
            payment_label = ctk.CTkLabel(
                member_frame,
                text=payment_text,
                font=ctk.CTkFont(size=11),
                text_color="#64748b",
                anchor="e"
            )
            payment_label.pack(side="right", padx=10, pady=8)
    
    def refresh_member_list(self):
        """Refresh both member lists"""
        self.refresh_automated_list()
        self.refresh_custom_list()
    
    def refresh_custom_list(self):
        """Refresh the custom message member list"""
        # Clear existing widgets
        for widget in self.custom_list_frame.winfo_children():
            widget.destroy()
        
        # Get search term
        search_term = self.search_entry.get().lower().strip()
        
        # Get all active members
        all_members = self.db.get_all_members(active_only=True)
        
        # Filter by search term
        if search_term:
            filtered_members = []
            for member in all_members:
                name = member.get('name', '').lower()
                phone = member.get('phone', '').lower()
                email = member.get('email', '').lower()
                if (search_term in name or search_term in phone or search_term in email):
                    filtered_members.append(member)
            members = filtered_members
        else:
            members = all_members
        
        if not members:
            no_results_label = ctk.CTkLabel(
                self.custom_list_frame,
                text="No members found",
                font=ctk.CTkFont(size=13),
                text_color="#64748b"
            )
            no_results_label.pack(pady=20)
            return
        
        # Display members with checkboxes
        for idx, member in enumerate(members):
            member_id = member['id']
            
            # Create checkbox variable if not exists
            if member_id not in self.selected_members:
                var = ctk.BooleanVar(value=False)
                self.selected_members[member_id] = {'var': var, 'member': member}
            else:
                var = self.selected_members[member_id]['var']
            
            member_frame = ctk.CTkFrame(
                self.custom_list_frame,
                fg_color="white" if idx % 2 == 0 else "#f8fafc",
                corner_radius=4
            )
            member_frame.pack(fill="x", padx=5, pady=2)
            
            # Checkbox
            checkbox = ctk.CTkCheckBox(
                member_frame,
                text="",
                variable=var,
                width=20
            )
            checkbox.pack(side="left", padx=10, pady=8)
            
            # Member info
            info_text = f"{member['name']} (ID: {member['id']})"
            info_label = ctk.CTkLabel(
                member_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                text_color="#1e293b",
                anchor="w"
            )
            info_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            
            # Phone number
            phone_text = f"Phone: {member.get('phone', 'N/A')}"
            phone_label = ctk.CTkLabel(
                member_frame,
                text=phone_text,
                font=ctk.CTkFont(size=11),
                text_color="#64748b",
                anchor="e"
            )
            phone_label.pack(side="right", padx=10, pady=8)
    
    def select_all_members(self):
        """Select all visible members"""
        for member_id, data in self.selected_members.items():
            data['var'].set(True)
    
    def deselect_all_members(self):
        """Deselect all members"""
        for member_id, data in self.selected_members.items():
            data['var'].set(False)
    
    def focus_browser_window(self):
        """Focus the browser window using OS-specific commands"""
        import platform
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                # Use AppleScript to focus Chrome/Safari/Edge
                scripts = [
                    'tell application "Google Chrome" to activate',
                    'tell application "Safari" to activate',
                    'tell application "Microsoft Edge" to activate',
                    'tell application "Firefox" to activate'
                ]
                for script in scripts:
                    try:
                        subprocess.run(['osascript', '-e', script], 
                                     capture_output=True, timeout=2)
                        time.sleep(0.5)
                        return True
                    except:
                        continue
            elif system == "Windows":
                # Use PowerShell to focus browser
                try:
                    subprocess.run(['powershell', '-Command', 
                                  'Get-Process | Where-Object {$_.MainWindowTitle -like "*WhatsApp*" -or $_.ProcessName -like "*chrome*" -or $_.ProcessName -like "*msedge*"} | ForEach-Object {[Microsoft.VisualBasic.Interaction]::AppActivate($_.Id)}'],
                                 timeout=2)
                    time.sleep(0.5)
                    return True
                except:
                    pass
            # For Linux, try using wmctrl if available
            elif system == "Linux":
                try:
                    subprocess.run(['wmctrl', '-a', 'WhatsApp'], timeout=2)
                    time.sleep(0.5)
                    return True
                except:
                    pass
        except Exception as e:
            print(f"Could not focus browser: {e}")
        
        return False
    
    def send_whatsapp(self, phone_number: str, message: str, wait_time: int = 15, is_first_message: bool = False):
        """
        Send WhatsApp message using browser automation (FREE method)
        Works with dual monitor setups
        Reuses the same browser window for multiple messages
        
        Args:
            phone_number: Phone number with country code (without +)
            message: Message text
            wait_time: Seconds to wait before typing the message (only used for first message)
            is_first_message: True if this is the first message (opens browser), False to reuse existing window
        """
        if not PYWHAKIT_AVAILABLE:
            raise ImportError("pywhatkit or pyautogui is not installed")
        
        # Get the main window to minimize it during sending
        main_window = None
        try:
            # Try to get the root window
            widget = self
            while widget.master:
                widget = widget.master
            main_window = widget
            # Minimize the window to prevent focus stealing
            main_window.iconify()
            time.sleep(0.5)  # Give time for window to minimize
        except:
            pass  # If we can't minimize, continue anyway
        
        try:
            # Clean phone number
            phone_number = phone_number.replace(" ", "").replace("-", "").replace("+", "")
            
            if not phone_number:
                raise ValueError("Phone number is empty")
            
            screen_width, screen_height = pyautogui.size()
            
            # Use WhatsApp Web URL to navigate to contact (more reliable than clicking search)
            from urllib.parse import quote
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}"
            
            if is_first_message:
                # First message: Open WhatsApp Web in browser
                import webbrowser
                webbrowser.open(whatsapp_url)
                # Wait for WhatsApp Web to fully load
                time.sleep(wait_time)
            else:
                # Subsequent messages: Navigate to new contact in same browser window
                # Use keyboard shortcut to focus address bar and navigate
                self.focus_browser_window()
                time.sleep(0.5)
                
                # Focus address bar: Cmd+L (Mac) or Ctrl+L (Windows/Linux)
                if platform.system() == "Darwin":
                    pyautogui.hotkey('command', 'l')
                else:
                    pyautogui.hotkey('ctrl', 'l')
                time.sleep(0.3)
                
                # Type the new URL
                pyautogui.write(whatsapp_url, interval=0.05)
                time.sleep(0.3)
                
                # Press Enter to navigate
                pyautogui.press('enter')
                # Wait longer for page to load and chat to open
                time.sleep(8)
            
            # Try to focus browser window using OS-specific commands
            self.focus_browser_window()
            time.sleep(1)
            
            # Try clicking in multiple locations to find the input field
            # WhatsApp input is usually at bottom center, but on dual monitors it might be on either screen
            click_positions = [
                (screen_width // 2, screen_height - 150),  # Primary monitor center-bottom
                (screen_width // 2, screen_height - 100),  # Primary monitor slightly higher
                (screen_width // 2, screen_height - 200),   # Primary monitor slightly lower
                (screen_width // 2, screen_height - 120),   # Another position
                (screen_width // 2, screen_height - 180),   # Another position
            ]
            
            # If there's a second monitor, try positions there too
            try:
                # Try to detect second monitor (rough estimate)
                second_monitor_x = screen_width + (screen_width // 2)
                click_positions.extend([
                    (second_monitor_x, screen_height - 150),
                    (second_monitor_x, screen_height - 100),
                    (second_monitor_x, screen_height - 120),
                ])
            except:
                pass
            
            # Try multiple times to click on the message input area
            input_clicked = False
            for attempt in range(3):  # Try up to 3 times
                for x, y in click_positions:
                    try:
                        pyautogui.click(x, y)
                        time.sleep(0.5)
                        # Try typing a test character to see if input is focused
                        # If it works, we'll continue, otherwise try next position
                        input_clicked = True
                        break
                    except:
                        continue
                if input_clicked:
                    break
                # If didn't work, wait a bit more and try again
                time.sleep(1)
            
            # Additional wait to ensure input field is ready
            time.sleep(1)
            
            # Try pressing Tab to navigate to input field if clicking didn't work
            if not input_clicked:
                pyautogui.press('tab')
                time.sleep(0.5)
            
            # Clear any existing text in input field (in case there's leftover text)
            pyautogui.hotkey('command', 'a') if platform.system() == "Darwin" else pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # Type the message
            pyautogui.write(message, interval=0.05)  # Type message directly
            
            # Wait a bit for typing to complete
            time.sleep(1.5)
            
            # Before pressing Enter, click again to ensure focus
            pyautogui.click(screen_width // 2, screen_height - 150)
            time.sleep(0.5)
            
            # Press Enter to send the message
            pyautogui.press('enter')
            
            # Wait a bit more to ensure message is sent
            time.sleep(3)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")
        finally:
            # Don't restore window until all messages are done (handled in calling function)
            pass
    
    def send_automated_reminders(self):
        """Send automated reminders to members with fees due in 1 day"""
        if not PYWHAKIT_AVAILABLE:
            messagebox.showerror("Error", "pywhatkit is not installed. Please install it with: pip install pywhatkit")
            return
        
        due_members = self.get_members_due_in_one_day()
        
        if not due_members:
            messagebox.showinfo("Info", "No members with fees due in 1 day.")
            return
        
        # Confirm before sending
        confirm_msg = f"Send payment reminders to {len(due_members)} member(s)?\n\n"
        confirm_msg += "IMPORTANT:\n"
        confirm_msg += "1. Make sure WhatsApp Web is open and you are logged in\n"
        confirm_msg += "2. DO NOT click on this application window while messages are sending\n"
        confirm_msg += "3. Keep the browser window visible and active\n\n"
        confirm_msg += "Click OK to start sending..."
        if not messagebox.askyesno("Confirm", confirm_msg):
            return
        
        # Send messages in a separate thread to avoid blocking UI
        def send_thread():
            success_count = 0
            failed_count = 0
            is_first_message = True
            
            for member in due_members:
                phone = member.get('phone', '').strip()
                if not phone:
                    failed_count += 1
                    continue
                
                # Create reminder message
                member_name = member.get('name', 'Member')
                next_payment = member.get('next_payment_date', 'soon')
                fee_amount = member.get('fee_amount', 0)
                
                message = f"Hello {member_name}! This is a reminder from Luwang Fitness. "
                message += f"Your membership fee of ₹{fee_amount:.2f} is due on {next_payment}. "
                message += "Please make the payment to avoid any inconvenience. Thank you!"
                
                try:
                    # For first message, open WhatsApp Web. For subsequent messages, reuse the same window
                    self.send_whatsapp(phone, message, wait_time=10, is_first_message=is_first_message)
                    is_first_message = False
                    success_count += 1
                    time.sleep(8)  # Wait between messages to avoid rate limiting and allow sending
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to send to {member['name']}: {str(e)}")
            
            # Show results (delayed to avoid focus issues)
            result_msg = f"Reminders sent!\n\nSuccess: {success_count}\nFailed: {failed_count}"
            # Delay the popup to avoid stealing focus during sending
            self.after(5000, lambda: messagebox.showinfo("Complete", result_msg))
            self.after(5000, self.refresh_automated_list)
        
        # Start thread
        thread = threading.Thread(target=send_thread, daemon=True)
        thread.start()
        
        # Removed popup to prevent focus stealing - messages are being sent in background
    
    def send_custom_messages(self):
        """Send custom messages to selected members"""
        if not PYWHAKIT_AVAILABLE:
            messagebox.showerror("Error", "pywhatkit is not installed. Please install it with: pip install pywhatkit")
            return
        
        # Get selected members
        selected = []
        for member_id, data in self.selected_members.items():
            if data['var'].get():
                selected.append(data['member'])
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one member.")
            return
        
        # Get message
        message = self.message_text.get("1.0", "end-1c").strip()
        if not message:
            messagebox.showwarning("No Message", "Please enter a message.")
            return
        
        # Confirm before sending
        confirm_msg = f"Send custom message to {len(selected)} selected member(s)?\n\n"
        confirm_msg += "IMPORTANT:\n"
        confirm_msg += "1. Make sure WhatsApp Web is open and you are logged in\n"
        confirm_msg += "2. DO NOT click on this application window while messages are sending\n"
        confirm_msg += "3. Keep the browser window visible and active\n\n"
        confirm_msg += "Click OK to start sending..."
        if not messagebox.askyesno("Confirm", confirm_msg):
            return
        
        # Send messages in a separate thread
        def send_thread():
            success_count = 0
            failed_count = 0
            main_window = None
            
            try:
                # Get main window to minimize
                widget = self
                while widget.master:
                    widget = widget.master
                main_window = widget
                main_window.iconify()
                time.sleep(0.5)
            except:
                pass
            
            try:
                for idx, member in enumerate(selected):
                    phone = member.get('phone', '').strip()
                    if not phone:
                        failed_count += 1
                        continue
                    
                    try:
                        # First message opens browser, subsequent ones reuse it
                        is_first = (idx == 0)
                        self.send_whatsapp(phone, message, wait_time=10, is_first_message=is_first)
                        success_count += 1
                        time.sleep(5)  # Wait between messages (reduced since we're reusing window)
                    except Exception as e:
                        failed_count += 1
                        print(f"Failed to send to {member['name']}: {str(e)}")
                
                # Show results (delayed to avoid focus issues)
                result_msg = f"Messages sent!\n\nSuccess: {success_count}\nFailed: {failed_count}"
                # Delay the popup to avoid stealing focus during sending
                self.after(5000, lambda: messagebox.showinfo("Complete", result_msg))
            finally:
                # Restore window after all messages are sent
                if main_window:
                    try:
                        main_window.deiconify()
                    except:
                        pass
        
        # Start thread
        thread = threading.Thread(target=send_thread, daemon=True)
        thread.start()
        
        # Removed popup to prevent focus stealing - messages are being sent in background

