import sqlite3
import logging
import os
import json

# Database Path
DB_PATH = "/data/synthia.db"

def connect_db():
    """Ensure database exists, create table if not, and establish connection."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        # Create table if it doesn't exist
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
        logging.info(f"✅ Connected to database and ensured table exists: {DB_PATH}")
        return conn
    except sqlite3.OperationalError as e:
        logging.error(f"❌ Database connection failed: {e}")
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

def clear_email_table():
    """Clear the email table to reset data."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not connect to database to clear emails.")
        return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM synthia_emails")
    conn.commit()
    conn.close()
    logging.info("Email table cleared.")

def save_email_data(unread_count, sender_counts):
    """Save unread email count & sender counts to Synthia's database."""
    logging.info("💾 Attempting to save email data to the database...")
    logging.info(f"📩 Unread Emails: {unread_count}")
    logging.info(f"📨 Sender Counts: {json.dumps(sender_counts, indent=2)}")

    conn = connect_db()
    if conn is None:
        logging.error("❌ Could not connect to database to save data.")
        return
    cursor = conn.cursor()

    try:
        for sender, count in sender_counts.items():
            logging.info(f"🔹 Inserting: {sender} - {count} emails")
            cursor.execute('''
                INSERT INTO synthia_emails (timestamp, unread_count, sender, email_count)
                VALUES (datetime('now'), ?, ?, ?)
            ''', (unread_count, sender, count))

        conn.commit()
        logging.info("✅ Email data successfully saved to Synthia's database.")

    except sqlite3.Error as e:
        logging.error(f"❌ Database error while saving email data: {e}")

    except Exception as e:
        logging.error(f"❌ Unexpected error while saving email data: {e}")

    finally:
        conn.close()
        logging.info("🔒 Database connection closed.")
        
def get_email_data():
    """Retrieve unread email count and sender information from the database."""
    logging.info("📥 Fetching email data from the database...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logging.info(f"✅ Connected to database: {DB_PATH}")

        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unread_count INTEGER,
                senders TEXT
            )
        """)
        conn.commit()
        logging.info("✅ Ensured 'email_data' table exists.")

        # Fetch the latest email data
        cursor.execute("SELECT unread_count, senders FROM email_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            unread_count = row[0]
            logging.info(f"📩 Retrieved unread_count: {unread_count}")

            try:
                senders = json.loads(row[1]) if row[1] else {}
                logging.info(f"📨 Retrieved senders: {senders}")
            except json.JSONDecodeError:
                logging.error("❌ Error decoding senders JSON.")
                senders = {}

            return unread_count, senders
        
        logging.warning("⚠️ No email data found in the database.")
        return 0, {}  # Default values if no data is found

    except sqlite3.Error as e:
        logging.error(f"❌ Database error: {e}")
        return 0, {}

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return 0, {}
