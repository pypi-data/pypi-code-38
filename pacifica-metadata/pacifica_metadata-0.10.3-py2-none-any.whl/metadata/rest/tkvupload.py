#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Core interface for the tkvupload metadata objects to interface with CherryPy."""
from pacifica.metadata.rest.tkvupload_queries.upload_entries import UploadEntries


# pylint: disable=too-few-public-methods
class TkvUploadAPI(object):
    """InstrumentInfo API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.upload_entries = UploadEntries
