from flask import Flask, render_template, jsonify
import sqlite3
import os
import sql

app = Flask(__name__)

def get_email_data():
    """Fetch email summary data from the database."""
    return sql.get_email_data()

@app.route("/")
def index():
    """Render main UI with email data."""
    data = get_email_data()
    return render_template("index.html", **data)

@app.route("/api/status")
def api_status():
    """Return email summary data as JSON."""
    return jsonify(get_email_data())

def run():
    """Run the Flask web server."""
    app.run(host="0.0.0.0", port=5005, debug=False)
