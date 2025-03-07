# Synthia - AI Personal Assistant

Synthia is your personal AI assistant for email summaries and more. It fetches unread emails from Gmail, stores them in an SQLite database, and provides a web interface to view email summaries and manage settings.

## Features

- Fetch unread emails from Gmail
- Store emails in an SQLite database
- Web interface with email summaries and settings
- Debug logging and configuration options

## Installation

### Prerequisites

- Home Assistant

### Steps

1. Add the repository to Home Assistant:

    1. Go to **Settings** in the Home Assistant sidebar.
    2. Click on the **Add-on Store** tab.
    3. Click on the **Repositories** button in the bottom right corner.
    4. Enter the repository URL: `https://github.com/danhajduk/synthia-repo`
    5. Click **Add**.

2. Install the Synthia add-on:

    1. Find the **Synthia - AI Personal Assistant** add-on in the list.
    2. Click on the add-on and then click **Install**.

3. Configure the add-on:

    1. Go to the **Configuration** tab of the add-on.
    2. Update the configuration options as needed (e.g., Gmail API credentials, fetch interval).
    3. Click **Save**.

4. Start the add-on:

    1. Go to the **Info** tab of the add-on.
    2. Click **Start**.

5. Access the web interface:

    Open your browser and go to `http://<your-home-assistant-ip>:5000`.

## Configuration

The configuration options are defined in `config.yaml` and `config.json`. You can update the configuration to customize Synthia's behavior.

### config.yaml

```yaml
name: "Synthia"
version: "0.0.16f"
slug: "synthia"
description: "Your personal AI assistant for email summaries and more."
arch:
  - amd64
  - armv7
  - armhf
init: false
ingress: true
ingress_port: 5000
ingress_entry: "/"
panel_icon: "mdi:email"
panel_title: "Synthia"
url: "https://github.com/danhajduk/synthia-repo"
changelog: "https://github.com/danhajduk/synthia-repo/synthia/CHANGELOG.md"
options:
  general:
    log_interval: 10
    fetch_interval_minutes: 10
    days_to_fetch: 7
    custom_message: "Synthia is on"
    debug: false
  gmail:
    enable_gmail: true
    gmail_api_key: ""
    client_id: ""
    client_secret: ""
    refresh_token: ""
  openai:
    openai_api_key: ""
  notifications:
    notify_service: "notify.mobile_app_your_phone"
schema:
  general:
    log_interval: int
    fetch_interval_minutes: int
    days_to_fetch: int
    custom_message: str
    debug: bool
  gmail:
    enable_gmail: bool
    gmail_api_key: str
    client_id: str
    client_secret: str
    refresh_token: str
  openai:
    openai_api_key: str
  notifications:
    notify_service: str
map:
  - data:rw
host_network: true
```

### config.json

```json
{
    "name": "Synthia - AI Personal Assistant",
    "version": "0.0.16f",
    "slug": "synthia",
    "description": "Your personal AI assistant for email summaries and more.",
    "arch": ["amd64", "armv7", "armhf"],
    "init": false,
    "ingress": true,
    "ingress_port": 5000,
    "ingress_entry": "/",
    "panel_icon": "mdi:email",
    "panel_title": "Synthia",
    "url": "https://github.com/danhajduk/synthia-repo",
    "changelog": "https://github.com/danhajduk/synthia-repo/synthia/CHANGELOG.md",
    "options": {
      "general": {
        "log_interval": 10,
        "fetch_interval_minutes": 10,
        "days_to_fetch": 7,
        "custom_message": "Synthia is on",
        "debug": false
      },
      "gmail": {
        "enable_gmail": true,
        "gmail_api_key": "",
        "client_id": "",
        "client_secret": "",
        "refresh_token": ""
      },
      "openai": {
        "openai_api_key": ""
      },
      "notifications": {
        "notify_service": "notify.mobile_app_your_phone"
      }
    },
    "schema": {
      "general": {
        "log_interval": "int",
        "fetch_interval_minutes": "int",
        "days_to_fetch": "int",
        "custom_message": "str",
        "debug": "bool"
      },
      "gmail": {
        "enable_gmail": "bool",
        "gmail_api_key": "str",
        "client_id": "str",
        "client_secret": "str",
        "refresh_token": "str"
      },
      "openai": {
        "openai_api_key": "str"
      },
      "notifications": {
        "notify_service": "str"
      }
    },
    "map": ["data:rw"],
    "host_network": true
}
```

## Usage

### Web Interface

- **Dashboard**: View email summaries and fetching status.
- **Settings**: Manage configuration options and perform actions like clearing and refreshing emails, checking for updates, and recreating the email table.

### Fetching Emails

Synthia fetches unread emails from Gmail every 10 minutes by default. You can customize the fetch interval in the configuration.

### Debug Logging

Enable debug logging by setting `debug: true` in the configuration. This will provide detailed logs for troubleshooting.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
