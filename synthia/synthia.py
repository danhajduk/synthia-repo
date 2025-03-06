import os
import json
import base64
import requests
import pickle
import time
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configure Logging
LOG_FILE = "/data/synthia.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # <-- Forces logs to console
    ]
)
logger = logging.getLogger(__name__)

logger.info("Synthia is starting...")

# Load Home Assistant Configuration
CONFIG_PATH = "/data/options.json"

try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
        NOTIFY_SERVICE = config.get("notify_service", "notify.default")
        logger.info(f"Using notify service: {NOTIFY_SERVICE}")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    NOTIFY_SERVICE = "notify.default"

# Path to credentials.json and token.pickle
CREDENTIALS_PATH = "/data/credentials.json"
TOKEN_PATH = "/data/token.pickle"

# Gmail API Scope
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """Authenticate with Gmail API and return a service object."""
    logger.info("Authenticating with Gmail API...")
    creds = None

    if os.path.exists(TOKEN_PATH):
        logger.info("Loading existing token...")
        try:
            with open(TOKEN_PATH, "rb") as token:
                creds = pickle.load(token)
        except Exception as e:
            logger.error(f"Error loading token: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired token...")
            creds.refresh(Request())
        else:
            logger.info("Requesting new authentication flow...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Failed to authenticate with Gmail API: {e}")
                return None

        # Save new credentials
        try:
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)
            logger.info("Token saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")

    return build("gmail", "v1", credentials=creds) if creds else None

def fetch_important_emails():
    """Fetch important unread emails from Gmail."""
    logger.debug("Step 1: Starting fetch_important_emails()")

    service = authenticate_gmail()
    if not service:
        logger.error("Step 2: Failed to authenticate Gmail API.")
        return []

    try:
        logger.debug("Step 3: Fetching unread important emails...")
        results = service.users().messages().list(userId="me", labelIds=["IMPORTANT", "INBOX"], q="is:unread").execute()
        messages = results.get("messages", [])

        logger.debug(f"Step 4: Found {len(messages)} unread emails.")

        email_summaries = []
        for msg in messages[:3]:  # Fetch max 3 emails
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            snippet = msg_data.get("snippet", "")
            email_summaries.append(snippet)
            logger.debug(f"Step 5: Email fetched - {snippet}")

        return email_summaries

    except Exception as e:
        logger.error(f"Step 6: Error fetching emails: {e}")
        return []

def send_notification(message):
    """Send a notification to Home Assistant."""
    logger.info(f"Sending notification: {message}")
    url = "http://supervisor/core/api/services/" + NOTIFY_SERVICE
    headers = {
        "Authorization": f"Bearer {os.getenv('SUPERVISOR_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {"message": message}

    try:
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"Notification sent: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

if __name__ == "__main__":
    logger.info("Synthia is fetching emails...")
    emails = fetch_important_emails()
    if emails:
        for email in emails:
            send_notification(f"📩 New Important Email: {email}")
    else:
        logger.info("No new important emails.")
