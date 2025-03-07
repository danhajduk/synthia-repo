# Changelog

## [0.0.15d] - 2025-03-07
### Added
- Added detailed logging to `save_email_data` function.
- Added button in settings page to delete and recreate the email table.
- Ensured correct number of arguments are passed to `save_email_data` function.
- Updated version in configuration files.
- Removed `config.json` and ensured all references are updated to use `config.yaml`.
- Updated `web.py` to read version from `config.yaml` and display it in the UI.

## [0.0.15c] - 2025-02-28
### Added
- Fetch unread emails from Gmail and store them in an SQLite database.
- Ensure no duplicate emails are stored.
- Check and correct the database table structure before fetching emails.
- Web interface with settings and dashboard.
- Settings page with buttons to clear and refresh emails, check for updates, and recreate the email table.
- Dashboard displaying email summaries and a list of email senders.
- Configuration options in `config.yaml`.
- Update mechanism to fetch the latest version from GitHub releases and update the configuration.
- Detailed logging for debugging and monitoring.

