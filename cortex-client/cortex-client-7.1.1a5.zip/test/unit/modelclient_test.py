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
import unittest
import uuid

from mocket.mockhttp import Entry
from mocket import mocketize
import requests

from cortex_client.modelclient import ModelClient, Model


class TestModelClient(unittest.TestCase):

    def setUp(self):
        self.mc = ModelClient('http://localhost:123', 2, 'token')
        self.model = Model(agent_id='a1', 
                           processor_id='p1', 
                           name='TC-{}'.format(uuid.uuid4()), 
                           description='A model',
                           _id=str(uuid.uuid4()))

    @mocketize
    def test_log_event(self):
        uri = 'models/events'
        url = self.mc._serviceconnector._construct_url(uri)
        body={"response": 123}
        Entry.single_register(Entry.POST,
                              url,
                              status = 200,
                              body = json.dumps(body))
        r = self.mc.log_event(self.model, 'cortex.train.status', 'success')

        self.assertIsInstance(r, requests.Response)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), body)
