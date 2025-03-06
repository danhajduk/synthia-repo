import time
import logging
import json
import os

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - INFO - %(message)s",
    level=logging.INFO
)

# Load Configuration from Home Assistant
CONFIG_PATH = "/data/options.json"

try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
        log_interval = config.get("log_interval", 10)
        custom_message = config.get("custom_message", "Synthia is on")
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    log_interval = 10
    custom_message = "Synthia is on"

if __name__ == "__main__":
    while True:
        logging.info(custom_message)
        time.sleep(log_interval)
