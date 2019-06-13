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

from cortex_client import CatalogClient

import collections
import datetime
from cortex.schema import Schema
from cortex.logger import getLogger


log = getLogger(__name__)


class SchemaBuilder:

    """
    Creates and replaces dataset schemas (types); not intended to be directly instantiated
    by clients.
    """

    def __init__(self, name: str, client: CatalogClient, camel='1.0.0'):
        self._camel = camel
        self._name = name
        self._title = ' '
        self._description = ' '
        self._parameters = {}
        self._client = client

    def title(self, title: str):
        """
        Sets the title property of the schema.

        :param title: the human-readable name of the schema
        :return: the builder instance
        """
        self._title = title
        return self

    def description(self, description: str):
        """
        Sets the description property of the schema.

        :param description: the human-readable long description of the schema
        :return: the builder instance
        """
        self._description = description
        return self

    def parameter(self, name, type, title=None, description=None, format=None, required=True):
        self._parameters[name] = {'name': name, 'type': type, 'title': title, 'description': description,
                                  'required': required}
        if format:
            self._parameters[name]['format'] = format

        return self

    def from_parameters(self, params):
        for param in params:
            self._parameters[param['name']] = param
        return self

    def from_dataclass(self, cls):
        try:
            import dataclasses
        except NameError:
            raise("Dataclasses not available.  Try 'pip install dataclasses' or use Python 3.7 or higher.")

        fields = dataclasses.fields(cls)
        for f in fields:
            param = {'name': f.name}
            if f.type == int:
                param['type'] = 'integer'
                param['format'] = 'int64'
            elif f.type == float:
                param['type'] = 'number'
                param['format'] = 'double'
            elif f.type == str:
                param['type'] = 'string'
            elif f.type == bool:
                param['type'] = 'boolean'
            elif f.type == object:
                param['type'] = 'object'
            elif f.type == datetime.date:
                param['type'] = 'string'
                param['format'] = 'date'
            elif f.type == datetime.datetime:
                param['type'] = 'string'
                param['format'] = 'date-time'
            elif repr(f.type).startswith('typing.Dict'):
                param['type'] = 'object'
            elif repr(f.type).startswith('typing.List'):
                param['type'] = 'array'
            elif f.type == list:
                param['type'] = 'array'
            elif f.type == dict:
                param['type'] = 'object'
            elif isinstance(f.type, dict):
                param['type'] = 'object'
            elif isinstance(f.type, collections.Iterable):
                param['type'] = 'array'
            else:
                param['type'] = 'string'

            log.debug("%s (%s): %s %s" % (f.name, f.type, param['type'], param.get('format', '')))

            self._parameters[f.name] = param

        return self

    def to_camel(self):
        doc = {
            'camel': self._camel,
            'name': self._name,
            'title': self._title,
            'description': self._description,
            'parameters': list(self._parameters.values())
        }

        return doc

    def build(self) -> Schema:
        schema = self.to_camel()
        self._client.save_type(schema)
        return Schema.get_schema(self._name, self._client)
