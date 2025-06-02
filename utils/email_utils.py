"""
Utility functions for sending emails.
"""

import smtplib
import os
import logging
from dotenv import load_dotenv
from email.message import EmailMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def send_email(recipient_email: str, subject: str, body: str) -> None:
    """
    Sends an email using SMTP.

    The email server details (SMTP server, port, sender email, password)
    are configured via environment variables:
    - SMTP_SERVER: The SMTP server hostname or IP address.
    - SMTP_PORT: The SMTP server port.
    - SMTP_SENDER_EMAIL: The email address of the sender.
    - SMTP_SENDER_PASSWORD: The password for the sender's email account.

    Args:
        recipient_email: The email address of the recipient.
        subject: The subject of the email.
        body: The body of the email.
    """
    try:
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port_str = os.environ.get('SMTP_PORT')
        sender_email = os.environ.get('SMTP_SENDER_EMAIL')
        sender_password = os.environ.get('SMTP_SENDER_PASSWORD')

        if not all([smtp_server, smtp_port_str, sender_email, sender_password]):
            logging.error("SMTP configuration is missing. Please set SMTP_SERVER, SMTP_PORT, SMTP_SENDER_EMAIL, and SMTP_SENDER_PASSWORD environment variables.")
            return

        try:
            smtp_port = int(smtp_port_str)
        except ValueError:
            logging.error(f"Invalid SMTP_PORT: {smtp_port_str}. Port must be an integer.")
            return

        # Create the email message properly
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content(body)


        with smtplib.SMTP(smtp_server, smtp_port, timeout=1000) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
            logging.info(f"Email sent successfully to {recipient_email}")

    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP authentication failed. Please check sender email and password.")
    except smtplib.SMTPConnectError:
        logging.error(f"Failed to connect to SMTP server {smtp_server}:{smtp_port}.")
    except smtplib.SMTPServerDisconnected:
        logging.error("Disconnected from SMTP server. Please try again later.")
    except smtplib.SMTPException as e:
        logging.error(f"An SMTP error occurred: {e}")
    except ConnectionRefusedError:
        logging.error(f"Connection refused by the SMTP server {smtp_server}:{smtp_port}.")
    except TimeoutError:
        logging.error(f"Connection to SMTP server {smtp_server}:{smtp_port} timed out.")
    except OSError as e: # Catching socket-related errors, e.g. [Errno 101] Network is unreachable
        logging.error(f"A network error occurred: {e}")
