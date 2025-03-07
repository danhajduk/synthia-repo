# Changelog

All notable changes to this project will be documented in this file.

## [0.0.12q] - 2025-03-07
### 🔧 Fixed
- Fixed `/settings` page not loading correctly in Home Assistant Ingress.
- Improved Flask request logging for better debugging.

### ✨ Added
- Improved `index.html` layout with a modern, card-based design.
- Added a **navbar with a "Settings" button**.
- Reformatted email summary section for better readability.

## [0.0.12p] - 2025-03-06
### 🔧 Fixed
- Fixed issue where `senders` was a list instead of a dictionary in Jinja templates.

## [0.0.12o] - 2025-03-05
### ✨ Added
- Added OpenAI summarization option (disabled by default).
- Implemented "Clear & Refresh Emails" button in **Settings**.

## [0.0.12n] - 2025-03-04
### 🔧 Fixed
- Fixed missing email subjects in logs.

## [0.0.12m] - 2025-03-03
### ✨ Added
- Added Gmail fetching for the **last 7 days** instead of limiting to 3 emails.
