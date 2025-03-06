from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path='/static')

CONFIG_PATH = "/data/options.json"
DATA_FILE = "/data/email_data.json"

def load_config():
    """Load the Home Assistant configuration file."""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except:
        return {}

def load_email_data():
    """Load the last email fetch data."""
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {"unread_count": 0, "last_fetch": "Never"}

@app.route("/")
def index():
    """Render the web UI."""
    config = load_config()
    email_data = load_email_data()

    # Calculate cutoff date based on `days_to_fetch`
    days_to_fetch = config.get("general", {}).get("days_to_fetch", 7)
    cutoff_date = (datetime.utcnow() - timedelta(days=days_to_fetch)).strftime("%Y-%m-%d")

    return render_template("index.html",
                           unread_count=email_data["unread_count"],
                           last_fetch=email_data["last_fetch"],
                           cutoff_date=cutoff_date)

@app.route("/api/status")
def status():
    """Return JSON data for the web UI."""
    email_data = load_email_data()
    return jsonify(email_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
