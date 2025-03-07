import requests
import json
import os
import logging

# GitHub repo details
GITHUB_REPO = "danhajduk/synthia-repo"
CONFIG_PATH = "/data/options.json"

logging.basicConfig(level=logging.INFO)

def get_latest_version():
    """Fetch the latest version from GitHub releases."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("tag_name", "").replace("v", "")
    except Exception as e:
        logging.error(f"Error fetching latest version: {e}")
        return None

def update_config(new_version):
    """Update config.json with the latest version."""
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

        current_version = config.get("version", "0.0.0")
        if new_version and new_version > current_version:
            config["version"] = new_version
            with open(CONFIG_PATH, "w") as f:
                json.dump(config, f, indent=2)
            logging.info(f"Updated version to {new_version}")
            return True
        else:
            logging.info("Already on the latest version.")
    except Exception as e:
        logging.error(f"Error updating version: {e}")
    return False

if __name__ == "__main__":
    latest_version = get_latest_version()
    if latest_version and update_config(latest_version):
        logging.info("Restarting add-on...")
        os.system("ha addons restart synthia")
