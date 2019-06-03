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

from cortex_client.types import InputMessage

class TestInputMessage(unittest.TestCase):

    def setUp(self):
        self.im = {
                    "instanceId": "agent1", 
                    "sessionId": "session1", 
                    "channelId": "proc1", 
                    "token": "foo", 
                    "apiEndpoint": "http://localhost:8000", 
                    "properties": {}, 
                    "payload": {}
                  }

    def test_from_params_exact(self):
        d = self.im.copy()
        r = InputMessage.from_params(d)

        self.assertEqual(r.to_params(), self.im)


    def test_from_params_more_than_expected(self):
        d = self.im.copy()
        d['extra'] = 'extra'
        r = InputMessage.from_params(d)

        self.assertNotEqual(r, d)
        self.assertEqual(r.to_params(), self.im)

