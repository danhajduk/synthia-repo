from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__, template_folder="/app/templates")

DB_PATH = "/data/synthia.db"

def get_email_data():
    """Retrieve latest email summary from Synthia's database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT sender, SUM(email_count) as total_emails
        FROM synthia_emails
        GROUP BY sender
        ORDER BY total_emails DESC
    ''')

    data = cursor.fetchall()
    conn.close()
    
    return {sender: count for sender, count in data}

@app.route("/")
def index():
    """Render the web UI."""
    email_data = get_email_data()
    return render_template("index.html", senders=email_data)

@app.route("/api/status")
def status():
    """Return JSON data for the web UI."""
    email_data = get_email_data()
    return jsonify(email_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
