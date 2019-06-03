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

from cortex_client.modelrunner import ModelRunner
from cortex_client.types import InputMessage


class TestModelRunner(unittest.TestCase):

    def setUp(self):
        message = {
            "instanceId": "agent1", 
            "sessionId":"session1", 
            "channelId": "proc1", 
            "typeName": "aType", 
            "timestamp":"12:00:00", 
            "token": "foo",
            "payload": {"a": "pay_a", "c": "pay_c"},
            "apiEndpoint": "http://google.com", 
            "properties": {"a": "prop_a", 
                           "b": '[["prop_b"]]',
                           "d": '"Hello"',
                           "e": '{"k": [1,2,3]}'}
        }
        self.message = InputMessage.from_params(message)

    def test_prepare_request_args_01(self):
        r = ModelRunner._prepare_request_args(self.message)
        expect = {"a":"pay_a", 
                  "b":[["prop_b"]], 
                  "c":"pay_c",
                  "d":"Hello",
                  "e":{"k": [1,2,3]}
                 }
        self.assertEqual(r, expect)
