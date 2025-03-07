# Changelog

## [0.0.17] - 2025-03-08
### Added
- Added dynamic updates to the email summary and fetch status on the index page using JavaScript.
- Added `/email_summary` endpoint to provide email summary data for dynamic updates.
- Updated `fetch_unread_emails` function to change `fetch_status` in the metadata table.
- Updated `web.py` to use the metadata table to get the fetch status.
- Added timestamps to log entries.
- Implemented periodic fetching and synchronization of emails.
- Marked emails as read if they are no longer unread.
- Deleted read emails from the database.

