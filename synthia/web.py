"""
This module provides the web interface for Synthia using Flask.
It includes routes for displaying the dashboard, fetching email data,
clearing and refreshing emails, checking for updates, and managing settings.
"""

from flask import Flask, render_template, jsonify, request
import logging
import json
import sql
import gmail
import update  # Import the update script
import yaml  # Import yaml module
import datetime  # Import datetime module
import threading  # Import threading for periodic fetching
import openai  # Import the openai module

app = Flask(__name__, template_folder="/app/templates")

# Enable logging for debugging with timestamps
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

fetching = False  # Track if emails are being fetched

def get_current_version():
    """
    Get the current version from config.json.

    Returns:
        str: The current version, or "Unknown" if an error occurs.
    """
    try:
        with open("/app/config.json", "r") as f:
            config = json.load(f)
            return config.get("version", "Unknown")
    except Exception as e:
        logging.error(f"Error reading version: {e}")
        return "Unknown"

@app.before_request
def log_request():
    """
    Log all incoming requests for debugging.
    """
    logging.info(f"📥 Received request: {request.method} {request.path} from {request.remote_addr}")

@app.route("/")
def index():
    """
    Render main dashboard.

    Returns:
        str: Rendered HTML of the main dashboard.
    """
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
    """
    Render settings page.

    Returns:
        str: Rendered HTML of the settings page.
    """
    logging.info("✅ Rendering settings.html")
    return render_template("settings.html")

@app.route("/fetch_status")
def fetch_status():
    """
    Return the current email fetching status.

    Returns:
        json: JSON object containing the fetch status.
    """
    status = sql.get_metadata("fetch_status") or "✅ Ready"
    return jsonify({"status": status})

@app.route("/email_summary")
def email_summary():
    """
    Return the current email summary.

    Returns:
        json: JSON object containing the email summary.
    """
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
    """
    Clear email table and fetch new emails.

    Returns:
        json: JSON object containing the result message.
    """
    global fetching
    try:
        fetching = True  # Set status to fetching
        sql.clear_email_table()
        emails = gmail.fetch_unread_emails()
        sql.save_email_data(emails)  # Pass the emails dictionary
        sql.set_metadata("last_fetch", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql.set_metadata("cutoff_date", (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))  # Change to 1 day

        logging.info("✅ Database cleared & emails refreshed.")
        return jsonify({"message": "Database cleared & emails refreshed."})
    except Exception as e:
        logging.error(f"❌ Error clearing and refreshing emails: {e}")
        return jsonify({"message": "Error occurred."}), 500
    finally:
        fetching = False  # Reset fetching status

@app.route("/check_update", methods=["POST"])
def check_update():
    """
    Check for updates and restart if needed.

    Returns:
        json: JSON object containing the result message.
    """
    latest_version = update.get_latest_version()
    if (latest_version and update.update_config(latest_version)):
        return jsonify({"message": f"Updated to {latest_version}, restarting..."})
    return jsonify({"message": "Already up to date."})

@app.route('/recreate_table', methods=['POST'])
def recreate_table():
    """
    Drop and recreate the email table.

    Returns:
        json: JSON object containing the result message.
    """
    try:
        sql.recreate_table()
        return jsonify({"message": "Email table recreated successfully."})
    except Exception as e:
        return jsonify({"message": f"Error recreating table: {e}"}), 500

@app.route('/toggle_debug', methods=['POST'])
def toggle_debug():
    """
    Toggle the debug state in the configuration.

    Returns:
        json: JSON object containing the result message.
    """
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
    """
    Get the current debug state from the configuration.

    Returns:
        json: JSON object containing the debug state.
    """
    try:
        with open("/app/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        debug = config['general'].get('debug', False)
        return jsonify({"debug": debug})
    except Exception as e:
        return jsonify({"message": f"Error retrieving debug state: {e}"}), 500

@app.route("/important_senders")
def important_senders():
    """
    Return the list of important senders with their categories.

    Returns:
        json: JSON object containing the list of important senders.
    """
    try:
        important_senders = sql.get_important_senders()
        return jsonify({"important_senders": important_senders})
    except Exception as e:
        logging.error(f"❌ Error retrieving important senders: {e}")
        return jsonify({"important_senders": []}), 500

@app.route("/check_senders_openai", methods=["POST"])
def check_senders_openai():
    """
    Check senders in OpenAI to identify important senders.

    Returns:
        json: JSON object containing the result message.
    """
    try:
        important_senders = openai.identify_important_senders()
        return jsonify({"message": "Important senders identified.", "important_senders": important_senders})
    except Exception as e:
        logging.error(f"❌ Error checking senders in OpenAI: {e}")
        return jsonify({"message": "Error occurred while checking senders in OpenAI."}), 500

def periodic_fetch():
    """
    Periodically fetch emails and synchronize the database.
    """
    while True:
        try:
            logging.info("⏳ Periodic fetch started.")
            emails = gmail.fetch_unread_emails()
            sql.save_email_data(emails)
            sql.set_metadata("last_fetch", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            sql.set_metadata("cutoff_date", (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m/%d"))  # Change to 1 day
            logging.info("✅ Periodic fetch completed.")
        except Exception as e:
            logging.error(f"❌ Error during periodic fetch: {e}")
        finally:
            time.sleep(600)  # Fetch every 10 minutes

def run():
    """
    Run the Flask web server on port 5000.
    """
    logging.info("🚀 Starting Flask web server on port 5000")
    threading.Thread(target=periodic_fetch, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    run()
