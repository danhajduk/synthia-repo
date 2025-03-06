import os
import json
import base64
import requests
import pickle
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load Home Assistant Configuration
CONFIG_PATH = "/data/options.json"
with open(CONFIG_PATH) as f:
    config = json.load(f)

NOTIFY_SERVICE = config["notify_service"]

# Path to credentials.json (update with correct path)
CREDENTIALS_PATH = "/data/credentials.json"
TOKEN_PATH = "/data/token.pickle"

# Gmail API Scope
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """Authenticate with Gmail API and return a service object."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

def fetch_important_emails():
    """Fetch important unread emails from Gmail."""
    service = authenticate_gmail()
    results = service.users().messages().list(userId="me", labelIds=["IMPORTANT", "INBOX"], q="is:unread").execute()
    messages = results.get("messages", [])

    email_summaries = []
    for msg in messages[:3]:  # Fetch max 3 emails
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        snippet = msg_data.get("snippet", "")
        email_summaries.append(snippet)

    return email_summaries

def send_notification(message):
    """Send a notification to Home Assistant."""
    url = "http://supervisor/core/api/services/" + NOTIFY_SERVICE
    headers = {
        "Authorization": f"Bearer {os.getenv('SUPERVISOR_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {"message": message}
    response = requests.post(url, headers=headers, json=data)
    print("Notification sent:", response.status_code)

if __name__ == "__main__":
    print("Synthia is fetching emails...")
    emails = fetch_important_emails()
    if emails:
        for email in emails:
            send_notification(f"📩 New Important Email: {email}")
    else:
        print("No new important emails.")

