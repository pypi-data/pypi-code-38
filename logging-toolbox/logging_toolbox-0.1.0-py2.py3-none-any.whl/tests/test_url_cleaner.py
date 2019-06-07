from unittest import TestCase

from logging_toolbox.utils import clean_url


class UrlCleanerTester(TestCase):
    """Tests the clean_url function."""

    def test_no_auth(self):
        """
        Test url with no user info component.

        Expected result: output is identical to input.
        """
        url = 'amqps://test.server'
        result = url
        self.assertEqual(clean_url(url), result)

    def test_no_password(self):
        """
        Test url with no password info component.

        Expected result: output is identical to input.
        """
        url = 'amqps://username@test.server'
        result = url
        self.assertEqual(clean_url(url), result)

    def test_port(self):
        """
        Test url with no user info component.

        Expected result: output is identical to input.
        """
        url = 'amqps://test.server:1234/'
        result = url
        self.assertEqual(clean_url(url), result)

    def test_no_port(self):
        """
        Test url with no user info component.

        Expected result: output has the password replaced with 6
        asterisks.
        """
        url = 'amqps://username:password@test.server/'
        result = 'amqps://username:******@test.server/'
        self.assertEqual(clean_url(url), result)

    def test_kitchen_sink(self):
        """
        Test url all components.

        Expected result: output has the password replaced with 6
        asterisks.
        """
        url = 'amqps://username:password@test.server:1234/?queryparam=1&abc=2#anchor'
        result = 'amqps://username:******@test.server:1234/?queryparam=1&abc=2#anchor'
        self.assertEqual(clean_url(url), result)
