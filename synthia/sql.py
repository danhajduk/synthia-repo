import sqlite3
import logging
import os
import json

# Database Path
DB_PATH = "/data/synthia.db"

def connect_db():
    """Ensure database exists, create tables if not, and establish connection."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synthia_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                email_id TEXT UNIQUE,
                sender TEXT,
                recipient TEXT,
                subject TEXT,
                analyzed BOOLEAN DEFAULT 0,
                category TEXT DEFAULT 'unknown'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synthia_email_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                email_count INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synthia_safe_senders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT UNIQUE
            )
        ''')
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
    cursor.execute("PRAGMA table_info(synthia_emails)")
    columns = cursor.fetchall()
    expected_columns = {
        "id": "INTEGER",
        "timestamp": "TEXT",
        "email_id": "TEXT",
        "sender": "TEXT",
        "recipient": "TEXT",
        "subject": "TEXT",
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

    # If the structure is incorrect, drop and recreate the tables
    logging.warning("Table structure is incorrect. Recreating tables.")
    cursor.execute("DROP TABLE IF EXISTS synthia_emails")
    cursor.execute("DROP TABLE IF EXISTS synthia_email_summary")
    cursor.execute("DROP TABLE IF EXISTS synthia_safe_senders")
    conn.commit()
    cursor.execute('''
        CREATE TABLE synthia_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            email_id TEXT UNIQUE,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            analyzed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    ''')
    cursor.execute('''
        CREATE TABLE synthia_email_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            email_count INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE synthia_safe_senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Tables 'synthia_emails', 'synthia_email_summary', and 'synthia_safe_senders' recreated.")

def create_table():
    """Create tables in Synthia's database if they don't exist."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not establish database connection.")
        return
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            email_id TEXT UNIQUE,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            analyzed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_email_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            email_count INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synthia_safe_senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Tables 'synthia_emails', 'synthia_email_summary', and 'synthia_safe_senders' created or already exist.")
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
            sender = email_data['sender']
            recipient = email_data['recipient']
            subject = email_data['subject']
            if not email_exists(email_id):
                logging.debug(f"🔹 Inserting: EmailID={email_id}, Sender={sender}")
                cursor.execute('''
                    INSERT INTO synthia_emails (timestamp, email_id, sender, recipient, subject, analyzed, category)
                    VALUES (datetime('now'), ?, ?, ?, ?, 0, 'unknown')
                ''', (email_id, sender, recipient, subject))
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synthia_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                email_id TEXT UNIQUE,
                sender TEXT,
                recipient TEXT,
                subject TEXT,
                analyzed BOOLEAN DEFAULT 0,
                category TEXT DEFAULT 'unknown'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synthia_email_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                email_count INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synthia_safe_senders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT UNIQUE
            )
        """)
        conn.commit()
        logging.info("✅ Ensured tables exist.")

        # Fetch email summary data
        cursor.execute("SELECT sender, email_count FROM synthia_email_summary ORDER BY id DESC")
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
    cursor.execute("DROP TABLE IF EXISTS synthia_emails")
    cursor.execute("DROP TABLE IF EXISTS synthia_email_summary")
    cursor.execute("DROP TABLE IF EXISTS synthia_safe_senders")
    conn.commit()
    cursor.execute('''
        CREATE TABLE synthia_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            email_id TEXT UNIQUE,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            analyzed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
    ''')
    cursor.execute('''
        CREATE TABLE synthia_email_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            email_count INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE synthia_safe_senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Tables 'synthia_emails', 'synthia_email_summary', and 'synthia_safe_senders' recreated.")