"""
MindfulChat — Emergency Alert System
SMS via Fast2SMS (Indian service, free tier available)
Email via Gmail SMTP
"""

import datetime
import logging
import smtplib
import json
import os
import requests as http_requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import database as db
from config import HARMFUL_ACTION_KEYWORDS

load_dotenv()

logging.basicConfig(
    filename="emergency_alerts.log",
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("MindfulChat.AlertSystem")

ALERT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ACTIVE_ALERTS.json")


def _get_fast2sms_config():
    api_key = os.getenv("FAST2SMS_API_KEY", "").strip()
    if api_key:
        return {"api_key": api_key}
    return None


def _get_email_config():
    sender = os.getenv("GMAIL_SENDER", "").strip()
    password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
    if sender and password:
        return {"sender": sender, "password": password}
    return None


def detect_harmful_actions(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in HARMFUL_ACTION_KEYWORDS)


def check_and_alert(nlp_analysis: dict, user: dict, message_text: str) -> dict:
    EMERGENCY_TRIGGER = nlp_analysis.get("emergency_flag", False)
    harmful_action = detect_harmful_actions(message_text)

    if not EMERGENCY_TRIGGER and not harmful_action:
        return {"triggered": False, "alert_data": None, "harmful_action": False}

    user_id = user.get("id", 0)
    display_name = user.get("display_name", "Unknown User")
    ec_name = user.get("emergency_contact_name", "")
    ec_phone = user.get("emergency_contact_phone", "")
    ec_email = user.get("emergency_contact_email", "")

    excerpt = message_text[:200] + "..." if len(message_text) > 200 else message_text
    alert_type = "HARMFUL_ACTION" if harmful_action else "CRISIS_EMERGENCY"

    alert_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_id": user_id,
        "user_name": display_name,
        "alert_type": alert_type,
        "distress_level": nlp_analysis["distress_level"],
        "detected_emotions": nlp_analysis.get("detected_emotions", []),
        "keywords_matched": nlp_analysis.get("keywords_matched", []),
        "message_excerpt": excerpt,
        "emergency_contact": {"name": ec_name, "phone": ec_phone, "email": ec_email},
        "notifications": [],
    }

    alert_sent_to = f"{ec_name} ({ec_phone})" if ec_phone else ec_name

    db.log_emergency(user_id, excerpt, nlp_analysis["distress_level"], alert_sent_to)

    logger.critical(
        f"ALERT {alert_type} | User: {display_name} (ID:{user_id}) | "
        f"Level: {nlp_analysis['distress_level']} | Contact: {alert_sent_to}"
    )

    print(f"\n{'='*60}\nEMERGENCY ALERT - {alert_type}\n"
          f"User: {display_name} | Contact: {ec_name} | Phone: {ec_phone}\n{'='*60}\n")

    _write_alert_file(alert_data)

    # SMS via Fast2SMS
    f2s = _get_fast2sms_config()
    if f2s and ec_phone:
        result = _send_sms_fast2sms(f2s, ec_phone, display_name, alert_type)
        alert_data["notifications"].append(result)

    # Email via Gmail
    email_cfg = _get_email_config()
    if email_cfg and ec_email:
        result = _send_email_gmail(email_cfg, ec_email, ec_name, display_name, alert_type, excerpt)
        alert_data["notifications"].append(result)

    return {"triggered": True, "alert_data": alert_data, "harmful_action": harmful_action}


def _send_sms_fast2sms(f2s: dict, to_phone: str, user_name: str, alert_type: str) -> dict:
    """Send SMS using Fast2SMS API — supports Indian mobile numbers (free tier available)."""
    # Fast2SMS needs a 10-digit Indian number (strip +91 or 91 prefix if present)
    number = to_phone.strip().replace(" ", "").replace("-", "")
    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("91") and len(number) == 12:
        number = number[2:]

    if alert_type == "HARMFUL_ACTION":
        message = (
            f"URGENT MindfulChat Alert: {user_name} has expressed deeply concerning behavior "
            f"and may need immediate help. Please contact them or call emergency services now."
        )
    else:
        message = (
            f"URGENT MindfulChat Crisis Alert: {user_name} appears to be in a mental health "
            f"crisis and needs immediate support. Please reach out to them now."
        )

    try:
        resp = http_requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={
                "authorization": f2s["api_key"],
                "Content-Type": "application/json",
            },
            json={
                "route": "q",
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": number,
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("return") is True:
            logger.critical(f"SMS SENT via Fast2SMS to {to_phone}")
            return {"channel": "sms", "status": "sent", "to": to_phone}
        else:
            err = data.get("message", str(data))
            logger.error(f"Fast2SMS FAILED to {to_phone}: {err}")
            return {"channel": "sms", "status": "failed", "error": err}
    except Exception as e:
        logger.error(f"Fast2SMS EXCEPTION: {e}")
        return {"channel": "sms", "status": "error", "error": str(e)}


def _send_email_gmail(cfg: dict, to_email: str, to_name: str,
                      user_name: str, alert_type: str, excerpt: str) -> dict:
    subject = f"URGENT: {user_name} needs immediate help — MindfulChat Alert"

    if alert_type == "HARMFUL_ACTION":
        body_text = (
            f"Dear {to_name},\n\n"
            f"This is an urgent automated alert from MindfulChat.\n\n"
            f"{user_name} has expressed deeply concerning behavior that requires immediate attention.\n\n"
            f"Please contact them right away. If you are unable to reach them, "
            f"please contact local emergency services immediately.\n\n"
            f"Time of alert: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"---\nMindfulChat Emergency Alert System"
        )
    else:
        body_text = (
            f"Dear {to_name},\n\n"
            f"This is an urgent automated alert from MindfulChat.\n\n"
            f"{user_name} appears to be experiencing a severe mental health crisis "
            f"and needs immediate support.\n\n"
            f"Please reach out to them right now. If you cannot reach them, "
            f"please contact emergency services or call iCall: 9152987821.\n\n"
            f"Time of alert: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"---\nMindfulChat Emergency Alert System\n"
            f"If you believe this is a false alert, please verify with {user_name} directly."
        )

    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["sender"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(cfg["sender"], cfg["password"])
            server.send_message(msg)

        logger.critical(f"EMAIL SENT to {to_email}")
        return {"channel": "email", "status": "sent", "to": to_email}
    except smtplib.SMTPAuthenticationError:
        logger.error(f"EMAIL AUTH FAILED — Check GMAIL_APP_PASSWORD in .env")
        return {"channel": "email", "status": "auth_failed",
                "error": "Gmail authentication failed. Check your App Password."}
    except Exception as e:
        logger.error(f"EMAIL EXCEPTION: {e}")
        return {"channel": "email", "status": "error", "error": str(e)}


def _write_alert_file(alert_data: dict):
    try:
        alerts = []
        if os.path.exists(ALERT_FILE):
            with open(ALERT_FILE, "r") as f:
                alerts = json.load(f)
        alerts.append(alert_data)
        with open(ALERT_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
    except Exception as e:
        logger.error(f"Alert file write failed: {e}")


def get_notification_status(alert_data: dict) -> str:
    notifications = alert_data.get("notifications", [])
    if not notifications:
        return "Alert logged (no credentials configured yet)"
    lines = []
    for n in notifications:
        ch = n["channel"].upper()
        if n["status"] == "sent":
            lines.append(f"✅ {ch} sent to {n.get('to', '')}")
        elif n["status"] == "auth_failed":
            lines.append(f"❌ {ch} auth failed — check credentials")
        else:
            lines.append(f"❌ {ch} failed: {n.get('error', 'unknown error')}")
    return " | ".join(lines)


def get_alert_status_message(alert_result: dict) -> str:
    if not alert_result.get("triggered"):
        return ""
    if alert_result.get("harmful_action"):
        return (
            "What you have described is very serious. Please speak to a professional "
            "or contact emergency services immediately. Help is available."
        )
    return (
        "Your safety matters. Please reach out to someone you trust right now "
        "or call iCall at 9152987821. You don't have to go through this alone."
    )


def get_emergency_history(user_id: int) -> list:
    return db.get_emergency_logs(user_id)