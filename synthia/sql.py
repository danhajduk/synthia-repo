import sqlite3
import logging
import os
import json

# Database Path
DB_PATH = "/data/synthia.db"

# Table structures
TABLES = {
    "synthia_emails": '''
        CREATE TABLE IF NOT EXISTS synthia_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            email_id TEXT UNIQUE,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            unread_count INTEGER,
            analyzed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    ''',
    "synthia_email_summary": '''
        CREATE TABLE IF NOT EXISTS synthia_email_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT UNIQUE,
            email_count INTEGER
        )
    ''',
    "synthia_safe_senders": '''
        CREATE TABLE IF NOT EXISTS synthia_safe_senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT UNIQUE
        )
    ''',
    "synthia_metadata": '''
        CREATE TABLE IF NOT EXISTS synthia_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    '''
}

EXPECTED_COLUMNS = {
    "synthia_emails": {
        "id": "INTEGER",
        "timestamp": "TEXT",
        "email_id": "TEXT",
        "sender": "TEXT",
        "recipient": "TEXT",
        "subject": "TEXT",
        "unread_count": "INTEGER",
        "analyzed": "BOOLEAN",
        "category": "TEXT"
    },
    "synthia_email_summary": {
        "id": "INTEGER",
        "sender": "TEXT",
        "email_count": "INTEGER"
    },
    "synthia_metadata": {
        "key": "TEXT",
        "value": "TEXT"
    }
}

def connect_db():
    """Ensure database exists, create tables if not, and establish connection."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        # Create tables if they don't exist
        for table_sql in TABLES.values():
            cursor.execute(table_sql)
        conn.commit()
        logging.info(f"✅ Connected to database and ensured tables exist: {DB_PATH}")
        return conn
    except sqlite3.OperationalError as e:
        logging.error(f"❌ Database connection failed: {e}")
        return None

def check_table_structure():
    """Check if the table structure is correct and recreate it if necessary."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return

    cursor = conn.cursor()
    logging.info("Checking table structure...")

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for column in columns:
            name, col_type = column[1], column[2]
            if name not in expected_columns or expected_columns[name] != col_type:
                logging.warning(f"Column {name} in table {table_name} has incorrect type {col_type}. Expected {expected_columns[name]}.")
                break
        else:
            continue
        break
    else:
        logging.info("Table structure is correct.")
        conn.close()
        return

    # If the structure is incorrect, drop and recreate the tables
    logging.warning("Table structure is incorrect. Recreating tables.")
    for table_name in TABLES.keys():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    for table_sql in TABLES.values():
        cursor.execute(table_sql)
    conn.commit()
    conn.close()
    logging.info("Tables recreated.")

def create_table():
    """Create tables in Synthia's database if they don't exist."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    for table_sql in TABLES.values():
        cursor.execute(table_sql)
    conn.commit()
    conn.close()
    logging.info("Tables created or already exist.")
    check_table_structure()

def clear_email_table():
    """Clear the email tables to reset data."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not connect to database to clear emails.")
        return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM synthia_emails")
    cursor.execute("DELETE FROM synthia_email_summary")
    conn.commit()
    conn.close()
    logging.info("Email tables cleared.")
    
def email_exists(email_id):
    """Check if an email with the given ID already exists in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM synthia_emails WHERE email_id = ?", (email_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_email_data(emails):
    """Save email headers and summary to Synthia's database."""
    logging.info("💾 Saving email data to the database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for email_id, email_data in emails.items():
            if not isinstance(email_data, dict):
                logging.error(f"Unexpected data format for email_id {email_id}: {email_data}")
                continue

            sender = email_data.get('sender', 'Unknown Sender')
            recipient = email_data.get('recipient', 'Unknown Recipient')
            subject = email_data.get('subject', 'No Subject')
            unread_count = email_data.get('unread_count', 1)  # Default to 1 if not provided

            if not email_exists(email_id):
                logging.debug(f"🔹 Inserting: EmailID={email_id}, Sender={sender}")
                cursor.execute('''
                    INSERT INTO synthia_emails (timestamp, email_id, sender, recipient, subject, unread_count, analyzed, category)
                    VALUES (datetime('now'), ?, ?, ?, ?, ?, 0, 'unknown')
                ''', (email_id, sender, recipient, subject, unread_count))
                cursor.execute('''
                    INSERT INTO synthia_email_summary (sender, email_count)
                    VALUES (?, 1)
                    ON CONFLICT(sender) DO UPDATE SET email_count = email_count + 1
                ''', (sender,))
            else:
                logging.debug(f"🔹 Skipping already stored email: EmailID={email_id}")

        conn.commit()
        logging.info("✅ Email data successfully saved.")
        cursor.execute("SELECT COUNT(*) FROM synthia_emails")
        count = cursor.fetchone()[0]
        logging.info(f"📊 Total emails in database: {count}")

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

        # Ensure tables exist
        for table_sql in TABLES.values():
            cursor.execute(table_sql)
        conn.commit()
        logging.info("✅ Ensured tables exist.")

        # Fetch email summary data
        cursor.execute("SELECT sender, email_count FROM synthia_email_summary ORDER BY email_count DESC, sender ASC")
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

def recreate_table():
    """Drop and recreate the email tables."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    for table_name in TABLES.keys():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    for table_sql in TABLES.values():
        cursor.execute(table_sql)
    conn.commit()
    conn.close()
    logging.info("Tables recreated.")

def get_metadata(key):
    """Retrieve a metadata value from the database."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM synthia_metadata WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_metadata(key, value):
    """Set a metadata value in the database."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO synthia_metadata (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    ''', (key, value))
    conn.commit()
    conn.close()
    logging.info(f"Metadata {key} set to {value}.")
