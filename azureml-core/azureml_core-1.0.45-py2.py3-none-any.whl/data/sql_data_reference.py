# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SQL data reference class."""

from azureml.data.data_reference import DataReference


class SqlDataReference(DataReference):
    """class of the representation of a SQL data source reference."""

    def __init__(self, datastore, data_reference_name=None,
                 sql_table=None, sql_query=None, sql_stored_procedure=None, sql_stored_procedure_params=None):
        """Initialize sql data reference.

        :param datastore: the Datastore to reference
        :type datastore: AzureSqlDatabaseDatastore or AzurePostgreSqlDatastore
        :param data_reference_name: the name of the data reference
        :type data_reference_name: str
        :param sql_table: the name of the table in SQL database
        :type sql_table: str, optional
        :param sql_query: the sql query when using an SQL database
        :type sql_query: str, optional
        :param sql_stored_procedure: the name of the stored procedure when using an SQL database
        :type sql_stored_procedure: str, optional
        :param sql_stored_procedure_params: the optional list of parameters to pass to stored procedure.
        :type sql_stored_procedure_params: [azureml.data.stored_procedure_parameter.StoredProcedureParameter], optional
        """
        self.sql_table = sql_table
        self.sql_query = sql_query
        self.sql_stored_procedure = sql_stored_procedure
        self.sql_stored_procedure_params = sql_stored_procedure_params

        super(SqlDataReference, self).__init__(datastore, data_reference_name=data_reference_name)

    def path(self, path=None, data_reference_name=None):
        """Create a DataReference instance based on the given path.

        :param path: the path on the datastore
        :type path: str
        :param data_reference_name: the name of the data reference
        :type data_reference_name: str
        :return: the data reference object
        :rtype: DataReference
        """
        raise NotImplementedError("SqlDataReference does not support `path` operation.")

    def as_download(self, path_on_compute=None, overwrite=False):
        """Switch data reference operation to download.

        :param path_on_compute: the path on the compute for the data reference
        :type path_on_compute: str
        :param overwrite: whether to overwrite the data if existing
        :type overwrite: bool
        :return: a new data reference object
        :rtype: DataReference
        """
        raise NotImplementedError("SqlDataReference does not support `download` operation.")

    def as_upload(self, path_on_compute=None, overwrite=False):
        """Switch data reference operation to upload.

        :param path_on_compute: the path on the compute for the data reference
        :type path_on_compute: str
        :param overwrite: whether to overwrite the data if existing
        :type overwrite: bool
        :return: a new data reference object
        :rtype: DataReference
        """
        raise NotImplementedError("SqlDataReference does not support `upload` operation.")

    def as_mount(self):
        """Switch data reference operation to mount.

        :return: a new data reference object
        :rtype: DataReference
        """
        raise NotImplementedError("SqlDataReference does not support `mount` operation.")

    def to_config(self):
        """Convert the DataReference object to DataReferenceConfiguration object.

        :return: a new azureml.core.runconfig.DataReferenceConfiguration object
        :rtype: azureml.core.runconfig.DataReferenceConfiguration
        """
        raise NotImplementedError("SqlDataReference does not support `to_config` operation.")

    def _clone(self):
        return SqlDataReference(
            datastore=self.datastore,
            sql_table=self.sql_table,
            sql_query=self.sql_query,
            sql_stored_procedure=self.sql_stored_procedure,
            sql_stored_procedure_params=self.sql_stored_procedure_params
        )
