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

from cortex_client.agentclient import build_agentclient
from cortex_client.agentclient import AgentClient

from cortex_client.catalogclient import build_catalogclient
from cortex_client.catalogclient import CatalogClient

from cortex_client.connectionclient import build_connectionclient
from cortex_client.connectionclient import ConnectionClient

from cortex_client.datasetsclient import build_datasetsclient
from cortex_client.datasetsclient import DatasetsClient

from cortex_client.modelclient import build_modelclient
from cortex_client.modelclient import ModelClient

from cortex_client.client import build_client
from cortex_client.client import _Client

from cortex_client.types import InputMessage

class Test_Client(unittest.TestCase):

    def setUp(self):
        self.message = {
            "instanceId": "agent1", 
            "sessionId":"session1", 
            "channelId": "proc1", 
            "typeName": "aType", 
            "timestamp":"12:00:00", 
            "token": "foo",
            "payload": {},
            "apiEndpoint": "http://google.com", 
            "properties": {}
        }

    def test_client_builds(self):
        """
        Some cortex clients (e.g. AgentClient) provide a convenience build function
        (e.g. build_agentclient) that allows a caller to build a cortex client of
        that type

        We test these build functions and make sure that they actually make the correct
        corresponding cortex client.
        """
        # array of buildClient and Client Pairs
        buildClient_Client_List = [
            (build_agentclient, AgentClient),
            (build_catalogclient, CatalogClient),
            (build_connectionclient, ConnectionClient),
            (build_datasetsclient, DatasetsClient),
            (build_modelclient, ModelClient),
        ]
        # we take advantage of the fact all buildClient have same parameters
        # to loop over each pair and test their correspondence
        for buildClient_client in buildClient_Client_List:
            buildClient, clientClass = buildClient_client

            im = InputMessage.from_params(self.message)
            client = buildClient(im, 5)
            self.assertIsInstance(client, clientClass)

    def test_build_client_base_url(self):
        im = InputMessage.from_params(self.message)
        c = build_client(_Client, im, 2)
        self.assertIsInstance(c, _Client)
        self.assertEqual(c._serviceconnector.base_url, 'http://google.com/v2')

    def test_build_dataset_client(self):
        im = InputMessage.from_params(self.message)
        c = build_client(DatasetsClient, im, 16)
        self.assertIsInstance(c, DatasetsClient)
        self.assertEqual(c._serviceconnector.base_url, 'http://google.com/v16')