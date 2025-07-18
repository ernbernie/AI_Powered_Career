import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from backend.email_sender import send_email

def test_send_email_real():
    # Set up debug logging to see exactly what's happening
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    recipient = "ernbernie143@gmail.com"
    subject = "Test Email from Goal-to-Market App"
    html_body = """
    <html>
      <body>
        <h1>Test Email</h1>
        <p>This is a test email sent from the Goal-to-Market app's pytest suite.</p>
        <p>If you receive this, the email functionality is working correctly!</p>
      </body>
    </html>
    """
    
    logging.info("Starting email test...")
    # Now the function will raise exceptions on any failure
    send_email(recipient, subject, html_body)
    logging.info("Email test completed successfully!") 