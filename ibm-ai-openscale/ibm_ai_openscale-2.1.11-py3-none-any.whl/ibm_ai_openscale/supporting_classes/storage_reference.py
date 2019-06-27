# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class StorageReference:
    def __init__(self, credentials):
        self.credentials = credentials

    def _get_explainability_payload(self):
        raise NotImplemented()


class DB2Reference(StorageReference):
    """
    Describes reference to table in DB2.

    :param credentials: credentials to db2 from Bluemix
    :type credentials: dict
    :param schema_name: schema name in db2
    :type schema_name: str
    :param table_name: table name in db2
    :type table_name: str
    """
    def __init__(self, credentials, schema_name, table_name):
        StorageReference.__init__(self, credentials)
        self.schema_name = schema_name
        self.table_name = table_name

    def _get_explainability_payload(self):
        training_data_reference_config = {
            'type': 'db2',
            'name': 'DB2 training data reference',
            'location':{
               'schema_name': self.schema_name,
               'table_name': self.table_name
            },
            'connection': self.credentials
        }

        return training_data_reference_config


class PostgresReference(StorageReference):
    """
    Describes reference to table in postgres.

    :param credentials: credentials to postgres from Bluemix
    :type credentials: dict
    :param table_name: table name in postgres
    :type table_name: str
    """
    def __init__(self, credentials, table_name):
        StorageReference.__init__(self, credentials)
        self.table_name = table_name

    def _get_explainability_payload(self):
        training_data_reference_config = {
            "name": "Postgres training data reference",
            "connection": self.credentials,
            "source": {
                "tablename": self.table_name,
                "type": 'postgres'
            }
        }

        return training_data_reference_config


class BluemixCloudObjectStorageReference(StorageReference):
    """
    Describes reference to file in COS.

    :param credentials: credentials to COS from Bluemix
    :type credentials: dict
    :param path: path within COS to file (bucket name + '/' + filename)
    :type path: str
    :param first_line_header: if csv, indicate if first row of file is header (optional)
    :type first_line_header: bool
    """
    def __init__(self, credentials, path, first_line_header=None):
        StorageReference.__init__(self, credentials)
        self.path = path
        self.first_line_header = first_line_header

    def _get_explainability_payload(self):
        training_data_reference_config = {
            "type": "cos",
            "name": "COS training data reference",
            "connection": {
                "url": "https://s3-api.us-geo.objectstorage.softlayer.net",
                "resource_instance_id": self.credentials['resource_instance_id'],
                "iam_url": "https://iam.bluemix.net/oidc/token",
                "api_key": self.credentials['apikey']
            },
            "location": {
                "file_name": self.path.split('/')[-1],
                "infer_schema": "1",
                "file_format": self.path.split('.')[-1],
                "bucket": '/'.join(self.path.split('/')[:-1]),
                "type": "bluemixcloudobjectstorage"
            }
        }

        if self.first_line_header is not None:
            training_data_reference_config['location']['firstlineheader'] = self.first_line_header

        return training_data_reference_config
