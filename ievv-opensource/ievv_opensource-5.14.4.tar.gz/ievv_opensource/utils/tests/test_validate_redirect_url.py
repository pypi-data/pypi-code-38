from django import test
from django.core.exceptions import ValidationError
from django.test import override_settings

from ievv_opensource.utils import validate_redirect_url


class TestIsValidUrl(test.TestCase):
    def test_path_is_valid_by_default(self):
        self.assertTrue(validate_redirect_url.is_valid_url('/test/ing'))

    def test_domain_is_not_valid_by_default(self):
        self.assertFalse(validate_redirect_url.is_valid_url('http://example.com/test/ing'))

    @override_settings(IEVV_VALID_REDIRECT_URL_REGEX='^(https://example\.com/|/).*$')
    def test_custom_regex(self):
        self.assertTrue(validate_redirect_url.is_valid_url('https://example.com/test/ing'))
        self.assertTrue(validate_redirect_url.is_valid_url('https://example.com/'))
        self.assertTrue(validate_redirect_url.is_valid_url('/test/path'))
        self.assertTrue(validate_redirect_url.is_valid_url('/'))
        self.assertFalse(validate_redirect_url.is_valid_url('http://example.com/test/ing'))
        self.assertFalse(validate_redirect_url.is_valid_url('http://example.com/'))
        self.assertFalse(validate_redirect_url.is_valid_url('https://example2.com/'))
        self.assertFalse(validate_redirect_url.is_valid_url('https://example2.com/test/ing'))


class TestValidateUrl(test.TestCase):
    def test_path_is_valid_by_default(self):
        # No ValidationError
        validate_redirect_url.validate_url('/test/ing')

    def test_domain_is_not_valid_by_default(self):
        with self.assertRaises(ValidationError):
            validate_redirect_url.validate_url('http://example.com/test/ing')

    @override_settings(IEVV_VALID_REDIRECT_URL_REGEX=r'^/test$')
    def test_invalid_url(self):
        with self.assertRaises(ValidationError):
            validate_redirect_url.validate_url('/test2')

    @override_settings(IEVV_VALID_REDIRECT_URL_REGEX=r'^/test$')
    def test_valid_url(self):
        # No ValidationError
        validate_redirect_url.validate_url('/test')
