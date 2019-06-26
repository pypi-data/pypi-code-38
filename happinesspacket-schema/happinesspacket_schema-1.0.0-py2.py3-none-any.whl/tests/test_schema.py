import unittest

from jsonschema import ValidationError
from .. import schema


class MessageV1Tests(unittest.TestCase):

    msg_class = schema.MessageV1

    def setUp(self):
        self.unknown_sender_message = {
            "id": "RandomString",
            "sender": "Anonymous",
            "recipient": "John Doe"
        }
        self.known_sender_message = {
            "id": "RandomString",
            "sender": "John Doe",
            "recipient": "John Doe v2"
        }

    def test_unknown_sender_message(self):
        """
        Assert the message schema validates a message with an unknown sender.
        """
        message = self.msg_class(body=self.unknown_sender_message)

        message.validate()

    def test_known_sender_message(self):
        """Assert the message schema validates with a known sender."""
        message = self.msg_class(body=self.known_sender_message)

        message.validate()

    def test_str_for_known_sender_message(self):
        """Assert __str__ produces a human-readable message for a message with all fields."""
        expected_str = "John Doe sent a happiness packet to John Doe v2"
        message = self.msg_class(body=self.known_sender_message)

        message.validate()
        self.assertEqual(expected_str, str(message))

    def test_str_for_unknown_sender_message(self):
        """Assert __str__ produces a human-readable message for a unknown sender message."""
        expected_str = "Anonymous sent a happiness packet to John Doe"
        message = self.msg_class(body=self.unknown_sender_message)

        message.validate()
        self.assertEqual(expected_str, str(message))

    def test_summary_for_known_sender_message(self):
        """Assert the summary matches the sender and then the recipient for a known sender message."""
        message = self.msg_class(body=self.known_sender_message)

        self.assertEqual("John Doe, John Doe v2", message.summary)
    
    def test_summary_for_unknown_sender_message(self):
        """Assert the summary matches the recipient for a unknown sender message."""
        message = self.msg_class(body=self.unknown_sender_message)

        self.assertEqual("John Doe", message.summary)

    def test_sender(self):
        """Assert the message provides a "sender" attribute."""
        message = self.msg_class(body=self.known_sender_message)

        self.assertEqual("John Doe", message.sender)

    def test_recipient(self):
        """Assert the message provides a "recipient" attribute."""
        message = self.msg_class(body=self.known_sender_message)

        self.assertEqual("John Doe v2", message.recipient)

    def test_usernames_for_known_sender_message(self):
        """Assert the message provides a "usernames" attribute in known sender message."""
        message = self.msg_class(body=self.known_sender_message)

        self.assertEqual(['John Doe', 'John Doe v2'], message.usernames)
    
    def test_usernames_for_unknown_sender_message(self):
        """Assert the message provides a "usernames" attribute in unknown sender message."""
        message = self.msg_class(body=self.unknown_sender_message)
        
        self.assertEqual(['John Doe',], message.usernames)

    def test_packages(self):
        """Assert the message provides a "packages" attribute."""
        message = self.msg_class(body=self.known_sender_message)
        
        self.assertEqual([], message.packages)