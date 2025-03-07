import logging
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

# Config path in Home Assistant add-on
CONFIG_PATH = "/data/options.json"

# Gmail API Scope
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def load_config():
    """Load configuration from Home Assistant."""
    try:
        logging.info(f"📂 Loading configuration from {CONFIG_PATH}")
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        logging.info("✅ Configuration successfully loaded.")
        return config["gmail"]
    except Exception as e:
        logging.error(f"❌ Failed to load configuration: {e}")
        return {}

def authenticate_gmail():
    """Authenticate with Gmail API using credentials from the configuration."""
    config = load_config()
    if not config:
        logging.error("❌ Gmail configuration is missing.")
        return None

    try:
        logging.info("🔑 Authenticating with Gmail API...")
        creds = Credentials.from_authorized_user_info({
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "refresh_token": config.get("refresh_token"),
            "token": config.get("token")
        }, SCOPES)

        if creds.expired and creds.refresh_token:
            logging.info("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
            logging.info("✅ Credentials refreshed successfully.")

        service = build("gmail", "v1", credentials=creds)
        logging.info("✅ Gmail service built successfully.")
        return service
    except Exception as e:
        logging.error(f"❌ Failed to authenticate with Gmail API: {e}")
        return None

def fetch_unread_emails():
    """Fetch unread emails from Gmail."""
    logging.info("📥 Fetching unread emails from Gmail...")

    service = authenticate_gmail()
    if not service:
        logging.error("❌ Failed to authenticate with Gmail API.")
        return {}

    try:
        # Define the time range for the last 7 days
        now = datetime.datetime.utcnow()
        past_week = (now - datetime.timedelta(days=7)).isoformat() + 'Z'  # 'Z' indicates UTC time

        # Fetch unread emails from the last 7 days
        logging.info(f"📅 Fetching emails from: {past_week} to {now.isoformat()}")

        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            q=f"is:unread after:{past_week}"
        ).execute()

        messages = results.get("messages", [])
        logging.info(f"📨 {len(messages)} unread emails fetched.")

        sender_counts = {}
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

            logging.info(f"📨 Email Fetched: Sender={sender}, Subject={subject}")
            sender_counts[sender] = sender_counts.get(sender, 0) + 1

        logging.info(f"📊 Processed {len(sender_counts)} unique senders.")
        return sender_counts

    except Exception as e:
        logging.error(f"❌ Error fetching emails: {e}")
        return {}
