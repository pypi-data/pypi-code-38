# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Reflected XSS callback
"""
from cgi import escape
from logging import getLogger

from ..utils import STRING_CLASS, UNICODE_CLASS, is_string
from .regexp_rule import RegexpRule

LOGGER = getLogger(__name__)


class ReflectedXSSCB(RegexpRule):
    def post(self, original, _return, *args, **kwargs):
        """ Check if a template node returns a content that is in the
        query parameters
        """
        request = self.storage.get_current_request()

        if not request:
            LOGGER.warning("No request was recorded abort")
            return

        if not is_string(_return):
            LOGGER.debug("Non string passed, type %s", type(_return))
            return

        if request.params_contains(_return):
            # If the payload is malicious, record the attack
            matching_regexp = self.match_regexp(_return)
            if matching_regexp:
                self.record_attack(
                    {"found": matching_regexp, "payload": _return}
                )

            # Only if the callback should block, sanitize the string
            if self.block:
                return {
                    "status": "override",
                    "new_return_value": self._escape(_return),
                }

    @staticmethod
    def _escape(value):
        """ Escape a malicious value to make it safe
        """

        # Convert the value if it's a string subclass to bypass escape
        value_class = value.__class__
        if value_class not in (STRING_CLASS, UNICODE_CLASS):
            bases = value_class.__bases__

            if UNICODE_CLASS in bases:
                value = UNICODE_CLASS(value)
            elif STRING_CLASS in bases:
                value = STRING_CLASS(value)
            else:
                err_msg = "Value '{!r}' has invalid type and bases: {!r}"
                raise TypeError(err_msg.format(value, bases))

        # Convert to str before avoiding problems with Jinja2 Markup classes
        return escape(value, True)
