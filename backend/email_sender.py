# backend/email_sender.py
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipient_email: str, subject: str, html_body: str):
    """
    Sends an HTML email using Gmail's SMTP server.
    """
    # Using the exact variable names from your .env file
    sender_email = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        logging.error("EMAIL_SENDER or GMAIL_APP_PASSWORD not set in .env file.")
        return

    logging.info(f"Preparing to send email to {recipient_email}...")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Goal-to-Market AI <{sender_email}>"
    msg['To'] = recipient_email

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
            logging.info(f"Successfully sent email to {recipient_email}")
    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP Authentication Error: Check your EMAIL_SENDER and GMAIL_APP_PASSWORD.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
