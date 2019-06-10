"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import tempfile
import shutil
import pickle
import cuid
from cortex.utils import md5sum, log_message
from cortex.logger import getLogger
from cortex.dataset import Dataset, LocalDataset
from cortex_client import DatasetsClient, ConnectionClient, CatalogClient


log = getLogger(__name__)


class DatasetBuilder:

    """
    A builder utility to aid in programmatic creation of Cortex datasets; not meant to be directly instantiated by
    clients.
    """

    def __init__(self, name: str, client: DatasetsClient, camel='1.0.0'):
        self._camel = camel
        self._name = name
        self._title = ' '
        self._description = ' '
        self._client = client
        self._connections = {}
        self._parameters = []
        self._pipelines = {}
        self._schema_name = None
        self._schema_title = None
        self._schema_description = None

    def title(self, title: str):
        """
        Sets the title property of a dataset.

        :param title: the human-readable name of the dataset.
        :return: the builder instance.
        """
        self._title = title
        return self

    def description(self, description: str):
        """
        Sets the description property of the dataset.

        :param description: The human-readable long description of the dataset.
        :return: The builder instance.
        """
        self._description = description
        return self


    def parameters(self, parameters: list):
        """
        Sets the parameters property of the dataset.

        :param parameters: The parameters to associate with the dataset.
        :return: The builder instance.
        """
        self._parameters = parameters
        return self

    def from_csv(self, file_name, **kwargs):
        """
        Creates a dataset from a csv file.

        :param file_name: name of the file
        :param kwargs: optional key-value dictionary of parameters to pass to pandas on creation
        """
        try:
            import pandas as pd
            return self.from_df(pd.read_csv(file_name, **kwargs), format='csv')
        except ImportError:
            raise Exception('from_csv requires pandas to be installed!')

    def from_json(self, file_name, **kwargs):
        """
        Creates a dataset from a json file.

        :param file_name: name of the file
        :param kwargs: optional key-value dictionary of parameters to pass to pandas on creation
        """
        try:
            import pandas as pd
            return self.from_df(pd.read_json(file_name, **kwargs), format='json')
        except ImportError:
            raise Exception('from_json requires pandas to be installed!')

    def from_df(self, df, format='json'):
        """
        Sets the content of the dataset to the provided pandas dataframe.  The datarrame is serialized and
        uploaded to the Cortex Managed Content service in the specified path.

        :param df: the pandas dataframe to use
        :param format: 'json' or 'csv'
        :return: the builder instance
        """

        # Reset connection and parameters
        self._connections = {}
        self._parameters = []

        content_client = ConnectionClient(
            self._client._serviceconnector.url,
            2,
            self._client._serviceconnector.token
        )

        content_query = [
            {'name': 'contentType', 'value': format.upper()}
        ]

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
                temp_path = temp.name
                content_type = 'text/csv'
                if format.lower() == 'json':
                    content_type = 'application/json-lines'
                    content_query.append({'name': 'json/style', 'value': 'lines'})

                    # Use the 'records' format and JSON lines style file
                    df.to_json(temp, orient='records', lines=True)
                elif format.lower() == 'csv':
                    content_query.append({'name': 'csv/delimiter', 'value': ','})
                    content_query.append({'name': 'csv/headerRow', 'value': True})

                    # Stick to Pandas defaults for CSV
                    df.to_csv(temp, index=False)
                else:
                    raise Exception('Invalid format %s, must be either "json" or "csv"' % format)

            md5 = md5sum(temp_path)
            upload_key = '/cortex/datasets/%s/%s.%s' % (self._name, md5, format.lower())
            content_query.append({'name': 'key', 'value': upload_key})

            if not content_client.exists(upload_key):
                log_message('file version not found, pushing to remote storage: ' + upload_key, log)
                with open(temp_path, 'rb') as f:
                    # content_client.uploadStreaming(key=upload_key, content_type=content_type, stream=f)
                    content_client.upload(key=upload_key, stream_name='df', content_type=content_type, stream=f)
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)

        self._connections['default'] = {
            'name': 'cortex/content',
            'type': 'managedContent',
            'query': content_query
        }

        self._add_dataframe_params(df)

        return self

    def _add_dataframe_params(self, df):
        for c in df.columns.values:
            # assume 'string' type, look for boolean, numeric, date, object
            param_type = 'string'
            param_format = None

            dtype = df[c].dtype
            if dtype.name == 'bool':
                param_type = 'boolean'
            elif dtype.name == 'object':
                param_type = 'string'
            elif dtype.name.startswith('int'):
                param_type = 'integer'
                param_format = 'int64'
            elif dtype.name.startswith('float'):
                param_type = 'number'
                param_format = 'float'
            elif dtype.name.startswith('date'):
                param_type = 'integer'
                param_format = 'timestamp.epoch'

            if param_format:
                self._parameters.append({'name': c, 'type': param_type, 'format': param_format})
            else:
                self._parameters.append({'name': c, 'type': param_type})

    def from_dataset(self, ds: Dataset):
        """
        Creates a dataset builder from a given dataset.

        :param ds: dataset to use in creation of this builder
        """
        self._camel = ds.camel
        self._name = ds.name
        self._title = ds.title
        self._description = ds.description
        self._parameters = ds.parameters or []
        self._pipelines = ds.pipelines or {}

        if ds.camel == '1.0.0':
            self._connections['default'] = {'name': ds.connectionName, 'query': ds.connectionQuery}
        else:
            self._connections = ds.connections or {}

        # NOTE: should this also set the dataframe / pandas data?
        return self

    def create_schema(self, name: str, title: str = None, description: str = None):
        """
        Creates or replaces a schema (type) based on the message parameters set in the builder once the build is
        called. The Cortex dataset refers to this schema rather than embedding the parameters inline.

        :param name: the resource name of the new schema
        :param title: human-readable display name
        :param description: human-readable long description
        :return: the builder instance
        """
        self._schema_name = name
        self._schema_title = title
        self._schema_description = description
        return self

    def to_camel(self):
        """
        Creates a dataset with the builder's CAMEL definitions.
        """
        ds = {
            'camel': self._camel,
            'name': self._name,
            'title': self._title,
            'description': self._description,
            'parameters': self._parameters,
            'pipelines': {key: pipeline.to_camel() for key, pipeline in self._pipelines.items()}
        }

        # Create/update a schema for the declared Dataset parameters
        if self._schema_name:
            catalog_client = CatalogClient(
                self._client._serviceconnector.url,
                3,
                self._client._serviceconnector.token
            )

            schema = {
                'camel': self._camel,
                'name': self._schema_name,
                'title': self._schema_title or '',
                'description': self._schema_description or '',
                'parameters': self._parameters
            }

            catalog_client.save_type(schema)
            ds['parameters'] = {'$ref': self._schema_name}

        if self._camel == '1.0.0':
            ds['connectionName'] = self._connections.get('default', {}).get('name')
            ds['connectionQuery'] = self._connections.get('default', {}).get('query')
        else:
            ds['connections'] = self._connections

        return ds

    def build(self) -> Dataset:
        """
        Builds and saves a dataset using the properties configured on the builder.

        :return: the resulting dataset
        """
        ds = self.to_camel()

        # Save the newly built dataset
        self._client.save_dataset(ds)

        return Dataset.get_dataset(self._name, self._client)


class LocalDatasetBuilder(DatasetBuilder):
    """
    Builds a local dataset.
    """
    def __init__(self, name: str, camel='1.0.0'):
        super().__init__(name, None, camel)
        self._dataset = LocalDataset(name)
        self._data_path = None

    def from_df(self, df, format='pk'):
        """
        Sets the content of the local dataset to the provided pandas dataframe.

        :param df: the pandas dataframe to use
        :param format: 'json' or 'csv'
        :return: the builder instance
        """
        temp_id = cuid.cuid()
        file_name = '{}.{}'.format(temp_id, format)
        file_path = self._dataset.data_dir / file_name

        if format == 'json':
            with open(file_path, 'w') as f:
                # Use the 'records' format and JSON lines style file
                df.to_json(f, orient='records', lines=True)
        elif format == 'csv':
            with open(file_path, 'w') as f:
                # Stick to Pandas defaults for CSV
                df.to_csv(f,index=False)
        else:
            # Pickle
            with open(file_path, 'w+b') as f:
                pickle.dump(df, f, protocol=pickle.DEFAULT_PROTOCOL)

        md5_hash = md5sum(file_path)
        self._data_path = '{}.{}'.format(md5_hash, format)
        shutil.move(file_path, self._dataset.data_dir / self._data_path)

        self._add_dataframe_params(df)

        return self

    def from_dataset(self, ds: Dataset):
        """
        Sets the content of the local dataset to the provided Dataset.

        :param df: the Dataset to use
        :return: the builder instance
        """
        self._camel = ds.camel
        self._name = ds.name
        self._title = ds.title
        self._description = ds.description
        self._parameters = ds.parameters or []
        self._pipelines = ds.pipelines or {}

        self.from_df(ds.as_pandas())

        return self


    def to_camel(self):
        """
        Creates a dataset with the builder's camel definition.
        """
        ds = {
            'camel': self._camel,
            'name': self._name,
            'title': self._title,
            'description': self._description,
            'parameters': self._parameters,
            'pipelines': {key: pipeline.to_camel() for key, pipeline in self._pipelines.items()}
        }

        return ds

    def build(self) -> LocalDataset:
        """
        Builds a LocalDataset.
        """
        self._dataset.title = self._title
        self._dataset.description = self._description
        self._dataset.content_key = self._data_path

        if self._schema_name:
            self._dataset.parameters = [{'$ref': self._schema_name}]
        else:
            self._dataset.parameters = self._parameters or []

        # TODO Pipelines

        self._dataset.save()

        return self._dataset
