"""
This module provides functionality to interact with the SQLite database used by Synthia.
It includes functions to connect to the database, create tables, save and retrieve email data,
and manage metadata.
"""

import sqlite3
import logging
import os
import json

# Database Path
DB_PATH = "/data/synthia.db"

# Enable logging for debugging with timestamps
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def connect_db():
    """
    Ensure database exists, create tables if not, and establish connection.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synthia_unread_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT UNIQUE,
                timestamp TEXT,
                unread_count INTEGER,
                sender TEXT,
                recipient TEXT,
                subject TEXT,
                analyzed INTEGER DEFAULT 0,
                category TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synthia_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synthia_senders_summary (
                sender TEXT PRIMARY KEY,
                email_count INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synthia_important_senders (
                sender TEXT PRIMARY KEY
            )
        ''')
        conn.commit()
        logging.info(f"✅ Connected to database and ensured tables exist: {DB_PATH}")
        return conn
    except sqlite3.OperationalError as e:
        logging.error(f"❌ Database connection failed: {e}")
        return None

def create_table():
    """
    Create tables in Synthia's database if they don't exist.
    """
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_unread_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT UNIQUE,
            timestamp TEXT,
            unread_count INTEGER,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            analyzed INTEGER DEFAULT 0,
            category TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_senders_summary (
            sender TEXT PRIMARY KEY,
            email_count INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_important_senders (
            sender TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Tables 'synthia_unread_emails', 'synthia_metadata', 'synthia_senders_summary', and 'synthia_important_senders' created or already exist.")

def clear_email_table():
    """
    Clear the email table to reset data.
    """
    conn = connect_db()
    if conn is None:
        logging.error("Could not connect to database to clear emails.")
        return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM synthia_unread_emails")
    conn.commit()
    conn.close()
    logging.info("Email table cleared.")

def save_email_data(emails):
    """
    Save email data to Synthia's database.

    Args:
        emails (dict): A dictionary containing email data to be saved.
    """
    logging.info("💾 Saving email data to the database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for email_id, email_data in emails.items():
            sender = email_data.get('sender', 'Unknown Sender')
            recipient = email_data.get('recipient', 'Unknown Recipient')
            subject = email_data.get('subject', 'No Subject')
            unread_count = email_data.get('unread_count', 1)  # Default to 1 if not provided

            logging.debug(f"Inserting email: {email_id}, {sender}, {recipient}, {subject}, {unread_count}")

            cursor.execute('''
                INSERT INTO synthia_unread_emails (email_id, timestamp, unread_count, sender, recipient, subject, analyzed, category)
                VALUES (?, datetime('now'), ?, ?, ?, ?, 0, NULL)
                ON CONFLICT(email_id) DO UPDATE SET 
                    unread_count = excluded.unread_count,
                    sender = excluded.sender,
                    recipient = excluded.recipient,
                    subject = excluded.subject,
                    analyzed = excluded.analyzed,
                    category = excluded.category
            ''', (email_id, unread_count, sender, recipient, subject))

            cursor.execute('''
                INSERT INTO synthia_senders_summary (sender, email_count)
                VALUES (?, 1)
                ON CONFLICT(sender) DO UPDATE SET 
                    email_count = email_count + 1
            ''', (sender,))

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
    """
    Retrieve email summary information from the database.

    Returns:
        dict: A dictionary containing email summary information.
    """
    logging.info("📥 Fetching email data from the database...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logging.info(f"✅ Connected to database: {DB_PATH}")

        # Fetch email summary data
        cursor.execute("SELECT sender, email_count FROM synthia_senders_summary ORDER BY email_count DESC, sender ASC")
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
    """
    Update the unread status of an email in the database.

    Args:
        email_id (str): The ID of the email to update.
        unread_count (int): The new unread count for the email.
    """
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE synthia_unread_emails
        SET unread_count = ?
        WHERE email_id = ?
    ''', (unread_count, email_id))
    conn.commit()
    conn.close()
    logging.info(f"Email {email_id} status updated to unread_count={unread_count}.")

def delete_read_emails():
    """
    Delete emails from the database that are no longer unread.
    """
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM synthia_unread_emails
        WHERE unread_count = 0
    ''')
    conn.commit()
    conn.close()
    logging.info("Read emails deleted from the database.")

def recreate_table():
    """
    Drop and recreate the email table.
    """
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS synthia_unread_emails")
    cursor.execute("DROP TABLE IF EXISTS synthia_senders_summary")
    cursor.execute("DROP TABLE IF EXISTS synthia_important_senders")
    conn.commit()
    create_table()
    logging.info("Tables 'synthia_unread_emails', 'synthia_senders_summary', and 'synthia_important_senders' recreated.")

def get_metadata(key):
    """
    Retrieve metadata value from the database.

    Args:
        key (str): The key of the metadata to retrieve.

    Returns:
        str: The value of the metadata, or None if not found.
    """
    logging.info(f"📥 Fetching metadata for key: {key}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM synthia_metadata WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()

        if result:
            logging.info(f"🔎 Retrieved metadata for key: {key}")
            return result[0]

        logging.warning(f"⚠️ No metadata found for key: {key}")
        return None

    except sqlite3.Error as e:
        logging.error(f"❌ Database error: {e}")
        return None

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return None

def set_metadata(key, value):
    """
    Set metadata value in the database.

    Args:
        key (str): The key of the metadata to set.
        value (str): The value of the metadata to set.
    """
    logging.info(f"💾 Setting metadata for key: {key} to value: {value}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO synthia_metadata (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        ''', (key, value))
        conn.commit()
        conn.close()
        logging.info(f"✅ Metadata for key: {key} set to value: {value}")

    except sqlite3.Error as e:
        logging.error(f"❌ Database error: {e}")

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")

    finally:
        conn.close()
        logging.info("🔒 Database connection closed.")

def add_important_sender(sender):
    """
    Add a sender to the important senders list.

    Args:
        sender (str): The email address of the sender to add.
    """
    logging.info(f"➕ Adding important sender: {sender}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO synthia_important_senders (sender)
            VALUES (?)
            ON CONFLICT(sender) DO NOTHING
        ''', (sender,))
        conn.commit()
        conn.close()
        logging.info(f"✅ Important sender added: {sender}")

    except sqlite3.Error as e:
        logging.error(f"❌ Database error while adding important sender: {e}")

    except Exception as e:
        logging.error(f"❌ Unexpected error while adding important sender: {e}")

    finally:
        conn.close()
        logging.info("🔒 Database connection closed.")

def remove_important_sender(sender):
    """
    Remove a sender from the important senders list.

    Args:
        sender (str): The email address of the sender to remove.
    """
    logging.info(f"➖ Removing important sender: {sender}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM synthia_important_senders
            WHERE sender = ?
        ''', (sender,))
        conn.commit()
        conn.close()
        logging.info(f"✅ Important sender removed: {sender}")

    except sqlite3.Error as e:
        logging.error(f"❌ Database error while removing important sender: {e}")

    except Exception as e:
        logging.error(f"❌ Unexpected error while removing important sender: {e}")

    finally:
        conn.close()
        logging.info("🔒 Database connection closed.")

def get_important_senders():
    """
    Retrieve the list of important senders from the database.

    Returns:
        list: A list of important senders.
    """
    logging.info("📥 Fetching important senders from the database...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT sender FROM synthia_important_senders")
        rows = cursor.fetchall()
        conn.close()

        important_senders = [row[0] for row in rows]
        logging.info(f"🔎 Retrieved {len(important_senders)} important senders from database.")
        return important_senders

    except sqlite3.Error as e:
        logging.error(f"❌ Database error: {e}")
        return []

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return []