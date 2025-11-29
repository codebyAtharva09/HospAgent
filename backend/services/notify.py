import os
import json
import logging
import time
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# Configure logging
logger = logging.getLogger("hospagent.notify")

# Environment Variables
EMAIL_PROVIDER_HOST = os.getenv("EMAIL_PROVIDER_HOST")
EMAIL_PROVIDER_PORT = os.getenv("EMAIL_PROVIDER_PORT")
EMAIL_PROVIDER_USER = os.getenv("EMAIL_PROVIDER_USER")
EMAIL_PROVIDER_PASSWORD = os.getenv("EMAIL_PROVIDER_PASSWORD")

SMS_PROVIDER_API_KEY = os.getenv("SMS_PROVIDER_API_KEY")
SMS_PROVIDER_SENDER_ID = os.getenv("SMS_PROVIDER_SENDER_ID")

CONFIG_PATH = os.path.join("data", "notification_config.json")

# --- Models ---

class NotificationConfig(BaseModel):
    critical_supply_emails: List[EmailStr] = []
    critical_supply_sms: List[str] = []
    high_risk_emails: List[EmailStr] = []
    high_risk_sms: List[str] = []
    festival_surge_emails: List[EmailStr] = []
    festival_surge_sms: List[str] = []

# --- Config Management ---

def load_notification_config() -> NotificationConfig:
    if not os.path.exists(CONFIG_PATH):
        return NotificationConfig()
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        return NotificationConfig(**data)
    except Exception:
        return NotificationConfig()

def save_notification_config(config: NotificationConfig):
    # Ensure directory exists
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config.dict(), f, indent=2)

# --- Alert Debouncing ---

_alert_history = {}

def should_send_alert(category: str, key: str, cooldown_mins: int = 60) -> bool:
    """
    Returns True if an alert should be sent (cooldown expired or never sent).
    """
    now = time.time()
    alert_id = f"{category}:{key}"
    last_sent = _alert_history.get(alert_id, 0)
    
    if now - last_sent > (cooldown_mins * 60):
        _alert_history[alert_id] = now
        return True
    return False

# --- Sending Logic ---

async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    category: str = "generic",
) -> None:
    """
    Sends an email to the specified recipients.
    If provider credentials are missing, logs the email instead.
    """
    if not recipients:
        return

    if not EMAIL_PROVIDER_HOST or not EMAIL_PROVIDER_USER:
        logger.warning(f"[MOCK EMAIL] To: {recipients} | Subject: {subject} | Body: {body[:50]}...")
        return

    try:
        # Placeholder for actual SMTP/Provider logic
        logger.info(f"Sending email to {recipients} via {EMAIL_PROVIDER_HOST}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

async def send_sms(
    phone_numbers: List[str],
    message: str,
    category: str = "generic",
) -> None:
    """
    Sends an SMS to the specified phone numbers.
    If provider credentials are missing, logs the SMS instead.
    """
    if not phone_numbers:
        return

    if not SMS_PROVIDER_API_KEY:
        logger.warning(f"[MOCK SMS] To: {phone_numbers} | Message: {message}")
        return

    try:
        # Placeholder for actual SMS Provider logic
        logger.info(f"Sending SMS to {phone_numbers}")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
