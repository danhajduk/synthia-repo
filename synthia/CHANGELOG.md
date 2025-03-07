# Changelog

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

