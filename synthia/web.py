from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="/app/templates", static_folder="/app/static")

CONFIG_PATH = "/data/options.json"
DATA_FILE = "/data/email_data.json"

def load_config():
    """Load the Home Assistant configuration file."""
    try:
        if not os.path.exists(CONFIG_PATH):
            return {}
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def load_email_data():
    """Load the last email fetch data."""
    try:
        if not os.path.exists(DATA_FILE):
            return {"unread_count": 0, "last_fetch": "Never"}
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
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
                           unread_count=email_data.get("unread_count", 0),
                           last_fetch=email_data.get("last_fetch", "Never"),
                           cutoff_date=cutoff_date)

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files like images."""
    return send_from_directory("/app/static", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
