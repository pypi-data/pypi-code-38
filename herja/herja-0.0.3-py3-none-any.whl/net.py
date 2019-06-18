"""A collection of utilities for performing network requests/connections."""


import logging

from requests import Session as RequestsSession

from .constants import HEADER_DEFAULTS
from .settings import Settings


class Session(RequestsSession):
    """A requests session with custom headers set."""

    def __init__(self, header_tuples=None):
        """Initialize a special requests session with the default headers."""
        super(Session, self).__init__()

        for key, value in HEADER_DEFAULTS if header_tuples is None else header_tuples:
            self.headers[key] = value
            logging.debug('Set Header "%s" to "%s"', key, value)


def get_form_inputs(form_soup):
    """Get the inputs of a form in a dictionary format."""
    inputs = {}
    for element in form_soup.find_all('input'):
        key = element.attrs['name']
        value = element.attrs['value'] if 'value' in element.attrs else ''
        inputs[key] = value
    return inputs
