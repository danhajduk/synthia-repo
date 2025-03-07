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
                email_id TEXT UNIQUE,
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
            email_id TEXT UNIQUE,
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

def save_email_data(emails):
    """Save email data to Synthia's database."""
    logging.info("💾 Saving email data to the database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for email_id, email_data in emails.items():
            sender = email_data.get('sender', 'Unknown Sender')
            unread_count = email_data.get('unread_count', 1)  # Default to 1 if not provided

            cursor.execute('''
                INSERT INTO synthia_emails (email_id, timestamp, unread_count, sender, email_count)
                VALUES (?, datetime('now'), ?, ?, ?)
                ON CONFLICT(email_id) DO UPDATE SET unread_count = excluded.unread_count
            ''', (email_id, unread_count, sender, unread_count))

        conn.commit()
        logging.info("✅ Email data successfully saved.")

    except sqlite3.Error as e:
        logging.error(f"❌ Database error while saving email data: {e}")

    except Exception as e:
        logging.error(f"❌ Unexpected error while saving email data: {e}")

    finally:
        conn.close()
        logging.info("🔒 Database connection closed.")

def get_email_data():
    """Retrieve email summary information from the database."""
    logging.info("📥 Fetching email data from the database...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logging.info(f"✅ Connected to database: {DB_PATH}")

        # Fetch email summary data
        cursor.execute("SELECT sender, email_count FROM synthia_emails ORDER BY email_count DESC, sender ASC")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            logging.info(f"🔎 Retrieved {len(rows)} rows from database.")
            senders = {row[0]: row[1] for row in rows}
            logging.info(f"📩 Data sent to UI: senders={json.dumps(senders, indent=2)}")
            return senders

        logging.warning("⚠️ No email data found in the database.")
        return {}

    except sqlite3.Error as e:
        logging.error(f"❌ Database error: {e}")
        return {}

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return {}

def update_email_status(email_id, unread_count):
    """Update the unread status of an email in the database."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE synthia_emails
        SET unread_count = ?
        WHERE email_id = ?
    ''', (unread_count, email_id))
    conn.commit()
    conn.close()
    logging.info(f"Email {email_id} status updated to unread_count={unread_count}.")

def delete_read_emails():
    """Delete emails from the database that are no longer unread."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM synthia_emails
        WHERE unread_count = 0
    ''')
    conn.commit()
    conn.close()
    logging.info("Read emails deleted from the database.")

def recreate_table():
    """Drop and recreate the email table."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS synthia_emails")
    conn.commit()
    create_table()
    logging.info("Table 'synthia_emails' recreated.")