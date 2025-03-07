import sqlite3
import logging
import os

# Database Path
DB_PATH = "/data/synthia.db"

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
    conn = connect_db()
    if conn is None:
        logging.error("Could not connect to database to save data.")
        return
    cursor = conn.cursor()

    for sender, count in sender_counts.items():
        cursor.execute('''
            INSERT INTO synthia_emails (timestamp, unread_count, sender, email_count)
            VALUES (datetime('now'), ?, ?, ?)
        ''', (unread_count, sender, count))

    conn.commit()
    conn.close()
    logging.info("Email data successfully saved to Synthia's database.")

def get_email_data():
    """Fetch email summary data from the database."""
    conn = connect_db()
    if conn is None:
        logging.error("Could not connect to database for reading.")
        return {
            "unread_count": 0,
            "last_fetch": "Never",
            "cutoff_date": "N/A",
            "senders": []
        }

    cursor = conn.cursor()
    
    # Fetch latest unread count and timestamp
    cursor.execute("SELECT timestamp, unread_count FROM synthia_emails ORDER BY id DESC LIMIT 1")
    latest = cursor.fetchone()
    
    # Fetch senders sorted by count
    cursor.execute("SELECT sender, SUM(email_count) FROM synthia_emails GROUP BY sender ORDER BY SUM(email_count) DESC")
    senders = [{"sender": row[0], "count": row[1]} for row in cursor.fetchall()]

    conn.close()

    return {
        "unread_count": latest[1] if latest else 0,
        "last_fetch": latest[0] if latest else "Never",
        "cutoff_date": "Last 7 Days",
        "senders": senders
    }
