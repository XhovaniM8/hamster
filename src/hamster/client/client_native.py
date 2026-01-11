# - coding: utf-8 -

# Copyright (C) 2007 Patryk Zawadzki <patrys at pld-linux.org>
# Copyright (C) 2007-2009 Toms Baugis <toms.baugis@gmail.com>
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


"""Native storage client for macOS - direct database access without D-Bus."""

import logging
logger = logging.getLogger(__name__)

from calendar import timegm
from gi.repository import GObject as gobject

import hamster
from hamster.storage import db
from hamster.lib.fact import Fact, FactError
from hamster.lib import datetime as dt


class Storage(gobject.GObject):
    """Hamster native client class - direct database access without D-Bus.

       This client provides the same API as the D-Bus client (hamster.client.Storage)
       but communicates directly with the database without requiring D-Bus.

       Subscribe to the `tags-changed`, `facts-changed` and `activities-changed`
       signals to be notified when an appropriate factoid of interest has been
       changed.

       In storage a distinguishment is made between the classificator of
       activities and the event in tracking log.
       When talking about the event we use term 'fact'. For the classificator
       we use term 'activity'.
       The relationship is - one activity can be used in several facts.
       The rest is hopefully obvious. But if not, please file bug reports!
    """
    __gsignals__ = {
        "tags-changed": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
        "facts-changed": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
        "activities-changed": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
        "toggle-called": (gobject.SignalFlags.RUN_LAST, gobject.TYPE_NONE, ()),
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        # Create direct database connection
        self._db = db.Storage(unsorted_localized="")

        # Wire up the storage callbacks to emit our signals
        self._db.tags_changed = self._on_tags_changed
        self._db.facts_changed = self._on_facts_changed
        self._db.activities_changed = self._on_activities_changed

        logger.info("Native storage client initialized (no D-Bus)")

    @staticmethod
    def _to_dict(columns, result_list):
        return [dict(zip(columns, row)) for row in result_list]

    def _on_tags_changed(self):
        self.emit("tags-changed")

    def _on_facts_changed(self):
        self.emit("facts-changed")

    def _on_activities_changed(self):
        self.emit("activities-changed")

    def toggle(self):
        """toggle visibility of the main application window if any"""
        # In native mode, we emit the signal directly
        # The GUI will handle this signal
        self.emit("toggle-called")

    def get_todays_facts(self):
        """returns facts of the current date, respecting hamster midnight
           hamster midnight is stored in config, and presented in minutes
        """
        return self._db.get_todays_facts()

    def get_facts(self, start, end=None, search_terms=""):
        """Returns facts for the time span matching the optional filter criteria.
           In search terms comma (",") translates to boolean OR and space (" ")
           to boolean AND.
           Filter is applied to tags, categories, activity names and description
        """
        range = dt.Range.from_start_end(start, end)
        return self._db.get_facts(range, search_terms=search_terms)

    def get_activities(self, search=""):
        """returns list of activities name matching search criteria.
           results are sorted by most recent usage.
           search is case insensitive
        """
        return self._to_dict(('name', 'category'),
                           [(a['name'], a['category'] or '')
                            for a in self._db.get_activities(search)])

    def get_categories(self):
        """returns list of categories"""
        return self._to_dict(('id', 'name'),
                           [(c['id'], c['name'])
                            for c in self._db.get_categories()])

    def get_tags(self, only_autocomplete=False):
        """returns list of all tags. by default only those that have been set for autocomplete"""
        return self._to_dict(('id', 'name', 'autocomplete'),
                           [(t['id'], t['name'], t['autocomplete'])
                            for t in self._db.get_tags(only_autocomplete)])

    def get_tag_ids(self, tags):
        """find tag IDs by name. tags should be a list of labels
           if a requested tag had been removed from the autocomplete list, it
           will be ressurrected. if tag with such label does not exist, it will
           be created.
           on database changes the `tags-changed` signal is emitted.
        """
        return self._to_dict(('id', 'name', 'autocomplete'),
                           [(t['id'], t['name'], t['autocomplete'])
                            for t in self._db.get_tag_ids(tags)])

    def update_autocomplete_tags(self, tags):
        """update list of tags that should autocomplete. this list replaces
           anything that is currently set"""
        self._db.update_autocomplete_tags(tags)

    def get_fact(self, id):
        """returns fact by it's ID"""
        return self._db.get_fact(id)

    def check_fact(self, fact, default_day=None):
        """Check Fact validity for inclusion in the storage.

        default_day (date): Default hamster day,
                            used to simplify some hint messages
                            (remove unnecessary dates).
                            None is safe (always show dates).
        """
        if not fact.start_time:
            raise FactError("Missing start time")

        try:
            self._db.check_fact(fact, default_day=default_day)
            return True, ""
        except FactError as e:
            raise e

    def add_fact(self, fact, temporary_activity=False):
        """Add fact (Fact)."""
        assert fact.activity, "missing activity"

        if not fact.start_time:
            logger.info("Adding fact without any start_time is deprecated")
            fact.start_time = dt.datetime.now()

        new_id = self._db.add_fact(fact)
        return new_id

    def stop_tracking(self, end_time=None):
        """Stop tracking current activity. end_time can be passed in if the
        activity should have other end time than the current moment"""
        if end_time is None:
            end_time = dt.datetime.now()
        return self._db.stop_tracking(end_time)

    def stop_or_restart_tracking(self):
        """Stop or restart tracking last activity."""
        return self._db.stop_or_restart_tracking()

    def remove_fact(self, fact_id):
        "delete fact from database"
        self._db.remove_fact(fact_id)

    def update_fact(self, fact_id, fact, temporary_activity=False):
        """Update fact values. See add_fact for rules.
        Update is performed via remove/insert, so the
        fact_id after update should not be used anymore. Instead use the ID
        from the fact dict that is returned by this function"""
        new_id = self._db.update_fact(fact_id, fact)
        return new_id

    def get_category_activities(self, category_id=None):
        """Return activities for category. If category is not specified, will
        return activities that have no category"""
        category_id = category_id or -1
        return self._to_dict(('id', 'name', 'category_id', 'category'),
                           [(a['id'], a['name'], a['category_id'], a['category'] or '')
                            for a in self._db.get_category_activities(category_id)])

    def get_category_id(self, category_name):
        """returns category id by name"""
        return self._db.get_category_id(category_name)

    def get_activity_by_name(self, activity, category_id=None, resurrect=True):
        """returns activity dict by name and optionally filtering by category.
           if activity is found but is marked as deleted, it will be resurrected
           unless told otherwise in the resurrect param
        """
        category_id = category_id or 0
        return self._db.get_activity_by_name(activity, category_id, resurrect)

    # category and activity manipulations (normally just via preferences)
    def remove_activity(self, id):
        self._db.remove_activity(id)

    def remove_category(self, id):
        self._db.remove_category(id)

    def change_category(self, id, category_id):
        return self._db.change_category(id, category_id)

    def update_activity(self, id, name, category_id):
        return self._db.update_activity(id, name, category_id)

    def add_activity(self, name, category_id=-1):
        return self._db.add_activity(name, category_id)

    def update_category(self, id, name):
        return self._db.update_category(id, name)

    def add_category(self, name):
        return self._db.add_category(name)
