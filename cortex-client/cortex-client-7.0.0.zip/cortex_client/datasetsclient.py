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
import json
from typing import Dict

from .serviceconnector import ServiceConnector
from .types import InputMessage
from .client import build_client

class DatasetsClient:
    """
    A client used to manage datasets.
    """
    URIs = {'datasets': 'datasets',
            'content':  'content'}

    def __init__(self, url, version, token):
        self._serviceconnector = ServiceConnector(url, version, token)

    def save_dataset(self, dataset: Dict[str, object]):
        """
        Saves a dataset.

        :param dataset: A Cortex dataset as dict.
        """
        uri = self.URIs['datasets']
        body_s = json.dumps(dataset)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, body_s, headers)
        r.raise_for_status()
        return r.json()

    def get_dataframe(self, dataset_name: str):
        """
        Gets data from a dataset as a dataframe.

        :param dataset_name: The name of the dataset to pull data.
        :return: A dataframe dictionary
        """
        uri = '/'.join([self.URIs['datasets'], dataset_name, 'dataframe'])
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return r.json()

    def get_stream(self, stream_name: str):
        """
        Gets a dataset as a stream.
        """
        uri = '/'.join([self.URIs['datasets'], stream_name, 'stream'])
        r = self._serviceconnector.request('GET', uri, stream=True)
        r.raise_for_status()
        return r.raw

    def post_stream(self, stream_name, data):
        uri = '/'.join([self.URIs['datasets'], stream_name, 'stream'])
        headers = {"Content-Type": "application/json-lines"}
        r = self._serviceconnector.request('POST', uri, data, headers)
        print(r.text)
        r.raise_for_status()
        return r.json()

    def get_pipeline(self, dataset_name: str, pipeline_name: str):
        uri = '/'.join([self.URIs['datasets'], dataset_name, 'pipelines', pipeline_name])
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return r.json()


def build_datasetsclient(input_message: InputMessage, version) -> DatasetsClient:
    """
    Builds a DatasetsClient.
    """
    return build_client(DatasetsClient, input_message, version)
