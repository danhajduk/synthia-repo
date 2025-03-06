import time
import logging
import json
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

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
        fetch_interval = config.get("fetch_interval_minutes", 10) * 60  # Convert to seconds
        days_to_fetch = config.get("days_to_fetch", 7)
        enable_gmail = config.get("enable_gmail", True)
        custom_message = config.get("custom_message", "Synthia is on")
        
        # Load Gmail Credentials
        gmail_config = config.get("gmail", {})
        gmail_client_id = gmail_config.get("client_id", "")
        gmail_client_secret = gmail_config.get("client_secret", "")
        gmail_refresh_token = gmail_config.get("refresh_token", "")
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    log_interval = 10
    fetch_interval = 600  # Default 10 minutes
    days_to_fetch = 7
    enable_gmail = True
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
    """Fetch the total number of unread emails within the configured date range."""
    if not enable_gmail:
        logging.info("Gmail fetching is disabled.")
        return

    logging.info("Checking for unread emails...")
    service = authenticate_gmail()

    if not service:
        logging.error("Failed to authenticate Gmail API.")
        return

    try:
        total_unread = 0
        next_page_token = None

        # Define the date range filter
        date_since = (datetime.utcnow() - timedelta(days=days_to_fetch)).strftime("%Y/%m/%d")
        query = f"is:unread after:{date_since}"

        while True:
            results = service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                q=query,
                maxResults=500,  # Fetch in batches of 500
                pageToken=next_page_token
            ).execute()

            messages = results.get("messages", [])
            total_unread += len(messages)

            # Check if there are more pages
            next_page_token = results.get("nextPageToken", None)
            if not next_page_token:
                break  # Exit loop when all emails are counted

        logging.info(f"📩 You have {total_unread} unread emails from the last {days_to_fetch} days.")

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

        # Fetch unread email count at the defined interval (if enabled)
        if enable_gmail and (current_time - last_fetch_time >= fetch_interval):
            fetch_unread_email_count()
            last_fetch_time = current_time
