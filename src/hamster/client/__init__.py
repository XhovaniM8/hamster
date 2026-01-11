# - coding: utf-8 -

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
Platform-aware client module.

Automatically selects the appropriate storage client based on the platform:
- macOS: Uses native client (direct database access, no D-Bus)
- Linux: Uses D-Bus client (communicates with hamster-service daemon)
"""

import platform
import logging

logger = logging.getLogger(__name__)

# Detect platform and import appropriate client
_platform = platform.system()

if _platform == 'Darwin':  # macOS
    logger.info("macOS detected - using native storage client")
    from hamster.client.client_native import Storage
else:  # Linux and others
    logger.info("Linux/Unix detected - using D-Bus storage client")
    from hamster.client.client_dbus import Storage

# Export Storage class
__all__ = ['Storage']
