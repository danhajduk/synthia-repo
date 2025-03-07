import time
import logging
import os
import sql
import gmail
import web
import yaml

# Load configuration
with open("/app/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Ensure 'general' key exists in the configuration
if "general" not in config:
    config["general"] = {}

# Configure Logging
log_level = logging.DEBUG if config["general"].get("debug", False) else logging.INFO
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=log_level
)

def log_directory_structure():
    """Log the directory structure for debugging."""
    logging.debug(f"Current working directory: {os.getcwd()}")

    directories = ["/", "/app", "/data"]
    for directory in directories:
        logging.debug(f"Listing files in {directory}:")
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                logging.debug(f" - {full_path} ({'DIR' if os.path.isdir(full_path) else 'FILE'})")
        except Exception as e:
            logging.error(f"Could not list {directory}: {e}")

def main_loop():
    """Main loop to check and save emails."""
    while True:
        logging.info("Checking for unread emails...")
        sql.check_table_structure()  # Ensure the table structure is correct
        emails = gmail.fetch_unread_emails()
        if emails:
            sql.save_email_data(emails)  # Pass the emails dictionary
            logging.info("Email data successfully saved to Synthia's database.")
        else:
            logging.info("No new emails found.")
        time.sleep(600)  # Fetch emails every 10 minutes

if __name__ == "__main__":
    logging.info("#####################################################################################")
    logging.info("Synthia is running...")
    #log_directory_structure()
    #sql.create_table()  # Ensure the database table exists
    logging.info("Starting Web UI...")
    web.run()  # Start the Flask web server in a separate thread
    main_loop()
