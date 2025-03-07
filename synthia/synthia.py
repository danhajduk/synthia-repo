import time
import logging
import sqlite3
import os
import json
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

# Database Path (Using Synthia's Own Database)
DB_PATH = "/data/synthia.db"
CONFIG_PATH = "/data/options.json"

def log_directory_structure():
    """Log the directory structure for debugging."""
    logging.info(f"Current working directory: {os.getcwd()}")

    data_dir = "/data"

    logging.info(f"Listing files in {data_dir}:")
    try:
        for item in os.listdir(data_dir):
            full_path = os.path.join(data_dir, item)
            logging.info(f" - {full_path} ({'DIR' if os.path.isdir(full_path) else 'FILE'})")
    except Exception as e:
        logging.error(f"Could not list {data_dir}: {e}")

def connect_db():
    """Ensure database exists and establish connection."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        return conn
    except sqlite3.OperationalError as e:
        logging.error(f"Database connection failed: {e}")
        return None

def create_table():
    """Create table in Synthia's database if it doesn't exist."""
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
    """Save unread email count & sender counts to Synthia's database."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
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
    logging.info("Email data successfully saved to Synthia's database.")

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
    """Fetch unread emails, process senders, & save data to Synthia's database."""
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
        save_email_data(total_unread, sender_counts)  # Save to Synthia's database

    except Exception as e:
        logging.error(f"Error fetching emails: {e}")

if __name__ == "__main__":
    logging.info("Synthia is running...")
    log_directory_structure()  # Log directory structure at startup
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
