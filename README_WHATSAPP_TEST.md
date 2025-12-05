# WhatsApp Message Test Script

This is a standalone test file for experimenting with WhatsApp messaging before integrating it into the main Gym Management System.

## Installation

1. Install the required package:
```bash
pip install pywhatkit
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## How to Use

1. **Edit the test file** (`test_whatsapp.py`):
   - Open the file and modify `TEST_PHONE_NUMBER` with the phone number you want to test
   - Modify `TEST_MESSAGE` with your test message
   - Phone number should include country code (e.g., "919876543210" for India, "1234567890" for US)

2. **Make sure WhatsApp Web is ready**:
   - Open WhatsApp Web in your browser: https://web.whatsapp.com
   - Log in and keep it open
   - Make sure your browser allows automatic opening/closing of tabs

3. **Run the test script**:
```bash
python test_whatsapp.py
```

4. **Choose a method**:
   - **Method 1 (Scheduled)**: Sends the message in 1 minute (gives time to open browser)
   - **Method 2 (Instant)**: Sends the message in 15 seconds (faster)

## Important Notes

- The script will automatically open WhatsApp Web in your default browser
- You must be logged into WhatsApp Web before running the script
- The phone number format should include country code (without + sign in the code, but the library adds it)
- For India: Use format like "919876543210" (91 is country code)
- For US: Use format like "1234567890" (1 is country code)
- Don't close the browser window while the message is being sent
- The script will automatically type and send the message

## Troubleshooting

1. **"ModuleNotFoundError: No module named 'pywhatkit'"**
   - Run: `pip install pywhatkit`

2. **Message not sending**
   - Make sure WhatsApp Web is open and you're logged in
   - Check that the phone number format is correct (with country code)
   - Make sure the browser window stays open

3. **Browser not opening**
   - Check your default browser settings
   - Try manually opening WhatsApp Web first

## Alternative Methods

If `pywhatkit` doesn't work well for your use case, we can explore:
- **Twilio WhatsApp API** (paid, more reliable, requires API setup)
- **WhatsApp Business API** (official, requires business verification)
- **Other Python libraries** for WhatsApp automation

Let me know if you encounter any issues or want to try a different approach!




