from django import test

from ievv_opensource.ievv_sms.backends import pswin


@test.override_settings(PSWIN_DEFAULT_COUNTRY_CODE='47')
class TestBackend(test.TestCase):
    def test_clean_phone_number__no_country_code(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number('12345678'),
            '4712345678')

    def test_clean_phone_number__plus_country_code(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number('+9912345678'),
            '9912345678')

    def test_clean_phone_number__00_country_code(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number('009912345678'),
            '9912345678')

    def test_clean_phone_number__whitespace(self):
        backend = pswin.Backend(
            phone_number='x',
            message='x')
        self.assertEqual(
            backend.clean_phone_number(' 123 45 678 '),
            '4712345678')

    @test.override_settings(PSWIN_SENDER='test')
    def test_pswin_sender_from_setting(self):
        backend = pswin.Backend(
            phone_number='12345678',
            message='test')
        self.assertEqual(backend.pswin_sender, 'test')

    def test_pswin_sender_from_send_as(self):
        backend = pswin.Backend(
            phone_number='12345678',
            message='test',
            send_as='A')
        self.assertEqual(backend.pswin_sender, 'A')

    def test_pswin_sender_from_pswin_sender_arg(self):
        backend = pswin.Backend(
            phone_number='12345678',
            message='test',
            pswin_sender='A')
        self.assertEqual(backend.pswin_sender, 'A')

    def test_pswin_sender_pswin_sender_arg_before_send_as(self):
        backend = pswin.Backend(
            phone_number='12345678',
            message='test',
            send_as='A',
            pswin_sender='B')
        self.assertEqual(backend.pswin_sender, 'B')

    @test.override_settings(PSWIN_SENDER='A')
    def test_pswin_sender_send_as_before_setting(self):
        backend = pswin.Backend(
            phone_number='12345678',
            message='test',
            send_as='B')
        self.assertEqual(backend.pswin_sender, 'B')
