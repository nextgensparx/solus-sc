#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

import gi
gi.require_version('Snapd', '1')

class PopulationFilter:
    """ A population filter is provided to the provider plugin to begin
        population of a given type
    """

    INSTALLED = 0
    SEARCH = 1
    CATEGORY = 2

class ItemStatus:
    """ The ItemStatus allows us to know the exact state of any given item
        as a combination of the various status flags
    """

    INSTALLED = 1 << 0
    UPDATE_NEEDED = 1 << 1 # We have an update available
    UPDATING = 1 << 2
    REMOVING = 1 << 3
    UPDATE_SECURITY = 1 << 4 # Security update available
    UPDATE_CRITICAL = 1 << 5 # Critical update available
    UPDATE_BUGFIX = 1 << 6 # Bugfix update available
    META_DEVEL = 1 << 7 # Is a development type of package

class ProviderStorage:
    """ ProviderStorage is an abstract type that should be populated by
        existing plugins

        Storage may be recycled at any time and is used simply to allow
        dynamic "pushing" of items into the storage
    """

    def add_item(self, id, item):
        raise RuntimeError("implement add_item")

    def clear(self):
        raise RuntimeError("implement clear")

class ProviderPlugin:
    """ A ProviderPlugin provides its own managemenet and access to the
        underlying package management system to provide the options to the
        user
    """

    def populate_storage(self, storage, popfilter, extra):
        """ Populate storage using the given filter """
        raise RuntimeError("implement populate_storage")

    def cancel(self):
        """ Cancel any ongoing populare_storage calls """
        raise RuntimeError("implement cancel")


class ProviderItem:
    """ A ProviderItem is addded to the ProviderStorage by each ProviderPlugin
        and enables access + caching of various backend package management
        systems
    """

    status = None

    def __init__(self):
        # Default to installed status
        self.status = ItemStatus.INSTALLED

    def get_status(self):
        """ Return the current status for this item """
        return self.status

    def remove_status(self, st):
        """ Remove a status field """
        self.status ^= st

    def add_status(self, st):
        """ Add a status field """
        self.status |= st

    def set_status(self, st):
        """ Set the complete status """
        self.status = st

    def has_status(self, st):
        return self.status & st == st

    def get_id(self):
        """ Every item should return their unique ID so that they can
            be tracked and differentiated between different backends
        """
        raise RuntimeError("implement get_id")

    def get_name(self):
        """ Actual name of the item. Title is stylised separateley """
        raise RuntimeError("implement get_name")

    def get_title(self):
        """ Each item should return an appropriate item for displaying
            as the stylised title
        """
        raise RuntimeError("implement get_title")

    def get_description(self):
        """ Each item should support returning their complete description
        """
        raise RuntimeError("implement get_description")

    def get_version(self):
        """ Each item should return a usable version string. This is purely
            for cosmectics
        """
        raise RuntimeError("implement get_version")