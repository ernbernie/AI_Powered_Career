# backend/email_sender.py
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipient_email: str, subject: str, html_body: str):
    """
    Sends an HTML email using Gmail's SMTP server.
    Raises exceptions on any failure for better debugging.
    """
    logging.info("=== EMAIL SENDER DEBUG START ===")
    
    # Check environment variables
    sender_email = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    
    logging.info(f"EMAIL_SENDER from env: {'SET' if sender_email else 'NOT SET'}")
    logging.info(f"GMAIL_APP_PASSWORD from env: {'SET' if app_password else 'NOT SET'}")
    
    if not sender_email:
        error_msg = "EMAIL_SENDER not set in .env file."
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    if not app_password:
        error_msg = "GMAIL_APP_PASSWORD not set in .env file."
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    logging.info(f"Preparing to send email to {recipient_email} from {sender_email}...")
    logging.info(f"Subject: {subject}")
    logging.info(f"HTML body length: {len(html_body)} characters")

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Goal-to-Market AI <{sender_email}>"
    msg['To'] = recipient_email
    msg.attach(MIMEText(html_body, 'html'))
    
    logging.info("Message created successfully")

    try:
        logging.info("Attempting to connect to smtp.gmail.com:465...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            logging.info("SMTP connection established")
            
            logging.info("Attempting to login...")
            server.login(sender_email, app_password)
            logging.info("Login successful")
            
            logging.info("Attempting to send message...")
            server.send_message(msg)
            logging.info(f"Successfully sent email to {recipient_email}")
            
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication Error: {e}. Check your EMAIL_SENDER and GMAIL_APP_PASSWORD."
        logging.error(error_msg)
        raise Exception(error_msg)
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {e}"
        logging.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error sending email: {e}"
        logging.error(error_msg)
        raise Exception(error_msg)
    
    logging.info("=== EMAIL SENDER DEBUG END ===")
