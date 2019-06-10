# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Abstract datastore class."""
from abc import ABCMeta

import sys


class AbstractDatastore(object):
    """Base class of all datastores."""

    __metaclass__ = ABCMeta

    def __init__(self, workspace, name, datastore_type):
        """Class AbstractDatastore constructor.

        This is a base class and users should not be creating this class using the constructor.
        """
        self.workspace = workspace
        self.name = name
        self.datastore_type = datastore_type

    def set_as_default(self):
        """Set the current datastore as the default datastore."""
        AbstractDatastore._client().set_default(self.workspace, self.name)

    def unregister(self):
        """Unregisters the datastore, the underlying storage account and container/share will not be deleted."""
        AbstractDatastore._client().delete(self.workspace, self.name)

    def _as_dict(self):
        return {
            "name": self.name,
            "datastore_type": self.datastore_type
        }

    def _get_console_logger(self):
        return sys.stdout

    @staticmethod
    def _client():
        from .datastore_client import _DatastoreClient
        return _DatastoreClient
