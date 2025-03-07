import logging
import datetime
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Gmail API Scope
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def load_gmail_config():
    """Load Gmail API credentials from the configuration file."""
    try:
        with open("/data/options.json", "r") as f:
            config = json.load(f)
        logging.info("✅ Gmail configuration successfully loaded.")
        logging.debug(f"Loaded config: {config}")
        return config["gmail"]
    except Exception as e:
        logging.error(f"❌ Failed to load Gmail configuration: {e}")
        return {}

def authenticate_gmail():
    """Authenticate with Gmail API using credentials from the configuration."""
    config = load_gmail_config()
    if not config:
        logging.error("❌ Gmail configuration is missing.")
        return None

    try:
        logging.info("🔑 Authenticating with Gmail API...")
        creds = Credentials.from_authorized_user_info({
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "refresh_token": config.get("refresh_token"),
        }, SCOPES)

        if creds.expired and creds.refresh_token:
            logging.info("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
            logging.info("✅ Credentials refreshed successfully.")

        service = build("gmail", "v1", credentials=creds)
        logging.info("✅ Gmail service built successfully.")
        logging.debug(f"Service: {service}")
        return service
    except Exception as e:
        logging.error(f"❌ Failed to authenticate with Gmail API: {e}")
        return None

def fetch_unread_emails():
    """Fetch unread emails from Gmail from the last 7 days."""
    logging.info("📥 Fetching unread emails from Gmail...")

    service = authenticate_gmail()
    if not service:
        logging.error("❌ Failed to authenticate with Gmail API.")
        return {}

    try:
        now = datetime.datetime.utcnow()
        past_week = (now - datetime.timedelta(days=7)).strftime('%Y/%m/%d')
        gmail_query = f"is:unread after:{past_week}"
        logging.info(f"📅 Fetching emails from: {past_week}")

        emails = {}
        next_page_token = None
        
        while True:
            results = service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                q=gmail_query,
                maxResults=500,  # Get more emails per request
                pageToken=next_page_token  # Continue fetching if there are more pages
            ).execute()

            messages = results.get("messages", [])
            logging.info(f"📨 {len(messages)} emails fetched (page).")
            logging.debug(f"Messages: {messages}")

            for msg in messages:
                msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
                headers = msg_data.get("payload", {}).get("headers", [])
                logging.debug(f"Message data: {msg_data}")

                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
                email_id = msg["id"]
                emails[email_id] = {
                    "sender": sender,
                    "recipient": next((h["value"] for h in headers if h["name"] == "To"), "Unknown Recipient"),
                    "subject": next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject"),
                    "unread_count": 1
                }

            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break  # No more pages, exit loop

        logging.info(f"📊 Processed {len(emails)} emails.")
        logging.debug(f"Emails: {emails}")
        return emails

    except Exception as e:
        error_message = str(e).lower()
        if "invalid_client" in error_message:
            logging.error("❌ Invalid OAuth client: Check your Client ID and Secret in Google Cloud.")
        elif "quotaExceeded" in error_message:
            logging.error("❌ Gmail API quota exceeded. Try again later.")
        else:
            logging.error(f"❌ Unexpected error fetching emails: {e}")
        return {}
