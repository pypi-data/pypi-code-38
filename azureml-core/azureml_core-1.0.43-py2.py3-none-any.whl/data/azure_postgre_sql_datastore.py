# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure PostgreSql datastore class."""
import azureml.data.constants as constants

from .abstract_datastore import AbstractDatastore


class AzurePostgreSqlDatastore(AbstractDatastore):
    """Datastore backed by Azure PostgreSQL."""

    def __init__(self, workspace, name, server_name, database_name,
                 user_id, user_password, port_number=None):
        """Initialize a new Azure PostgreSQL.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param name: the datastore name
        :type name: str
        :param server_name: the PostgreSQL server name
        :type server_name: str
        :param database_name: the PostgreSQL database name
        :type database_name: str
        :param user_id: the User Id of the PostgreSQL server
        :type user_id: str
        :param user_password: the User Password of the PostgreSQL server
        :type user_password: str
        :param port_number: the port number of the PostgreSQL server
        :type port_number: str
        """
        super(AzurePostgreSqlDatastore, self).__init__(workspace, name, constants.AZURE_POSTGRESQL)
        self.server_name = server_name
        self.database_name = database_name
        self.user_id = user_id
        self.user_password = user_password
        self.port_number = port_number

    def _as_dict(self, hide_secret=True):
        output = super(AzurePostgreSqlDatastore, self)._as_dict()
        output["server_name"] = self.server_name
        output["database_name"] = self.database_name
        output["user_id"] = self.user_id
        output["port_number"] = self.port_number

        if not hide_secret:
            output["user_password"] = self.user_password

        return output
