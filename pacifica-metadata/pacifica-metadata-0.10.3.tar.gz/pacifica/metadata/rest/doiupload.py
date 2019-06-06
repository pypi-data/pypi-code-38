#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Core interface to upload DOI registration info into metadata with CherryPy."""
from pacifica.metadata.rest.doi_queries.doi_registration_update import DOIRegistrationUpdate
from pacifica.metadata.rest.doi_queries.doi_registration_entry import DOIRegistrationEntry
from pacifica.metadata.rest.doi_queries.doi_modified_time_update import DOIModifiedTimeUpdate


# pylint: disable=too-few-public-methods
class DOIUploadAPI(object):
    """InstrumentInfo API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.update = DOIRegistrationUpdate
        self.new_entry = DOIRegistrationEntry
        self.update_modified_time = DOIModifiedTimeUpdate
