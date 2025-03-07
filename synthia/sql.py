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
                email_count INTEGER,
                email_id TEXT UNIQUE,
                analyzed BOOLEAN DEFAULT 0,
                category TEXT DEFAULT 'unknown'
            )
        ''')
        conn.commit()
        logging.info(f"✅ Connected to database and ensured table exists: {DB_PATH}")
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
    cursor.execute("PRAGMA table_info(synthia_emails)")
    columns = cursor.fetchall()
    expected_columns = {
        "id": "INTEGER",
        "timestamp": "TEXT",
        "unread_count": "INTEGER",
        "sender": "TEXT",
        "email_count": "INTEGER",
        "email_id": "TEXT",
        "analyzed": "BOOLEAN",
        "category": "TEXT"
    }

    # Check if all expected columns are present and have the correct type
    for column in columns:
        name, col_type = column[1], column[2]
        if name not in expected_columns or expected_columns[name] != col_type:
            logging.warning(f"Column {name} has incorrect type {col_type}. Expected {expected_columns[name]}.")
            break
    else:
        logging.info("Table structure is correct.")
        conn.close()
        return

    # If the structure is incorrect, drop and recreate the table
    logging.warning("Table structure is incorrect. Recreating table.")
    cursor.execute("DROP TABLE IF EXISTS synthia_emails")
    conn.commit()
    cursor.execute('''
        CREATE TABLE synthia_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            unread_count INTEGER,
            sender TEXT,
            email_count INTEGER,
            email_id TEXT UNIQUE,
            analyzed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Table 'synthia_emails' recreated.")

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
            email_count INTEGER,
            email_id TEXT UNIQUE,
            analyzed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Table 'synthia_emails' created or already exists.")
    check_table_structure()

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
    
def email_exists(email_id):
    """Check if an email with the given ID already exists in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM synthia_emails WHERE email_id = ?", (email_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_email_data(emails):
    """Save unread email count & sender counts to Synthia's database."""
    logging.info("💾 Saving email data to the database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for email_id, sender in emails.items():
            if not email_exists(email_id):
                logging.info(f"🔹 Inserting: EmailID={email_id}, Sender={sender}")
                cursor.execute('''
                    INSERT INTO synthia_emails (timestamp, email_id, sender, analyzed, category, email_count)
                    VALUES (datetime('now'), ?, ?, 0, 'unknown', 1)
                ''', (email_id, sender))
            else:
                logging.info(f"🔹 Skipping already stored email: EmailID={email_id}")

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
                email_count INTEGER,
                email_id TEXT UNIQUE,
                analyzed BOOLEAN DEFAULT 0,
                category TEXT DEFAULT 'unknown'
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
                count = row[2] if row[2] is not None else 0  # Handle NoneType values
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

def recreate_table():
    """Drop and recreate the email table."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS synthia_emails")
    conn.commit()
    cursor.execute('''
        CREATE TABLE synthia_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            unread_count INTEGER,
            sender TEXT,
            email_count INTEGER,
            email_id TEXT UNIQUE,
            analyzed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Table 'synthia_emails' recreated.")