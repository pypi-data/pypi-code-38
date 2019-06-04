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
import io
import uuid
import unittest

from cortex_client.cache import CacheHandler
from cortex_client.types import Model

class TestCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cache = CacheHandler('/tmp/pythonlib-test')
        cls.model = Model('a1', 'p1', 'model-name', 'Model desc.', uuid.uuid4())

    def test_save_state_load_state_bytes_success(self):
        key = 'test-key-{}'.format(uuid.uuid4())
        data = b'some binary thing'
        self.cache.save_state(self.model, key, data)
        state = self.cache.load_state(self.model, key)
        self.assertEqual(state, data)

    def test_save_state_load_state_stream_success(self):
        key = 'test-key-{}'.format(uuid.uuid4())
        data = io.BytesIO(b"some data")
        self.cache.save_state(self.model, key, data)
        state = self.cache.load_state(self.model, key)
        self.assertEqual(state.read(), b'some data')

    def test_load_state_failure(self):
        state = self.cache.load_state(self.model, 'non-existent-key')
        self.assertEqual(state, None)

