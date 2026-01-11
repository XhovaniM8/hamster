# Hamster Time Tracker - macOS Port

This is a macOS port of the Hamster Time Tracker, maintaining the GTK3 interface while adapting the backend for macOS.

## Status

✅ **Working!** The core functionality is operational on macOS.

### What's Implemented

- ✅ Native storage client (no D-Bus dependency)
- ✅ macOS plist-based configuration (replaces GSettings)
- ✅ macOS standard directories (`~/Library/Application Support`)
- ✅ Platform-aware client selection
- ✅ GTK3 GUI working on macOS
- ✅ Basic time tracking functionality

### What's Pending

- ⏳ File monitoring using watchdog (currently using Gio)
- ⏳ macOS app bundle (.app) creation
- ⏳ Menu bar integration (optional)
- ⏳ macOS native notifications (optional)

## Installation

### Prerequisites

1. **Homebrew** (https://brew.sh)
2. **Python 3.11** (or later)

### Install Dependencies

```bash
# Install GTK3 and required libraries
brew install gtk+3 adwaita-icon-theme

# Install Python dependencies
pip3 install PyGObject pycairo watchdog
```

### Run from Source

```bash
# Clone or navigate to the repository
cd /path/to/hamster

# Run the application
python3.11 src/hamster-cli.py
```

## Architecture

### Original Linux Architecture
```
┌─────────────────┐    D-Bus IPC     ┌──────────────────┐
│  hamster-cli.py │ ◄───────────────► │ hamster-service  │
│  (GTK3 GUI)     │  (Session Bus)    │  (Storage Daemon)│
└─────────────────┘                   └──────────────────┘
         │                                     │
         ▼                                     ▼
   GSettings                             SQLite Database
   (~/.config)                      (~/.local/share/hamster/)
```

### macOS Architecture
```
┌──────────────────────────────────────┐
│      Hamster.app (Single Process)    │
│  ┌────────────┐   ┌──────────────┐  │
│  │  GTK3 GUI  │──►│ db.Storage   │  │
│  │            │   │ (Direct Call)│  │
│  └────────────┘   └──────────────┘  │
│         │               │            │
│         ▼               ▼            │
│    plist Config    SQLite DB         │
│   (UserDefaults)  (~/Library/...)    │
└──────────────────────────────────────┘
```

## Key Changes

### 1. No D-Bus Dependency

The Linux version uses D-Bus for IPC between the GUI and storage daemon. On macOS, we eliminated this by:

- Creating `src/hamster/client/client_native.py` - Direct database access
- Platform detection in `src/hamster/client/__init__.py` - Auto-selects the right client
- Merged service and GUI into single process

### 2. macOS Configuration Storage

Replaced GSettings with plist files:

- Configuration: `~/Library/Preferences/com.projecthamster.hamster.plist`
- Implementation: `src/hamster/lib/configuration_macos.py`
- Same API as GSettings for compatibility

Settings stored:
- `day-start-minutes`: When the hamster day starts (default: 330 = 5:30 AM)
- `last-report-folder`: Last folder used for saving reports

### 3. macOS Standard Directories

Updated paths to follow macOS conventions:

| Purpose | Linux | macOS |
|---------|-------|-------|
| Database | `~/.local/share/hamster/` | `~/Library/Application Support/Hamster/` |
| Config | GSettings | `~/Library/Preferences/*.plist` |

### 4. Modified Files

Key files changed for macOS compatibility:

- `src/hamster/client/__init__.py` - Platform detection and client selection
- `src/hamster/client/client_native.py` - New native storage client
- `src/hamster/lib/configuration.py` - Platform-aware config store
- `src/hamster/lib/configuration_macos.py` - New macOS config implementation
- `src/hamster/storage/db.py` - macOS directory paths

## Testing

Run the test suite to verify the port:

```bash
python3.11 test_macos_port.py
```

All tests should pass:
- ✅ Platform Detection
- ✅ Native Client Import
- ✅ Config Store
- ✅ Config Operations
- ✅ Database Path
- ✅ Storage Client Operations

## Database

The database file is located at:
```
~/Library/Application Support/Hamster/hamster.db
```

It's a standard SQLite database that's portable between Linux and macOS.

## Troubleshooting

### "Icon not present in theme" Error

Install the Adwaita icon theme:
```bash
brew install adwaita-icon-theme
```

### "No module named 'gi'" Error

Install PyGObject:
```bash
pip3 install PyGObject
```

### Wrong Python Version

Make sure you're using Python 3.11 (where PyGObject is installed):
```bash
python3.11 src/hamster-cli.py
```

### Circular Import Errors

Make sure you pulled the latest changes. The RuntimeStore in `configuration.py` uses lazy initialization to avoid circular imports.

## Development

### Adding Features

When adding features, be aware of:

1. **Import Cycles**: The native client creates potential circular imports. Use lazy initialization when needed.

2. **Platform Detection**: Use `platform.system() == 'Darwin'` to detect macOS and provide platform-specific implementations.

3. **File Paths**: Always use the appropriate paths for each platform:
   - macOS: `~/Library/Application Support/`
   - Linux: `~/.local/share/` (via GLib.get_user_data_dir())

### Running Tests

```bash
# Full test suite
python3.11 test_macos_port.py

# Run with debug logging
python3.11 src/hamster-cli.py --log DEBUG
```

## Contributing

To contribute to the macOS port:

1. Test your changes on macOS
2. Ensure backward compatibility with Linux
3. Update tests if needed
4. Document any new dependencies

## Known Limitations

1. **File Monitoring**: Currently uses Gio file monitoring. Should be replaced with native macOS FSEvents or the `watchdog` library for better integration.

2. **No App Bundle**: The app runs from the terminal. Creating a proper macOS `.app` bundle would improve the user experience.

3. **No Menu Bar Integration**: Unlike typical macOS apps, Hamster doesn't integrate with the menu bar. This could be added as an enhancement.

4. **GTK Theme**: Uses GTK's Adwaita theme which may not match macOS aesthetics perfectly.

## Future Enhancements

### High Priority
- [ ] Replace Gio file monitoring with watchdog
- [ ] Create macOS .app bundle
- [ ] Add installation script

### Medium Priority
- [ ] Menu bar integration
- [ ] macOS native notifications
- [ ] Dock icon customization
- [ ] macOS-native file dialogs

### Low Priority
- [ ] macOS theme integration (make it look more native)
- [ ] Touch Bar support
- [ ] iCloud sync support
- [ ] Keyboard shortcuts that match macOS conventions

## License

Same as the original Hamster Time Tracker: GPL v3+

## Credits

- Original Hamster Time Tracker: https://github.com/projecthamster/hamster
- macOS Port: 2024
