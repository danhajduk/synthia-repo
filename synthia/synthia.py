import time
import logging
import sqlite3
import os

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - INFO - %(message)s",
    level=logging.INFO
)

# Database Path (Using Synthia's Own Database)
DB_PATH = "/data/synthia.db"

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

if __name__ == "__main__":
    logging.info("Synthia is running...")
    log_directory_structure()  # Log directory structure at startup
    create_table()  # Ensure table exists
