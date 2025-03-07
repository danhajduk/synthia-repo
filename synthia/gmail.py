import logging
import os
import pickle
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Paths
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
