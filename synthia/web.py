from flask import Flask, render_template, jsonify
import sqlite3
import os
import logging
import threading
import synthia  # Import main script

app = Flask(__name__)

# Database Path
DB_PATH = "/data/synthia.db"

def get_email_data():
    """Fetch email summary data from the database."""
    if not os.path.exists(DB_PATH):
        return {"unread_count": 0, "last_fetch": "Never", "cutoff_date": "N/A", "senders": []}

    conn = sqlite3.connect(DB_PATH)
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

@app.route("/")
def index():
    """Render main UI with email data."""
    data = get_email_data()
    return render_template("index.html", **data)

@app.route("/api/status")
def api_status():
    """Return email summary data as JSON."""
    return jsonify(get_email_data())

def start_synthia():
    """Start Synthia email fetcher in a separate thread."""
    logging.info("Starting Synthia email fetcher in background...")
    threading.Thread(target=synthia.run, daemon=True).start()

if __name__ == "__main__":
    start_synthia()
    logging.info("Starting Flask web UI on port 5000...")
    app.run(host="0.0.0.0", port=5005, debug=False)
