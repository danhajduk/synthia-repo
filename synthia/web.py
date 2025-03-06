from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="/app/templates")

CONFIG_PATH = "/data/options.json"
DATA_FILE = "/data/email_data.json"

def load_email_data():
    """Load the last email fetch data and sort senders by email count."""
    try:
        if not os.path.exists(DATA_FILE):
            return {"unread_count": 0, "last_fetch": "Never", "senders": {}}
        with open(DATA_FILE, "r") as f:
            email_data = json.load(f)
        
        # Sort senders by email count (highest to lowest)
        email_data["senders"] = dict(sorted(email_data.get("senders", {}).items(), key=lambda item: item[1], reverse=True))
        return email_data
    except json.JSONDecodeError:
        return {"unread_count": 0, "last_fetch": "Never", "senders": {}}

@app.route("/")
def index():
    """Render the web UI."""
    email_data = load_email_data()
    return render_template("index.html",
                           unread_count=email_data["unread_count"],
                           last_fetch=email_data["last_fetch"],
                           cutoff_date="Unknown",
                           senders=email_data.get("senders", {}))

@app.route("/api/status")
def status():
    """Return JSON data for the web UI."""
    email_data = load_email_data()
    return jsonify(email_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
