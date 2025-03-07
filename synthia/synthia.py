import time
import logging
import sqlite3
import os

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - INFO - %(message)s",
    level=logging.INFO
)

# Database Path
DB_PATH = "/config/home-assistant_v2.db"

def log_directory_structure():
    """Log the directory structure for debugging."""
    logging.info(f"Current working directory: {os.getcwd()}")

    config_dir = "/config"
    data_dir = "/data"

    logging.info(f"Listing files in {config_dir}:")
    try:
        for item in os.listdir(config_dir):
            full_path = os.path.join(config_dir, item)
            logging.info(f" - {full_path} ({'DIR' if os.path.isdir(full_path) else 'FILE'})")
    except Exception as e:
        logging.error(f"Could not list {config_dir}: {e}")

    logging.info(f"Listing files in {data_dir}:")
    try:
        for item in os.listdir(data_dir):
            full_path = os.path.join(data_dir, item)
            logging.info(f" - {full_path} ({'DIR' if os.path.isdir(full_path) else 'FILE'})")
    except Exception as e:
        logging.error(f"Could not list {data_dir}: {e}")

def wait_for_db():
    """Wait for Home Assistant's database to be available."""
    retries = 10
    while not os.path.exists(DB_PATH) and retries > 0:
        logging.warning(f"Database file {DB_PATH} not found. Retrying in 10 seconds...")
        time.sleep(10)
        retries -= 1

    if os.path.exists(DB_PATH):
        logging.info(f"Database {DB_PATH} is now available.")
        return True
    else:
        logging.error("Database is still missing after multiple attempts.")
        return False

def connect_db():
    """Ensure database exists and has correct permissions."""
    if not wait_for_db():
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
    logging.info("Email data successfully saved to database.")

if __name__ == "__main__":
    logging.info("Synthia is running...")
    log_directory_structure()  # Log directory structure at startup
    create_table()  # Ensure table exists
