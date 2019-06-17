# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure sql database datastore class."""
import azureml.data.constants as constants

from .abstract_datastore import AbstractDatastore


class AzureSqlDatabaseDatastore(AbstractDatastore):
    """Datastore backed by Azure data lake."""

    def __init__(self, workspace, name, server_name, database_name,
                 tenant_id, client_id, client_secret,
                 resource_url=None, authority_url=None):
        """Initialize a new Azure SQL Database Datastore.

        :param workspace: the workspace this datastore belongs to
        :type workspace: str
        :param name: the datastore name
        :type name: str
        :param server_name: the SQL server name
        :type server_name: str
        :param database_name: the SQL database name
        :type database_name: str
        :param tenant_id: the Directory ID/Tenant ID of the service principal
        :type tenant_id: str
        :param client_id: the Client ID/Application ID of the service principal
        :type client_id: str
        :param client_secret: the secret of the service principal
        :type client_secret: str
        :param resource_url: the resource url, which determines what operations will be performed on
        the SQL database store, if None, defaults to https://database.windows.net/
        :type resource_url: str, optional
        :param authority_url: the authority url used to authenticate the user, defaults to
        https://login.microsoftonline.com
        :type authority_url: str, optional
        """
        super(AzureSqlDatabaseDatastore, self).__init__(workspace, name, constants.AZURE_SQL_DATABASE)
        self.server_name = server_name
        self.database_name = database_name
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_url = resource_url
        self.authority_url = authority_url

    def _as_dict(self, hide_secret=True):
        output = super(AzureSqlDatabaseDatastore, self)._as_dict()
        output["server_name"] = self.server_name
        output["database_name"] = self.database_name
        output["tenant_id"] = self.tenant_id
        output["client_id"] = self.client_id
        output["resource_url"] = self.resource_url
        output["authority_url"] = self.authority_url

        if not hide_secret:
            output["client_secret"] = self.client_secret

        return output
