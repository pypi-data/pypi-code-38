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
from cortex import Cortex
from cortex.pipeline import Pipeline
from cortex_client import DatasetsClient

import os
import json
import uuid
import unittest
from mocket.mockhttp import Entry
from mocket import mocketize

import pandas as pd
from .fixtures import john_doe_token, mock_api_endpoint, build_mock_url


class DatasetTest(unittest.TestCase):
    """
    Tests for datasets. Test that they can be constructed and generate correct yaml. Eventually other tests
    """
    dataset_name = 'test/ds'
    unique_dataset_name = 'test/ds' + uuid.uuid4().hex
    data_file = './test/data/simple.csv'

    def setUp(self):
        self.cortex = Cortex.client(
            api_endpoint=mock_api_endpoint(), api_version=3, token=john_doe_token())
        self.test_dataset_builder = self.cortex.builder().dataset(self.dataset_name)

    def register_entry(self, verb, url, body):
        print('Registering mock for', verb, url)
        Entry.single_register(verb,
                              url,
                              status=200,
                              body=json.dumps(body))

    def local_dataset_builder(self, name): 
        local = Cortex.local()
        builder = local.builder()
        return builder.dataset(name)

    def test_can_build(self):
        self.assertTrue(self.test_dataset_builder is not None)

    @mocketize
    def test_to_camel(self):
        # set up mocks
        pipeline_name = 'test_pipeline'
        post_uri = DatasetsClient.URIs['datasets']
        get_uri = '/'.join([post_uri, self.dataset_name])
        head_uri = 'http://1.2.3.4:8000/v2/content/cortex/datasets/test/ds/a95148ae236a44a91cde4f7cd00f96e2.json'
        get_pipeline_uri = '/'.join([get_uri, 'pipelines', pipeline_name])
        get_returns = {'camel': '1.0.0', 'name': self.dataset_name, 'title': 'rahr',
                       'description': 'test dataset description', 'parameters': [], 'pipelines': {}}
        get_pipeline_returns = {'name': pipeline_name,
                                'steps': [], 'dependencies': []}
        post_returns = {'name': self.dataset_name}
        self.register_entry(Entry.GET, build_mock_url(get_uri), get_returns)
        self.register_entry(Entry.POST, build_mock_url(post_uri), post_returns)
        self.register_entry(Entry.GET, build_mock_url(
            get_pipeline_uri), get_pipeline_returns)
        self.register_entry(Entry.HEAD, head_uri, None)
        # configure dataset builder
        self.test_dataset_builder.title('rahr')
        self.test_dataset_builder.description('test dataset description')

        # test dataset builder to_camel
        result_camel = self.test_dataset_builder.to_camel()
        expected_camel = {
            'camel': '1.0.0', 'name': self.dataset_name,
            'title': 'rahr', 'description': 'test dataset description',
            'parameters': [], 'pipelines': {},
            'connectionName': None, 'connectionQuery': None,
        }
        self.assertDictEqual(result_camel, expected_camel)
        # make a dataset from the builder
        self.test_dataset_builder.from_df(
            pd.read_csv(self.data_file))
        test_ds = self.test_dataset_builder.build()
        test_ds.pipeline('test_pipeline')

        # test dataset to camel returns pipeline
        result = test_ds.to_camel()
        self.assertTrue('pipelines' in result)
        self.assertTrue(pipeline_name in result['pipelines'])


    def test_local_ds_to_camel(self):
        local_title = 'local rahr'
        local_description = 'test dataset description'
        expected_camel = {
            'camel': '1.0.0', 
            'name': self.unique_dataset_name,
            'title': local_title, 
            'description': local_description,
            'parameters': [],  
            'pipelines': {
                'test_pipeline': {
                    'context': {},
                    'dependencies': [],
                    'name': 'test_pipeline',
                    'steps': []
                }
            }
        }

        ds_builder = self.local_dataset_builder(self.unique_dataset_name)
        ds_builder.title(local_title)
        ds_builder.description(local_description)
        test_ds = ds_builder.build()
        test_ds.to_camel()
        test_ds.pipeline('test_pipeline')
        result_camel = test_ds.to_camel()
        # b/c _version is unreliable, (it depends on whether the test has been locally before)
        # we can't test the whole thing at once
        # self.assertDictEqual(result_camel, expected_camel)
        self.assertEqual(result_camel['camel'],expected_camel['camel'])
        self.assertEqual(result_camel['name'],expected_camel['name'])
        self.assertEqual(result_camel['title'],expected_camel['title'])
        self.assertEqual(result_camel['description'],expected_camel['description'])
        self.assertEqual(result_camel['parameters'],expected_camel['parameters'])
        self.assertDictEqual(result_camel['pipelines'],expected_camel['pipelines'])


    def test_get_dataframe(self):
        ds_builder = self.local_dataset_builder(self.unique_dataset_name)
        data_set = ds_builder.from_csv(self.data_file).build()
        df = data_set.get_dataframe()
        self.assertTrue(len(df.columns) is 2)