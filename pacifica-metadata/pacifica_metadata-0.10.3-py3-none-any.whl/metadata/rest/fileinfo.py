#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Core interface for the fileinfo metadataobjects."""
from pacifica.metadata.rest.fileinfo_queries.file_details import FileDetailsLookup
from pacifica.metadata.rest.fileinfo_queries.earliest_latest import EarliestLatestFiles
from pacifica.metadata.rest.fileinfo_queries.files_with_tkv import FilesWithTransactionKeyValue


# pylint: disable=too-few-public-methods
class FileInfoAPI(object):
    """FileInfoAPI."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.file_details = FileDetailsLookup()
        self.files_for_keyvalue = FilesWithTransactionKeyValue()
        self.earliest_latest = EarliestLatestFiles()
