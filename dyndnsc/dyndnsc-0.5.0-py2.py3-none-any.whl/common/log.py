# -*- coding: utf-8 -*-

"""Logging related code."""

class RedactingFormatter(object):
    """Logging formatter to redact logged records.
    """
    def __init__(self, orig_formatter, patterns):
        self.orig_formatter = orig_formatter
        self._patterns = patterns

    def format(self, record):
        """Redact log record.
        """
        msg = self.orig_formatter.format(record)
        for pattern in self._patterns:
            msg = msg.replace(pattern, "***")
        return msg

    def __getattr__(self, attr):
        return getattr(self.orig_formatter, attr)
