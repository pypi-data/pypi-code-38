from django import test

from ievv_opensource.ievv_sms import sms_registry


class TestAbstractSmsBackend(test.TestCase):
    def test_get_sms_text_length(self):
        self.assertEqual(sms_registry.AbstractSmsBackend.get_sms_text_length('Åge{^'), 7)

    def test_get_max_length(self):
        self.assertEqual(sms_registry.AbstractSmsBackend.get_max_length(), 918)

    def test_get_part_count_simple(self):
        self.assertEqual(sms_registry.AbstractSmsBackend.get_part_count('Test'), 1)

    def test_get_part_count_exactly_fill_1(self):
        self.assertEqual(sms_registry.AbstractSmsBackend.get_part_count('x' * 160), 1)

    def test_get_part_count_6(self):
        self.assertEqual(sms_registry.AbstractSmsBackend.get_part_count('x' * 900), 6)
