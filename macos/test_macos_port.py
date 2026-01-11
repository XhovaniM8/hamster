#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for macOS port of Hamster.
Verifies that the native client and macOS-specific features work correctly.
"""

import sys
import os

# Add src to path so we can import hamster modules
# This script is in macos/, so we need to go up one level to find src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_platform_detection():
    """Test that platform is correctly detected as macOS."""
    import platform
    print("Platform: {}".format(platform.system()))
    assert platform.system() == 'Darwin', "Not running on macOS!"
    print("✓ Platform detection passed")

def test_client_import():
    """Test that the native client is imported on macOS."""
    from hamster import client
    print("Client module: {}".format(client))
    print("Storage class: {}".format(client.Storage))
    print("Storage module: {}".format(client.Storage.__module__))
    assert 'client_native' in client.Storage.__module__, "Should use native client on macOS"
    print("✓ Native client import passed")

def test_config_store():
    """Test that macOS config store is used."""
    from hamster.lib.configuration import conf
    print("Config store type: {}".format(type(conf).__name__))
    assert type(conf).__name__ == 'MacOSConfigStore', "Should use MacOSConfigStore on macOS"
    print("✓ Config store passed")

def test_config_operations():
    """Test basic config operations."""
    from hamster.lib.configuration import conf

    # Test getting default value
    day_start = conf.get('day-start-minutes')
    print("Day start minutes: {}".format(day_start))
    assert day_start == 330, "Default should be 330 (5:30 AM)"

    # Test setting and getting
    conf.set('last-report-folder', '/tmp/test')
    value = conf.get('last-report-folder')
    print("Last report folder: {}".format(value))
    assert value == '/tmp/test', "Should be able to set and get values"

    # Test day_start property
    day_start_time = conf.day_start
    print("Day start time: {}".format(day_start_time))

    print("✓ Config operations passed")

def test_database_path():
    """Test that database path uses macOS location."""
    from hamster.storage import db

    storage = db.Storage(unsorted_localized="")
    db_path = storage.db_path
    print("Database path: {}".format(db_path))

    # Should be in ~/Library/Application Support/hamster/
    assert 'Library/Application Support/hamster' in db_path, \
        "Database should be in Application Support directory"
    print("✓ Database path passed")

def test_storage_client():
    """Test that native storage client works."""
    from hamster import client
    from hamster.lib import datetime as dt
    from hamster.lib.fact import Fact

    print("Creating storage client...")
    storage = client.Storage()
    print("Storage client created: {}".format(storage))

    # Test getting facts (should be empty initially)
    facts = storage.get_todays_facts()
    print("Today's facts: {}".format(facts))

    # Test getting categories
    categories = storage.get_categories()
    print("Categories: {}".format(categories))

    # Test getting activities
    activities = storage.get_activities()
    print("Activities: {}".format(activities))

    print("✓ Storage client operations passed")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Hamster macOS Port - Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Platform Detection", test_platform_detection),
        ("Client Import", test_client_import),
        ("Config Store", test_config_store),
        ("Config Operations", test_config_operations),
        ("Database Path", test_database_path),
        ("Storage Client", test_storage_client),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print("\nRunning: {}".format(name))
        print("-" * 60)
        try:
            test_func()
            passed += 1
        except Exception as e:
            print("✗ Test failed: {}".format(e))
            import traceback
            traceback.print_exc()
            failed += 1
        print()

    print("=" * 60)
    print("Test Results: {} passed, {} failed".format(passed, failed))
    print("=" * 60)

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
