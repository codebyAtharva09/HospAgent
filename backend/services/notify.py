import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio Client (optional)
try:
    from twilio.rest import Client
except ImportError:
    Client = None

async def send_email(to: str, subject: str, body: str) -> None:
    """
    Send email using SMTP.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        logger.warning(f"Email credentials missing. Mock sending email to {to}: {subject}")
        return

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to, msg.as_string())
        server.quit()
        logger.info(f"Email sent to {to}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

async def send_sms(to: str, body: str) -> None:
    """
    Send SMS using Twilio.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM")

    if not all([account_sid, auth_token, from_number]):
        logger.warning(f"Twilio credentials missing. Mock sending SMS to {to}: {body}")
        return

    if not Client:
        logger.warning("Twilio library not installed. Mock sending SMS.")
        return

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=body,
            from_=from_number,
            to=to
        )
        logger.info(f"SMS sent: {message.sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
