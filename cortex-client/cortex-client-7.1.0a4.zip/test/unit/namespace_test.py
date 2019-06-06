"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

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
import pandas as pd
from .fixtures import john_doe_token, mock_api_endpoint


class NameSpaceTest(unittest.TestCase):
    """Cortex assets, like datasets and skills, must be created within a 
       name space. That is, the path to the asset cannot be located in 
       the root directory. 'folder/file' is good, 'file' is bad."""

    def setUp(self):
        self.cortex = Cortex.client(api_endpoint=mock_api_endpoint(), api_version=3, token=john_doe_token())
        self.builder = self.cortex.builder()

    def test_dataset_rejects_invalid_namespace(self):
        test_df = pd.read_csv('./test/data/ames/test.csv')
        with self.assertRaises(ValueError):
            self.builder.dataset('name-without-namespace')
        
    def test_dataset_accepts_valid_namespace(self):
        test_df = pd.read_csv('./test/data/ames/test.csv')
        dsb = self.builder.dataset('namespace/name')
        self.assertEquals(dsb.to_camel().get('name'),'namespace/name')

    def test_skill_rejects_invalid_namespace(self):
        with self.assertRaises(ValueError):
            self.builder.skill('name-without-namespace')

    def test_skill_accepts_valid_namespace(self):
        sb = self.builder.skill('namespace/name')
        self.assertEquals(sb.to_camel().get('name'),'namespace/name')

    def test_action_rejects_invalid_namespace(self):   
        with self.assertRaises(ValueError):
            self.builder.action('name-without-namespace')

    def test_action_accepts_valid_namespace(self):
        ab = self.builder.action('namespace/name')
        self.assertEquals(ab.name,'namespace/name')

    def test_connection_rejects_invalid_namespace(self):
        with self.assertRaises(ValueError):
            self.builder.connection('name-without-namespace')
        
    def test_connection_accepts_valid_namespace(self):
        cb = self.builder.connection('namespace/name')
        self.assertEquals(cb.to_camel().get('name'),'namespace/name')

    def test_schema_rejects_invalid_namespace(self):
        with self.assertRaises(ValueError):
            self.builder.schema('name-without-namespace')
        
    def test_schema_accepts_valid_namespace(self):
        cb = self.builder.schema('namespace/name')
        self.assertEquals(cb.to_camel().get('name'),'namespace/name')