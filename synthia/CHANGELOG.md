# Changelog

## [0.0.17] - 2025-03-08
### Added
- Added dynamic updates to the email summary and fetch status on the index page using JavaScript.
- Added `/email_summary` endpoint to provide email summary data for dynamic updates.
- Updated `fetch_unread_emails` function to change `fetch_status` in the metadata table.
- Updated `web.py` to use the metadata table to get the fetch status.

## [0.0.16p] - 2025-03-08
### Added
- Added dynamic updates to the email summary and fetch status on the index page using JavaScript.
- Added `/email_summary` endpoint to provide email summary data for dynamic updates.
- Updated `fetch_unread_emails` function to change `fetch_status` in the metadata table.
- Updated `web.py` to use the metadata table to get the fetch status.

## [0.0.16] - 2025-03-07
### Added
- Modified database structure to include `recipient`, `subject`, and `unread_count` fields.
- Added `synthia_email_summary` and `synthia_safe_senders` tables.
- Added debug logging and debug switch to the configuration.
- Updated logging in `gmail.py`, `web.py`, and `sql.py` to include both info and debug levels.
- Added check to ensure the `general` key exists in the configuration.
- Added debug switch to the settings page and routes to get and toggle the debug state.
- Added debug switch to `config.json`.
- Added debugging logs to identify and fix the issue with saving email data.
- Fixed SQL syntax issues to ensure proper table creation.
- Added `email_count` column to the expected columns in `check_table_structure`.
- Defined table structures and expected columns as variables in `sql.py`.
- Added `UNIQUE` constraint to the `sender` column in the `synthia_email_summary` table.

## [0.0.15] - 2025-03-07
### Added
- Fixed email count increments.
- Fix DB type error.
- Reintroduced `config.json` and updated the version.
- Updated `web.py` to read version from `config.json` and display it in the UI.
- Added detailed logging to `save_email_data` function.
- Added button in settings page to delete and recreate the email table.
- Ensured correct number of arguments are passed to `save_email_data` function.
- Removed `config.json` and ensured all references are updated to use `config.yaml`.
- Updated `web.py` to read version from `config.yaml` and display it in the UI.
- Fetch unread emails from Gmail and store them in an SQLite database.
- Ensure no duplicate emails are stored.
- Check and correct the database table structure before fetching emails.
- Web interface with settings and dashboard.
- Settings page with buttons to clear and refresh emails, check for updates, and recreate the email table.
- Dashboard displaying email summaries and a list of email senders.
- Configuration options in `config.yaml`.
- Update mechanism to fetch the latest version from GitHub releases and update the configuration.
- Detailed logging for debugging and monitoring.

