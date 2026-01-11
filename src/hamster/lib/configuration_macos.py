# -*- coding: utf-8 -*-

# Copyright (C) 2024 macOS Port

# This file is part of Project Hamster.

# Project Hamster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Project Hamster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Project Hamster.  If not, see <http://www.gnu.org/licenses/>.

"""
macOS configuration storage using plist files.
Provides the same interface as GSettingsStore but uses macOS UserDefaults.
"""

import logging
logger = logging.getLogger(__name__)

import os
import plistlib
from pathlib import Path

from gi.repository import GObject as gobject

from hamster.lib import datetime as dt


class MacOSConfigStore(gobject.GObject):
    """
    Settings implementation which stores settings in macOS plist format.
    Provides the same interface as GSettingsStore for compatibility.
    """

    __gsignals__ = {
        "changed": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))
    }

    # Default values matching the GSettings schema
    _defaults = {
        'day-start-minutes': 330,  # 5:30 AM
        'last-report-folder': '',
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        # macOS preferences location: ~/Library/Preferences/com.projecthamster.hamster.plist
        self._plist_dir = Path.home() / 'Library' / 'Preferences'
        self._plist_path = self._plist_dir / 'com.projecthamster.hamster.plist'

        # Ensure the directory exists
        self._plist_dir.mkdir(parents=True, exist_ok=True)

        # Load existing settings or create with defaults
        self._settings = self._load_settings()
        logger.info("macOS configuration loaded from: {}".format(self._plist_path))

    def _load_settings(self):
        """Load settings from plist file, or create with defaults if not exists."""
        if self._plist_path.exists():
            try:
                with open(self._plist_path, 'rb') as f:
                    settings = plistlib.load(f)
                logger.debug("Loaded settings from plist: {}".format(settings))

                # Merge with defaults to handle any missing keys
                for key, default_value in self._defaults.items():
                    if key not in settings:
                        settings[key] = default_value

                return settings
            except Exception as e:
                logger.warning("Failed to load plist, using defaults: {}".format(e))
                return self._defaults.copy()
        else:
            logger.info("No existing plist found, creating with defaults")
            return self._defaults.copy()

    def _save_settings(self):
        """Save current settings to plist file."""
        try:
            with open(self._plist_path, 'wb') as f:
                plistlib.dump(self._settings, f)
            logger.debug("Saved settings to plist: {}".format(self._settings))
        except Exception as e:
            logger.error("Failed to save plist: {}".format(e))

    def get(self, key, default=None):
        """
        Returns the value of the key or the default value if the key is
        not in settings
        """
        value = self._settings.get(key)
        if value is None:
            if default is not None:
                return default
            logger.warning("Unknown settings key: {}".format(key))
            return self._defaults.get(key)

        return value

    def set(self, key, value):
        """
        Sets the key value in settings and saves to plist
        """
        logger.debug("Setting {} -> {}".format(key, value))

        # Validate against defaults (type checking)
        if key in self._defaults:
            default_value = self._defaults[key]
            if not isinstance(value, type(default_value)) and default_value != '':
                logger.warning("Type mismatch for key {}: expected {}, got {}".format(
                    key, type(default_value), type(value)))

        self._settings[key] = value
        self._save_settings()

        # Emit changed signal for compatibility with GSettings
        self.emit('changed', key, value)
        return True

    def bind(self, key, obj, prop):
        """
        Bind a setting to a GObject property.
        Note: This is a simplified implementation compared to GSettings.bind()
        It only does one-way binding (settings -> property).
        """
        logger.debug("Binding {} to {}.{}".format(key, obj, prop))

        # Set initial value
        value = self.get(key)
        obj.set_property(prop, value)

        # Connect to changed signal to update property
        def on_changed(store, changed_key, new_value):
            if changed_key == key:
                obj.set_property(prop, new_value)

        self.connect('changed', on_changed)

    @property
    def day_start(self):
        """Start of the hamster day."""
        day_start_minutes = self.get("day-start-minutes")
        hours, minutes = divmod(day_start_minutes, 60)
        return dt.time(hours, minutes)
