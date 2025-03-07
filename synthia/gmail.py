import logging
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Config path in Home Assistant add-on
CONFIG_PATH = "/data/options.json"

# Gmail API Scope
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def load_config():
    """Load configuration from Home Assistant."""
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        return config["gmail"]
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return {}

def authenticate_gmail():
    """Authenticate with Gmail API using credentials from the configuration."""
    config = load_config()
    if not config:
        logging.error("Gmail configuration is missing.")
        return None

    creds = Credentials.from_authorized_user_info({
        "client_id": config.get("client_id"),
        "client_secret": config.get("client_secret"),
        "refresh_token": config.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token"
    })

    return build("gmail", "v1", credentials=creds)

def fetch_unread_emails():
    """Fetch unread emails from Gmail."""
    service = authenticate_gmail()
    if not service:
        return []

    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
        messages = results.get("messages", [])
        email_summaries = []

        for msg in messages[:3]:  # Fetch max 3 emails
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            snippet = msg_data.get("snippet", "")
            email_summaries.append(snippet)

        return email_summaries
    except Exception as e:
        logging.error(f"Failed to fetch emails: {e}")
        return []
