import time
import logging
import sqlite3
import json
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from threading import Thread
from web import app  # Import Flask app

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - INFO - %(message)s",
    level=logging.INFO
)

# Log the current working directory (for debugging)
logging.info(f"Current working directory: {os.getcwd()}")

# Paths
CONFIG_PATH = "/data/options.json"
DB_PATH = "/config/home-assistant_v2.db"  # Home Assistant's database path

def connect_db():
    """Ensure database exists and has correct permissions."""
    if not os.path.exists(DB_PATH):
        logging.error(f"Database file {DB_PATH} does not exist!")
        return None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        return conn
    except sqlite3.OperationalError as e:
        logging.error(f"Database connection failed: {e}")
        return None

def create_table():
    """Create table in HA's database if it doesn't exist."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            unread_count INTEGER,
            sender TEXT,
            email_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Table 'synthia_emails' created or already exists.")

def save_email_data(unread_count, sender_counts):
    """Save unread email count & sender counts to HA's database."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    conn = connect_db()
    if conn is None:
        logging.error("Could not connect to database to save data.")
        return
    cursor = conn.cursor()

    for sender, count in sender_counts.items():
        cursor.execute('''
            INSERT INTO synthia_emails (timestamp, unread_count, sender, email_count)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, unread_count, sender, count))

    conn.commit()
    conn.close()
    logging.info("Email data successfully saved to database.")

# Load Configuration from Home Assistant
try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)

        # General Settings
        general_config = config.get("general", {})
        log_interval = general_config.get("log_interval", 10)
        fetch_interval = general_config.get("fetch_interval_minutes", 10) * 60
        days_to_fetch = general_config.get("days_to_fetch", 7)
        custom_message = general_config.get("custom_message", "Synthia is on")

        # Gmail Settings
        gmail_config = config.get("gmail", {})
        enable_gmail = gmail_config.get("enable_gmail", True)
        gmail_client_id = gmail_config.get("client_id", "")
        gmail_client_secret = gmail_config.get("client_secret", "")
        gmail_refresh_token = gmail_config.get("refresh_token", "")
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")

def authenticate_gmail():
    """Authenticate with Gmail API using OAuth credentials."""
    if not gmail_client_id or not gmail_client_secret or not gmail_refresh_token:
        logging.error("Missing Gmail API credentials.")
        return None

    creds = Credentials.from_authorized_user_info({
        "client_id": gmail_client_id,
        "client_secret": gmail_client_secret,
        "refresh_token": gmail_refresh_token
    })

    return build("gmail", "v1", credentials=creds)

def fetch_unread_email_count():
    """Fetch unread emails, process senders, & save data to HA's database."""
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
        sender_counts = {}
        next_page_token = None
        date_since = (datetime.utcnow() - timedelta(days=days_to_fetch)).strftime("%Y/%m/%d")
        query = f"is:unread after:{date_since}"

        while True:
            results = service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                q=query,
                maxResults=500,
                pageToken=next_page_token
            ).execute()

            messages = results.get("messages", [])
            total_unread += len(messages)

            for msg in messages:
                msg_data = service.users().messages().get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From"]).execute()
                headers = msg_data.get("payload", {}).get("headers", [])
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

                # Extract sender name or domain
                sender_name = sender.split("<")[0].strip() if "<" in sender else sender.split("@")[0]
                sender_counts[sender_name] = sender_counts.get(sender_name, 0) + 1

            # Check if there are more pages
            next_page_token = results.get("nextPageToken", None)
            if not next_page_token:
                break  # Exit loop when all emails are counted

        logging.info(f"📩 You have {total_unread} unread emails.")
        save_email_data(total_unread, sender_counts)  # Save to HA's database

    except Exception as e:
        logging.error(f"Error fetching emails: {e}")

if __name__ == "__main__":
    logging.info("Synthia is running...")
    create_table()  # Ensure table exists
    last_fetch_time = 0

    # Start Flask UI in a separate thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False)).start()

    while True:
        current_time = time.time()
        logging.info(custom_message)
        time.sleep(log_interval)

        if enable_gmail and (current_time - last_fetch_time >= fetch_interval):
            fetch_unread_email_count()
            last_fetch_time = current_time
