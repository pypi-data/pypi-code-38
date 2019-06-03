"Tests for OutboundMessageDeque."
#   Copyright 2019 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
import unittest

sys.path.append("..")  # noqa

from wolk_gateway_module.outbound_message_deque import OutboundMessageDeque
from wolk_gateway_module.model.message import Message


class OutboundMessageDequeTests(unittest.TestCase):
    """OutboundMessageDeque Tests."""

    def test_put(self):
        """Test put message into storage."""
        deque = OutboundMessageDeque()

        self.assertTrue(deque.put("test"))
        self.assertEqual(deque.queue_size(), 1)

    def test_get_something(self):
        """Test get from empty storage."""
        deque = OutboundMessageDeque()
        value = "test"
        deque.put(value)

        self.assertEqual(value, deque.get())

    def test_get_nothing(self):
        """Test get message from storage."""
        deque = OutboundMessageDeque()
        deque.put(None)

        self.assertEqual(None, deque.get())

    def test_queue_size(self):
        """Test getting queue storage size."""
        deque = OutboundMessageDeque()
        deque.put(1)
        deque.put(2)
        deque.put(3)

        self.assertEqual(3, deque.queue_size())

    def test_remove(self):
        """Test removing from queue."""
        deque = OutboundMessageDeque()
        deque.put(1)
        deque.put(2)
        deque.put(3)

        deque.remove(2)

        self.assertEqual(2, deque.queue_size())

    def test_get_no_messages_for_device(self):
        """Test getting no messages for specific device from empty queue."""
        deque = OutboundMessageDeque()
        device_key = "some_key"

        self.assertFalse(deque.get_messages_for_device(device_key))

    def test_get_no_matching_messages_for_device(self):
        """Test getting no messages for specific device from queue."""
        deque = OutboundMessageDeque()
        device_key = "some_key"

        deque.put(Message("some_other_key"))
        deque.put(Message("another_key"))
        deque.put(Message("different_key"))

        self.assertFalse(deque.get_messages_for_device(device_key))

    def test_get_messages_for_device(self):
        """Test getting some messages for specific device from queue."""
        deque = OutboundMessageDeque()
        device_key = "some_key"

        deque.put(Message("some_key/2"))
        deque.put(Message("another_key"))
        deque.put(Message("some_key/1"))

        self.assertEqual(
            [Message("some_key/2"), Message("some_key/1")],
            deque.get_messages_for_device(device_key),
        )


if __name__ == "__main__":
    unittest.main()
