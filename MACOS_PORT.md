# Hamster macOS Port - Implementation Guide

> **WORK IN PROGRESS**: This document describes the macOS port implementation, which is currently in testing phase.

## Overview

This document outlines the strategy for porting Hamster Time Tracker to macOS while keeping the GTK3 interface intact.

## Architecture Changes

### Current Linux Architecture
```
┌─────────────────┐         D-Bus IPC        ┌──────────────────┐
│  hamster-cli.py │ ◄─────────────────────► │ hamster-service  │
│  (GTK3 GUI)     │    (Session Bus)         │  (Storage Daemon)│
└─────────────────┘                          └──────────────────┘
         │                                            │
         │                                            │
         ▼                                            ▼
   GSettings                                    SQLite Database
   (config)                                 (~/.local/share/hamster/)
```

### New macOS Architecture
```
┌──────────────────────────────────────┐
│      Hamster.app                     │
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

**Key Change**: Merge service and GUI into single process, eliminate D-Bus dependency.

## Implementation Tasks

### 1. D-Bus Replacement (CRITICAL)

**Strategy**: Create a new `hamster/client_native.py` that directly wraps `db.Storage` without D-Bus.

**Files to modify**:
- Create: `src/hamster/client_native.py` - Native storage client (no D-Bus)
- Modify: `src/hamster-cli.py` - Use native client on macOS
- Keep: `src/hamster/client.py` - Original D-Bus client (for Linux)

**Implementation**:
```python
# src/hamster/client_native.py
from gi.repository import GObject as gobject
from hamster.storage import db

class Storage(gobject.GObject):
    """Native storage client - direct database access without D-Bus"""
    __gsignals__ = {
        "tags-changed": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
        "facts-changed": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
        "activities-changed": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
        "toggle-called": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
    }

    def __init__(self):
        gobject.GObject.__init__(self)
        self._db = db.Storage()
        # Wire up callbacks to emit signals on data changes

    # Implement same API as client.Storage but call self._db directly
```

### 2. GSettings Replacement

**Strategy**: Create macOS-specific configuration module using plist files.

**Files to modify**:
- Create: `src/hamster/lib/configuration_macos.py`
- Modify: `src/hamster/lib/configuration.py` - Add platform detection
- Keep: Original GSettings code for Linux

**Paths**:
- Config: `~/Library/Preferences/com.projecthamster.hamster.plist`
- Use Foundation's NSUserDefaults or Python's plistlib

**Config Keys** (from `data/org.gnome.hamster.gschema.xml`):
- `day-start-minutes` (int): Default 330 (5:30 AM)
- `last-report-folder` (string)

### 3. File Monitoring Replacement

**Strategy**: Use Python's `watchdog` library (cross-platform, works on macOS).

**Files to modify**:
- Modify: `src/hamster/storage/db.py` - Replace Gio file monitoring
- Add dependency: `watchdog` to requirements

**Current Gio monitoring** (`src/hamster/storage/db.py:79-100`):
```python
self.__file_monitor = self.__file.monitor_file(...)
self.__file_monitor.connect("changed", self._on_db_file_change)
```

**New watchdog monitoring**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# Implement file change handler
```

### 4. Path Updates

**Strategy**: Replace XDG directories with macOS standard locations.

**Files to modify**:
- `src/hamster/storage/db.py` (lines 104-127)

**Path Mappings**:
```python
# Linux:
~/.local/share/hamster/hamster.db

# macOS:
~/Library/Application Support/Hamster/hamster.db
```

**Implementation**:
```python
import platform
if platform.system() == 'Darwin':  # macOS
    data_dir = os.path.expanduser('~/Library/Application Support/Hamster')
else:  # Linux
    data_dir = os.path.join(GLib.get_user_data_dir(), 'hamster')
```

### 5. Build System & Dependencies

**Strategy**: Create macOS-specific installation using setuptools.

**Files to create**:
- `setup.py` - Python package setup
- `requirements-macos.txt` - macOS-specific dependencies
- `build_macos.sh` - Build script for macOS

**Dependencies** (via Homebrew):
```bash
brew install python3 gtk+3 pygobject3 adwaita-icon-theme
pip3 install watchdog
```

### 6. App Bundle Creation

**Strategy**: Create standard macOS `.app` bundle structure.

**Structure**:
```
Hamster.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/
│   │   └── hamster (launcher script)
│   ├── Resources/
│   │   ├── hamster.icns
│   │   └── data/ (UI files, icons)
│   └── Frameworks/ (if bundling GTK)
```

**Files to create**:
- `data/Info.plist.in` - macOS app bundle metadata
- `build/create_app_bundle.sh` - Bundle creation script

## Testing Plan

1. **Unit Tests**: Verify storage operations work without D-Bus
2. **Integration Tests**: Test GUI with native storage client
3. **Manual Tests**:
   - Start/stop tracking
   - Add/edit/delete facts
   - Generate reports
   - Preferences changes persist
   - Database migrations work

## Compatibility

**Supported macOS versions**: 10.14 (Mojave) and later
**Reason**: GTK3 via Homebrew requires recent macOS

**Python version**: 3.6+ (same as Linux version)

## Migration Path

Users can keep using Linux version alongside macOS version:
- Database is portable (SQLite file)
- Can sync via Dropbox/iCloud by symlinking database

## Open Questions

1. **Icon theme**: Adwaita icons work on macOS but may look out of place. Consider alternative?
2. **Global hotkey**: Linux uses D-Bus for toggle. macOS alternative?
3. **Menu bar integration**: Should we add macOS menu bar icon for quick access?
4. **Notifications**: GTK notifications vs macOS native notifications?

## References

- GTK on macOS: https://www.gtk.org/docs/installations/macos/
- Python app bundling: https://py2app.readthedocs.io/
- macOS HIG: https://developer.apple.com/design/human-interface-guidelines/macos/
