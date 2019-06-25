# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DBFS class."""
import azureml.data.constants as constants

from .abstract_datastore import AbstractDatastore


class DBFSDatastore(AbstractDatastore):
    """A Databricks File System (DBFS) Datastore."""

    def __init__(self, workspace, name):
        """Initialize a new Databricks File System (DBFS) datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param name: the datastore name
        :type name: str
        """
        super(DBFSDatastore, self).__init__(workspace, name, constants.DBFS)

    def _as_dict(self, hide_secret=True):
        output = super(DBFSDatastore, self)._as_dict()

        return output
