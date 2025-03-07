from flask import Flask, render_template, jsonify, request
import logging
import json
import sql
import gmail
import update  # Import the update script
import yaml  # Import yaml module
import datetime  # Import datetime module

app = Flask(__name__, template_folder="/app/templates")

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

fetching = False  # Track if emails are being fetched

def get_current_version():
    """Get the current version from config.json"""
    try:
        with open("/app/config.json", "r") as f:
            config = json.load(f)
            return config.get("version", "Unknown")
    except Exception as e:
        logging.error(f"Error reading version: {e}")
        return "Unknown"

@app.before_request
def log_request():
    """Log all incoming requests for debugging."""
    logging.info(f"📥 Received request: {request.method} {request.path} from {request.remote_addr}")

@app.route("/")
def index():
    """Render main dashboard."""
    logging.info("✅ Rendering index.html")
    
    try:
        senders = sql.get_email_data()
        unread_count = sum(senders.values())
        last_fetch = sql.get_metadata("last_fetch") or "N/A"
        cutoff_date = sql.get_metadata("cutoff_date") or "N/A"
    except Exception as e:
        logging.error(f"❌ Error retrieving email data: {e}")
        unread_count, senders = 0, {}
        last_fetch, cutoff_date = "N/A", "N/A"

    return render_template("index.html", version=get_current_version(), unread_count=unread_count, senders=senders, last_fetch=last_fetch, cutoff_date=cutoff_date)

@app.route("/settings")
def settings():
    """Render settings page."""
    logging.info("✅ Rendering settings.html")
    return render_template("settings.html")

@app.route("/fetch_status")
def fetch_status():
    """Return the current email fetching status."""
    status = sql.get_metadata("fetch_status") or "✅ Ready"
    return jsonify({"status": status})

@app.route("/email_summary")
def email_summary():
    """Return the current email summary."""
    try:
        senders = sql.get_email_data()
        unread_count = sum(senders.values())
        last_fetch = sql.get_metadata("last_fetch") or "N/A"
        cutoff_date = sql.get_metadata("cutoff_date") or "N/A"
        return jsonify({
            "unread_count": unread_count,
            "senders": senders,
            "last_fetch": last_fetch,
            "cutoff_date": cutoff_date
        })
    except Exception as e:
        logging.error(f"❌ Error retrieving email summary: {e}")
        return jsonify({
            "unread_count": 0,
            "senders": {},
            "last_fetch": "N/A",
            "cutoff_date": "N/A"
        }), 500

@app.route("/clear_and_refresh", methods=["POST"])
def clear_and_refresh():
    """Clear email table and fetch new emails."""
    global fetching
    try:
        fetching = True  # Set status to fetching
        sql.clear_email_table()
        emails = gmail.fetch_unread_emails()
        sql.save_email_data(emails)  # Pass the emails dictionary
        sql.set_metadata("last_fetch", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql.set_metadata("cutoff_date", (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))

        logging.info("✅ Database cleared & emails refreshed.")
        return jsonify({"message": "Database cleared & emails refreshed."})
    except Exception as e:
        logging.error(f"❌ Error clearing and refreshing emails: {e}")
        return jsonify({"message": "Error occurred."}), 500
    finally:
        fetching = False  # Reset fetching status

@app.route("/check_update", methods=["POST"])
def check_update():
    """Check for updates and restart if needed."""
    latest_version = update.get_latest_version()
    if latest_version and update.update_config(latest_version):
        return jsonify({"message": f"Updated to {latest_version}, restarting..."})
    return jsonify({"message": "Already up to date."})

@app.route('/recreate_table', methods=['POST'])
def recreate_table():
    try:
        sql.recreate_table()
        return jsonify({"message": "Email table recreated successfully."})
    except Exception as e:
        return jsonify({"message": f"Error recreating table: {e}"}), 500

@app.route('/toggle_debug', methods=['POST'])
def toggle_debug():
    try:
        data = request.json
        debug = data.get('debug', False)
        with open("/app/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        config['general']['debug'] = debug
        with open("/app/config.yaml", "w") as f:
            yaml.safe_dump(config, f)
        return jsonify({"message": "Debug state updated successfully."})
    except Exception as e:
        return jsonify({"message": f"Error updating debug state: {e}"}), 500

@app.route('/get_debug_state', methods=['GET'])
def get_debug_state():
    try:
        with open("/app/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        debug = config['general'].get('debug', False)
        return jsonify({"debug": debug})
    except Exception as e:
        return jsonify({"message": f"Error retrieving debug state: {e}"}), 500

def run():
    """Run the Flask web server on port 5000."""
    logging.info("🚀 Starting Flask web server on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    run()
