"""
Test script for sending WhatsApp messages
This is a standalone test file to experiment with WhatsApp messaging
before integrating into the main application.
"""

import pywhatkit as pwk
from datetime import datetime, timedelta
import time

def send_whatsapp_message(phone_number: str, message: str):
    """
    Send a WhatsApp message to a phone number
    
    Args:
        phone_number: Phone number with country code (e.g., "+1234567890" or "1234567890")
        message: Message text to send
    
    Note:
        - Phone number should include country code without '+' or with '+'
        - This will open WhatsApp Web in your default browser
        - You need to be logged into WhatsApp Web
        - The message will be sent automatically after a few seconds
    """
    try:
        # Remove any spaces or dashes from phone number
        phone_number = phone_number.replace(" ", "").replace("-", "").replace("+", "")
        
        # Ensure country code is included (add + if not present)
        if not phone_number.startswith("+"):
            # You may need to add your country code here
            # For example, for India: phone_number = "+91" + phone_number
            print(f"Warning: Phone number should include country code. Using: {phone_number}")
        
        # Get current time and add 1 minute (pywhatkit needs time to open browser)
        now = datetime.now()
        send_time = now + timedelta(minutes=1)
        hour = send_time.hour
        minute = send_time.minute
        
        print(f"Preparing to send message to {phone_number}")
        print(f"Message: {message}")
        print(f"Scheduled time: {hour}:{minute:02d}")
        print("Opening WhatsApp Web...")
        print("Please make sure you are logged into WhatsApp Web in your browser.")
        print("The message will be sent automatically in about 1 minute...")
        
        # Send message
        # Format: sendwhatmsg(phone_no, message, time_hour, time_min)
        pwk.sendwhatmsg(f"+{phone_number}", message, hour, minute)
        
        print("Message sent successfully!")
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure pywhatkit is installed: pip install pywhatkit")
        print("2. Make sure you're logged into WhatsApp Web")
        print("3. Check that the phone number format is correct (with country code)")
        print("4. Make sure your browser can open automatically")


def send_whatsapp_instant(phone_number: str, message: str, wait_time: int = 15):
    """
    Send WhatsApp message instantly (alternative method)
    
    Args:
        phone_number: Phone number with country code
        message: Message text to send
        wait_time: Seconds to wait before sending (default 15)
    
    Note:
        This method opens WhatsApp Web and sends immediately
    """
    try:
        # Remove any spaces or dashes from phone number
        phone_number = phone_number.replace(" ", "").replace("-", "").replace("+", "")
        
        print(f"Opening WhatsApp Web for {phone_number}...")
        print(f"Message will be sent in {wait_time} seconds...")
        print("Please keep the browser window open and don't close it.")
        
        # Send message instantly
        pwk.sendwhatmsg_instantly(f"+{phone_number}", message, wait_time=wait_time, tab_close=True)
        
        print("Message sent successfully!")
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure pywhatkit is installed: pip install pywhatkit")
        print("2. Make sure you're logged into WhatsApp Web")
        print("3. Check that the phone number format is correct")


if __name__ == "__main__":
    # Test configuration - MODIFY THESE VALUES
    TEST_PHONE_NUMBER = "917005531177"  # Replace with actual phone number (include country code, e.g., "919876543210" for India)
    TEST_MESSAGE = "Hello! This is a test message from the Luwang Fitness. Your membership is due for renewal on 15th December 2025. Please make the payment to avoid any inconvenience. Thank you."
    
    print("=" * 60)
    print("WhatsApp Message Test Script")
    print("=" * 60)
    print()
    
    # Choose method
    print("Choose sending method:")
    print("1. Scheduled (sends in 1 minute)")
    print("2. Instant (sends in 15 seconds)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        send_whatsapp_message(TEST_PHONE_NUMBER, TEST_MESSAGE)
    elif choice == "2":
        send_whatsapp_instant(TEST_PHONE_NUMBER, TEST_MESSAGE)
    else:
        print("Invalid choice. Using scheduled method by default.")
        send_whatsapp_message(TEST_PHONE_NUMBER, TEST_MESSAGE)
    
    print("\nTest completed!")




