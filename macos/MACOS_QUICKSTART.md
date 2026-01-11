# Hamster Time Tracker - macOS Quick Start

> **WORK IN PROGRESS**: This macOS port is experimental and under testing. Please report any issues you encounter!

## Installation (5 minutes)

### Option 1: Automated Installation

Run the install script from the project root:
```bash
./macos/install_macos.sh
```

### Option 2: Manual Installation

```bash
# 1. Install Homebrew (if not already installed)
# Visit https://brew.sh for instructions

# 2. Install dependencies
brew install gtk+3 adwaita-icon-theme python@3.11
pip3 install PyGObject pycairo watchdog

# 3. Verify installation (from project root)
python3.11 macos/test_macos_port.py
```

## Running Hamster

### Easy Way
```bash
./macos/hamster
```

### Manual Way
```bash
python3.11 src/hamster-cli.py
```

## First Time Setup

When you first run Hamster:

1. The app will create its database at:
   ```
   ~/Library/Application Support/Hamster/hamster.db
   ```

2. Configuration is stored in:
   ```
   ~/Library/Preferences/com.projecthamster.hamster.plist
   ```

3. Default categories and activities will be created for you

## Basic Usage

### Adding a Time Entry

1. Click "Add Activity" or press the add button
2. Type your activity name (e.g., "Coding")
3. Optionally add:
   - Category (e.g., "Work")
   - Tags (e.g., "#python #debugging")
   - Description
4. Click "Track" to start tracking

### Stopping Tracking

1. Click "Stop" in the main window
2. Or add a new activity (stops the previous one)

### Viewing History

1. Open the Overview window
2. See all your tracked time
3. Filter by date, activity, or search terms
4. Generate reports

### Editing Preferences

1. Click the preferences icon
2. Set your day start time (when your tracking day begins)
3. Manage activities and categories

## Tips

- **Day Start Time**: Set to 5:30 AM by default. Activities before this time count toward the previous day.
- **Keyboard Shortcuts**: Use Tab to navigate between fields quickly
- **Continuous Tracking**: Starting a new activity automatically stops the previous one
- **Search**: In the overview, you can search across all fields

## Troubleshooting

### App Won't Start

Check if dependencies are installed:
```bash
python3.11 -c "from gi.repository import Gtk; print('GTK OK')"
```

### Icons Missing

Install Adwaita icons:
```bash
brew install adwaita-icon-theme
```

### Wrong Python Version

Ensure you're using Python 3.11:
```bash
which python3.11
python3.11 --version
```

### Database Issues

Your database is at `~/Library/Application Support/Hamster/hamster.db`

To reset (WARNING: deletes all data):
```bash
rm -rf ~/Library/Application\ Support/Hamster/
```

## Getting Help

- Documentation: See `README_MACOS.md`
- Porting guide: See `MACOS_PORT.md`
- Original project: https://github.com/projecthamster/hamster

## Next Steps

Now that you have Hamster running:

1. **Customize your categories** - Edit or add categories that match your work
2. **Start tracking** - Begin logging your activities
3. **Review regularly** - Check your time reports to understand where time goes
4. **Explore reports** - Export data for further analysis

Enjoy tracking your time with Hamster on macOS! 🐹⏰
