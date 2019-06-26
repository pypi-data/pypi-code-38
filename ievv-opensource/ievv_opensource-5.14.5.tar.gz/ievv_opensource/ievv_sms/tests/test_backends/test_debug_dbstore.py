from django import test

from ievv_opensource.ievv_sms.backends import debug_dbstore
from ievv_opensource.ievv_sms.models import DebugSmsMessage


class TestBackend(test.TestCase):
    def test_sms_record_is_created_in_db(self):
        debug = debug_dbstore.Backend(message="Hi there!", phone_number="1234567", send_as='7654321')
        debug.send()
        self.assertEqual(
            DebugSmsMessage.objects.first().message,
            "Hi there!")
        self.assertEqual(
            DebugSmsMessage.objects.first().phone_number,
            "1234567")
        self.assertEqual(
            DebugSmsMessage.objects.first().send_as,
            "7654321")

    def test_sms_record_send_as_default_blank(self):
        debug = debug_dbstore.Backend(message="Hi there!", phone_number="1234567")
        debug.send()
        self.assertEqual(
            DebugSmsMessage.objects.first().send_as,
            '')
