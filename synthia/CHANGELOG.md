# Changelog

All notable changes to this project will be documented in this file.

## [0.0.13] - 2025-03-07
### ✨ Added
- **Auto-update feature**: Synthia can now automatically check for updates and restart if a new version is available.
- **Check for Updates button**: Added a button in the **Settings page** to manually check for updates.
- **Version display**: The current version is now displayed on the **main dashboard**.
- **New UI layout**: Redesigned **index.html** with a modern card-based look.
- **Better navigation**: Added a top navigation bar with a **Settings** button.

### 🔧 Fixed
- Fixed an issue where **`senders`** was being passed as a list instead of a dictionary in **index.html**.
- Improved Flask request logging for better debugging.
- **Ingress compatibility fixes** (still pending full integration).

### 🛠 Improvements
- **Cleaner UI layout**: Email data now displayed in structured **summary cards**.
- **More responsive design**: Works better on mobile and tablet devices.
- **Better error handling** for missing database files and API failures.

## [0.0.12] - 2025-03-06
### 🔧 Fixed
- Fixed issue where **email summaries** were being limited to 3 instead of fetching from the **last 7 days**.
- Improved logging format and error messages.

