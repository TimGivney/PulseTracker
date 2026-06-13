# PulseTracker v3.0 - Build Guide

## Overview
PulseTracker v3.0 is a complete industrial CRM suite with dual identity system. This guide covers building the standalone executable and deployment.

## System Requirements
- Windows 7 or later
- Python 3.8+ (for building from source)
- 100 MB free disk space

## Building from Source (Windows)

### Step 1: Prerequisites
Ensure Python is installed and added to your PATH. Verify by running:
```
python --version
```

### Step 2: Extract and Navigate
Extract the `PulseTracker_v3.0_Ultimate_BuildKit.zip` and open Command Prompt in the extracted directory.

### Step 3: Run Build Script
Execute the build script:
```
build.bat
```

The script will automatically:
1. Create a virtual environment
2. Install all required dependencies
3. Build the standalone executable
4. Generate `PulseTracker.exe` in the `dist` folder

### Step 4: Locate Executable
After successful build, your executable is located at:
```
dist/PulseTracker.exe
```

## Features Implemented

### Equipment Tracking (Primary Tab)
The Equipment tab is the main priority with quick-entry fields for Owner, Location, Equipment Name, Serial #, Batch Time (Install Date), and Status. All data is persisted to the SQLite database.

### Functional "Stake New Claim" Button
The Accounts tab now includes a fully functional "Stake New Claim" button that opens a dialog to add new companies/accounts to the system.

### Dual Identity System
The application starts as a clean, professional SaaS product. Click the hidden "●" button in the bottom-right corner 3 times to unlock Dark Matter Mode, which transforms the interface into the "Tired Technician" theme with sarcastic Red Dwarf personality.

### Database Integration
All equipment and account data is stored in a local SQLite database (`pulsetracker.db`), ensuring data persistence across sessions.

## Deployment

### Single User
Simply copy `PulseTracker.exe` to any location and run it. The database will be created automatically in the same directory.

### Shared Network Drive
The application includes a single-instance lock mechanism to prevent database conflicts when multiple users access the same database on a shared drive.

## Troubleshooting

### Build Fails with "Python not found"
Ensure Python is installed and added to your system PATH. Restart Command Prompt after adding Python to PATH.

### Build Fails with "PyInstaller not found"
The build script will automatically install PyInstaller. If it fails, manually run:
```
pip install pyinstaller
```

### Executable Won't Start
Ensure all dependencies are installed. Try running the build script again with administrator privileges.

### Database Locked Error
Close all running instances of PulseTracker. The single-instance lock file (`pulse.lock`) may need to be manually deleted if the application crashed.

## Version Information
- **Version**: 3.0
- **Build Date**: April 2026
- **Executable Name**: PulseTracker.exe
- **Database**: SQLite (pulsetracker.db)

## Support
For issues or feature requests, refer to the included README.md or check the application logs for error details.
