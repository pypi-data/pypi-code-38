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
import unittest

from cortex import Cortex
from .fixtures import john_doe_token, mock_api_endpoint


class TestConnection(unittest.TestCase):

    def setUp(self):
        self.cortex = Cortex.client(api_endpoint=mock_api_endpoint(), api_version=3, token=john_doe_token())

    def test_connection_to_camel(self):
        builder = self.cortex.builder()
        con = builder.connection('unittest/Connection1').title('Connection Unit Test').description('Building a Connection').connection_type('mongo')
        con = con.params(name='mongoUri', value='uri')
        con_save = con.to_camel()
        connection_camel = {
            'camel': '1.0.0',
            'name': 'unittest/Connection1',
            'title': 'Connection Unit Test',
            'connectionType': 'mongo',
            'params': [{'name': 'mongoUri',
                        'value': 'uri'}],
            'description': 'Building a Connection'
        }
        self.assertEqual(con_save, connection_camel)
