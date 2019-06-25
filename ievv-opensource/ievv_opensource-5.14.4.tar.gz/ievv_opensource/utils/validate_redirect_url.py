import re

from django.conf import settings
from django.core.exceptions import ValidationError


def is_valid_url(url):
    """
    Returns ``True`` if the provided URL matches the :setting:`IEVV_VALID_REDIRECT_URL_REGEX`
    regex.

    Args:
        url (str): An URL. Can just be a path too (E.g.: all of these work
            ``http://example.com``, ``/test``, ``http://example.com/test``.

    """
    allowed_redirect_url_regex = getattr(settings, 'IEVV_VALID_REDIRECT_URL_REGEX', r'^/.*$')
    return bool(re.match(allowed_redirect_url_regex, url))


def validate_url(url):
    """
    Validate the provided url against the regex in the :setting:`IEVV_VALID_REDIRECT_URL_REGEX`
    setting.

    Args:
        url (str): An URL. Can just be a path too (E.g.: all of these work
            ``http://example.com``, ``/test``, ``http://example.com/test``.

    Raises:
        django.core.exceptions.ValidationError: If the ``url`` is not valid.
    """
    if not is_valid_url(url):
        raise ValidationError('Invalid redirect URL: {}'.format(url))
