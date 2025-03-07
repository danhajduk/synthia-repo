import logging
import datetime
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Gmail API Scope
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """Authenticate with Gmail API using credentials from the configuration."""
    try:
        logging.info("🔑 Authenticating with Gmail API...")
        creds = Credentials.from_authorized_user_info({
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "refresh_token": "YOUR_REFRESH_TOKEN",
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

        sender_counts = {}
        next_page_token = None

        while True:
            results = service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                q=gmail_query,
                maxResults=500,  # Get more emails
                pageToken=next_page_token  # Continue fetching if there are more pages
            ).execute()

            messages = results.get("messages", [])
            logging.info(f"📨 {len(messages)} emails fetched (page).")

            for msg in messages:
                msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
                headers = msg_data.get("payload", {}).get("headers", [])

                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

                logging.info(f"📨 Email Fetched: Sender={sender}, Subject={subject}")
                sender_counts[sender] = sender_counts.get(sender, 0) + 1

            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break  # No more pages, exit loop

        logging.info(f"📊 Processed {len(sender_counts)} unique senders.")
        return sender_counts

    except Exception as e:
        logging.error(f"❌ Error fetching emails: {e}")
        return {}
