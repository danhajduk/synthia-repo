import time
import logging
import json
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - INFO - %(message)s",
    level=logging.INFO
)

# Load Configuration from Home Assistant
CONFIG_PATH = "/data/options.json"

try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
        log_interval = config.get("log_interval", 10)
        fetch_interval = config.get("fetch_interval", 60)
        custom_message = config.get("custom_message", "Synthia is on")
        gmail_client_id = config.get("gmail_client_id", "")
        gmail_client_secret = config.get("gmail_client_secret", "")
        gmail_refresh_token = config.get("gmail_refresh_token", "")
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    log_interval = 10
    fetch_interval = 60
    custom_message = "Synthia is on"
    gmail_client_id = ""
    gmail_client_secret = ""
    gmail_refresh_token = ""

def authenticate_gmail():
    """Authenticate with Gmail API using OAuth credentials."""
    if not gmail_client_id or not gmail_client_secret or not gmail_refresh_token:
        logging.error("Missing Gmail API credentials. Please configure in Home Assistant.")
        return None

    creds = Credentials.from_authorized_user_info({
        "client_id": gmail_client_id,
        "client_secret": gmail_client_secret,
        "refresh_token": gmail_refresh_token
    })

    return build("gmail", "v1", credentials=creds)

def fetch_unread_email_count():
    """Fetch the number of unread emails."""
    logging.info("Checking for unread emails...")
    service = authenticate_gmail()

    if not service:
        logging.error("Failed to authenticate Gmail API.")
        return

    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
        messages = results.get("messages", [])
        unread_count = len(messages)
        logging.info(f"📩 You have {unread_count} unread emails.")
    except Exception as e:
        logging.error(f"Error fetching emails: {e}")

if __name__ == "__main__":
    logging.info("Synthia is running...")
    last_fetch_time = 0

    while True:
        current_time = time.time()

        # Log message at the defined interval
        logging.info(custom_message)
        time.sleep(log_interval)

        # Fetch unread email count at the defined interval
        if current_time - last_fetch_time >= fetch_interval:
            fetch_unread_email_count()
            last_fetch_time = current_time
