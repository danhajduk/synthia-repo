# Changelog

## [0.0.16] - 2025-03-07
### Added
- Modified database structure to include `recipient` and `subject` fields.
- Added `synthia_email_summary` and `synthia_safe_senders` tables.
- Added debug logging and debug switch to the configuration.
- Updated logging in `gmail.py`, `web.py`, and `sql.py` to include both info and debug levels.
- Added check to ensure the `general` key exists in the configuration.

## [0.0.15k] - 2025-03-07
### Added
- Fixed email count increments.

## [0.0.15i] - 2025-03-07
### Added
- Fix DB type error

## [0.0.15h] - 2025-03-07
### Added
- Reintroduced `config.json` and updated the version.
- Updated `web.py` to read version from `config.json` and display it in the UI.

## [0.0.15g] - 2025-03-07
### Added
- Added detailed logging to `save_email_data` function.
- Added button in settings page to delete and recreate the email table.
- Ensured correct number of arguments are passed to `save_email_data` function.
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

