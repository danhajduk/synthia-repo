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
            CREATE TABLE IF NOT EXISTS synthia_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                unread_count INTEGER,
                sender TEXT,
                email_count INTEGER
            )
        """)
        conn.commit()
        logging.info("✅ Ensured 'synthia_emails' table exists.")

        # Fetch all email data
        cursor.execute("SELECT unread_count, sender, email_count FROM synthia_emails ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            logging.info(f"🔎 Retrieved {len(rows)} rows from database.")
            unread_count = rows[0][0]  # Use first row's unread count
            senders = {}

            for row in rows:
                sender = row[1]
                count = row[2]
                senders[sender] = senders.get(sender, 0) + count

            logging.info(f"📩 Data sent to UI: unread_count={unread_count}, senders={json.dumps(senders, indent=2)}")
            return unread_count, senders

        logging.warning("⚠️ No email data found in the database.")
        return 0, {}

    except sqlite3.Error as e:
        logging.error(f"❌ Database error: {e}")
        return 0, {}

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return 0, {}